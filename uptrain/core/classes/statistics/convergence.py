import numpy as np
import copy

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.distances import DistanceResolver
from uptrain.core.classes.statistics import AbstractStatistic
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Statistic


class Convergence(AbstractStatistic):
    dashboard_name = "convergence_stats"
    anomaly_type = Statistic.CONVERGENCE_STATS

    def __init__(self, fw, check):
        self.allowed_model_values = check['model_args'].get('allowed_values', [])
        self.children = []

        if len(self.allowed_model_values) > 1:
            for m in self.allowed_model_values:
                check_copy = copy.deepcopy(check)
                check_copy['model_args']['allowed_values'] = [m]
                self.children.append(Convergence(fw, check_copy))
        else:
            self.dashboard_name = self.dashboard_name + "_" + self.allowed_model_values[0]
            self.log_handler = fw.log_handler
            self.log_handler.add_writer(self.dashboard_name)
            self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
            self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
                fw
            )
            self.count_measurable = MeasurableResolver(check["count_args"]).resolve(
                fw
            )
            self.feature_meaasurables = [
                MeasurableResolver(x).resolve(fw) for x in check["feature_args"]
            ]
            self.model_measurable = MeasurableResolver(check["model_args"]).resolve(
                fw
            )
            self.item_counts = {}
            self.reference = check["reference"]
            self.distance_types = check["distance_types"]

            self.count_checkpoints = np.unique(np.array([0] + check["count_checkpoints"]))

            self.feats_dictn = dict(zip(list(self.count_checkpoints), [{} for x in list(self.count_checkpoints)]))
            # ex: {0: {agg_id_0: val_0, ..}, 200: {}, 500: {}, 1000: {}, 5000: {}, 20000: {}}

            self.distances_dictn = dict(zip(list(self.count_checkpoints), [dict(zip(self.distance_types, [[] for x in list(self.distance_types)])) for y in list(self.count_checkpoints)]))
            #ex: {0: {'cosine_distance': [d1, d2, ..]}, 200: {'cosine_distance': []}, 500: {'cosine_distance': []}, 1000: {'cosine_distance': []}, 5000: {'cosine_distance': []}, 20000: {'cosine_distance': []}}

            self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

    def check(self, inputs, outputs, gts=None, extra_args={}):
        if len(self.children) > 0:
            [x.check(inputs, outputs, gts, extra_args) for x in self.children]
        else:
            vals = self.measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            aggregate_ids = self.aggregate_measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            counts = self.count_measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            models = self.model_measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            all_features = [x.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            ) for x in self.feature_meaasurables]
            update_counts = []
            for idx in range(len(aggregate_ids)):
                if models[idx] not in self.allowed_model_values:
                    continue

                if aggregate_ids[idx] not in self.item_counts:
                    self.item_counts.update({aggregate_ids[idx]: 0})

                this_item_count_prev = self.item_counts[aggregate_ids[idx]]
                if this_item_count_prev == counts[idx]:
                    continue
                self.item_counts[aggregate_ids[idx]] = counts[idx]
                this_item_count = self.item_counts[aggregate_ids[idx]]

                crossed_checkpoint_arr = (np.logical_xor((self.count_checkpoints > this_item_count), (self.count_checkpoints > this_item_count_prev)))
                has_crossed_checkpoint = sum(crossed_checkpoint_arr)

                if has_crossed_checkpoint: # this_item_count in self.count_checkpoints:
                    if aggregate_ids[idx] not in self.feats_dictn[0]:
                        crossed_checkpoint = 0
                    else:
                        crossed_checkpoint = self.count_checkpoints[np.where(crossed_checkpoint_arr == True)[0][-1]]

                    this_val = extract_data_points_from_batch(vals, [idx])

                    self.feats_dictn[crossed_checkpoint].update({aggregate_ids[idx]: this_val})
                    if crossed_checkpoint > 0:
                        if self.reference == "running_diff":
                            this_count_idx = np.where(self.count_checkpoints == crossed_checkpoint)[0][0]
                            prev_count_idx = max(0, this_count_idx - 1)
                            found_ref = False
                            while not found_ref:
                                ref_item_count = self.count_checkpoints[prev_count_idx]
                                if aggregate_ids[idx] in self.feats_dictn[ref_item_count]:
                                    break
                                prev_count_idx = max(0, prev_count_idx - 1)
                        else:
                            ref_item_count = 0
                        this_distances = dict(
                            zip(
                                self.distance_types,
                                [
                                    x.compute_distance(
                                        this_val,
                                        self.feats_dictn[ref_item_count][
                                            aggregate_ids[idx]
                                        ],
                                    )
                                    for x in self.dist_classes
                                ],
                            )
                        )
                        update_counts.append(crossed_checkpoint)
                        if self.reference == "running_diff":
                            del self.feats_dictn[ref_item_count][aggregate_ids[idx]]
                        else:
                            del self.feats_dictn[crossed_checkpoint][aggregate_ids[idx]]

                        for distance_key in list(this_distances.keys()):
                            self.distances_dictn[crossed_checkpoint][distance_key].append(
                                this_distances[distance_key]
                            )

            for count in list(self.distances_dictn.keys()):
                if (count > 0) and (count in update_counts):
                    for distance_type in self.distance_types:
                        plot_name = (
                            distance_type
                            + " "
                            + str(self.reference)
                            # + self.measurable.col_name()
                            # + " "
                            # + self.aggregate_measurable.col_name()
                        )
                        this_data = list(
                            np.reshape(
                                np.array(self.distances_dictn[count][distance_type]), -1
                            )
                        )
                        self.log_handler.add_histogram(
                            self.dashboard_name + "_" + plot_name,
                            this_data,
                            self.dashboard_name,
                            count
                        )
