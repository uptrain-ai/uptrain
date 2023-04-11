import numpy as np

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.distances import DistanceResolver
from uptrain.core.classes.statistics import AbstractStatistic
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Statistic
from uptrain.core.lib.cache import make_cache_container


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

        # setup a cache to store interim state for aggregates
        attrs_to_store = {"prev_count": np.ndarray}
        self.cache = make_cache_container(fw, attrs_to_store)

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
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
        vals = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        aggregate_ids = self.aggregate_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        counts = self.count_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )

        # TODO: what is this for?
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
        [prev_count_cache] = self.cache.fetch_col_values_for_ids(
            np.asarray(aggregate_ids),
            ["prev_count"],
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
            # 1. prev_count > max(checkpoints): we skip processing this row altogether
            # 2. prev_count = None: first time we see this aggregate id, so we skip processing it. Save the current state in the cache.
            # 3. curr_count < prev_count: this row is out of order, so we skip processing it. Save the previous state in the cache.
            # 4. max(checkpoints) >= curr_count > prev_count: we have seen this aggregate id before, so we process it. Save the current state in the cache.
            if prev_count is None:
                set_ids_to_cache.add(active_id)
                prev_count_cache[active_id] = curr_count
            elif prev_count > self.count_checkpoints[-1]:
                continue
            elif curr_count < prev_count:
                set_ids_to_cache.add(active_id)
                # prev count doesn't need to be updated
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
                    pass  # TODO: update the histogram

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
