import numpy as np

from typing import List, Tuple


class ReplayBuffer:
    def __init__(self, memory_size: int, input_shape: List[int]) -> None:
        """Initializes the ReplayBuffer.

        Parameters
        ----------
        memory_size: int
            The size of the replay buffer.
        input_shape: List[int]
            The shape of the input.
        """
        self.memory_size = memory_size
        self.memory_counter = 0
        self.state_memory = np.zeros((self.memory_size, *input_shape), np.float32)
        self.new_state_memory = np.zeros((self.memory_size, *input_shape), np.float32)
        self.action_memory = np.zeros(self.memory_size, np.int32)
        self.reward_memory = np.zeros(self.memory_size, np.float32)
        self.terminal_memory = np.zeros(self.memory_size, np.bool8)

    def store_transition(self, state, action, reward, new_state, terminal) -> None:
        """Stores a transition in the replay buffer.

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
        index = self.memory_counter % self.memory_size
        self.state_memory[index] = state
        self.new_state_memory[index] = new_state
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.terminal_memory[index] = terminal
        self.memory_counter += 1

    def sample_buffer(self, batch_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Samples a batch from the replay buffer.

        Parameters
        ----------
        batch_size: int
            The size of the batch to sample.
        
        Returns
        -------
        states: np.ndarray
            The sampled states.
        actions: np.ndarray
            The sampled actions.
        rewards: np.ndarray
            The sampled rewards.
        new_states: np.ndarray
            The sampled next states.
        terminals: np.ndarray
            The sampled terminal flag for states.
        """
        max_memory = min(self.memory_counter, self.memory_size)
        batch = np.random.choice(max_memory, batch_size, replace=False)
        states = self.state_memory[batch]
        new_states = self.new_state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        terminals = self.terminal_memory[batch]
        return states, actions, rewards, new_states, terminals
