import numpy as np

from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.core.classes.anomalies.measurables import MeasurableResolver
from uptrain.constants import Anomaly


class DataIntegrity(AbstractAnomaly):
    dashboard_name = "data_integrity"
    anomaly_type = Anomaly.DATA_INTEGRITY

    def __init__(self, fw, check):
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        self.integrity_type = check["integrity_type"]
        self.threshold = check.get("threshold", None)
        self.count = 0
        self.num_issues = 0

    def check(self, inputs, outputs, gts=None, extra_args={}):
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
            {plot_name: 1 - self.num_issues / self.count},
            self.count,
            self.dashboard_name,
        )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"]))

    def need_ground_truth(self):
        return False
