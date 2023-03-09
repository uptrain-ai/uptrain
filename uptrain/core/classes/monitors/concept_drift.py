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
            self.measurable = MeasurableResolver(
                {"type": MeasurableType.ACCURACY}).resolve(fw)
        self.acc_arr = []
        self.avg_acc = 0
        self.drift_alerted = False
        if check["algorithm"] == DataDriftAlgo.DDM:
            warm_start = check.get("warm_start", 500)
            warn_threshold = check.get("warn_threshold", 2.0)
            alarm_threshold = check.get("alarm_threshold", 3.0)
            self.algo = drift.DDM(warm_start, warn_threshold, alarm_threshold)
        else:
            raise Exception("Data drift algo type not supported")

    def need_ground_truth(self):
        return True

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        batch_acc = self.measurable.compute_and_log(inputs, outputs, gts, extra_args)
        for acc in enumerate(batch_acc):
            alert = None
            self.algo.update(0 if acc else 1)

            if self.algo._drift_detected and not self.drift_alerted:
                alert = f'Drift detected with DDM at time: {int(self.algo._p.n)}'
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
                    "Model Performance Degradation Alert 🚨",
                    alert,
                    self.dashboard_name
                )