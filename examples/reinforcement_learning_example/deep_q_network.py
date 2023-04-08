import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from typing import List
from agent import AbstractAgent


class DeepQNetwork(nn.Module):
    def __init__(
        self,
        input_dims: List[int],
        hidden_dims: List[int],
        num_actions: int,
        *,
        device: str = "cpu",
        lr: float = 0.001,
    ) -> None:
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.hidden_dims = hidden_dims
        self.num_actions = num_actions
        self.device = device

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

    def forward(self, state):
        x = state
        for layer in self.layers:
            x = F.relu(layer(x))
        Q = self.Q(x)
        return Q


class DQNAgent(AbstractAgent):
    def __init__(self, *args, filename="dqn_agent", **kwargs) -> None:
        super().__init__(*args, filename=filename, **kwargs)
        self.q_network = DeepQNetwork(
            input_dims=self.input_dims,
            hidden_dims=self.hidden_dims,
            num_actions=self.num_actions,
            device=self.device,
        )

    def get_action_training(self, observation) -> int:
        if np.random.random() < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            state = torch.tensor(np.array([observation])).to(self.q_network.device)
            actions = self.q_network.forward(state)
            action = torch.argmax(actions).item()
        return int(action)

    def get_action_testing(self, observation) -> int:
        state = torch.tensor(np.array([observation])).to(self.q_network.device)
        actions = self.q_network.forward(state)
        action = int(torch.argmax(actions).item())
        return int(action)

    def learn(self) -> None:
        if self.memory.memory_counter < self.warmup_steps:
            return

        states, actions, rewards, new_states, terminals = map(
            lambda x: torch.tensor(x).to(self.device),
            self.memory.sample_buffer(self.batch_size),
        )
        batch_indices = np.arange(self.batch_size)

        q_eval = self.q_network.forward(states)[batch_indices, actions]
        q_next = self.q_network.forward(new_states)
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

    def save_model(self) -> None:
        torch.save(self.q_network, f"{self.filename}_q_network.pt")

    def load_model(self) -> None:
        self.q_network = torch.load(f"{self.filename}_q_network.pt")
