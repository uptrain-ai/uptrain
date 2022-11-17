from oodles.constants import Anomaly, DataDriftAlgo
from oodles.core.classes.anomalies.edge_case_manager import EdgeCaseManager
from oodles.core.classes.anomalies.data_drift_ddm import DataDriftDDM
from oodles.core.classes.anomalies.custom_anomaly import CustomAnomaly


class AnomalyManager:
    def __init__(self, checks=[]):
        self.anomalies_to_check = []
        for check in checks:
            self.add_anomaly_to_monitor(check)

    def add_anomaly_to_monitor(self, check):
        if check["type"] == Anomaly.EDGE_CASE:
            edge_case_manager = EdgeCaseManager(check["signal_formulae"])
            self.anomalies_to_check.append(edge_case_manager)
        elif check["type"] == Anomaly.DATA_DRIFT:
            # TODO: Add a generic Data drift class to handle its algos
            if check["algorithm"] == DataDriftAlgo.DDM:
                warn_thres = check.get("warn_thres", 2)
                alarm_thres = check.get("alarm_thres", 3)
                ddm_manager = DataDriftDDM(warn_thres, alarm_thres)
            else:
                raise Exception("Data drift algo type not supported")
            self.anomalies_to_check.append(ddm_manager)
        elif check["type"] == Anomaly.CUSTOM_MONITOR:
            custom_monitor = CustomAnomaly(check["func"])
            self.anomalies_to_check.append(custom_monitor)
        else:
            raise Exception("Check type not Supported")

    def check(self, inputs, outputs, extra_args={}):
        for anomaly in self.anomalies_to_check:
            anomaly.check(inputs, outputs)

    def is_data_interesting(self, inputs, outputs, extra_args={}):
        is_interesting = [
            x.is_data_interesting(inputs, outputs, extra_args=extra_args)
            for x in self.anomalies_to_check
        ]
        return sum(is_interesting) > 0
