import numpy as np
import pandas as pd
from uptrain.core.classes.monitors import AbstractMonitor
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Monitor
from uptrain.core.lib.helper_funcs import read_json

from scipy.stats import zscore

class DataIntegrity(AbstractMonitor):
    dashboard_name = "data_integrity"
    monitor_type = Monitor.DATA_INTEGRITY

    def base_init(self, fw, check):
        self.integrity_type = check["integrity_type"]
        self.threshold = check.get("threshold", None)
        # Threshold for when to alert on percentage of outliers (default 2%)
        self.outliers_alert_thres = check.get("outliers_alert_thres", 2)
        self.count = 0
        self.num_issues = 0
        self.has_reference_dataset = "reference_dataset" in check
        if self.has_reference_dataset:
            self.reference_dataset = check["reference_dataset"]
            self.ref_mean, self.ref_std = self.get_ref_data_stats()
            
    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        signal_value = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        signal_value = np.squeeze(np.array(signal_value))

        if self.integrity_type == "non_null":
            has_issue = signal_value == None
        elif self.integrity_type == "less_than":
            has_issue = signal_value > self.threshold
        elif self.integrity_type == "equal_to":
            has_issue = signal_value == self.threshold
        elif self.integrity_type == "greater_than":
            has_issue = signal_value < self.threshold
        elif self.integrity_type == "minus_one":
            has_issue = signal_value == -1
        elif self.integrity_type == "z_score":
            if self.threshold is None:
                self.threshold = 3
            
            # Calculating Z-scores w.r.t. the reference dataset
            if self.has_reference_dataset:
                z_score = (signal_value - self.ref_mean) / self.ref_std
            # Calculating Z-scores w.r.t. the current dataset
            else:
                z_score = zscore(signal_value)
            has_issue = np.abs(z_score) > self.threshold
            outliers = signal_value[has_issue]
            valid_signal = signal_value[~has_issue]
            
            feat_name = self.measurable.col_name()
            plot_name = f"z_score_feature_{feat_name}"
            self.log_handler.add_histogram(
                plot_name=plot_name,
                data=valid_signal,
                dashboard_name=self.dashboard_name,
                file_name=f"valid_z_scores",
            )
            percentage_outliers = 100 * len(outliers) / len(z_score)
            if len(outliers) > 0 and percentage_outliers > self.outliers_alert_thres:
                self.log_handler.add_histogram(
                    plot_name=plot_name,
                    data=outliers,
                    dashboard_name=self.dashboard_name,
                    file_name=f"outliers",
                )
                perc = round(percentage_outliers, 1)
                self.log_handler.add_alert(
                    alert_name = f"Z-score outliers detected for {feat_name} 🚨",
                    alert = f"{len(outliers)} of {len(z_score)} samples have Z-Score > {self.threshold} ({perc}%)",
                    dashboard_name = self.dashboard_name
                )
        else:
            raise NotImplementedError(
                "Data integrity check {} not implemented".format(self.integrity_type)
            )            
        self.count += len(signal_value)
        self.num_issues += np.sum(np.array(has_issue))

        self.log_handler.add_scalars(
            self.integrity_type + "_outliers_ratio",
            {"y_outliers": self.num_issues / self.count},
            self.count,
            self.dashboard_name,
            file_name=self.measurable.col_name(),
        )

    def need_ground_truth(self):
        return False

    def get_ref_data_stats(self):
        """
        Find the mean and std for z-score in ref_arr. The data can be numerical or categorical.
        """
        if self.reference_dataset.split('.')[-1] == 'json':
            data = read_json(self.reference_dataset)
            all_inputs = np.array(
                [self.measurable.extract_val_from_training_data(x) for x in data]
            )
        elif self.reference_dataset.split('.')[-1] == 'csv':
            data = pd.read_csv(self.reference_dataset).to_dict()
            for key in data:
                data[key] = list(data[key].values())
            all_inputs = np.array(self.measurable.extract_val_from_training_data(data))
        else:
            raise Exception("Reference data file type not recognized.")
        
        return np.mean(all_inputs), np.std(all_inputs)
