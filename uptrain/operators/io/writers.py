from __future__ import annotations
import typing as t
import os
import shutil

import polars as pl
import deltalake as dl
from pathlib import Path

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


# -----------------------------------------------------------
# Write to a Delta Table
# -----------------------------------------------------------


@register_op
class DeltaWriter(OpBaseModel):
    fpath: str
    columns: t.Optional[list[str]] = None

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)
        data.write_delta(self.fpath, mode="append")
        return {"output": None}

    def to_reader(self):
        from uptrain.operators.io.readers import DeltaReader

        return DeltaReader(fpath=self.fpath)  # type: ignore


@register_op
class JsonWriter(OpBaseModel):
    fpath: str
    columns: t.Optional[list[str]] = None

    def setup(self, settings: Settings):
        return self

    def to_reader(self):
        from uptrain.operators.io.readers import JsonReader

        return JsonReader(fpath=self.fpath)  # type: ignore

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)
        with open(self.fpath, "w") as f:
            f.write(data.write_ndjson())
        return {"output": None}
