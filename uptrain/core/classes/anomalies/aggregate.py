import numpy as np

from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.core.classes.anomalies.measurables import MeasurableResolver


class Aggregate(AbstractAnomaly):
    dashboard_name = "aggregate"

    def __init__(self, fw, check):
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(fw)
        self.counts = {}

    def check(self, inputs, outputs, gts=None, extra_args={}):
        vals = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        aggregate_ids = self.aggregate_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        distance_types = self.measurable.distance_types
        plot_names = [
            col_name
            + " "
            + self.aggregate_measurable.col_name()
            for col_name in self.measurable.col_name(return_str=False)
        ]

        for idx in range(len(aggregate_ids)):
            if aggregate_ids[idx] not in self.counts:
                self.counts.update({aggregate_ids[idx]: 0})
            self.counts[aggregate_ids[idx]] += 1
            for jdx in range(len(distance_types)):
                self.log_handler.add_scalars(
                    self.dashboard_name + "_" + plot_names[jdx],
                    {str(aggregate_ids[idx]): vals[distance_types[jdx]][idx]},
                    self.counts[aggregate_ids[idx]],
                    self.dashboard_name,
                )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"]))

    def need_ground_truth(self):
        return False
