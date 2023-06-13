from __future__ import annotations
import typing as t
import os
import shutil

from pydantic import BaseModel
import polars as pl
import deltalake as dl
from pathlib import Path

from uptrain.operators.base import *
from uptrain.io.readers import *

if t.TYPE_CHECKING:
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

    def to_reader(self):
        return DeltaReader(fpath=self.fpath)

class DeltaWriterExecutor(OperatorExecutor):
    op: DeltaWriter
    columns: t.Optional[list[str]] = None

    def __init__(self, op: DeltaWriter):
        self.op = op
        self.columns = list(self.op.columns) if self.op.columns is not None else None

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        if os.path.exists(self.op.fpath):
            shutil.rmtree(self.op.fpath)
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
        return JsonReader(fpath=self.fpath)

class JsonWriterExecutor(OperatorExecutor):
    op: JsonWriter
    columns: t.Optional[list[str]] = None

    def __init__(self, op: JsonWriter):
        self.op = op
        self.columns = list(self.op.columns) if self.op.columns is not None else None

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        if os.path.exists(self.op.fpath):
            os.remove(self.op.fpath)
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)

        # TODO: There should be a better way to create folders than below
        Path(self.op.fpath.split(".")[0]).mkdir(parents=True, exist_ok=True)
        data.write_ndjson(file=self.op.fpath)
        return {"output": None}
