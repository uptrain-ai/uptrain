"""
Implement some metrics common to a lot of checks. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import BaseModel
import numpy as np
import polars as pl

from .base import TYPE_OP_OUTPUT
from uptrain.framework.config import Settings


class SchemaAccuracy(BaseModel):
    col_prediction: str = "prediction"
    col_ground_truth: str = "ground_truth"


class Accuracy(BaseModel):
    kind: t.Literal["NOT_EQUAL", "ABS_ERROR"]
    schema_data: SchemaAccuracy = SchemaAccuracy()

    def make_executor(self, settings: t.Optional[Settings] = None):
        return AccuracyExecutor(self)


class AccuracyExecutor:
    op: Accuracy

    def __init__(self, op: Accuracy):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        preds = data.get_column(self.op.schema_data.col_prediction)
        gts = data.get_column(self.op.schema_data.col_ground_truth)

        if self.op.kind == "NOT_EQUAL":
            acc = np.not_equal(preds, gts)
        else:
            acc = np.abs(preds - gts)
        return {"output": pl.Series(values=acc)}
