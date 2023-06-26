"""
Implement checks to return the input dataset as it is. 
"""

from __future__ import annotations
import typing as t

import numpy as np
from loguru import logger
from pydantic import BaseModel
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class Identity(BaseModel):
    def make_executor(self, settings: t.Optional[Settings] = None):
        return IdentityExecutor(self, settings)


class IdentityExecutor(OperatorExecutor):
    op: Identity

    def __init__(self, op: Identity, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        return {"output": data}


@register_op
class ColumnExpand(BaseModel):
    col_out_names: list[str]
    col_vals: list

    def make_executor(self, settings: t.Optional[Settings] = None):
        return ColumnExpandExecutor(self, settings)


class ColumnExpandExecutor(OperatorExecutor):
    op: ColumnExpand

    def __init__(self, op: ColumnExpand, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        arr = []
        for idx in range(len(self.op.col_out_names)):
            arr.append(
                pl.Series(
                    self.op.col_out_names[idx], [self.op.col_vals[idx]] * len(data)
                )
            )
        return {"output": data.with_columns(arr)}


@register_op
class Concatenation(BaseModel):
    readers: list

    def make_executor(self, settings: t.Optional[Settings] = None):
        return ConcatenationExecutor(self, settings)


class ConcatenationExecutor(OperatorExecutor):
    op: Concatenation

    def __init__(self, op: Concatenation, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        arr = []
        for reader in self.op.readers:
            arr.append(reader.make_executor().run()["output"])
        return {"output": pl.concat(arr)}
