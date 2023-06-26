"""
Implement some metrics common to a lot of checks. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import BaseModel
import numpy as np
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class Accuracy(BaseModel):
    kind: t.Literal["NOT_EQUAL", "ABS_ERROR"]
    col_in_prediction: str = "prediction"
    col_in_ground_truth: str = "ground_truth"
    col_out: str = get_output_col_name_at(0)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return AccuracyExecutor(self)


class AccuracyExecutor(OperatorExecutor):
    op: Accuracy

    def __init__(self, op: Accuracy):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        preds = data.get_column(self.op.col_in_prediction)
        gts = data.get_column(self.op.col_in_ground_truth)

        if self.op.kind == "NOT_EQUAL":
            acc = np.not_equal(preds, gts)
        else:
            acc = np.abs(preds - gts)

        return {"output": data.with_columns([pl.Series(self.op.col_out, acc)])}
