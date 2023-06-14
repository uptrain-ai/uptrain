"""This module implements visualization operators for simple-checks in uptrain."""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import BaseModel, Field
import polars as pl
import plotly.express as px

if t.TYPE_CHECKING:
    from uptrain.framework.config import *
from uptrain.operators.base import *


__all__ = ["PlotlyChart"]


@register_op
class PlotlyChart(BaseModel):
    kind: t.Literal["line", "scatter", "bar", "histogram", "table"]
    props: dict = Field(default_factory=dict)
    title: str = ""
    filter_on: list[str] = Field(default_factory=list)
    pivot_args: list[dict] = Field(default_factory=list)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return PlotlyExecutor(self)


class PlotlyExecutor(OperatorExecutor):
    op: PlotlyChart

    def __init__(self, op: PlotlyChart):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        if self.op.kind == "table":
            return {"output": None}
        else:
            chart = getattr(px, self.op.kind)(data.to_pandas(), **self.op.props)
            return {"output": None, "extra": {"chart": chart}}
