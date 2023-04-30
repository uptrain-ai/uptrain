import numpy as np
import torch

from dueling_deep_q_network import DuelingDeepQNetwork, DuelingDQNAgent


class DoubleDuelingDQNAgent(DuelingDQNAgent):
    """Implementation of an agent that uses the Double Dueling Deep Q Network."""

    def __init__(
        self,
        *args,
        target_update_frequency: int = 100,
        filename="double_dueling_dqn_agent",
        **kwargs,
    ) -> None:
        """Initializes the DoubleDuelingDQNAgent.

        Parameters
        ----------
        *args
            The positional arguments for the AbstractAgent.
        target_update_frequency: int, optional
            The frequency to update the target network (default is 100).
        filename: str, optional
            The name of the file to save the model to (default is "double_dueling_dqn_agent").
        **kwargs
            The keyword arguments for the AbstractAgent.
        """
        super().__init__(*args, filename=filename, **kwargs)
        self.target_update_frequency = target_update_frequency
        self.q_network = DuelingDeepQNetwork(
            input_dims=self.input_dims,
            hidden_dims=self.hidden_dims,
            num_actions=self.num_actions,
            device=self.device,
        )
        self.q_target_network = DuelingDeepQNetwork(
            input_dims=self.input_dims,
            hidden_dims=self.hidden_dims,
            num_actions=self.num_actions,
            device=self.device,
        )
        self.step_count = 0

    def learn(self) -> None:
        """Learns from the experiences in the replay buffer."""

        # Do not learn if there are not enough experiences in the replay buffer
        if self.memory.memory_counter < self.warmup_steps:
            return
        
        # Update the target network
        if self.step_count % self.target_update_frequency == 0:
            self.q_target_network.load_state_dict(self.q_network.state_dict())

        # Sample a batch of experiences from the replay buffer
        states, actions, rewards, new_states, terminals = map(
            lambda x: torch.tensor(x).to(self.device),
            self.memory.sample_buffer(self.batch_size),
        )
        batch_indices = np.arange(self.batch_size)

        # Compute Q-values by the evaluation network
        q_eval = self.q_network.forward(states)[batch_indices, actions]

        # Compute Q-values by the target network
        q_next = self.q_target_network.forward(new_states)
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

        # Increment the step count
        self.step_count += 1

    def save_model(self) -> None:
        """Saves the model."""
        torch.save(self.q_network, f"{self.filename}_q_network.pt")
        torch.save(self.q_target_network, f"{self.filename}_q_target_network.pt")

    def load_model(self) -> None:
        """Loads the model."""
        self.q_network = torch.load(f"{self.filename}_q_network.pt")
        self.q_target_network = torch.load(f"{self.filename}_q_target_network.pt")
