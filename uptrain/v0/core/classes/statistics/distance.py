from __future__ import annotations
from typing import TYPE_CHECKING, Union
import numpy as np

from uptrain.v0.core.classes.statistics import AbstractStatistic
from uptrain.v0.core.classes.distances import DistanceResolver
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.constants import Statistic
from uptrain.v0.core.lib.cache import make_cache_container


if TYPE_CHECKING:
    from uptrain.v0.core.classes.logging.new_log_handler import (
        LogHandler as NewLogHandler,
        LogWriter,
    )
    from uptrain.v0.core.classes.logging.log_handler import LogHandler


class Distance(AbstractStatistic):
    log_handler: Union["LogHandler", "NewLogHandler"]
    log_writers: list["LogWriter"]
    dashboard_name = "distance"
    statistic_type = Statistic.DISTANCE

    def base_init(self, fw, check):
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
            fw
        )
        self.count_measurable = MeasurableResolver(check["count_args"]).resolve(fw)
        self.reference = check["reference"]
        self.distance_types: list = check["distance_types"]
        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

        # setup a cache to store interim state for aggregates
        attrs_to_store = {"ref_embedding": np.ndarray}
        self.cache = make_cache_container(fw, attrs_to_store)

        # get handles to log writers for each distance type
        if hasattr(self.log_handler, "make_logger"):
            self.log_writers = [
                self.log_handler.make_logger(
                    self.dashboard_name, distance_type + "_" + str(self.reference)
                )
                for distance_type in self.distance_types
            ]
        else:
            self.log_writers = []

    def base_check(self, inputs, outputs=None, gts=None, extra_args={}):
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
        [ref_embs_cache] = self.cache.fetch_col_values_for_ids(
            np.asarray(aggregate_ids), ["ref_embedding"]
        )  # NOTE: this gives us a unique value for each id, as observed from previous batches

        # Get the reference embedding for each row in this batch.
        # - for initial diff, you want the first value seen for this id - either cached or from this batch
        # - for running diff, you want the previous value seen for this id - either cached or from this batch
        ref_embs_prev, list_ref_vals = {}, []
        for i, key in enumerate(aggregate_ids):
            value_from_cache = ref_embs_cache.get(key, vals[i])
            value_prev_seen_this_batch = ref_embs_prev.get(key, vals[i])
            if self.reference == "running":
                list_ref_vals.append(value_prev_seen_this_batch)
                ref_embs_prev[key] = vals[i]
            else:
                list_ref_vals.append(value_from_cache)
                ref_embs_prev[key] = value_from_cache

        ref_vals = np.vstack(list_ref_vals)
        if len(ref_vals.shape) == 1:
            ref_vals = np.expand_dims(ref_vals, 0)
        distances = dict(
            zip(
                self.distance_types,
                [x.compute_distance(vals, ref_vals) for x in self.dist_classes],
            )
        )

        for idx in range(len(aggregate_ids)):
            idx_in_original_batch = select_idxs[idx]
            models = dict(
                zip(
                    self.model_names,
                    [
                        all_models[jdx][idx_in_original_batch]
                        for jdx in range(len(self.model_names))
                    ],
                )
            )
            features = dict(
                zip(
                    self.feature_names,
                    [
                        all_features[jdx][idx_in_original_batch]
                        for jdx in range(len(self.feature_names))
                    ],
                )
            )

            if len(self.log_writers) > 0:
                for k, distance_type in enumerate(self.distance_types):
                    self.log_writers[k].log(
                        {
                            "check": distances[distance_type][idx],
                            self.aggregate_measurable.feature_name: aggregate_ids[idx],  # type: ignore
                            self.count_measurable.feature_name: counts[idx],  # type: ignore
                            **models,
                            **features,
                        }
                    )
            else:
                for distance_type in self.distance_types:
                    plot_name = distance_type + "_" + str(self.reference)
                    self.log_handler.add_scalars(
                        self.dashboard_name + "_" + plot_name,
                        {"y_" + distance_type: distances[distance_type][idx]},
                        counts[idx],
                        self.dashboard_name,
                        features=features,
                        models=models,
                        file_name=str(aggregate_ids[idx]),
                    )

        # save the reference embeddings for use in the next batch
        self.cache.upsert_ids_n_col_values(
            np.asarray(list(ref_embs_prev.keys())),
            {"ref_embedding": np.asarray(list(ref_embs_prev.values()))},
        )
