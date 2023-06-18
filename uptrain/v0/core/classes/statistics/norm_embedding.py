from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

from uptrain.v0.core.classes.statistics import AbstractStatistic
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.constants import Statistic

if TYPE_CHECKING:
    from uptrain.v0.core.classes.logging.new_log_handler import (
        LogHandler as NewLogHandler,
        LogWriter,
    )
    from uptrain.v0.core.classes.logging.log_handler import LogHandler


class NormEmbedding(AbstractStatistic):
    """Class that computes the norm of an embedding column."""

    log_handler: "NewLogHandler"
    log_writer: "LogWriter"
    dashboard_name = "norm_embedding"
    statistic_type = Statistic.NORM_EMBEDDING

    def base_init(self, fw, check):
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
            fw
        )
        self.count_measurable = MeasurableResolver(check["count_args"]).resolve(fw)

        # get handles to log writers for each distance type
        if hasattr(self.log_handler, "make_logger"):
            self.log_writer = self.log_handler.make_logger(self.dashboard_name, "check")
        else:
            raise Exception(
                f"Check type: {self.statistic_type} not supported by this log handler"
            )

    def base_check(self, inputs=None, outputs=None, gts=None, extra_args={}):
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

        if len(vals_all) == 0:
            return  # nothing for us to do here

        emb_values = np.vstack(vals_all)
        norm_values = np.linalg.norm(emb_values, axis=1)

        for idx in range(len(aggregate_ids_all)):
            models = dict(
                zip(
                    self.model_names,
                    [all_models[jdx][idx] for jdx in range(len(self.model_names))],
                )
            )
            features = dict(
                zip(
                    self.feature_names,
                    [all_features[jdx][idx] for jdx in range(len(self.feature_names))],
                )
            )
            self.log_writer.log(
                {
                    "check": norm_values[idx],
                    self.aggregate_measurable.feature_name: aggregate_ids_all[idx],  # type: ignore
                    self.count_measurable.feature_name: counts_all[idx],  # type: ignore
                    **models,
                    **features,
                }
            )
