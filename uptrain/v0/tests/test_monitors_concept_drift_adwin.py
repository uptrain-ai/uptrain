import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import uptrain.v0 as v0


def test_concept_drift_adwin():
    """Test concept drift detection using ADWIN algorithm.

    We generate 2 distributions:
        - The first distribution contains 1000 values with mean 0.2 and standard deviation 0.03
        - The second distribution contains 1000 values with mean 0.5 and standard deviation 0.08

    Let's assume the following as well:
        For the first distribution:
            - ground truth is 0.2
        For the second distribution
            - ground truth is 0.5 for the first half of values
            - ground truth is 0.6 for the first half of values

    To maintain the simplicity of this test, we will also assume that we have a hypothetical
    trained model that has learned to predict the output as the same as input. However, as can
    be seen from the ground truth values, this is not the case. The model will correctly predict
    the first distribution as well as the first half of the second distribution. However, it
    will make incorrect predictions on the second half of the second distribution.

    This means that between the model predictions and ground truths, a concept drift will arise.
    The drift will arise somewhere around the 1500th value.

    Why?
      - The model will predict values approximately equal to 0.2 for the first distribution.
        This is correctly predicted.
      - The model will predict values approximately equal to 0.5 for the first half of the
        second distribution. This is correctly predicted as well.
      - The model will predict values approximately equal to 0.5 for the second half of the
        second distribution. This is incorrectly predicted, which causes the error rate to
        grow higher. After it crosses a set threshold, a concept drift alert is raised.

    In this test, we use the UpTrain framework to log the inputs, outputs, and ground truths.
    We set up the framework to use the ADWIN algorithm to monitor the error rate of the model.
    We use two error rates for detection of concept drift:
        - The first error rate is calculated as the mean absolute difference between the
          predictions and the ground truths.
        - The second error rate is calculated as the mean absolute percentage difference
          between the predictions and the ground truths.

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
            },
            # Second check: monitor concept drift using ADWIN algorithm with
            # mean absolute percentage error as the measurable for the feature "data".
            # Notice that we need a different delta value (significance value)
            # for using MAPE as the measurable instead of MAE.
            {
                "type": v0.Monitor.CONCEPT_DRIFT,
                "algorithm": v0.DataDriftAlgo.ADWIN,
                "measurable_args": {
                    "type": v0.MeasurableType.MAPE,
                    "feature_name": "data",
                },
                "delta": 0.1,
            },
        ],
        # Specify where the logging data should be stored
        "retraining_folder": "uptraining_smart_data_concept_drift_adwin",
        # Specify logging arguments
        # "st_logging" should be True if we want streamlit logging, False otherwise
        "logging_args": {"st_logging": True},
    }

    framework = v0.Framework(cfg)
    batch_size = 64
    size = len(stream)

    # Feed the data to the framework
    for i in range(size // batch_size):
        inputs = {"data": stream[i * batch_size : (i + 1) * batch_size]}
        outputs = stream[i * batch_size : (i + 1) * batch_size]
        gts = ground_truths[i * batch_size : (i + 1) * batch_size]
        ids = framework.log(inputs=inputs, outputs=outputs)
        framework.log(identifiers=ids, gts=gts)
