import numpy as np
from copy import deepcopy

from uptrain.v0.constants import Monitor, Statistic, Visual, MeasurableType
from uptrain.v0.core.classes.monitors import (
    Accuracy,
    ConceptDrift,
    DataDrift,
    FeatureDrift,
    CustomMonitor,
    ModelBias,
    DataIntegrity,
    EdgeCase,
    OutputComparison,
)
from uptrain.v0.core.classes.statistics import (
    Distance,
    Convergence,
    Distribution,
    NormEmbedding,
)
from uptrain.v0.core.classes.visuals import (
    DimensionalityReduction,
    Shap,
    Plot,
)
from uptrain.v0.core.classes.finetuning import Finetune


class CheckManager:
    def __init__(self, framework, checks=[]):
        self.monitors_to_check = []
        self.statistics_to_check = []
        self.visuals_to_check = []
        self.fw = framework
        for check in checks:
            if check["type"] in list(Monitor):
                self.add_monitor(check)
            if check["type"] in list(Statistic):
                self.add_statistic(check)
            if check["type"] in list(Visual):
                self.add_visual(check)

    def add_monitor(self, check):
        if check["type"] == Monitor.EDGE_CASE:
            edge_case_manager = EdgeCase(self.fw, check)
            self.monitors_to_check.append(edge_case_manager)
        elif check["type"] == Monitor.ACCURACY:
            acc_manager = Accuracy(self.fw, check)
            self.monitors_to_check.append(acc_manager)
        elif check["type"] == Monitor.CONCEPT_DRIFT:
            drift_manager = ConceptDrift(self.fw, check)
            self.monitors_to_check.append(drift_manager)
        elif (
            check["type"] == Monitor.DATA_DRIFT
            or check["type"] == Monitor.FEATURE_DRIFT
        ):
            if check["type"] == Monitor.DATA_DRIFT:
                drift_class = DataDrift
            else:
                drift_class = FeatureDrift
            if "measurable_args" in check:
                drift_managers = [drift_class(self.fw, check)]
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
                    drift_managers.append(drift_class(self.fw, check_copy))
            self.monitors_to_check.extend(drift_managers)
        elif check["type"] == Monitor.POPULARITY_BIAS:
            bias_manager = ModelBias(self.fw, check)
            self.monitors_to_check.append(bias_manager)
        elif check["type"] == Monitor.CUSTOM_MONITOR:
            custom_monitor = CustomMonitor(self.fw, check)
            self.monitors_to_check.append(custom_monitor)
        elif check["type"] == Monitor.DATA_INTEGRITY:
            if "measurable_args" in check:
                integrity_managers = [DataIntegrity(self.fw, check)]
            else:
                integrity_managers = []
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
                    integrity_managers.append(DataIntegrity(self.fw, check_copy))
            self.monitors_to_check.extend(integrity_managers)
        elif check["type"] == Monitor.OUTPUT_COMPARISON:
            comparison_monitor = OutputComparison(self.fw, check)
            self.monitors_to_check.append(comparison_monitor)
        else:
            raise Exception("Monitor type not Supported")

    def add_statistic(self, check):
        if check["type"] == Statistic.DISTANCE:
            custom_monitor = Distance(self.fw, check)
            self.statistics_to_check.append(custom_monitor)
        elif check["type"] == Statistic.DISTRIBUTION_STATS:
            custom_monitor = Distribution(self.fw, check)
            self.statistics_to_check.append(custom_monitor)
        elif check["type"] == Statistic.CONVERGENCE_STATS:
            custom_monitor = Convergence(self.fw, check)
            self.statistics_to_check.append(custom_monitor)
        elif check["type"] == Statistic.FINETUNE:
            finetune_monitor = Finetune(self.fw, check)
            self.statistics_to_check.append(finetune_monitor)
        elif check["type"] == Statistic.NORM_EMBEDDING:
            self.statistics_to_check.append(NormEmbedding(self.fw, check))
        else:
            raise Exception("Statistic type not Supported")

    def add_visual(self, check):
        if check["type"] == Visual.UMAP:
            custom_monitor = DimensionalityReduction(self.fw, check)
            self.visuals_to_check.append(custom_monitor)
        elif check["type"] == Visual.TSNE:
            custom_monitor = DimensionalityReduction(self.fw, check)
            self.visuals_to_check.append(custom_monitor)
        elif check["type"] == Visual.SHAP:
            custom_monitor = Shap(self.fw, check)
            self.visuals_to_check.append(custom_monitor)
        elif check["type"] == Visual.PLOT:
            custom_monitor = Plot(self.fw, check)
            self.visuals_to_check.append(custom_monitor)
        else:
            raise Exception("Visual type not Supported")

    def check(self, inputs, outputs, gts=None, extra_args={}):
        for monitor in self.monitors_to_check:
            if monitor.need_ground_truth() == (gts[0] is not None):
                monitor.check(inputs, outputs, gts=gts, extra_args=extra_args)
        for stats in self.statistics_to_check:
            stats.check(inputs, outputs, gts=gts, extra_args=extra_args)
        for visual in self.visuals_to_check:
            if visual.need_ground_truth() == (gts[0] is not None):
                visual.check(inputs, outputs, gts=gts, extra_args=extra_args)

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        is_interesting = []
        reasons = []
        for monitor in self.monitors_to_check:
            if monitor.need_ground_truth() == (gts[0] is not None):
                res = monitor.is_data_interesting(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
                is_interesting.append(res[0])
                reasons.append(res[1])
        if len(reasons):
            final_reason = ["None"] * len(reasons[0])
            for reas in reasons:
                for jdx in range(len(reas)):
                    if not (reas[jdx] == "None"):
                        final_reason[jdx] = reas[jdx]
        else:
            final_reason = []
        return np.greater(np.sum(np.array(is_interesting), axis=0), 0), np.array(
            final_reason
        )
