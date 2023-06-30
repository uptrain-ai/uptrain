import numpy as np
import random
import uptrain.v0 as v0


def test_visuals_plot():
    """Test Visual Plot API functionality.
    
    In this test, we test the plotting functionality of the framework.
    We test the following plots:
        - Line chart
        - Bar chart
        - Histogram
    
    For each of the above plots, we generate random data.

    The test passes if the plots are generated correctly.
    """

    # Data for line chart
    line_n = 100
    epoch = list(range(line_n))
    loss = [random.randint(0, 100) for _ in range(line_n)]

    # Data for bar chart
    bar_n = 10
    bar1_y = [i for i in range(bar_n)]
    bar1_x = [f"feature: {i}" for i in range(bar_n)]
    bar2_y = [i for i in range(bar_n - 1, -1, -1)]
    bar2_x = [f"feature: {i}" for i in range(bar_n)]

    # Data for histogram
    hist_n = 1000
    hist_model_a = np.random.normal(size=hist_n)
    hist_model_b = np.random.gumbel(size=hist_n)

    # Create a configuration for the framework
    cfg = {
        # Define checks for the framework
        "checks": [
            # Line chart for epoch vs loss on default dashboard
            {
                "type": v0.Visual.PLOT,
                "plot": v0.PlotType.LINE_CHART,
                "x_feature_name": "epoch",
                "y_feature_name": "loss",
                "plot_name": "epoch vs loss",
            },

            # Line chart for epoch vs loss on a different dashboard
            {
                "type": v0.Visual.PLOT,
                "plot": v0.PlotType.LINE_CHART,
                "y_feature_name": "loss",
                "plot_name": "epoch vs loss 2",
                "dashboard_name": "Plot 2"
            },

            # Bar chart for bar1 and bar2 on default dashboard
            {
                "type": v0.Visual.PLOT,
                "plot": v0.PlotType.BAR_CHART,
                "x_feature_name": "key",
                "y_feature_name": "value",
                "bars": ["bar1", "bar2"],
                "plot_name": "bar chart",
            },

            # Histogram for model_a on default dashboard
            {
                "type": v0.Visual.PLOT,
                "plot": v0.PlotType.HISTOGRAM,
                "feature_name": "model_a",
                "plot_name": "single histogram",
            },

            # Histogram for model_b on default dashboard with multiple models
            {
                "type": v0.Visual.PLOT,
                "plot": v0.PlotType.HISTOGRAM,
                "feature_name": "model_a",
                "plot_name": "multiple histogram",
            },

            # Histogram for model_b on default dashboard with multiple models
            {
                "type": v0.Visual.PLOT,
                "plot": v0.PlotType.HISTOGRAM,
                "feature_name": "model_b",
                "plot_name": "multiple histogram",
            },
        ],

        # Specify logging arguments
        # "st_logging" should be True if we want streamlit logging, False otherwise
        "logging_args": {"st_logging": True},
    }

    framework = v0.Framework(cfg)

    # Log data to the framework
    framework.log({"epoch": epoch, "loss": loss})
    framework.log(
        {
            "bars": ["bar1"] * bar_n + ["bar2"] * bar_n,
            "key": bar1_x + bar2_x,
            "value": bar1_y + bar2_y,
        }
    )
    framework.log({"model_a": hist_model_a})
    framework.log({"model_b": hist_model_b})
