import numpy as np

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.distances import DistanceResolver
from uptrain.core.classes.statistics import AbstractStatistic
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Statistic
from uptrain.core.lib.cache import make_cache_container

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
        self.count_checkpoints = list(sorted(set([0] + check["count_checkpoints"])))

        self.distances_dictn = dict(
            zip(
                self.count_checkpoints,
                [
                    dict(
                        zip(
                            self.distance_types, [[] for x in list(self.distance_types)]
                        )
                    )
                    for y in self.count_checkpoints
                ],
            )
        )
        # ex: {0: {'cosine_distance': [d1, d2, ..]}, 200: {'cosine_distance': []}, 500: {'cosine_distance': []}, 1000: {'cosine_distance': []}, 5000: {'cosine_distance': []}, 20000: {'cosine_distance': []}}

        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]
        self.total_count = 0
        self.prev_calc_at = 0

        # setup a cache to store interim state for aggregates
        props_to_store = {
            "ref_embedding": np.ndarray,
            "prev_count": int,
            "first_checkpoint": int,
        }
        self.cache = make_cache_container(fw, props_to_store)

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
        self.total_count += len(extra_args["id"])
        models = dict(
            zip(
                ["model_" + x for x in self.model_names],
                [
                    self.allowed_model_values[jdx][0]
                    for jdx in range(len(self.model_names))
                ],
            )
        )

        # read previous state from the cache
        # - ref_embs_cache: the reference embedding for each aggregate id
        # - prev_count_cache: the previous view count seen for each aggregate id
        # - first_crossed_checkpoint_cache: the first checkpoint that was crossed for each aggregate id
        [
            ref_embs_cache,
            prev_count_cache,
            first_crossed_checkpoint_cache,
        ] = self.cache.fetch_col_values_for_ids(
            np.asarray(aggregate_ids),
            ["ref_embedding", "prev_count", "first_checkpoint"],
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
            prev_count = prev_count_cache.get(active_id, None)
            curr_count = counts[idx]
            ref_emb = ref_embs_cache.get(active_id, None)
            curr_emb = vals[idx]

            print("-------------------------")
            print(active_id)
            print("prev_count", prev_count)
            print("curr_count", curr_count)

            # Four possible cases:
            # 1. prev_count = None: first time we see this aggregate id, so we skip processing it. Save the current state in the cache.
            # 2. prev_count > max(checkpoints): we skip processing this row altogether since all checkpoints have been crossed.
            # 3. prev_count > curr_count: this row is out of order, so we skip processing it.
            # 4. curr_count > prev_count: we have seen this aggregate id before, so we process it. Save the current state in the cache.
            if prev_count is None:
                set_ids_to_cache.add(active_id)
                ref_embs_cache[active_id] = curr_emb
                prev_count_cache[active_id] = curr_count
                # negative value as the placeholder for `not checkpoints crossed yet`
                first_crossed_checkpoint_cache[active_id] = -1
            elif prev_count > self.count_checkpoints[-1]:
                continue
            elif prev_count > curr_count:
                continue
            else:
                last_crossed_checkpoint = None
                for cp in reversed(self.count_checkpoints):
                    if prev_count > cp:
                        break  # we are already past this checkpoint or those smaller than it
                    elif (prev_count < cp) and (cp <= curr_count):
                        last_crossed_checkpoint = cp
                        break

                set_ids_to_cache.add(active_id)
                prev_count_cache[active_id] = curr_count

                if last_crossed_checkpoint is None:
                    # no new checkpoint crossed, so we just update the last count seen and move on
                    continue
                elif first_crossed_checkpoint_cache[active_id] < 0:
                    # new checkpoint crossed but this is the first one, so store the reference embedding and move on.
                    first_crossed_checkpoint_cache[active_id] = last_crossed_checkpoint
                    ref_embs_cache[active_id] = curr_emb
                    print("crossed checkpoint ", last_crossed_checkpoint)
                else:
                    # new checkpoint crossed and we have a reference embedding, so compute the statistics.
                    # Update the reference embedding if necessary.
                    print("crossed checkpoint ", last_crossed_checkpoint)
                    print("written log")
                    assert ref_emb is not None
                    if self.reference == "running_diff":
                        ref_embs_cache[active_id] = curr_emb

                    # compute the statistics
                    this_distances = dict(
                        zip(
                            self.distance_types,
                            [
                                x.compute_distance(curr_emb, ref_emb)
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

        if len(set_ids_to_cache) > 0:
            # save the current state in the cache
            list_ids = list(set_ids_to_cache)
            list_ref_embs, list_counts, list_first_checkpoints = [], [], []
            for _id in list_ids:
                list_ref_embs.append(ref_embs_cache[_id])
                list_counts.append(prev_count_cache[_id])
                list_first_checkpoints.append(first_crossed_checkpoint_cache[_id])

            self.cache.upsert_ids_n_col_values(
                np.asarray(list_ids),
                {
                    "ref_embedding": np.asarray(list_ref_embs),
                    "prev_count": np.asarray(list_counts),
                    "first_checkpoint": np.asarray(list_first_checkpoints),
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
