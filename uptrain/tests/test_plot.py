import random
import uptrain

# For line chart
line_n = 100
epoch = list(range(line_n))
loss = [random.randint(0, 100) for _ in range(line_n)]

# For bar chart
bar_n = 10
bar1_y = [i for i in range(bar_n)]
bar1_x = ["date: " + str(i) for i in range(bar_n)]

bar2_y = [i for i in range(bar_n - 1, -1, -1)]
bar2_x = ["date: " + str(i) for i in range(bar_n)]

cfg = {
    "checks": [
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.LINE_CHART,
            "x_feature_name": "epoch",
            "y_feature_name": "loss",
            "plot_name": "epoch vs loss 1"
        },
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.LINE_CHART,
            "y_feature_name": "loss",
            "plot_name": "epoch vs loss 2"
        },
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.BAR_CHART,
            "x_feature_name": "key",
            "y_feature_name": "value",
            "plot_name": "this is the bar chart"
        }
    ],
    "logging_args": {"st_logging": True}
}

framework = uptrain.Framework(cfg)

framework.log({"epoch": epoch, "loss": loss})
framework.log({"bars": ["bar1"] * bar_n, "key": bar1_x, "value": bar1_y})
framework.log({"bars": ["bar2"] * bar_n, "key": bar2_x, "value": bar2_y})
