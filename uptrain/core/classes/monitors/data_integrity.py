import numpy as np

from uptrain.core.classes.monitors import AbstractMonitor
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Monitor


class DataIntegrity(AbstractMonitor):
    dashboard_name = "data_integrity"
    anomaly_type = Monitor.DATA_INTEGRITY

    def base_init(self, fw, check):
        self.integrity_type = check["integrity_type"]
        self.threshold = check.get("threshold", None)
        self.count = 0
        self.num_issues = 0

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        signal_value = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        if self.integrity_type == "non_null":
            has_issue = signal_value == None
        elif self.integrity_type == "less_than":
            has_issue = signal_value > self.threshold
        elif self.integrity_type == "greater_than":
            has_issue = signal_value < self.threshold
        self.count += len(signal_value)
        self.num_issues += np.sum(np.array(has_issue))
        plot_name = (
            self.measurable.col_name()
            + " "
            + self.integrity_type
            + " "
            + str(self.threshold)
        )
        self.log_handler.add_scalars(
            self.dashboard_name + "_" + plot_name,
            {"y_" + plot_name: 1 - self.num_issues / self.count},
            self.count,
            self.dashboard_name,
        )

    def need_ground_truth(self):
        return False
