import numpy as np

from uptrain.core.classes.monitors import AbstractMonitor
from uptrain.core.classes.algorithms import DataDriftDDM
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
        if check["algorithm"] == DataDriftAlgo.DDM:
            warn_thres = check.get("warn_thres", 2)
            alarm_thres = check.get("alarm_thres", 3)
            self.algo = DataDriftDDM(warn_thres, alarm_thres)
        else:
            raise Exception("Data drift algo type not supported")

    def need_ground_truth(self):
        return True

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        batch_acc = self.measurable.compute_and_log(inputs, outputs, gts, extra_args)
        for acc in batch_acc:
            if acc:
                alert = self.algo.add_prediction(0)
            else:
                alert = self.algo.add_prediction(1)

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