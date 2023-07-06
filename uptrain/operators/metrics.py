"""
This module provides the Accuracy operator that computes the accuracy between predicted and ground truth values.

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
    """
    Operator for computing accuracy measures between predicted values and ground truth values.

    Attributes:
        kind (Literal["NOT_EQUAL", "ABS_ERROR"]): The type of accuracy measure.
        col_in_prediction (str): The name of the column containing the predicted values.
        col_in_ground_truth (str): The name of the column containing the ground truth values.
        col_out (str): The name of the output column containing the accuracy scores.

    Example:
        ```
        from uptrain.operators import Accuracy
        from uptrain.operators import CsvReader

        # Create an instance of the Accuracy operator
        op = Accuracy(
                kind="NOT_EQUAL",
                col_in_prediction="prediction",
                col_in_ground_truth="ground_truth"
            )

        # Set up the operator
        op.setup()

        # Run the operator on the input data
        input_data = pl.DataFrame(...)
        accuracy_scores = op.run(input_data)["output"]

        # Print the accuracy scores
        print(accuracy_scores)
        ```

    Output:
        ```
        shape: (3,)
        Series: '_col_0' [bool]
        [
                true
                false
                true
        ]
        ```

    """

    kind: t.Literal["NOT_EQUAL", "ABS_ERROR"]
    col_in_prediction: str = "prediction"
    col_in_ground_truth: str = "ground_truth"
    col_out: str = "accuracy"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        preds = np.array(data.get_column(self.col_in_prediction))
        gts = np.array(data.get_column(self.col_in_ground_truth))

        if self.kind == "NOT_EQUAL":
            acc = np.not_equal(preds, gts)
        else:
            acc = np.abs(preds - gts)
        return {"output": data.with_columns([pl.Series(self.col_out, acc)])}
