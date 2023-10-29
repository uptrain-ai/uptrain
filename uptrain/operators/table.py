"""
Implement checks to return the input dataset as it is.

This module provides the `ColumnExpand` class, which returns the input DataFrame as it is without any modifications. It can be used to pass the data through unchanged in a pipeline.

"""

from __future__ import annotations
import typing as t

import numpy as np
from loguru import logger
from pydantic import Field
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *

@register_op
class Table(OpBaseModel):
    """
    Operator to generate a table.

    Attributes:
        props (dict): Additional properties to pass to the Table constructor.
        title (str): The title of the chart.

    """

    props: dict = Field(default_factory=dict)
    title: str = ""

    kind = "table"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        return {"output": None}


@register_op
class ColumnExpand(ColumnOp):
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


@register_op
class ColumnComparison(ColumnOp):
    """
    Column operation to add a new boolean column which represents if the given columns are row-wise same or not

    Attributes:
        col_in_1 (str): The name of the 1st input column to be compared row-wise.
        col_in_2 (str): The name of the 2nd input column to be compared row-wise.
        col_out (str): The name of the output boolean column 

    Returns:
        dict: A dictionary containing the input DataFrame.

    Example:
        ```
        from uptrain.operators import ColumnComparison
        df = pl.DataFrame({
            "column1": [1, 2, 3],
            "column2": [1, 2, 1],
            "column3": [2, 2, 4]
        })

        # Create an instance of the ColumnComparison class
        compare_op = ColumnComparison(
                        col_in_1="column1",
                        col_in_2="column2",
                        col_out="is_equal"
                    )

        # Run the compare operation
        output_df = compare_op.run(df)["output"]

        # Print the output DataFrame
        print(output_df)
        ```

    Output:
        ```
        shape: (3, 2)
        ┌─────────┬─────────┐─────────┐─────────┐
        │ column1 ┆ column2 ┆ column3 ┆is_equal │
        │ ---     ┆ ---     ┆ ---     ┆ ---     │
        │ i64     ┆ i64     ┆ i64     ┆ bool    │
        ╞═════════╪═════════╪═════════╪═════════╡
        │ 1       ┆ 1       ┆ 2       ┆ True    │
        │ 2       ┆ 2       ┆ 2       ┆ True    │
        │ 3       ┆ 1       ┆ 4       ┆ False   │
        └─────────┴─────────┴─────────┴─────────┘
        ```

    """

    col_in_1: str
    col_in_2: str
    col_out: str

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        return {"output": data.with_columns(data.select(
            pl.col(self.col_in_1) ==
            pl.col(self.col_in_2)
        )['Output'].alias(self.col_out))}


@register_op
class ColumnReduce(ColumnOp):
    """
    Operator to drop a list of columns from the input dataframe.

    Attributes:
        col_drop_names (list[str]): The names of the columns to be dropped.

    Returns:
        dict: A dictionary containing the input DataFrame.

    Example:
        ```
        from uptrain.operators import ColumnReduce
        df = pl.DataFrame({
            "column1": [1, 2, 3],
            "column2": ["A", "B", "C"]
        })

        # Create an instance of the ColumnReduce class
        reduce_op = ColumnReduce(
                        col_drop_names=["column2"],
                    )

        # Run the reduce operation
        output_df = reduce_op.run(df)["output"]

        # Print the output DataFrame
        print(output_df)
        ```

    Output:
        ```
        shape: (3, 2)
        ┌─────────┐
        │ column1 ┆
        │ ---     ┆
        │ i64     ┆
        ╞═════════╡
        │ 1       ┆
        │ 2       ┆
        │ 3       ┆
        └─────────┘
        ```

    """

    col_drop_names: list[str]

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        out = data.drop(self.col_drop_names)
        return {"output": out}
