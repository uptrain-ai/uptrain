import numpy as np
import torch

from dueling_deep_q_network import DuelingDeepQNetwork, DuelingDQNAgent


class DoubleDuelingDQNAgent(DuelingDQNAgent):
    def __init__(
        self,
        *args,
        target_update_frequency: int = 100,
        filename="double_dueling_dqn_agent",
        **kwargs,
    ) -> None:
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
        if self.memory.memory_counter < self.batch_size:
            return
        if self.step_count % self.target_update_frequency == 0:
            self.q_target_network.load_state_dict(self.q_network.state_dict())

        states, actions, rewards, new_states, terminals = map(
            lambda x: torch.tensor(x).to(self.device),
            self.memory.sample_buffer(self.batch_size),
        )
        batch_indices = np.arange(self.batch_size)

        q_eval = self.q_network.forward(states)[batch_indices, actions]
        q_next = self.q_target_network.forward(new_states)
        q_next[terminals] = 0

        q_target = rewards + self.gamma * torch.max(q_next, dim=1)[0]

        loss = self.q_network.loss(q_target, q_eval).to(self.device)
        self.q_network.optimizer.zero_grad()
        loss.backward()
        self.q_network.optimizer.step()

        self.epsilon = (
            self.epsilon - self.epsilon_decrement
            if self.epsilon > self.min_epsilon
            else self.min_epsilon
        )
        self.step_count += 1

    def save_model(self) -> None:
        torch.save(self.q_network, f"{self.filename}_q_network.pt")
        torch.save(self.q_target_network, f"{self.filename}_q_target_network.pt")

    def load_model(self) -> None:
        self.q_network = torch.load(f"{self.filename}_q_network.pt")
        self.q_target_network = torch.load(f"{self.filename}_q_target_network.pt")
