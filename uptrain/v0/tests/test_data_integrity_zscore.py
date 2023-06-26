import matplotlib.pyplot as plt
import numpy as np
import uptrain.v0 as v0

from scipy.stats import zscore


def plot_graph(exam_scores):
    """Plot z-score graph."""

    z_scores = zscore(exam_scores)
    plt.hist(z_scores, bins=50, alpha=0.5, label="Z score", color="green")

    # Add a legend and labels
    plt.legend()
    plt.xlabel("Z score")
    plt.ylabel("Frequency")
    plt.title("Distribution of Z scores with outliers")

    # Show the plot
    plt.show()


def test_data_integrity_zscore():
    """Test data integrity z-score.

    The test generates random exam scores, adds some random outliers to the data,
    and shuffles the data. Then, the UpTrain framework is used to monitor the
    data integrity of the generated data using z-score.

    To generate the test, 5000 random exam scores are generated with a mean of
    0 and a standard deviation of 250. Then, 250 random outliers are added
    to the data. The outliers account for about 2-5%  of the total data depending
    on the randomly generated values.

    The test passes if the monitored z-score data integrity detects the presence
    of outliers in the data.
    """

    random_state = np.random.RandomState(seed=1337)
    mean = 0
    std = 250
    num_samples = 5000
    exam_scores = random_state.normal(mean, std, num_samples)

    # Add some random outliers that are not normally distributed
    num_outliers = 250
    outliers = np.concatenate(
        (
            random_state.uniform(-1500, -500, num_outliers // 2),
            random_state.uniform(500, 1500, num_outliers // 2),
        )
    )

    # Add the outliers to the exam scores
    exam_scores = np.concatenate((exam_scores, outliers))

    # Shuffle the scores
    # random_state.shuffle(exam_scores)

    # plot_graph(exam_scores)

    # Create a configuration for the framework
    cfg = {
        # Define checks to be performed
        "checks": [
            {
                "type": v0.Monitor.DATA_INTEGRITY,
                "measurable_args": {
                    "type": v0.MeasurableType.INPUT_FEATURE,
                    "feature_name": "scores",
                },
                "integrity_type": "z_score",
                "threshold": 3,
            }
        ],
        # Specify where the data from z-score data integrity should be stored
        "retraining_folder": "uptrain_smart_data_integrity_zscore",
        # # Specify logging arguments
        # "st_logging" should be True if we want streamlit logging, False otherwise
        "logging_args": {
            "st_logging": True,
            "log_folder": "uptrain_data_integrity_zscore",
        },
    }

    framework = v0.Framework(cfg)
    batch_size = 64
    size = len(exam_scores)

    # Feed the data to the framework
    for i in range(size // batch_size):
        framework.log(
            inputs={
                "scores": exam_scores[i * batch_size : (i + 1) * batch_size],
            }
        )
