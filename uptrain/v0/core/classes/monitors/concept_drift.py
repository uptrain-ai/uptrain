import numpy as np

from river import drift

from uptrain.v0.core.classes.monitors import AbstractMonitor
from uptrain.v0.constants import DataDriftAlgo, MeasurableType
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.constants import Monitor
from uptrain.v0.core.lib.helper_funcs import add_data_to_warehouse


class ConceptDrift(AbstractMonitor):
    monitor_type = Monitor.CONCEPT_DRIFT

    def base_init(self, fw, check):
        if check.get("measurable_args", None):
            self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        else:
            self.measurable = MeasurableResolver(
                {"type": MeasurableType.ACCURACY}
            ).resolve(fw)

        self.avg_acc = 0
        self.drift_alerted = False
        self.algorithm = check["algorithm"]
        self.counter = 0
        self.plot_name = f"avg_accuracy_{self.measurable.col_name()}"
        self.feat_slicing = check.get("feat_slicing", False)

        if self.algorithm == DataDriftAlgo.DDM:
            warm_start = check.get("warm_start", 500)
            warn_threshold = check.get("warn_threshold", 2.0)
            alarm_threshold = check.get("alarm_threshold", 3.0)
            self.algo = drift.DDM(warm_start, warn_threshold, alarm_threshold)
        elif self.algorithm == DataDriftAlgo.ADWIN:
            delta = check.get("delta", 0.002)
            clock = check.get("clock", 32)
            max_buckets = check.get("max_buckets", 5)
            min_window_length = check.get("min_window_length", 5)
            grace_period = check.get("grace_period", 5)
            self.algo = drift.ADWIN(
                delta, clock, max_buckets, min_window_length, grace_period
            )
        else:
            raise Exception("Data drift algo type not supported")

    def need_ground_truth(self):
        return True

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        all_models = [
            x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
            for x in self.model_measurables
        ]
        all_features = [
            x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
            for x in self.feature_measurables
        ]

        batch_acc = self.measurable.compute_and_log(inputs, outputs, gts, extra_args)
        batch_acc = self._preprocess(batch_acc)

        for i, acc in enumerate(batch_acc):
            alert = None
            self.algo.update(acc)

            if self.algo.drift_detected and not self.drift_alerted:
                alert = f"Concept Drift detected! [Algorithm: {self.algorithm}] [Time: {self.counter}] [Measurable: {self.measurable.col_name()}]"
                print(alert)
                self.drift_alerted = True

            self.avg_acc = (self.avg_acc * self.counter + acc) / (self.counter + 1)
            self.counter += 1
            models = dict(
                zip(
                    self.model_names,
                    [all_models[jdx][i] for jdx in range(len(self.model_names))],
                )
            )
            features = dict(
                zip(
                    self.feature_names,
                    [all_features[jdx][i] for jdx in range(len(self.feature_names))],
                )
            )
            self.log_handler.add_scalars(
                self.plot_name,
                {"y_avg_accuracy": self.avg_acc},
                self.counter,
                self.dashboard_name,
                features=features,
                models=models,
            )

            if isinstance(alert, str):
                self.log_handler.add_alert(
                    "Model Performance Degradation Alert 🚨", alert, self.dashboard_name
                )
        if self.feat_slicing:
            add_data_to_warehouse(
                {"id": inputs["id"], self.dashboard_name: batch_acc},
                self.path_dashboard_data,
            )

    def _preprocess(self, batch):
        if self.algorithm == DataDriftAlgo.DDM:
            return np.array([0 if x else 1 for x in batch])
        else:
            return np.array(batch)
