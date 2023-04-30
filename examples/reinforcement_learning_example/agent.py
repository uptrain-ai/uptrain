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
        warmup_steps: int = 100,
        **kwargs,
    ) -> None:
        """Initialize the AbstractAgent.

        Parameters
        ----------
        num_actions: int
            The number of possible actions.
        input_dims: List[int]
            The dimensions of the input.
        environment: str, optional
            The name of the environment (default is "").
        learning_rate: float, optional
            The learning rate for the optimizer (default is 0.001).
        gamma: float, optional
            The discount factor (default is 0.99).
        batch_size: int, optional
            The batch size (default is 64).
        epsilon: float, optional
            The initial value for epsilon (default is 1).
        epsilon_decrement: float, optional
            The amount to decrement epsilon by (default is 0.001).
        min_epsilon: float, optional
            The minimum value for epsilon (default is 0.01).
        memory_size: int, optional
            The size of the replay buffer (default is 100000).
        filename: str, optional
            The name of the file to save the model to (default is "agent").
        hidden_dims: List[int], optional
            The number of units in each hidden layer (default is [128, 128]).
        device: str, optional
            The device to run the model on (default is "cpu").
        warmup_steps: int, optional
            The number of steps to take before training (default is 100).
        """
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
        self.warmup_steps = warmup_steps
        self.memory = ReplayBuffer(memory_size, input_dims)

    def store_transition(self, state, action, reward, new_state, terminal) -> None:
        """Store a transition in the replay buffer.

        Parameters
        ----------
        state: np.ndarray
            The current state.
        action: int
            The action taken.
        reward: float
            The reward received.
        new_state: np.ndarray
            The new state.
        terminal: bool
            Whether or not the episode is over.
        """
        self.memory.store_transition(state, action, reward, new_state, terminal)

    @abc.abstractmethod
    def get_action_training(self, observation) -> None:
        """Get an action during training.
        
        Parameters
        ----------
        observation: np.ndarray
            The current state.
        
        Note that this method is an abstract method, so it must be implemented
        in the child class.
        """
        return

    @abc.abstractmethod
    def get_action_testing(self, observation) -> None:
        """Get an action during testing.
        
        Parameters
        ----------
        observation: np.ndarray
            The current state.
        
        Note that this method is an abstract method, so it must be implemented
        in the child class.
        """
        return

    @abc.abstractmethod
    def learn(self) -> None:
        """Makes the model undergo training.
        
        Note that this method is an abstract method, so it must be implemented
        in the child class.
        """
        return

    @abc.abstractmethod
    def save_model(self) -> None:
        """Saves the model.
        
        Note that this method is an abstract method, so it must be implemented
        in the child class.
        """
        return

    @abc.abstractmethod
    def load_model(self) -> None:
        """Loads the model.
        
        Note that this method is an abstract method, so it must be implemented
        in the child class.
        """
        return
