import abc

from memory import ReplayBuffer
from typing import List


class AbstractAgent(abc.ABC):
    def __init__(
        self,
        num_actions: int,
        input_dims: List[int],
        *,
        environment: str = "",
        learning_rate: float = 0.001,
        gamma: float = 0.99,
        batch_size: int = 64,
        epsilon: float = 1,
        epsilon_decrement: float = 0.001,
        min_epsilon: float = 0.01,
        memory_size: int = 100000,
        filename: str = "agent",
        hidden_dims: List[int] = [128, 128],
        device: str = "cpu",
        **kwargs,
    ) -> None:
        self.num_actions = num_actions
        self.input_dims = input_dims
        self.action_space = list(range(num_actions))
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.batch_size = batch_size
        self.epsilon = epsilon
        self.epsilon_decrement = epsilon_decrement
        self.min_epsilon = min_epsilon
        self.memory_size = memory_size
        self.filename = f"{environment}_{filename}"
        self.hidden_dims = hidden_dims
        self.device = device
        self.memory = ReplayBuffer(memory_size, input_dims)

    def store_transition(self, state, action, reward, new_state, terminal) -> None:
        self.memory.store_transition(state, action, reward, new_state, terminal)

    @abc.abstractmethod
    def get_action_training(self, observation) -> None:
        return

    @abc.abstractmethod
    def get_action_testing(self, observation) -> None:
        return

    @abc.abstractmethod
    def learn(self) -> None:
        return

    @abc.abstractmethod
    def save_model(self) -> None:
        return

    @abc.abstractmethod
    def load_model(self) -> None:
        return
