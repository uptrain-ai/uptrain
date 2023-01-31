import numpy as np

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.anomalies.distances import DistanceResolver
from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.core.classes.anomalies.measurables import MeasurableResolver
from uptrain.constants import Anomaly

class DistributionStats(AbstractAnomaly):
    dashboard_name = "distribution_stats"
    anomaly_type = Anomaly.DISTRIBUTION_STATS

    def __init__(self, fw, check):
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(fw)
        self.item_counts = {}
        self.feats_dictn = {}
        self.distances_dictn = {}
        self.count_checkpoints = check['count_checkpoints']
        self.distance_types = check['distance_types']
        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

    def check(self, inputs, outputs, gts=None, extra_args={}):
        vals = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        aggregate_ids = self.aggregate_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        updated_counts = []
        for idx in range(len(aggregate_ids)):
            if aggregate_ids[idx] not in self.item_counts:
                self.item_counts.update({aggregate_ids[idx]: 0})
            this_item_count = self.item_counts[aggregate_ids[idx]]
            if this_item_count in self.count_checkpoints:
                if this_item_count not in self.feats_dictn:
                    self.feats_dictn.update({this_item_count: {}})
                    self.distances_dictn.update({this_item_count: {}})
                this_val = extract_data_points_from_batch(vals, [idx])
                self.feats_dictn[this_item_count].update({aggregate_ids[idx]: this_val})
                if len(list(self.feats_dictn[this_item_count].keys())) > 1:
                    updated_counts.append(this_item_count)
                for agg_i in list(self.feats_dictn[this_item_count].keys()):
                    if agg_i == aggregate_ids[idx]:
                        continue
                    this_distances = dict(zip(self.distance_types, [x.compute_distance(this_val, self.feats_dictn[this_item_count][agg_i]) for x in self.dist_classes]))
                    if len(self.distances_dictn[this_item_count]) == 0:
                        for distance_type in self.distance_types:
                            self.distances_dictn[this_item_count].update({distance_type: [this_distances[distance_type]]})
                    else:
                        for distance_key in list(this_distances.keys()):
                            self.distances_dictn[this_item_count][distance_key].append(this_distances[distance_key])
            self.item_counts[aggregate_ids[idx]] += 1

        for count in list(self.distances_dictn.keys()):
            if count in updated_counts:
                for distance_type in self.distance_types:
                    plot_name = (distance_type
                        + " "
                        + self.measurable.col_name()
                        + " "
                        + self.aggregate_measurable.col_name())
                    

                    self.log_handler.add_histogram(
                        self.dashboard_name + "_" + plot_name,
                        self.distances_dictn[count][distance_type],
                        np.log(max(count, 1)),
                        self.dashboard_name,
                    )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"]))

    def need_ground_truth(self):
        return False

    def get_feats_for_clustering(self, count):
        if count in self.feats_dictn:
            return self.feats_dictn[count]
        else:
            return []