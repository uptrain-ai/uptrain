import numpy as np

from river import drift

from uptrain.core.classes.monitors import AbstractMonitor
from uptrain.constants import DataDriftAlgo, MeasurableType
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Monitor


class ConceptDrift(AbstractMonitor):
    dashboard_name = "concept_drift_acc"
    anomaly_type = Monitor.CONCEPT_DRIFT

    def base_init(self, fw, check):
        if check.get("measurable_args", None):
            self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        else:
            self.measurable = MeasurableResolver({"type": MeasurableType.ACCURACY}).resolve(fw)

        self.acc_arr = []
        self.avg_acc = 0
        self.drift_alerted = False
        self.algorithm = check["algorithm"]

        if self.algorithm == DataDriftAlgo.DDM:
            warm_start = check.get("warm_start", 500)
            warn_threshold = check.get("warn_threshold", 2.0)
            alarm_threshold = check.get("alarm_threshold", 3.0)
            self.algo = drift.DDM(warm_start, warn_threshold, alarm_threshold)
        elif self.algorithm == DataDriftAlgo.ADWIN:
            delta = check.get("delta", 0.002)
            clock = check.get("clock", 32)
            max_buckets = check.get("max_buckets", 5)
            min_window_length = check.get("min_window_length", 5)
            grace_period = check.get("grace_period", 5)
            self.algo = drift.ADWIN(delta, clock, max_buckets, min_window_length, grace_period)
        else:
            raise Exception("Data drift algo type not supported")

    def need_ground_truth(self):
        return True

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        batch_acc = self.measurable.compute_and_log(inputs, outputs, gts, extra_args)
        batch_acc = self._preprocess(batch_acc)

        for time, acc in enumerate(batch_acc):
            alert = None
            self.algo.update(acc)

            if self.algo.drift_detected and not self.drift_alerted:
                alert = f"Drift detected with {self.algorithm} at time: {time}"
                print(alert)
                self.drift_alerted = True

            self.acc_arr.append(acc)
            self.avg_acc = (self.avg_acc * (len(self.acc_arr) - 1) + acc) / len(
                self.acc_arr
            )
            self.log_handler.add_scalars(
                "avg_accuracy",
                {"y_avg_accuracy": self.avg_acc},
                len(self.acc_arr),
                self.dashboard_name,
            )
            if isinstance(alert, str):
                self.log_handler.add_alert(
                    "Model Performance Degradation Alert 🚨", alert, self.dashboard_name
                )
    
    def _preprocess (self, batch):
        if self.algorithm == DataDriftAlgo.DDM:
            return np.array([0 if x else 1 for x in batch])
        else:
            return np.array(batch)
