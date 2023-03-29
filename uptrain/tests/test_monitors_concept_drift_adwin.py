import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import uptrain


def test_concept_drift_adwin():
    """Test concept drift detection using ADWIN algorithm.

    We generate 2 distributions:
      - The first distribution contain 1000 values with mean 0.2 and standard deviation 0.03
      - The second distribution contain 1000 values with mean 0.5 and standard deviation 0.08

    To maintain the simplicity of this test, we will assume that there is a hypothetical model
    that predicts the output is the same as input. However, this is not the case.
    In reality:
      - the ground truth for the first distribution is 0.2
      - the ground truth for the first half of second distribution is 0.5
      - the ground truth for the second half of second distribution is 0.6

    This means that between the model predictions and ground truths, a concept drift will arise.
    The drift will arise somewhere around the 1500th value.

    Why?
      - The model will predict values approximately equal to 0.0 for the first distribution.
        This is correctly predicted.
      - The model will predict values approximately equal to 0.5 for the first half of the
        second distribution. This is correctly predicted as well.
      - The model will predict values approximately equal to 0.5 for the second half of the
        second distribution. This is incorrectly predicted, which causes the error rate to
        grow higher and after it crosses the threshold, an alert is displayed.

    In this test, we use the UpTrain framework to log the inputs, outputs, and ground truths.
    We set up the framework to use the ADWIN algorithm to monitor the error rate of the model.
    The error rate is calculated as the mean absolute difference between the predictions and
    the ground truths.

    The test passes if the ADWIN algorithm successfully detects the concept drift and raises
    an alert around the point where the model's predictions start becoming inaccurate.
    """

    random_state = np.random.RandomState(seed=1337)
    n = 1000
    params = [(0.2, 0.03, n), (0.5, 0.08, n)]
    distributions = np.array([random_state.normal(*param) for param in params])

    ground_truths = np.array([0.2] * n + [0.5] * (n // 2) + [0.6] * (n // 2))
    stream = distributions.flatten()

    def plot_data(drifts=None):
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
    # plot_data()

    # Create a configuration for the framework
    cfg = {
        # Define checks to be performed
        "checks": [
            {
                "type": uptrain.Monitor.CONCEPT_DRIFT,
                "algorithm": uptrain.DataDriftAlgo.ADWIN,
                "measurable_args": {
                    "type": uptrain.MeasurableType.MAE,
                    "feature_name": "data",
                },

                # Configurable parameters that the ADWIN algorithm supports
                "delta": 0.002,
                "clock": 32,
                "max_buckets": 5,
                "min_window_length": 5,
                "grace_period": 5,
            },
            {
                "type": uptrain.Monitor.CONCEPT_DRIFT,
                "algorithm": uptrain.DataDriftAlgo.ADWIN,
                "measurable_args": {
                    "type": uptrain.MeasurableType.MAPE,
                    "feature_name": "data",
                },
                "delta": 0.1
            }
        ],

        # Specify where the logging data should be stored
        "retraining_folder": "uptraining_smart_data_concept_drift_adwin",
        
        # True if we want streamlit logging, False otherwise
        "logging_args": {"st_logging": True},
    }

    framework = uptrain.Framework(cfg)
    batch_size = 64
    size = len(stream)

    for i in range(size // batch_size):
        inputs = {"data": stream[i * batch_size : (i + 1) * batch_size]}
        outputs = stream[i * batch_size : (i + 1) * batch_size]
        gts = ground_truths[i * batch_size : (i + 1) * batch_size]
        ids = framework.log(inputs=inputs, outputs=outputs)
        framework.log(identifiers=ids, gts=gts)
