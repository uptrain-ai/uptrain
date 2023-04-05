import copy
import os
import uuid

import duckdb
import numpy as np

from uptrain.core.classes.helpers.arrow_utils import (
    upsert_ids_n_values,
    fetch_values_for_ids,
)

from uptrain.core.lib.helper_funcs import extract_data_points_from_batch
from uptrain.core.classes.statistics import AbstractStatistic
from uptrain.core.classes.distances import DistanceResolver
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.constants import Statistic


class Distance(AbstractStatistic):
    dashboard_name = "distance"
    statistic_type = Statistic.DISTANCE

    def base_init(self, fw, check):
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
            fw
        )
        self.count_measurable = MeasurableResolver(check["count_args"]).resolve(fw)
        self.item_counts = {}
        self.feats_dictn = {}
        self.reference = check["reference"]
        self.distance_types = check["distance_types"]
        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

        # setup a duckdb database to cache interim state for aggregates
        db_dir = os.path.join(fw.fold_name, "dbs", "distance")
        os.makedirs(db_dir, exist_ok=True)
        self.conn = duckdb.connect(os.path.join(db_dir, str(uuid.uuid4()) + ".db"))
        self.conn.execute("CREATE TABLE ref_embs (id LONG PRIMARY KEY, value FLOAT[])")

    def base_check(self, inputs, outputs=None, gts=None, extra_args={}):
        vals_all = self.measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        aggregate_ids_all = self.aggregate_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        counts = self.count_measurable.compute_and_log(
            inputs, outputs, gts=gts, extra=extra_args
        )
        all_models = [
            x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
            for x in self.model_measurables
        ]
        all_features = [
            x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
            for x in self.feature_measurables
        ]

        # collect all valid indices first. TODO: what does "valid" mean in this context?
        idxs = []
        for idx in range(len(aggregate_ids_all)):
            is_model_invalid = sum(
                [
                    all_models[jdx][idx] not in self.allowed_model_values[jdx]
                    for jdx in range(len(self.allowed_model_values))
                ]
            )
            if not is_model_invalid:
                idxs.append(idx)

        aggregate_ids = aggregate_ids_all[idxs]
        vals = vals_all[idxs, :]
        ref_embs_cache = fetch_values_for_ids(
            self.conn, "ref_embs", np.asarray(aggregate_ids)
        )

        # Get the reference embedding for each row in this batch.
        # - for initial diff, you want the first value seen from this id - either cached or from this batch
        # - for running diff, you want the previous value seen from this id - either cached or from this batch
        ref_embs_prev, list_ref_vals = {}, []
        for i, key in enumerate(aggregate_ids):
            value_from_cache = ref_embs_cache.get(key, vals[i])
            value_prev_seen_this_batch = ref_embs_prev.get(key, vals[i])
            if self.reference == "running_diff":
                list_ref_vals.append(value_prev_seen_this_batch)
                ref_embs_prev[key] = vals[i]
            else:
                list_ref_vals.append(value_from_cache)
                ref_embs_prev[key] = value_from_cache
        ref_vals = np.vstack(list_ref_vals)

        if len(vals) > 0:
            if len(ref_vals.shape) == 1:
                ref_vals = np.expand_dims(ref_vals, 0)
            distances = dict(
                zip(
                    self.distance_types,
                    [x.compute_distance(vals, ref_vals) for x in self.dist_classes],
                )
            )

            for idx in range(len(aggregate_ids)):
                models = dict(
                    zip(
                        ["model_" + x for x in self.model_names],
                        [all_models[jdx][idx] for jdx in range(len(self.model_names))],
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
            upsert_ids_n_values(
                self.conn,
                "ref_embs",
                np.asarray(list(ref_embs_prev.keys())),
                np.asarray(list(ref_embs_prev.values())),
            )
