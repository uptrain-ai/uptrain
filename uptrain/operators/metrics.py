"""
Implement some metrics common to a lot of checks. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import BaseModel, root_validator
import numpy as np
import pyarrow as pa

from .base import TYPE_OP_OUTPUT
from uptrain.utilities import table_arrow_to_np_arrays, np_arrays_to_arrow_table


class SchemaAccuracy(BaseModel):
    col_prediction: str = "prediction"
    col_ground_truth: str = "ground_truth"
    col_result: str = "metric"


class Accuracy(BaseModel):
    kind: t.Literal["EQUAL", "ABS_ERROR"]
    schema_data: SchemaAccuracy = SchemaAccuracy()

    def make_executor(self):
        return AccuracyExecutor(self)


class AccuracyExecutor:
    op: Accuracy

    def __init__(self, op: Accuracy):
        self.op = op

    def run(self, batch: pa.Table) -> TYPE_OP_OUTPUT:
        [preds, gts] = table_arrow_to_np_arrays(
            batch,
            [self.op.schema_data.col_prediction, self.op.schema_data.col_ground_truth],
        )
        if self.op.kind == "EQUAL":
            acc = np.equal(preds, gts)
        else:
            acc = np.abs(preds - gts)
        return {
            "output": np_arrays_to_arrow_table([acc], [self.op.schema_data.col_result])
        }
