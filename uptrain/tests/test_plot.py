import random
import uptrain

n = 100
epochs = list(range(n))
loss = [random.randint(0, 100) for _ in range(n)]

cfg = {
    "checks": [
        {
            "type": uptrain.Visual.PLOT,
            "plot": uptrain.PlotType.LINE_CHART,
            "x_feature_name": "epochs",
            "y_feature_name": "loss",
            "plot_name": "this is da line chart"
        }
    ],
    "logging_args": {"st_logging": True}
}

framework = uptrain.Framework(cfg)

framework.log({"epochs": epochs, "loss": loss})
