from oodles.core.classes.anomalies.abstract_anomaly import AbstractAnomaly
from oodles.core.classes.anomalies.algorithms.data_drift_ddm import DataDriftDDM
from oodles.constants import DataDriftAlgo


class ConceptDrift(AbstractAnomaly):
    dashboard_name = 'concept_drift_acc'

    def __init__(self, check, log_args={}):
        super().__init__(log_args=log_args)
        self.acc_arr = []
        if check["algorithm"] == DataDriftAlgo.DDM:
            warn_thres = check.get("warn_thres", 2)
            alarm_thres = check.get("alarm_thres", 3)
            self.algo = DataDriftDDM(warn_thres, alarm_thres)
        else:
            raise Exception("Data drift algo type not supported")

    def need_ground_truth(self):
        return True

    def check(self, inputs, outputs, gts=None, extra_args={}):
        y_gt = gts
        y_pred = outputs
        acc = (y_pred[0] == y_gt[0])
        if acc:
            self.algo.add_prediction(0)
        else:
            self.algo.add_prediction(1)
        
        self.acc_arr.append(acc)
        avg_acc = sum(self.acc_arr)/len(self.acc_arr)
        self.plot_scalar("Avg accuracy", avg_acc, len(self.acc_arr))

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return False
