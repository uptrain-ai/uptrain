from __future__ import annotations
import typing as t

from pydantic import BaseModel
import polars as pl
import deltalake as dl

from uptrain.framework.config import *


# -----------------------------------------------------------
# Write to a Delta Table
# -----------------------------------------------------------


@register_op
class DeltaWriter(BaseModel):
    fpath: str
    columns: t.Optional[list[str]] = None

    def make_executor(self, settings: t.Optional[Settings] = None):
        return DeltaWriterExecutor(self)


class DeltaWriterExecutor:
    op: DeltaWriter
    columns: t.Optional[list[str]] = None

    def __init__(self, op: DeltaWriter):
        self.op = op
        self.columns = list(self.op.columns) if self.op.columns is not None else None

    def run(self, data: pl.DataFrame):
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)
        dl.write_deltalake(self.op.fpath, data.to_arrow())
