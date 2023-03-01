import numpy as np
from scipy import stats
from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Anomaly


class ZScoreAnalysis(AbstractAnomaly):
    dashboard_name = "zscore_analysis"
    anomaly_type = Anomaly.Z_SCORE

    def __init__(self, fw, check,threshold=3):
        self.log_handler = fw.log_handler
        self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        self.threshold = threshold
        self.count = 0
        self.num_outliers = 0

    def check(self, inputs, outputs, gts=None, extra_args={}):
        signal_value = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )

        z_scores = np.abs(stats.zscore(signal_value))

        outliers = np.any(z_scores > self.threshold, axis=1)

        self.count += len(signal_value)
        self.num_outliers += len(outliers)

        plot_name = self.measurable.col_name() + " Z-score analysis"
        self.log_handler.add_scalars(
            self.dashboard_name + "_" + plot_name,
            {"y_" + plot_name: 1 - self.num_outliers / self.count},
            self.count,
            self.dashboard_name,
        )
        return outliers
    def is_data_interesting(self):
        return 

    def need_ground_truth(self):
        return False