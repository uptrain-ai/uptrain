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
        self.reference = check["reference"]
        self.distance_types = check["distance_types"]
        self.count_checkpoints = np.unique(np.array([0] + check["count_checkpoints"]))

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
            "CREATE TABLE ref_embs (id LONG PRIMARY KEY, value FLOAT[], prevCount LONG, prevCheckpoint LONG);"
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
        vals = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        aggregate_ids = self.aggregate_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        counts = self.count_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )

        # TODO: dunno what this is for
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

        # read previous state from the cache
        [
            ref_embs_cache,
            prev_count_cache,
            prev_checkpoint_cache,
        ] = fetch_col_values_for_ids(
            self.conn,
            "ref_embs",
            np.asarray(aggregate_ids),
            ["value", "prevCount", "prevCheckpoint"],
        )

        set_ids_to_cache = set()  # track which ids we need to update in the cache
        for idx in range(len(aggregate_ids)):
            is_model_invalid = sum(
                [
                    all_models[jdx][idx] not in self.allowed_model_values[jdx]
                    for jdx in range(len(self.allowed_model_values))
                ]
            )
            if is_model_invalid:
                continue

            active_id = aggregate_ids[idx]
            prev_count = prev_count_cache.get(aggregate_ids[idx], None)
            curr_count = counts[idx]

            # Four possible cases:
            # 1. curr_count > max(checkpoints): we skip processing this row altogether
            # 2. prev_count = 0: first time we see this aggregate id, so we skip processing it. Save the current state in the cache.
            # 3. curr_count < prev_count: this row is out of order, so we skip processing it. Save the previous state in the cache.
            # 4. max(checkpoints) >= curr_count > prev_count: we have seen this aggregate id before, so we process it. Save the current state in the cache.
            if curr_count > self.count_checkpoints[-1]:
                continue
            elif prev_count is None:
                set_ids_to_cache.add(active_id)
                ref_embs_cache[active_id] = vals[idx]
                prev_count_cache[active_id] = curr_count
                for cp in reversed(self.count_checkpoints):
                    if cp <= curr_count:
                        prev_checkpoint_cache[active_id] = cp
                        break
            elif curr_count < prev_count:
                set_ids_to_cache.add(active_id)
                # ref_emb, count, checkpoint don't need to be updated
            else:
                last_crossed_checkpoint = None
                for cp in reversed(self.count_checkpoints):
                    if prev_count < cp <= curr_count:
                        last_crossed_checkpoint = cp
                        break

                if (
                    last_crossed_checkpoint is None
                ):  # no checkpoints crossed, only need to update the running count
                    set_ids_to_cache.add(active_id)
                    prev_count_cache[active_id] = curr_count
                else:
                    ref_emb = ref_embs_cache[active_id]
                    this_val = vals[idx]
                    # compute the statistics
                    this_distances = dict(
                        zip(
                            self.distance_types,
                            [
                                x.compute_distance(this_val, ref_emb)
                                for x in self.dist_classes
                            ],
                        )
                    )
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
                        self.distances_dictn[last_crossed_checkpoint][
                            distance_key
                        ].extend(this_data)
                        self.log_handler.add_histogram(
                            plot_name,
                            this_data,
                            self.dashboard_name,
                            models=[models] * len(this_data),
                            features=[features] * len(this_data),
                            file_name=str(last_crossed_checkpoint),
                        )

                    set_ids_to_cache.add(active_id)
                    ref_embs_cache[active_id] = (
                        this_val if self.reference == "running_diff" else ref_emb
                    )
                    prev_count_cache[active_id] = curr_count
                    prev_checkpoint_cache[active_id] = last_crossed_checkpoint

        if len(set_ids_to_cache) > 0:
            # save the current state in the cache
            list_ids = list(set_ids_to_cache)
            list_ref_embs, list_counts, list_checkpoints = [], [], []
            for _id in list_ids:
                list_ref_embs.append(ref_embs_cache[_id])
                list_counts.append(prev_count_cache[_id])
                list_checkpoints.append(prev_checkpoint_cache[_id])

            upsert_ids_n_col_values(
                self.conn,
                "ref_embs",
                np.asarray(list_ids),
                {
                    "value": np.asarray(list_ref_embs),
                    "prevCount": np.asarray(list_counts),
                    "prevCheckpoint": np.asarray(list_checkpoints),
                },
            )

        # TODO: dunno what this is for
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
