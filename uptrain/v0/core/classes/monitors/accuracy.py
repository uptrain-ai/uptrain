import numpy as np

from uptrain.v0.core.classes.monitors import AbstractMonitor
from uptrain.v0.constants import MeasurableType
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.constants import Monitor


class Accuracy(AbstractMonitor):
    dashboard_name = "accuracy"
    monitor_type = Monitor.ACCURACY

    def base_init(self, fw, check):
        if check.get("measurable_args", None):
            self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
            self.plot_name = check["measurable_args"]["type"]
        else:
            self.measurable = MeasurableResolver({"type": MeasurableType.MAE}).resolve(
                fw
            )
        self.abs_err_arr = np.array([])
        self.avg_acc = 0
        self.log_handler = fw.log_handler

    def need_ground_truth(self):
        return True

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        batch_abs_error = self.measurable.compute_and_log(
            inputs, outputs, gts, extra_args
        )
        self.abs_err_arr = np.append(self.abs_err_arr, batch_abs_error)

        self.log_handler.add_scalars(
            self.plot_name,
            {"y_" + self.plot_name: np.mean(self.abs_err_arr)},
            len(self.abs_err_arr),
            self.dashboard_name,
        )
