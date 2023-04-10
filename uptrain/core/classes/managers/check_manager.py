import numpy as np
from copy import deepcopy

from uptrain.constants import Monitor, Statistic, Visual, MeasurableType
from uptrain.core.classes.monitors import (
    Accuracy,
    ConceptDrift,
    DataDrift,
    FeatureDrift,
    CustomMonitor,
    ModelBias,
    DataIntegrity,
    EdgeCase,
)
from uptrain.core.classes.statistics import (
    Distance,
    Convergence,
    Distribution,
)
from uptrain.core.classes.visuals import DimensionalityReduction, UMAP_PRESENT, Shap, SHAP_PRESENT, Plot
from uptrain.core.classes.finetuning import Finetune


class CheckManager:
    def __init__(self, framework, checks=[]):
        self.monitors_to_check = []
        self.statistics_to_check = []
        self.visuals_to_check = []
        self.fw = framework
        for check in checks:
            if check["type"] in Monitor:
                self.add_monitor(check)
            if check["type"] in Statistic:
                self.add_statistic(check)
            if check["type"] in Visual:
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
        elif check["type"] == Monitor.DATA_DRIFT or Monitor.FEATURE_DRIFT:
            if check["type"] == Monitor.DATA_DRIFT:
                drift_class = DataDrift
            else:
                drift_class = FeatureDrift
            if "measurable_args" in check:
                drift_managers = [DataDrift(self.fw, check)]
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
                    drift_managers.append(DataDrift(self.fw, check_copy))
            self.monitors_to_check.extend(drift_managers)
        elif check["type"] == Monitor.POPULARITY_BIAS:
            bias_manager = ModelBias(self.fw, check)
            self.monitors_to_check.append(bias_manager)
        elif check["type"] == Monitor.CUSTOM_MONITOR:
            custom_monitor = CustomMonitor(self.fw, check)
            self.monitors_to_check.append(custom_monitor)
        elif check["type"] == Monitor.DATA_INTEGRITY:
            custom_monitor = DataIntegrity(self.fw, check)
            self.monitors_to_check.append(custom_monitor)
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
        else:
            raise Exception("Statistic type not Supported")

    def add_visual(self, check):
        if check["type"] == Visual.UMAP:
            if UMAP_PRESENT:
                custom_monitor = DimensionalityReduction(self.fw, check)
                self.visuals_to_check.append(custom_monitor)
            else:
                print(
                    """UMAP is not installed. For UMAP visualization, please install umap by running `pip install umap-learn`."""
                )
        elif check["type"] == Visual.TSNE:
            custom_monitor = DimensionalityReduction(self.fw, check)
            self.visuals_to_check.append(custom_monitor)
        elif check["type"] == Visual.SHAP:
            if SHAP_PRESENT:
                custom_monitor = Shap(self.fw, check)
                self.visuals_to_check.append(custom_monitor)
            else:
                print(
                    """SHAP is not installed. For SHAP explainability, please install it by running `pip install shap matplotlib`."""
                )
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
        for visuals in self.visuals_to_check:
            visuals.check(inputs, outputs, gts=gts, extra_args=extra_args)

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
