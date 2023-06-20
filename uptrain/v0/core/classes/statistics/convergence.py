from __future__ import annotations
from typing import TYPE_CHECKING, Union
import numpy as np

from uptrain.v0.core.lib.helper_funcs import make_2d_np_array
from uptrain.v0.core.classes.distances import DistanceResolver
from uptrain.v0.core.classes.statistics import AbstractStatistic
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.constants import Statistic
from uptrain.v0.core.lib.cache import make_cache_container

if TYPE_CHECKING:
    from uptrain.v0.core.classes.logging.new_log_handler import (
        LogHandler as NewLogHandler,
        LogWriter,
    )
    from uptrain.v0.core.classes.logging.log_handler import LogHandler

# from uptrain.v0.core.classes.algorithms import Clustering
# from uptrain.v0.core.lib.algorithms import estimate_earth_moving_cost


class Convergence(AbstractStatistic):
    log_handler: Union["LogHandler", "NewLogHandler"]
    log_writers: list["LogWriter"]
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

        # setup a cache to store interim state for aggregates
        props_to_store = {
            "ref_embedding": np.ndarray,
            "prev_count": int,
            "first_checkpoint": int,
        }
        self.cache = make_cache_container(fw, props_to_store)

        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]
        if hasattr(self.log_handler, "make_logger"):
            self.log_writers = [
                self.log_handler.make_logger(
                    self.dashboard_name, distance_type + "_" + str(self.reference)
                )
                for distance_type in self.distance_types
            ]  # get handles to log writers for each distance type
        else:
            self.log_writers = []

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

            # Four possible cases:
            # 1. prev_count = None: first time we see this aggregate id, so we skip processing it. Save the current state in the cache.
            # 2. prev_count > max(checkpoints): we skip processing this row altogether since all checkpoints have been crossed.
            # 3. prev_count > curr_count: this row is out of order, so we skip processing it.
            # 4. curr_count > prev_count: we have seen this aggregate id before, so we process it. Save the current state in the cache.
            if prev_count is None:
                crossed_checkpoint = max(
                    cp for cp in self.count_checkpoints if cp <= curr_count
                )

                set_ids_to_cache.add(active_id)
                prev_count_cache[active_id] = curr_count
                ref_embs_cache[active_id] = curr_emb
                first_crossed_checkpoint_cache[active_id] = crossed_checkpoint
            elif prev_count > self.count_checkpoints[-1]:
                continue
            elif prev_count > curr_count:
                continue
            else:
                last_crossed_checkpoint = None
                for cp in reversed(self.count_checkpoints):
                    if prev_count > cp:
                        break  # we are already past this checkpoint or those smaller than it
                    elif (prev_count <= cp) and (cp < curr_count):
                        last_crossed_checkpoint = cp
                        break

                set_ids_to_cache.add(active_id)
                prev_count_cache[active_id] = curr_count

                if last_crossed_checkpoint is None:
                    # no new checkpoint crossed, so we just update the last count seen and move on
                    continue
                else:
                    # new checkpoint crossed and we have a reference embedding, so compute the statistics.
                    # Update the reference embedding if necessary.
                    assert ref_emb is not None
                    if self.reference == "running":
                        ref_embs_cache[active_id] = curr_emb

                    # compute the statistics
                    distances = dict(
                        zip(
                            self.distance_types,
                            [
                                x.compute_distance(
                                    make_2d_np_array(curr_emb),
                                    make_2d_np_array(ref_emb),
                                )[0]
                                for x in self.dist_classes
                            ],
                        )
                    )

                    models = dict(
                        zip(
                            self.model_names,
                            [
                                all_models[jdx][idx]
                                for jdx in range(len(self.model_names))
                            ],
                        )
                    )
                    features = dict(
                        zip(
                            self.feature_names,
                            [
                                all_features[jdx][idx]
                                for jdx in range(len(self.feature_names))
                            ],
                        )
                    )

                    if len(self.log_writers) > 0:
                        for k, distance_type in enumerate(self.distance_types):
                            self.log_writers[k].log(
                                {
                                    "check": distances[distance_type],
                                    self.aggregate_measurable.feature_name: aggregate_ids[idx],  # type: ignore
                                    self.count_measurable.feature_name: last_crossed_checkpoint,  # type: ignore
                                    **models,
                                    **features,
                                }
                            )
                    else:
                        for distance_key in list(distances.keys()):
                            plot_name = distance_key + " " + str(self.reference)
                            this_data = list(
                                np.reshape(np.array(distances[distance_key]), -1)
                            )
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
