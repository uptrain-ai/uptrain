import numpy as np

from uptrain.core.classes.monitors import AbstractMonitor
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Monitor

from scipy.stats import zscore

class DataIntegrity(AbstractMonitor):
    dashboard_name = "data_integrity"
    monitor_type = Monitor.DATA_INTEGRITY

    def base_init(self, fw, check):
        self.integrity_type = check["integrity_type"]
        self.threshold = check.get("threshold", None)
        self.count = 0
        self.num_issues = 0
            
    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        # Perform measurable compute and log only if the measurable feature is
        # present in the inputs
        if self.measurable.col_name() not in inputs.keys():
            return
        signal_value = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )

        if self.integrity_type == "non_null":
            has_issue = signal_value == None
        elif self.integrity_type == "less_than":
            has_issue = signal_value > self.threshold
        elif self.integrity_type == "greater_than":
            has_issue = signal_value < self.threshold
        elif self.integrity_type == "z_score":
            if self.threshold is None:
                self.threshold = 3
            
            z_score = zscore(signal_value)
            has_issue = np.abs(z_score) > self.threshold
            outliers = np.array([z_score[i] for i in np.where(np.abs(z_score) >= self.threshold)[0]])
            valid_z_scores = np.array([z_score[i] for i in np.where(np.abs(z_score) < self.threshold)[0]])
            
            self.log_handler.add_histogram(
                plot_name=f"z_score",
                data=valid_z_scores,
                dashboard_name=self.dashboard_name,
                file_name=f"valid_z_scores",
            )

            if len(outliers) > 0:
                percentage_outliers = round(100 * len(outliers) / len(z_score), 1)
                self.log_handler.add_histogram(
                    plot_name=f"z_score",
                    data=outliers,
                    dashboard_name=self.dashboard_name,
                    file_name=f"outliers",
                )
                self.log_handler.add_alert(
                    alert_name = "Outliers Detected 🚨",
                    alert = f"{percentage_outliers}% of total samples are outliers",
                    dashboard_name = self.dashboard_name
                )
        else:
            raise NotImplementedError(
                "Data integrity check {} not implemented".format(self.integrity_type)
            )            
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
