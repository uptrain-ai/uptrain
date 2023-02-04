import numpy as np
from copy import deepcopy

from uptrain.constants import Anomaly, Statistic, Visual, MeasurableType
from uptrain.core.classes.anomalies import (
    ConceptDrift,
    DataDrift,
    CustomAnomaly,
    RecommendationBias,
    DataIntegrity,
    EdgeCase,
)
from uptrain.core.classes.statistics import (
    Distance,
    Convergence,
    Distribution,
)
from uptrain.core.classes.visuals import Umap


class CheckManager:
    def __init__(self, framework, checks=[]):
        self.anomalies_to_check = []
        self.statistics_to_check = []
        self.visuals_to_check = []
        self.fw = framework
        for check in checks:
            if check["type"] in Anomaly:
                self.add_anomaly_to_monitor(check)
            if check["type"] in Statistic:
                self.add_statistics_to_monitor(check)
            if check["type"] in Visual:
                self.add_visuals(check)

    def add_anomaly_to_monitor(self, check):
        if check["type"] == Anomaly.EDGE_CASE:
            edge_case_manager = EdgeCase(self.fw, check["signal_formulae"])
            self.anomalies_to_check.append(edge_case_manager)
        elif check["type"] == Anomaly.CONCEPT_DRIFT:
            drift_manager = ConceptDrift(self.fw, check)
            self.anomalies_to_check.append(drift_manager)
        elif check["type"] == Anomaly.DATA_DRIFT:
            if "measurable_args" in check:
                drift_managers = [
                    DataDrift(
                        self.fw, check, is_embedding=check.get("is_embedding", None)
                    )
                ]
            else:
                drift_managers = []
                all_feats = self.fw.feat_name_list
                for feat in all_feats:
                    check_copy = deepcopy(check)
                    check_copy.update(
                        {
                            "measurable_args": {
                                "type": MeasurableType.INPUT_FEATURE,
                                "feature_name": feat,
                            }
                        }
                    )
                    drift_managers.append(
                        DataDrift(
                            self.fw,
                            check_copy,
                            is_embedding=check_copy.get("is_embedding", None),
                        )
                    )
            self.anomalies_to_check.extend(drift_managers)
        elif check["type"] == Anomaly.POPULARITY_BIAS:
            bias_manager = RecommendationBias(self.fw, check)
            self.anomalies_to_check.append(bias_manager)
        elif check["type"] == Anomaly.CUSTOM_MONITOR:
            custom_monitor = CustomAnomaly(self.fw, check)
            self.anomalies_to_check.append(custom_monitor)
        elif check["type"] == Anomaly.DATA_INTEGRITY:
            custom_monitor = DataIntegrity(self.fw, check)
            self.anomalies_to_check.append(custom_monitor)
        else:
            raise Exception("Anomaly type not Supported")

    def add_statistics_to_monitor(self, check):
        if check["type"] == Statistic.DISTANCE:
            custom_monitor = Distance(self.fw, check)
            self.statistics_to_check.append(custom_monitor)
        elif check["type"] == Statistic.DISTRIBUTION_STATS:
            custom_monitor = Distribution(self.fw, check)
            self.statistics_to_check.append(custom_monitor)
        elif check["type"] == Statistic.CONVERGENCE_STATS:
            custom_monitor = Convergence(self.fw, check)
            self.statistics_to_check.append(custom_monitor)
        else:
            raise Exception("Statistic type not Supported")

    def add_visuals(self, check):
        if check["type"] == Visual.UMAP:
            custom_monitor = Umap(self.fw, check)
            self.visuals_to_check.append(custom_monitor)
        else:
            raise Exception("Visual type not Supported")

    def check(self, inputs, outputs, gts=None, extra_args={}):
        for anomaly in self.anomalies_to_check:
            if anomaly.need_ground_truth() == (gts[0] is not None):
                anomaly.check(inputs, outputs, gts=gts, extra_args=extra_args)
        for stats in self.statistics_to_check:
            stats.check(inputs, outputs, gts=gts, extra_args=extra_args)
        for visuals in self.visuals_to_check:
            visuals.check(inputs, outputs, gts=gts, extra_args=extra_args)

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        is_interesting = []
        for anomaly in self.anomalies_to_check:
            if anomaly.need_ground_truth() == (gts[0] is not None):
                is_interesting.append(
                    anomaly.is_data_interesting(
                        inputs, outputs, gts=gts, extra_args=extra_args
                    )
                )
        return np.greater(np.sum(np.array(is_interesting), axis=0), 0)
