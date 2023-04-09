import numpy as np
import random
import uptrain

# For line chart
line_n = 100
epoch = list(range(line_n))
loss = [random.randint(0, 100) for _ in range(line_n)]
loss2 = [random.randint(0, 100) for _ in range(line_n)]

# For bar chart
bar_n = 10
bar1_y = [i for i in range(bar_n)]
bar1_x = [f"feature: {i}" for i in range(bar_n)]
bar2_y = [i for i in range(bar_n - 1, -1, -1)]
bar2_x = [f"feature: {i}" for i in range(bar_n)]

# For histogram
hist_n = 1000
hist_data = np.random.normal(size=1000)
hist_data2 = np.random.gumbel(size=1000)

cfg = {
    "checks": [
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.LINE_CHART,
            "x_feature_name": "epoch",
            "y_feature_name": "loss",
            "plot_name": "epoch vs loss",
        },
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.LINE_CHART,
            "y_feature_name": "loss",
            "plot_name": "epoch vs loss 2",
            "dashboard_name": "Plot 2"
        },
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.BAR_CHART,
            "x_feature_name": "key",
            "y_feature_name": "value",
            "bars": ["bar1", "bar2"],
            "plot_name": "bar chart",
        },
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.HISTOGRAM,
            "feature_name": "data",
            "plot_name": "histogram",
        },
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.HISTOGRAM,
            "feature_name": "data",
            "plot_name": "histogram 2",
        },
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.HISTOGRAM,
            "feature_name": "data2",
            "plot_name": "histogram 2",
        },
    ],
    "logging_args": {"st_logging": True},
}

framework = uptrain.Framework(cfg)

framework.log({"epoch": epoch, "loss": loss})
framework.log(
    {
        "bars": ["bar1"] * bar_n + ["bar2"] * bar_n,
        "key": bar1_x + bar2_x,
        "value": bar1_y + bar2_y,
    }
)
framework.log({"data": hist_data})
framework.log({"data2": hist_data2})
