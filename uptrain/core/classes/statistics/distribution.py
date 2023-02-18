import numpy as np
import copy
import random

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.distances import DistanceResolver
from uptrain.core.classes.statistics import AbstractStatistic
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Statistic


class Distribution(AbstractStatistic):
    dashboard_name = "distribution_stats"
    statistic_type = Statistic.DISTRIBUTION_STATS

    def __init__(self, fw, check):
        self.allowed_model_values = [x['allowed_values'] for x in check['model_args']]
        self.num_model_options = sum([len(x) > 1 for x in self.allowed_model_values])
        self.children = []

        if self.num_model_options > 0:
            for m in self.allowed_model_values[0]:
                check_copy = copy.deepcopy(check)
                check_copy['model_args'][0]['allowed_values'] = [m]
                check_copy['model_args'].append(copy.deepcopy(check_copy['model_args'][0]))
                del check_copy['model_args'][0]
                self.children.append(Distribution(fw, check_copy))
        else:
            self.log_handler = fw.log_handler
            self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
            self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
                fw
            )
            self.count_measurable = MeasurableResolver(check["count_args"]).resolve(
                fw
            )
            self.feature_measurables = [
                MeasurableResolver(x).resolve(fw) for x in check["feature_args"]
            ]
            self.model_measurables = [
                MeasurableResolver(x).resolve(fw) for x in check["model_args"]
            ]
            self.model_names = [x.col_name() for x in self.model_measurables]
            self.feature_names = [x.col_name() for x in self.feature_measurables]

            self.item_counts = {}

            self.distance_types = check["distance_types"]
            # ex: ['cosine_distance']

            self.count_checkpoints = np.unique(np.array([0] + check["count_checkpoints"]))
            # ex: array([    0,   200,   500,  1000,  5000, 20000])

            self.vals_dictn = dict(zip(list(self.count_checkpoints), [{} for x in list(self.count_checkpoints)]))
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
            all_models = [x.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            ) for x in self.model_measurables]
            all_features = dict(zip([x.feature_name for x in self.feature_measurables], 
                [x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args) 
                for x in self.feature_measurables]))

            models = dict(zip(['model_' + x for x in self.model_names], [self.allowed_model_values[jdx][0] for jdx in range(len(self.model_names))]))
            for idx in range(len(aggregate_ids)):
                is_model_invalid = sum([all_models[jdx][idx] not in self.allowed_model_values[jdx] for jdx in range(len(self.allowed_model_values))])
                if is_model_invalid:
                    continue

                if aggregate_ids[idx] not in self.item_counts:
                    self.item_counts.update({aggregate_ids[idx]: 0})

                this_item_count_prev = self.item_counts[aggregate_ids[idx]]
                if this_item_count_prev == counts[idx]:
                    continue
                self.item_counts[aggregate_ids[idx]] = counts[idx]
                this_item_count = self.item_counts[aggregate_ids[idx]]

                crossed_checkpoint_arr = (np.logical_xor((self.count_checkpoints > this_item_count), 
                    (self.count_checkpoints > this_item_count_prev)))
                has_crossed_checkpoint = sum(crossed_checkpoint_arr)

                if has_crossed_checkpoint: # this_item_count in self.count_checkpoints:

                    if aggregate_ids[idx] not in self.vals_dictn[0]:
                        crossed_checkpoint = 0
                    else:
                        crossed_checkpoint = self.count_checkpoints[np.where(crossed_checkpoint_arr == True)[0][-1]]

                    this_val = extract_data_points_from_batch(vals, [idx])
                    # TODO: Make the following general

                    if aggregate_ids[idx] not in self.vals_dictn[crossed_checkpoint]:
                        self.vals_dictn[crossed_checkpoint].update({aggregate_ids[idx]: {}})
                    self.vals_dictn[crossed_checkpoint][aggregate_ids[idx]].update({'val': this_val})
                    for feat_name, feats in all_features.items():
                        this_feat = extract_data_points_from_batch(feats, [idx])
                        self.vals_dictn[crossed_checkpoint][aggregate_ids[idx]].update({feat_name: this_feat})

                    selected_ids_to_sample = random.choices(list(self.vals_dictn[crossed_checkpoint].keys()), k=min(10, len(self.vals_dictn[crossed_checkpoint].keys())))
                    # for agg_i in list(self.vals_dictn[crossed_checkpoint].keys()):
                    for agg_i in selected_ids_to_sample:
                        if agg_i == aggregate_ids[idx]:
                            continue
                        this_distances = dict(
                            zip(
                                self.distance_types,
                                [
                                    x.compute_distance(
                                        this_val, self.vals_dictn[crossed_checkpoint][agg_i]['val']
                                    )
                                    for x in self.dist_classes
                                ],
                            )
                        )
    
                        for distance_key in list(this_distances.keys()):

                            plot_name = distance_key
                            this_data = list(np.reshape(np.array(this_distances[distance_key]),-1))

                            self.log_handler.add_histogram(
                                plot_name,
                                this_data,
                                self.dashboard_name,
                                count = crossed_checkpoint,
                                models = [models]*len(this_data),
                                file_name = str(crossed_checkpoint)
                            )

    
            # for count in list(self.distances_dictn.keys()):
            #     if count in updated_counts:
            #         for distance_type in self.distance_types:
            #             plot_name = (
            #                 distance_type
            #                 # + " "
            #                 # + self.measurable.col_name()
            #                 # + " "
            #                 # + self.aggregate_measurable.col_name()
            #             )

            #             this_data = list(
            #                 np.reshape(
            #                     np.array(self.distances_dictn[count][distance_type]), -1
            #                 )
            #             )
            #             self.log_handler.add_histogram(
            #                 self.dashboard_name + "_" + plot_name,
            #                 this_data,
            #                 self.dashboard_name,
            #                 count = count,
            #                 size_limit = 1000,
            #                 models = [models]*len(this_data),
            #                 file_name = str(count)
            #             )

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