import uptrain
import random


def test_dashboard():
    cfg = {"st_logging": True}
    fw = uptrain.Framework(cfg)

    dashboard_name = "count_dashboard"
    for count in [0, 500, 1000]:
        data = [random.randint(1, 100) for _ in range(100)]
        fw.log_handler.add_histogram(
                dashboard_name + "_hist_count",
                data,
                "hist_count_dashboard",
                count,
            )

    fw.log_handler.add_alert(
        "Alerting",
        "A test alert",
        dashboard_name
    )