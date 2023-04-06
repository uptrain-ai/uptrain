import copy
import os
import uuid

import duckdb
import numpy as np

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.distances import DistanceResolver
from uptrain.core.classes.statistics import AbstractStatistic
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Statistic
from uptrain.ee.arrow_utils import fetch_col_values_for_ids, upsert_ids_n_col_values

# from uptrain.core.classes.algorithms import Clustering
# from uptrain.core.lib.algorithms import estimate_earth_moving_cost


class Convergence(AbstractStatistic):
    dashboard_name = "convergence_stats"
    statistic_type = Statistic.CONVERGENCE_STATS

    def base_init(self, fw, check):
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
            fw
        )
        self.count_measurable = MeasurableResolver(check["count_args"]).resolve(fw)
        self.item_counts = {}
        self.first_count_checkpoint = {}
        self.reference = check["reference"]
        self.distance_types = check["distance_types"]

        self.count_checkpoints = np.unique(np.array([0] + check["count_checkpoints"]))

        self.feats_dictn = dict(
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
        self.total_count = 0
        self.prev_calc_at = 0

        # setup a duckdb database to cache interim state for aggregates
        db_dir = os.path.join(fw.fold_name, "dbs", "convergence")
        os.makedirs(db_dir, exist_ok=True)
        self.conn = duckdb.connect(os.path.join(db_dir, str(uuid.uuid4()) + ".db"))
        self.conn.execute(
            "CREATE TABLE ref_embs (id LONG PRIMARY KEY, value FLOAT[], count LONG);"
        )

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        all_models = [
            x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
            for x in self.model_measurables
        ]
        all_features = [
            x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
            for x in self.feature_measurables
        ]
        vals_all = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        aggregate_ids_all = self.aggregate_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        counts_all = self.count_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )

        # CHECK: unsure what these two variables are for
        models = dict(
            zip(
                ["model_" + x for x in self.model_names],
                [
                    self.allowed_model_values[jdx][0]
                    for jdx in range(len(self.model_names))
                ],
            )
        )
        self.total_count += len(extra_args["id"])

        # each batch has rows corresponding to all model values, so we filter out the ones worked on elsewhere
        select_idxs = []
        for idx in range(len(aggregate_ids_all)):
            is_model_invalid = sum(
                [
                    all_models[jdx][idx] not in self.allowed_model_values[jdx]
                    for jdx in range(len(self.allowed_model_values))
                ]
            )
            if not is_model_invalid:
                select_idxs.append(idx)
        if len(select_idxs) == 0:
            return  # nothing for us to do here

        # get the subset of id, counts and values we need to work with
        aggregate_ids = aggregate_ids_all[select_idxs]
        vals = vals_all[select_idxs, :]
        counts = counts_all[select_idxs]
        [ref_embs_cache, counts_cache] = fetch_col_values_for_ids(
            self.conn,
            "ref_embs",
            np.asarray(aggregate_ids_all[select_idxs]),
            ["value", "count"],
        )

        for idx in range(len(aggregate_ids)):
            idx_in_original_batch = select_idxs[idx]
            if aggregate_ids[idx] not in counts_cache:
                counts_cache[aggregate_ids[idx]] = 0

            this_item_count_prev = counts_cache[aggregate_ids[idx]]
            if this_item_count_prev >= counts[idx]:
                continue  # this row is out of order
            else:
                this_item_count = counts[idx]
                counts_cache[aggregate_ids[idx]] = this_item_count

            crossed_checkpoint_arr = np.logical_xor(
                (self.count_checkpoints > this_item_count),
                (self.count_checkpoints > this_item_count_prev),
            )
            has_crossed_checkpoint = sum(crossed_checkpoint_arr)

            if has_crossed_checkpoint:
                crossed_checkpoint = self.count_checkpoints[
                    np.where(crossed_checkpoint_arr == True)[0][-1]
                ]

                if aggregate_ids[idx] not in self.first_count_checkpoint:
                    self.first_count_checkpoint.update(
                        {aggregate_ids[idx]: crossed_checkpoint}
                    )

                this_val = extract_data_points_from_batch(vals, [idx])

                self.feats_dictn[crossed_checkpoint].update(
                    {aggregate_ids[idx]: this_val}
                )
                if crossed_checkpoint > self.first_count_checkpoint[aggregate_ids[idx]]:
                    if self.reference == "running_diff":
                        this_count_idx = np.where(
                            self.count_checkpoints == crossed_checkpoint
                        )[0][0]
                        prev_count_idx = max(0, this_count_idx - 1)
                        found_ref = False
                        while not found_ref:
                            ref_item_count = self.count_checkpoints[prev_count_idx]
                            if aggregate_ids[idx] in self.feats_dictn[ref_item_count]:
                                break
                            prev_count_idx = max(0, prev_count_idx - 1)
                    else:
                        ref_item_count = self.first_count_checkpoint[aggregate_ids[idx]]
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
                    if self.reference == "running_diff":
                        del self.feats_dictn[ref_item_count][aggregate_ids[idx]]
                    else:
                        del self.feats_dictn[crossed_checkpoint][aggregate_ids[idx]]

                    features = dict(
                        zip(
                            ["feature_" + x for x in self.feature_names],
                            [
                                all_features[jdx][idx]
                                for jdx in range(len(self.feature_names))
                            ],
                        )
                    )

                    for distance_key in list(this_distances.keys()):
                        plot_name = distance_key + " " + str(self.reference)
                        this_data = list(
                            np.reshape(np.array(this_distances[distance_key]), -1)
                        )

                        self.distances_dictn[crossed_checkpoint][distance_key].extend(
                            this_data
                        )

                        self.log_handler.add_histogram(
                            plot_name,
                            this_data,
                            self.dashboard_name,
                            models=[models] * len(this_data),
                            features=[features] * len(this_data),
                            file_name=str(crossed_checkpoint),
                        )

        if (self.total_count - self.prev_calc_at) > 50000:
            self.prev_calc_at = self.total_count
            for count in list(self.distances_dictn.keys()):
                if count > 0:
                    for distance_type in self.distance_types:
                        plot_name = distance_type + " " + str(self.reference)
                        this_data = np.reshape(
                            np.array(self.distances_dictn[count][distance_type]), -1
                        )

                        if len(this_data) > 5:
                            self.log_handler.add_scalars(
                                plot_name + "_mean",
                                {"y_mean": np.mean(this_data)},
                                count,
                                self.dashboard_name,
                                models=models,
                                features={"tagGenre": "All"},
                                file_name=str("count"),
                                update_val=True,
                            )

                            # next_count_idx = np.where(self.count_checkpoints == (count))[0][0] + 1
                            # if next_count_idx < len(self.count_checkpoints):
                            #     next_data = np.reshape(
                            #         np.array(self.distances_dictn[self.count_checkpoints[next_count_idx]][distance_type]), -1
                            #     )
                            #     if len(next_data) > 5:
                            #         clustering_helper = Clustering({"num_buckets": 2, "is_embedding": False})
                            #         this_data = np.expand_dims(np.array(this_data), axis=(1))
                            #         next_data = np.expand_dims(np.array(next_data), axis=(1,2))
                            #         this_count_clustering_res = clustering_helper.cluster_data(this_data)
                            #         next_count_clustering_res = clustering_helper.infer_cluster_assignment(next_data)
                            #         emd_cost = estimate_earth_moving_cost(np.reshape(next_count_clustering_res[1]/next_data.shape[0],-1), np.reshape(clustering_helper.dist[0],-1), clustering_helper.clusters[0])
                            #         self.log_handler.add_scalars(
                            #             plot_name + "_emd",
                            #             {'y_distance': emd_cost},
                            #             count,
                            #             # self.total_count,
                            #             self.dashboard_name,
                            #             models = models,
                            #             features = {"tagGenre": "All"},
                            #             file_name = str("count"),
                            #             update_val = True
                            #         )
