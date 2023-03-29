import gymnasium as gym
import numpy as np
import sys
import torch

from deep_q_network import DQNAgent
from double_deep_q_network import DoubleDQNAgent
from dueling_deep_q_network import DuelingDQNAgent
from double_dueling_deep_q_network import DoubleDuelingDQNAgent


config = {
    "environment": "LunarLander-v2",
    # 'environment': "MountainCar-v0",
    "max_episode_step_count": 400,
    "num_episodes": 5,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "gamma": 0.99,
    "learning_rate": 0.001,
    "epsilon": 1,
    "epsilon_decrement": 0.0001,
    "min_epsilon": 0.01,
    "memory_size": 100000,
    "batch_size": 64,
    "hidden_dims": [64, 32],
    "target_update_frequecy": 1000,
}


def main():
    env = gym.make(
        config.get("environment"),
        max_episode_steps=config.get("max_episode_step_count"),
    )
    # agent = DQNAgent(num_actions=env.action_space.n, input_dims=env.observation_space.shape, **config)
    # agent = DoubleDQNAgent(num_actions=env.action_space.n, input_dims=env.observation_space.shape, **config)
    # agent = DuelingDQNAgent(num_actions=env.action_space.n, input_dims=env.observation_space.shape, **config)
    agent = DoubleDuelingDQNAgent(
        num_actions=env.action_space.n, input_dims=env.observation_space.shape, **config
    )

    if sys.argv[1] == "train":
        scores = []
        eps_history = []

        for i in range(config.get("num_episodes")):
            done = False
            score = 0
            steps = 0
            observation = env.reset()[0]

            while not done:
                action = agent.get_action_training(observation)
                observation_, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                score += reward
                steps += 1
                agent.store_transition(observation, action, reward, observation_, done)
                observation = observation_
                agent.learn()

            scores.append(score)
            eps_history.append(agent.epsilon)
            avg_score = np.mean(scores[-100:])

            print(
                "episode %d" % i,
                "steps %d" % steps,
                "score %.1f" % score,
                "average score %.1f" % avg_score,
                "epsilon %.2f" % agent.epsilon,
            )

        agent.save_model()

    elif sys.argv[1] == "test":
        env = gym.make(
            config.get("environment"),
            max_episode_steps=config.get("max_episode_step_count"),
            render_mode="human",
        )
        agent.load_model()

        done = False
        score = 0
        observation = env.reset()[0]

        while not done:
            action = agent.get_action_testing(observation)
            observation_, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            score += reward
            observation = observation_

        print("score %.1f" % score)

    else:
        print("Invalid Option")


if __name__ == "__main__":
    main()
