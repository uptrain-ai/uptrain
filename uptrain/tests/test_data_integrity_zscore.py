import matplotlib.pyplot as plt
import numpy as np
import uptrain

from scipy.stats import norm, zscore


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

    # Calculate the z-scores for each SAT score
    z_scores = zscore(sat_scores)
    outliers = np.array([z_scores[i] for i in np.where(np.abs(z_scores) > 3)[0]])

    sorted_zscores = sorted(z_scores)
    q1 = sorted_zscores[len(sorted_zscores) // 4]
    q3 = sorted_zscores[len(sorted_zscores) * 3 // 4]
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    lower_fence = q1 - 1.5 * iqr
    iqr_indices = np.where(
        (sorted_zscores <= upper_fence) & (sorted_zscores >= lower_fence)
    )[0]
    iqr_values = [sorted_zscores[i] for i in iqr_indices]

    def plot_graph(drifts=None):
        plt.hist(z_scores, bins=50, alpha=0.5, label="Z score", color="green")
        plt.plot([upper_fence, upper_fence], [0, 1000], color="red")
        plt.plot([lower_fence, lower_fence], [0, 1000], color="red")

        # Add a legend and labels
        plt.legend()
        plt.xlabel("SAT score")
        plt.ylabel("Frequency")
        plt.title("Distribution of SAT scores with outliers")

        # Show the plot
        plt.show()

    # plot_graph()

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
            },
            {
                "type": uptrain.Visual.PLOT,
                "plot": uptrain.PlotType.HISTOGRAM,
                "feature_name": "z_scores",
                "plot_name": "SAT z-scores",
            },
            {
                "type": uptrain.Visual.PLOT,
                "plot": uptrain.PlotType.HISTOGRAM,
                "feature_name": "outliers",
                "plot_name": "SAT z-scores",
            },
            {
                "type": uptrain.Visual.PLOT,
                "plot": uptrain.PlotType.HISTOGRAM,
                "feature_name": "iqr",
                "plot_name": "SAT z-scores",
            },
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

    framework.log(inputs={"z_scores": z_scores})
    framework.log(inputs={"outliers": outliers})
    framework.log(inputs={"iqr": iqr_values})

    for i in range(size // batch_size):
        framework.log(
            inputs={
                "scores": sat_scores[i * batch_size : (i + 1) * batch_size],
            }
        )
