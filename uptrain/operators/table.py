"""
Implement checks to return the input dataset as it is. 
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
class ColumnExpand(TableOp):
    col_out_names: list[str]
    col_vals: list[t.Any]

    def setup(self, _: t.Optional[Settings] = None):
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
