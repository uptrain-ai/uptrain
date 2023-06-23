"""
Implement some metrics common to a lot of checks. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
import numpy as np
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class Accuracy(ColumnOp):
    kind: t.Literal["NOT_EQUAL", "ABS_ERROR"]
    col_in_prediction: str = "prediction"
    col_in_ground_truth: str = "ground_truth"

    def setup(self, _: t.Optional[Settings] = None):
        pass

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        preds = data.get_column(self.col_in_prediction)
        gts = data.get_column(self.col_in_ground_truth)

        if self.kind == "NOT_EQUAL":
            acc = np.not_equal(preds, gts)
        else:
            acc = np.abs(preds - gts)
        return {"output": pl.Series(get_output_col_name_at(0), acc)}
