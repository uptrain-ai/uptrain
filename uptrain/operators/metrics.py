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
    from uptrain.framework.config import *
from uptrain.operators.base import *


class SchemaAccuracy(BaseModel):
    in_col_prediction: str = "prediction"
    in_col_ground_truth: str = "ground_truth"
    out_col: str = get_output_col_name_at(0)


@register_op
class Accuracy(BaseModel):
    kind: t.Literal["NOT_EQUAL", "ABS_ERROR"]
    dataschema: SchemaAccuracy = SchemaAccuracy()

    def make_executor(self, settings: t.Optional[Settings] = None):
        return AccuracyExecutor(self)


class AccuracyExecutor(OperatorExecutor):
    op: Accuracy

    def __init__(self, op: Accuracy):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        preds = data.get_column(self.op.dataschema.in_col_prediction)
        gts = data.get_column(self.op.dataschema.in_col_ground_truth)

        if self.op.kind == "NOT_EQUAL":
            acc = np.not_equal(preds, gts)
        else:
            acc = np.abs(preds - gts)

        return {
            "output": data.with_columns([pl.Series(self.op.dataschema.out_col, acc)])
        }
