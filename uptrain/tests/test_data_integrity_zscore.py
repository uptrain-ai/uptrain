import matplotlib.pyplot as plt
import numpy as np
import uptrain

from scipy.stats import norm, zscore


def plot_graph(sat_scores):
    z_scores = zscore(sat_scores)
    plt.hist(z_scores, bins=50, alpha=0.5, label="Z score", color="green")

    # Add a legend and labels
    plt.legend()
    plt.xlabel("SAT score")
    plt.ylabel("Frequency")
    plt.title("Distribution of SAT scores with outliers")

    # Show the plot
    plt.show()


# Generate 5000 SAT scores from a normal distribution with mean=1200 and std=200
def test_data_integrity_zscore():
    random_state = np.random.RandomState(seed=1337)
    mean = 1200
    std = 200
    num_samples = 5000
    sat_scores = random_state.normal(mean, std, num_samples)

    # Add some random outliers that are not normally distributed
    num_outliers = 250
    outliers = np.concatenate(
        (
            random_state.uniform(0, 200, num_outliers // 2),
            random_state.uniform(2000, 2500, num_outliers // 2),
        )
    )

    # Add the outliers to the SAT scores
    sat_scores = np.concatenate((sat_scores, outliers))

    # shuffle the scores
    random_state.shuffle(sat_scores)

    # plot_graph(sat_scores)

    cfg = {
        "checks": [
            {
                "type": uptrain.Monitor.DATA_INTEGRITY,
                "measurable_args": {
                    "type": uptrain.MeasurableType.INPUT_FEATURE,
                    "feature_name": "scores",
                },
                "integrity_type": "z_score",
                "threshold": 3,
            }
        ],
        "retraining_folder": "uptrain_smart_data_data_integrity",
        "logging_args": {
            "st_logging": True,
            "log_folder": "uptrain_data_integrity_zscore",
        },
    }

    framework = uptrain.Framework(cfg)
    batch_size = 64
    size = len(sat_scores)

    for i in range(size // batch_size):
        framework.log(
            inputs={
                "scores": sat_scores[i * batch_size : (i + 1) * batch_size],
            }
        )
