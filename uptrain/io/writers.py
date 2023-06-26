from __future__ import annotations
import typing as t
import os
import shutil

from pydantic import BaseModel
import polars as pl
import deltalake as dl
from pathlib import Path

from uptrain.operators.base import *

if t.TYPE_CHECKING:
    from uptrain.framework import Settings


# -----------------------------------------------------------
# Write to a Delta Table
# -----------------------------------------------------------


@register_op
class DeltaWriter(BaseModel):
    fpath: str
    columns: t.Optional[list[str]] = None

    def make_executor(self, settings: t.Optional[Settings] = None):
        return DeltaWriterExecutor(self)

    def to_reader(self):
        from uptrain.io.readers import DeltaReader

        return DeltaReader(fpath=self.fpath)


class DeltaWriterExecutor(OperatorExecutor):
    op: DeltaWriter
    columns: t.Optional[list[str]] = None

    def __init__(self, op: DeltaWriter):
        self.op = op
        self.columns = list(self.op.columns) if self.op.columns is not None else None

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)
        data.write_delta(self.op.fpath, mode="append")
        return {"output": None}


@register_op
class JsonWriter(BaseModel):
    fpath: str
    columns: t.Optional[list[str]] = None

    def make_executor(self, settings: t.Optional[Settings] = None):
        return JsonWriterExecutor(self)

    def to_reader(self):
        from uptrain.io.readers import JsonReader

        return JsonReader(fpath=self.fpath)


class JsonWriterExecutor(OperatorExecutor):
    op: JsonWriter
    columns: t.Optional[list[str]] = None

    def __init__(self, op: JsonWriter):
        self.op = op
        self.columns = list(self.op.columns) if self.op.columns is not None else None

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        if os.path.exists(self.op.fpath):
            raise Exception(
                f"{self.op.fpath} already exists! JsonWriter currently doesn't support appending new rows to an existing file"
            )
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)

        data.write_ndjson(file=self.op.fpath)
        return {"output": None}
