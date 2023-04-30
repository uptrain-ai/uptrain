import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from typing import List
from agent import AbstractAgent


class DeepQNetwork(nn.Module):
    """Implementation of a Deep Q Network."""

    def __init__(
        self,
        input_dims: List[int],
        hidden_dims: List[int],
        num_actions: int,
        *,
        device: str = "cpu",
        lr: float = 0.001,
    ) -> None:
        """Initializes the Deep Q-network model.

        Parameters
        ----------
        input_dims: List[int]
            The shape of the input state.
        hidden_dims: List[int]
            The number of units in each hidden layer.
        num_actions: int
            The number of possible actions.
        device: str, optional
            The device to run the model on (default is "cpu").
        lr: float, optional
            The learning rate for the optimizer (default is 0.001).
        """
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.hidden_dims = hidden_dims
        self.num_actions = num_actions
        self.device = device
        self.lr = lr

        self.layers = nn.ModuleList()
        self.layers.append(
            nn.Linear(in_features=input_dims[0], out_features=hidden_dims[0])
        )
        for i in range(len(hidden_dims) - 1):
            self.layers.append(
                nn.Linear(in_features=hidden_dims[i], out_features=hidden_dims[i + 1])
            )
        self.Q = nn.Linear(in_features=hidden_dims[-1], out_features=num_actions)

        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()

        self.to(device)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Computes the Q-values for the given state.

        Parameters
        ----------
        state: torch.Tensor
            The input state.

        Returns
        -------
        Q : torch.Tensor
            The Q-values for the given state.
        """
        x = state
        for layer in self.layers:
            x = F.relu(layer(x))
        Q = self.Q(x)
        return Q


class DQNAgent(AbstractAgent):
    """Implementation of an agent that uses the Deep Q Network."""

    def __init__(self, *args, filename="dqn_agent", **kwargs) -> None:
        """Initializes the DQNAgent.

        Parameters
        ----------
        *args
            The positional arguments for the AbstractAgent.
        filename: str, optional
            The name of the file to save the model to (default is "dqn_agent").
        **kwargs
            The keyword arguments for the AbstractAgent.
        """
        super().__init__(*args, filename=filename, **kwargs)
        self.q_network = DeepQNetwork(
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
            state = torch.tensor(np.array([observation])).to(self.q_network.device)
            actions = self.q_network.forward(state)
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
        state = torch.tensor(np.array([observation])).to(self.q_network.device)
        actions = self.q_network.forward(state)
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
