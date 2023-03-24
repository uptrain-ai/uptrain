import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import uptrain


def test_concept_drift_adwin():
    random_state = np.random.RandomState(seed=1337)
    
    # We generate 2 distributions:
    #   - The first distribution contain 1000 values with mean 0.0 and standard deviation 0.03
    #   - The second distribution contain 1000 values with mean 0.5 and standard deviation 0.08
    #
    # To maintain the simplicity of this test, we will assume that there is a hypothetical model
    # that predicts the output is the same as input. However, this is not the case.
    # In reality:
    #   - the ground truth for the first distribution is 0.0
    #   - the ground truth for the first half of second distribution is 0.5
    #   - the ground truth for the second half of second distribution is 0.6
    #
    # This means that between the model predictions and ground truths, a concept drift will arise.
    # The drift will arise somewhere around the 1500th value.
    #
    # Why?
    #  - The model will predict values approximately equal to 0.0 for the first distribution.
    #    This is correct.
    #  - The model will predict values approximately equal to 0.5 for the first half of the
    #    second distribution. This is correct.
    #  - The model will predict values approximately equal to 0.5 for the second half of the
    #    second distribution. This is incorrect.
    #
    # The concept drift will be detected by the ADWIN algorithm.

    n = 1000
    params = [(0.0, 0.03, n), (0.5, 0.08, n)]
    distributions = np.array([random_state.normal(*param) for param in params])
    
    ground_truths = np.array([0.0] * n + [0.5] * (n // 2) + [0.6] * (n // 2))
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
                "delta": 0.002,
                "clock": 32,
                "max_buckets": 5,
                "min_window_length": 5,
                "grace_period": 5,
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
