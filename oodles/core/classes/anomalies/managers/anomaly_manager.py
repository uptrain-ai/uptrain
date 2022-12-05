from oodles.constants import Anomaly
from .edge_case_manager import EdgeCaseManager
from oodles.core.classes.anomalies import ConceptDrift
from oodles.core.classes.anomalies import DataDrift
from oodles.core.classes.anomalies import CustomAnomaly
from oodles.core.classes.anomalies import RecommendationBias


class AnomalyManager:
    def __init__(self, checks=[], log_args={}):
        self.anomalies_to_check = []
        self.log_args = log_args
        for check in checks:
            self.add_anomaly_to_monitor(check)

    def add_anomaly_to_monitor(self, check):
        if check["type"] == Anomaly.EDGE_CASE:
            edge_case_manager = EdgeCaseManager(
                check["signal_formulae"], log_args=self.log_args
            )
            self.anomalies_to_check.append(edge_case_manager)
        elif check["type"] == Anomaly.CONCEPT_DRIFT:
            drift_manager = ConceptDrift(check, log_args=self.log_args)
            self.anomalies_to_check.append(drift_manager)
        elif check["type"] == Anomaly.DATA_DRIFT:
            drift_manager = DataDrift(check, log_args=self.log_args)
            self.anomalies_to_check.append(drift_manager)
        elif check["type"] == Anomaly.POPULARITY_BIAS:
            bias_manager = RecommendationBias(check, log_args=self.log_args)
            self.anomalies_to_check.append(bias_manager)
        elif check["type"] == Anomaly.CUSTOM_MONITOR:
            custom_monitor = CustomAnomaly(check, log_args=self.log_args)
            self.anomalies_to_check.append(custom_monitor)
        else:
            raise Exception("Check type not Supported")

    def check(self, inputs, outputs, gts=None, extra_args={}):
        for anomaly in self.anomalies_to_check:
            if anomaly.need_ground_truth() == (gts is not None):
                anomaly.check(inputs, outputs, gts=gts, extra_args=extra_args)

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        is_interesting = [
            x.is_data_interesting(inputs, outputs, gts=gts, extra_args=extra_args)
            for x in self.anomalies_to_check
        ]
        return sum(is_interesting) > 0
