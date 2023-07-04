"""
Implement checks to return the input dataset as it is.

This module provides the `ColumnExpand` class, which returns the input DataFrame as it is without any modifications. It can be used to pass the data through unchanged in a pipeline.

"""

from __future__ import annotations
import typing as t

import numpy as np
from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class ColumnExpand(TransformOp):
    """
    Table operation to return the input DataFrame as it is without any modifications.

    Attributes:
        col_out_names (list[str]): The names of the output columns. Must be the same length as `col_vals`.
        col_vals (list[Any]): The values for the output columns. Must be the same length as `col_out_names`.

    Returns:
        dict: A dictionary containing the input DataFrame.

    Example:
        ```
        from uptrain.operators import ColumnExpand
        df = pl.DataFrame({
            "column1": [1, 2, 3],
            "column2": ["A", "B", "C"]
        })

        # Create an instance of the ColumnExpand class
        expand_op = ColumnExpand(
                        col_out_names=["column1", "column2"],
                        col_vals=[df["column1"], df["column2"]]
                    )

        # Run the expand operation
        output_df = expand_op.run(df)["output"]

        # Print the output DataFrame
        print(output_df)
        ```

    Output:
        ```
        shape: (3, 2)
        ┌─────────┬─────────┐
        │ column1 ┆ column2 │
        │ ---     ┆ ---     │
        │ i64     ┆ str     │
        ╞═════════╪═════════╡
        │ 1       ┆ A       │
        │ 2       ┆ B       │
        │ 3       ┆ C       │
        └─────────┴─────────┘
        ```

    """

    col_out_names: list[str]
    col_vals: list[t.Any]

    def setup(self, settings: Settings):
        assert len(self.col_out_names) == len(self.col_vals)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        out = data.with_columns(
            [
                pl.lit(self.col_vals[idx]).alias(self.col_out_names[idx])
                for idx in range(len(self.col_out_names))
            ]
        )
        return {"output": out}
