"""
Not used currently, refactored version of distribution.py
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Union
import numpy as np
import random

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


class Distribution(AbstractStatistic):
    log_handler: Union["LogHandler", "NewLogHandler"]
    log_writers: list["LogWriter"]  # one for each distance type
    dashboard_name = "distribution_stats"
    statistic_type = Statistic.DISTRIBUTION_STATS
    bucket_size = 400  # max num of embeddings sampled at each checkpoint
    refresh_rate = 0.1  # churn from the previous set at each checkpoint

    def base_init(self, fw, check):
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
            fw
        )
        self.count_measurable = MeasurableResolver(check["count_args"]).resolve(fw)
        self.distance_types = check["distance_types"]
        self.count_checkpoints = list(sorted(set([0] + check["count_checkpoints"])))

        # setup a dict to store the sampled embeddings at each checkpoint
        self.values_for_cp = {cp: [] for cp in self.count_checkpoints}

        # setup a cache to store interim state for aggregates
        attrs_to_store = {"prev_count": np.ndarray, "first_checkpoint": int}
        self.cache = make_cache_container(fw, attrs_to_store)

        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]
        if hasattr(self.log_handler, "make_logger"):
            self.log_writers = [
                self.log_handler.make_logger(self.dashboard_name, distance_type)
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

        # new embeddings seen for each checkpoint
        new_values_for_cp = {cp: [] for cp in self.count_checkpoints}

        # read previous state from the cache
        # - prev_count_cache: the previous view count seen for each aggregate id
        # - first_crossed_checkpoint_cache: the first checkpoint that was crossed for each aggregate id
        [
            prev_count_cache,
            first_crossed_checkpoint_cache,
        ] = self.cache.fetch_col_values_for_ids(
            np.asarray(aggregate_ids),
            ["prev_count", "first_checkpoint"],
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
                    # new checkpoint crosses, so add this embedding to the list for this checkpoint
                    new_values_for_cp[last_crossed_checkpoint].append(vals[idx])

        # update samples for each checkpoint and compute distributions
        for cp in self.count_checkpoints:
            num_new_samples = len(new_values_for_cp[cp])
            num_to_add = int(self.refresh_rate * self.bucket_size)
            if num_to_add > num_new_samples:
                # we have enough new samples to replace the old ones
                self.values_for_cp[cp] += new_values_for_cp[cp]
            else:
                # we have too many new samples, so randomly choose from them
                self.values_for_cp[cp] += random.sample(
                    new_values_for_cp[cp], num_to_add
                )
            self.values_for_cp[cp] = self.values_for_cp[cp][-self.bucket_size :]

            # samples N pairs from these embedding values and compute distance between them
            num_pairs_to_sample = 400
            total_num_samples = len(self.values_for_cp[cp])

            first_indices = np.random.choice(total_num_samples, num_pairs_to_sample)
            second_indices = np.random.choice(total_num_samples, num_pairs_to_sample)
            invalid_pairs = first_indices == second_indices
            second_indices[invalid_pairs] = (second_indices[invalid_pairs] + 1) % total_num_samples  # type: ignore

            first_vector = np.vstack(
                [self.values_for_cp[cp][idx] for idx in first_indices]
            )
            second_vector = np.vstack(
                [self.values_for_cp[cp][idx] for idx in second_indices]
            )
            for k, dist_class in enumerate(self.dist_classes):
                distances = dist_class.compute_distance(first_vector, second_vector)
                # TODO: are we creating separate histograms for each model, feature type pair?

        # update the cache with data from this batch
        if len(set_ids_to_cache) > 0:
            # save the current state in the cache
            list_ids = list(set_ids_to_cache)
            list_counts, list_first_checkpoints = [], []
            for _id in list_ids:
                list_counts.append(prev_count_cache[_id])
                list_first_checkpoints.append(first_crossed_checkpoint_cache[_id])

            self.cache.upsert_ids_n_col_values(
                np.asarray(list_ids),
                {
                    "prev_count": np.asarray(list_counts),
                    "first_checkpoint": np.asarray(list_first_checkpoints),
                },
            )
