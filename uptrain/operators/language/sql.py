"""
Implement oeprators over text data.
"""

from __future__ import annotations
import re
import typing as t
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel, Field
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework.config import *
from uptrain.operators.base import *

__all__ = ["HasStar"]


# Check if SQL has star
class SchemaHasStar(BaseModel):
    col_sql: str


@register_op
class HasStar(BaseModel):
    schema_data: SchemaHasStar = Field(default_factory=SchemaHasStar)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return HasStarExecutor(self)


class HasStarExecutor(OperatorExecutor):
    op: HasStar

    def __init__(self, op: HasStar):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        sqls = data.get_column(self.op.schema_data.col_sql)
        results = ["*" in sql for sql in sqls]
        return {"output": add_output_cols_to_data(data, [pl.Series(values=results)])}