from __future__ import annotations
import typing as t

from pydantic import BaseModel
import pyarrow as pa
import deltalake as dl


# -----------------------------------------------------------
# Write to a Delta Table
# -----------------------------------------------------------


class DeltaWriter(BaseModel):
    fpath: str
    columns: t.Optional[t.List[str]] = None


class DeltaWriterExecutor:
    op: DeltaWriter
    columns: t.Optional[t.List[str]] = None

    def __init__(self, op: DeltaWriter):
        self.op = op
        self.columns = list(self.op.columns) if self.op.columns is not None else None

    def run(self, data: pa.Table):
        if self.columns is None:
            self.columns = list(data.column_names)
        assert set(self.columns) == set(data.column_names)
        dl.write_deltalake(self.op.fpath, data)
