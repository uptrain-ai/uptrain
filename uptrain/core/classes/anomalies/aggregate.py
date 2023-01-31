import numpy as np

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.core.classes.anomalies.distances import DistanceResolver
from uptrain.core.classes.anomalies.measurables import MeasurableResolver
from uptrain.constants import Anomaly


class Aggregate(AbstractAnomaly):
    dashboard_name = "aggregate"
    anomaly_type = Anomaly.AGGREGATE

    def __init__(self, fw, check):
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(fw)
        self.item_counts = {}
        self.feats_dictn = {}
        self.reference = check['reference']
        self.distance_types = check['distance_types']
        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

    def check(self, inputs, outputs, gts=None, extra_args={}):
        vals = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        aggregate_ids = self.aggregate_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )

        for idx in range(len(aggregate_ids)):
            if aggregate_ids[idx] not in self.item_counts:
                self.item_counts.update({aggregate_ids[idx]: 0})
            this_item_count = self.item_counts[aggregate_ids[idx]]
            this_val = extract_data_points_from_batch(vals, [idx])

            if this_item_count > 0:
                this_distances = dict(zip(self.distance_types, [x.compute_distance(this_val, self.feats_dictn[aggregate_ids[idx]]) for x in self.dist_classes]))
                if self.reference == "running_diff":
                    self.feats_dictn[aggregate_ids[idx]] = this_val
                for distance_type in self.distance_types:
                    plot_name = (distance_type
                        + " "
                        + str(self.reference)
                        + self.measurable.col_name()
                        + " "
                        + self.aggregate_measurable.col_name())
                    self.log_handler.add_scalars(
                        self.dashboard_name + "_" + plot_name,
                        {str(aggregate_ids[idx]): this_distances[distance_type]},
                        this_item_count,
                        self.dashboard_name,
                    )
            else:
                self.feats_dictn.update({aggregate_ids[idx]: this_val})
            self.item_counts[aggregate_ids[idx]] += 1

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"]))

    def need_ground_truth(self):
        return False
