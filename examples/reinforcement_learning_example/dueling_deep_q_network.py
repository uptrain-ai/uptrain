import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from agent import AbstractAgent
from deep_q_network import DeepQNetwork


class DuelingDeepQNetwork(DeepQNetwork):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.V = nn.Linear(in_features=self.hidden_dims[-1], out_features=1)
        self.A = nn.Linear(
            in_features=self.hidden_dims[-1], out_features=self.num_actions
        )

        self.to(self.device)

    def forward(self, state):
        x = state
        for layer in self.layers:
            x = F.relu(layer(x))
        V = self.V(x)
        A = self.A(x)
        Q = V + (A - torch.mean(A, dim=1, keepdim=True))
        return Q

    def advantage(self, state):
        x = state
        for layer in self.layers:
            x = F.relu(layer(x))
        A = self.A(x)
        return A


class DuelingDQNAgent(AbstractAgent):
    def __init__(self, *args, filename="dueling_dqn_agent", **kwargs) -> None:
        super().__init__(*args, filename=filename, **kwargs)
        self.q_network = DuelingDeepQNetwork(
            input_dims=self.input_dims,
            hidden_dims=self.hidden_dims,
            num_actions=self.num_actions,
            device=self.device,
        )

    def get_action_training(self, observation) -> int:
        if np.random.random() < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            state = torch.tensor(np.array([observation])).to(self.device)
            actions = self.q_network.advantage(state)
            action = torch.argmax(actions).item()
        return int(action)

    def get_action_testing(self, observation) -> int:
        state = torch.tensor(np.array([observation])).to(self.device)
        actions = self.q_network.advantage(state)
        action = int(torch.argmax(actions).item())
        return int(action)

    def learn(self) -> None:
        if self.memory.memory_counter < self.batch_size:
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
