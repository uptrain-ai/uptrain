import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import uptrain.v0 as v0


# if __name__ == "__main__":
def test_a_b_testing():
    """Test A/B testing using concept drift ADWIN algorithm.

    Refer to the documentation in the test for concept drift for more information
    on the concept drift detection using ADWIN algorithm part.

    Here, we will use the same concept drift detection algorithm to detect A/B testing.
    We have two models that we want to compare:
        - both models predict the ground truths almost correctly for the first 1000 values
        - model_1 predicts the ground truths almost correctly for the next 500 values
        - model_2, however, has higher variance in its predictions for the next 500 values
    We would like to compare the performance of both models on the same data and see
    how concept drift detection is used in A/B testing here.

    In this test, we use the UpTrain framework to log the inputs, outputs, and ground truths.
    We set up the framework to use the ADWIN algorithm to monitor the concept drift of the
    different models. We use one error rate for detection of concept drift:
        - The error rate is calculated as the mean absolute difference between the
          predictions and the ground truths.

    The test passes if the ADWIN algorithm successfully detects the concept drift and raises
    an alert around the point where predictions from the models start becoming inaccurate.
    """

    random_state = np.random.RandomState(seed=1337)
    n = 1000
    params_model_1 = [(0.2, 0.03, n), (0.5, 0.08, n)]
    params_model_2 = [(0.2, 0.03, n), (0.55, 0.1, n)]
    distributions_model_1 = np.array(
        [random_state.normal(*param) for param in params_model_1]
    )
    distributions_model_2 = np.array(
        [random_state.normal(*param) for param in params_model_2]
    )
    ground_truths = np.array([0.2] * n + [0.5] * (n // 2) + [0.6] * (n // 2))
    stream_model_1 = distributions_model_1.flatten()
    stream_model_2 = distributions_model_2.flatten()

    def plot_data(stream, distributions, drifts=None):
        """Helper function to plot data."""

        _ = plt.figure(figsize=(7, 3), tight_layout=True)
        gridspecs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])

        ax1, ax2 = plt.subplot(gridspecs[0]), plt.subplot(gridspecs[1])
        ax1.grid()
        ax1.plot(stream, label="stream")
        ax2.grid(axis="y")

        for index, dist in enumerate(distributions):
            ax2.hist(dist, label=f"dist_{index}")

        drift_color = "red"
        if drifts is not None:
            for drift_detected in drifts:
                ax1.axvline(drift_detected, color=drift_color)
        plt.tight_layout()
        plt.show()

    # Plot data for debugging
    # plot_data(stream_model_1, distributions_model_1)
    # plot_data(stream_model_2, distributions_model_2)

    # Create a configuration for the framework
    cfg = {
        # Define checks to be performed
        "checks": [
            # First check: monitor concept drift using ADWIN algorithm with
            # mean absolute error as the measurable for the feature "data".
            {
                "type": v0.Monitor.CONCEPT_DRIFT,
                "algorithm": v0.DataDriftAlgo.ADWIN,
                "measurable_args": {"type": v0.MeasurableType.MAE},
                # Configurable parameters that the ADWIN algorithm supports
                "delta": 0.002,
                "clock": 32,
                "max_buckets": 5,
                "min_window_length": 5,
                "grace_period": 5,
                # Add arguments to handle multiple models for A/B testing
                "model_args": [
                    {
                        "type": v0.MeasurableType.INPUT_FEATURE,
                        "feature_name": "model_name",
                        "allowed_values": ["model_1", "model_2"],
                    }
                ],
            },
        ],
        # Specify where the logging data should be stored
        "retraining_folder": "uptrain_a_b_testing",
        # Specify logging arguments
        # "st_logging" should be True if we want streamlit logging, False otherwise
        "logging_args": {"st_logging": True},
    }

    framework = v0.Framework(cfg)
    batch_size = 64
    size = len(stream_model_1)

    # Feed the data to the framework
    for i in range(size // batch_size):
        data_model_1 = stream_model_1[i * batch_size : (i + 1) * batch_size]
        data_model_2 = stream_model_2[i * batch_size : (i + 1) * batch_size]
        data = np.concatenate([data_model_1, data_model_2])
        inputs = {
            "data": data,
            "model_name": ["model_1"] * len(data_model_1)
            + ["model_2"] * len(data_model_2),
        }
        outputs = data
        gts = ground_truths[i * batch_size : (i + 1) * batch_size]
        gts = np.concatenate([gts, gts])
        ids = framework.log(inputs=inputs, outputs=outputs)
        framework.log(identifiers=ids, gts=gts)
