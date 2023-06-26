from typing import TYPE_CHECKING
import numpy as np
import random

from uptrain.v0.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.v0.core.classes.distances import DistanceResolver
from uptrain.v0.core.classes.statistics import AbstractStatistic
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.constants import Statistic

if TYPE_CHECKING:
    from uptrain.v0.core.classes.logging.log_handler import LogHandler, CsvWriter


class Distribution(AbstractStatistic):
    dashboard_name = "distribution_stats"
    statistic_type = Statistic.DISTRIBUTION_STATS

    def base_init(self, fw, check):
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
            fw
        )
        self.count_measurable = MeasurableResolver(check["count_args"]).resolve(fw)
        self.item_counts = {}
        self.distance_types = check["distance_types"]

        # ex: ['cosine_distance']
        self.count_checkpoints = np.unique(np.array([0] + check["count_checkpoints"]))
        # ex: array([    0,   200,   500,  1000,  5000, 20000])
        self.vals_dictn = dict(
            zip(
                list(self.count_checkpoints), [{} for x in list(self.count_checkpoints)]
            )
        )
        # ex: {0: {agg_id_0: val_0, ..}, 200: {}, 500: {}, 1000: {}, 5000: {}, 20000: {}}
        self.distances_dictn = dict(
            zip(
                list(self.count_checkpoints),
                [
                    dict(
                        zip(
                            self.distance_types, [[] for x in list(self.distance_types)]
                        )
                    )
                    for y in list(self.count_checkpoints)
                ],
            )
        )
        # ex: {0: {'cosine_distance': [d1, d2, ..]}, 200: {'cosine_distance': []}, 500: {'cosine_distance': []}, 1000: {'cosine_distance': []}, 5000: {'cosine_distance': []}, 20000: {'cosine_distance': []}}

        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        vals = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        aggregate_ids = self.aggregate_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        counts = self.count_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        all_models = [
            x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
            for x in self.model_measurables
        ]
        all_features = dict(
            zip(
                self.feature_names,
                [
                    x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
                    for x in self.feature_measurables
                ],
            )
        )

        models = dict(
            zip(
                ["model_" + x for x in self.model_names],
                [
                    self.allowed_model_values[jdx][0]
                    for jdx in range(len(self.model_names))
                ],
            )
        )
        for idx in range(len(aggregate_ids)):
            is_model_invalid = sum(
                [
                    all_models[jdx][idx] not in self.allowed_model_values[jdx]
                    for jdx in range(len(self.allowed_model_values))
                ]
            )
            if is_model_invalid:
                continue

            if aggregate_ids[idx] not in self.item_counts:
                self.item_counts.update({aggregate_ids[idx]: 0})

            this_item_count_prev = self.item_counts[aggregate_ids[idx]]
            if this_item_count_prev == counts[idx]:
                continue
            self.item_counts[aggregate_ids[idx]] = counts[idx]
            this_item_count = self.item_counts[aggregate_ids[idx]]

            crossed_checkpoint_arr = np.logical_xor(
                (self.count_checkpoints > this_item_count),
                (self.count_checkpoints > this_item_count_prev),
            )
            has_crossed_checkpoint = sum(crossed_checkpoint_arr)

            if has_crossed_checkpoint:
                if aggregate_ids[idx] not in self.vals_dictn[0]:
                    crossed_checkpoint = 0
                else:
                    crossed_checkpoint = self.count_checkpoints[
                        np.where(crossed_checkpoint_arr == True)[0][-1]
                    ]

                this_val = extract_data_points_from_batch(vals, [idx])

                if aggregate_ids[idx] not in self.vals_dictn[crossed_checkpoint]:
                    self.vals_dictn[crossed_checkpoint].update({aggregate_ids[idx]: {}})
                self.vals_dictn[crossed_checkpoint][aggregate_ids[idx]].update(
                    {"val": this_val}
                )
                self.vals_dictn[crossed_checkpoint][aggregate_ids[idx]].update(
                    {
                        "visual_hover_text_"
                        + self.aggregate_measurable.col_name(): aggregate_ids[idx]
                    }
                )
                for feat_name, feats in all_features.items():
                    this_feat = extract_data_points_from_batch(feats, [idx])
                    self.vals_dictn[crossed_checkpoint][aggregate_ids[idx]].update(
                        {"visual_label_" + feat_name: this_feat}
                    )

                selected_ids_to_sample = random.choices(
                    list(self.vals_dictn[crossed_checkpoint].keys()),
                    k=min(10, len(self.vals_dictn[crossed_checkpoint].keys())),
                )
                for agg_i in selected_ids_to_sample:
                    if agg_i == aggregate_ids[idx]:
                        continue
                    this_distances = dict(
                        zip(
                            self.distance_types,
                            [
                                x.compute_distance(
                                    this_val,
                                    self.vals_dictn[crossed_checkpoint][agg_i]["val"],
                                )
                                for x in self.dist_classes
                            ],
                        )
                    )

                    for distance_key in list(this_distances.keys()):
                        plot_name = distance_key
                        this_data = list(
                            np.reshape(np.array(this_distances[distance_key]), -1)
                        )

                        self.log_handler.add_histogram(
                            plot_name,
                            this_data,
                            self.dashboard_name,
                            models=[models] * len(this_data),
                            file_name=str(crossed_checkpoint),
                        )

    def get_feats_for_clustering(self, count, allowed_model_values):
        if len(self.children) > 0:
            res = {}
            feats = {}
            for x in self.children:
                val = x.get_feats_for_clustering(count, allowed_model_values)
                res.update(val)
            return res
        else:
            if self.allowed_model_values == allowed_model_values:
                if count in self.vals_dictn:
                    return self.vals_dictn[count]
                else:
                    return {}
            else:
                return {}
