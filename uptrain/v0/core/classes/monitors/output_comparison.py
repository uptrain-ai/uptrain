import numpy as np
from uptrain.v0.core.classes.monitors import AbstractMonitor
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.constants import Monitor, ComparisonModel, ComparisonMetric


class OutputComparison(AbstractMonitor):
    dashboard_name = "output_comparison"
    monitor_type = Monitor.OUTPUT_COMPARISON

    def base_init(self, fw, check):
        self.comparison_model_base = check["comparison_model"]
        self.comparison_model_resolved = ComparisonModelResolver().resolve(
            check["comparison_model"]
        )
        self.comparison_model_inputs = MeasurableResolver(
            check.get("comparison_model_input_args", None)
        ).resolve(fw)
        self.comparison_metric_base = check["comparison_metric"]
        self.comparison_metric_resolved = ComparisonMetricResolver().resolve(
            check["comparison_metric"]
        )
        self.threshold = check["threshold"]
        self.count = 0

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        vals = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )

        comparison_model_inputs = self.comparison_model_inputs.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )

        comparison_model_outputs = self.comparison_model_resolved(
            comparison_model_inputs
        )
        batch_metrics = self.comparison_metric_resolved(vals, comparison_model_outputs)
        self.batch_metrics = batch_metrics

        extra_args.update(
            {
                self.comparison_model_base + " outputs": comparison_model_outputs,
                self.comparison_metric_base: batch_metrics,
            }
        )

        feat_name = self.comparison_metric_base
        plot_name = (
            f"{feat_name} Comparison - Production vs {self.comparison_model_base}"
        )
        self.count += len(extra_args["id"])

        self.log_handler.add_scalars(
            plot_name,
            {"y_" + feat_name: np.mean(batch_metrics)},
            self.count,
            self.dashboard_name,
            file_name=plot_name,
        )

    def need_ground_truth(self):
        return False

    def base_is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        reasons = ["None"] * len(extra_args["id"])
        is_interesting = self.batch_metrics < self.threshold
        reasons = []
        for idx in range(len(extra_args["id"])):
            if is_interesting[idx] == 0:
                reasons.append("None")
            else:
                reasons.append(
                    f"Different output compared to {self.comparison_model_base}"
                )
        return is_interesting, reasons


class ComparisonModelResolver:
    def resolve(self, model):
        if model == ComparisonModel.FASTER_WHISPER:
            from uptrain.v0.ee.lib.algorithms import faster_whisper_speech_to_text

            return faster_whisper_speech_to_text
        else:
            raise Exception(f"{model} can't be resolved")


class ComparisonMetricResolver:
    def resolve(self, metric):
        if metric == ComparisonMetric.ROGUE_L_F1:
            from uptrain.v0.ee.lib.algorithms import rogue_l_similarity

            return rogue_l_similarity
        else:
            raise Exception(f"{metric} can't be resolved")
