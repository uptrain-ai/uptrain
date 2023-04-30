import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from agent import AbstractAgent
from deep_q_network import DeepQNetwork


class DuelingDeepQNetwork(DeepQNetwork):
    """Implementation of a Dueling Deep Q Network."""

    def __init__(self, *args, **kwargs) -> None:
        """Initializes the DuelingDeepQNetwork.

        Parameters
        ----------
        *args
            The positional arguments for the DeepQNetwork.
        **kwargs
            The keyword arguments for the DeepQNetwork.
        """
        super().__init__(*args, **kwargs)
        self.V = nn.Linear(in_features=self.hidden_dims[-1], out_features=1)

        self.optimizer = optim.Adam(self.parameters(), lr=self.lr)
        self.loss = nn.MSELoss()

        self.to(self.device)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Computes the Q-values for the given state.
        
        Parameters
        ----------
        state: torch.Tensor
            The input state.
        
        Returns
        -------
        Q: torch.Tensor
            The Q-values for the given state.
        """
        x = state
        for layer in self.layers:
            x = F.relu(layer(x))
        V = self.V(x)
        A = self.Q(x)
        Q = V + (A - torch.mean(A, dim=1, keepdim=True))
        return Q

    def advantage(self, state: torch.Tensor) -> torch.Tensor:
        """Computes the advantage for the given state.

        Parameters
        ----------
        state: torch.Tensor
            The input state.
        
        Returns
        -------
        A: torch.Tensor
            The advantage for the given state.
        """
        x = state
        for layer in self.layers:
            x = F.relu(layer(x))
        A = self.Q(x)
        return A


class DuelingDQNAgent(AbstractAgent):
    """Implementation of an agent that uses the Dueling Deep Q Network."""

    def __init__(self, *args, filename="dueling_dqn_agent", **kwargs) -> None:
        """Initializes the DuelingDQNAgent.

        Parameters
        ----------
        *args
            The positional arguments for the AbstractAgent.
        filename: str, optional
            The name of the file to save the model to (default is "dueling_dqn_agent").
        **kwargs
            The keyword arguments for the AbstractAgent.
        """
        super().__init__(*args, filename=filename, **kwargs)
        self.q_network = DuelingDeepQNetwork(
            input_dims=self.input_dims,
            hidden_dims=self.hidden_dims,
            num_actions=self.num_actions,
            device=self.device,
        )

    def get_action_training(self, observation) -> int:
        """Returns the action to take given the current observation.
        
        Parameters
        ----------
        observation: np.ndarray
            The current observation.
        
        Returns
        -------
        action: int
            The action to take.
        
        Notes
        -----
        The action is chosen using the epsilon-greedy policy.
        """
        if np.random.random() < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            state = torch.tensor(np.array([observation])).to(self.device)
            actions = self.q_network.advantage(state)
            action = torch.argmax(actions).item()
        return int(action)

    def get_action_testing(self, observation) -> int:
        """Returns the action to take given the current observation.

        Parameters
        ----------
        observation: np.ndarray
            The current observation.
        
        Returns
        -------
        action: int
            The action to take.
        
        Notes
        -----
        Instead of using the epsilon-greedy policy, the action is chosen based
        on what the model has learnt so far and hence, no randomness is present
        in the action chosen unlike `get_action_training`.
        """
        state = torch.tensor(np.array([observation])).to(self.device)
        actions = self.q_network.advantage(state)
        action = int(torch.argmax(actions).item())
        return int(action)

    def learn(self) -> None:
        """Learns from the experiences in the replay buffer."""

        # Do not learn if there are not enough experiences in the replay buffer
        if self.memory.memory_counter < self.warmup_steps:
            return

        # Sample a batch of experiences from the replay buffer
        states, actions, rewards, new_states, terminals = map(
            lambda x: torch.tensor(x).to(self.device),
            self.memory.sample_buffer(self.batch_size),
        )
        batch_indices = np.arange(self.batch_size)

        # Compute Q-values by the evaluation network
        q_eval = self.q_network.forward(states)[batch_indices, actions]

        # Compute Q-values by the target network
        q_next = self.q_network.forward(new_states)
        q_next[terminals] = 0

        q_target = rewards + self.gamma * torch.max(q_next, dim=1)[0]

        # Compute the loss
        loss = self.q_network.loss(q_target, q_eval).to(self.device)

        # Backpropagate the loss
        self.q_network.optimizer.zero_grad()
        loss.backward()
        self.q_network.optimizer.step()

        # Epsilon-greedy policy
        self.epsilon = (
            self.epsilon - self.epsilon_decrement
            if self.epsilon > self.min_epsilon
            else self.min_epsilon
        )

    def save_model(self) -> None:
        """Saves the model."""
        torch.save(self.q_network, f"{self.filename}_q_network.pt")

    def load_model(self) -> None:
        """Loads the model."""
        self.q_network = torch.load(f"{self.filename}_q_network.pt")
