import numpy as np

from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.core.classes.algorithms import DataDriftDDM
from uptrain.constants import DataDriftAlgo, MeasurableType
from uptrain.core.classes.anomalies.measurables import MeasurableResolver
from uptrain.constants import Anomaly


class ConceptDrift(AbstractAnomaly):
    dashboard_name = "concept_drift_acc"
    anomaly_type = Anomaly.CONCEPT_DRIFT

    def __init__(self, fw, check):
        self.measurable = MeasurableResolver({"type": MeasurableType.ACCURACY}).resolve(
            fw
        )
        self.acc_arr = []
        self.avg_acc = 0
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        if check["algorithm"] == DataDriftAlgo.DDM:
            warn_thres = check.get("warn_thres", 2)
            alarm_thres = check.get("alarm_thres", 3)
            self.algo = DataDriftDDM(warn_thres, alarm_thres)
        else:
            raise Exception("Data drift algo type not supported")

    def need_ground_truth(self):
        return True

    def check(self, inputs, outputs, gts=None, extra_args={}):
        batch_acc = self.measurable.compute_and_log(inputs, outputs, gts, extra_args)
        for acc in batch_acc:
            if acc:
                self.algo.add_prediction(0)
            else:
                self.algo.add_prediction(1)

            self.acc_arr.append(acc)
            self.avg_acc = (self.avg_acc * (len(self.acc_arr) - 1) + acc) / len(
                self.acc_arr
            )
            self.log_handler.add_scalars(
                "avg_accuracy",
                {"avg_accuracy": self.avg_acc},
                len(self.acc_arr),
                self.dashboard_name,
            )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"]))
