from __future__ import annotations
import typing as t

from pydantic import BaseModel
import polars as pl
import deltalake as dl

from uptrain.operators.base import *

if t.TYPE_CHECKING:
    from uptrain.framework.config import *

# -----------------------------------------------------------
# Read from text file formats - csv and json
# -----------------------------------------------------------


@register_op
class CsvReader(BaseModel):
    fpath: str
    batch_size: t.Optional[int] = None

    def make_executor(self, settings: t.Optional[Settings] = None):
        return TextReaderExecutor(self)


@register_op
class JsonReader(BaseModel):
    fpath: str
    batch_size: t.Optional[int] = None

    def make_executor(self, settings: t.Optional[Settings] = None):
        return TextReaderExecutor(self)


class TextReaderExecutor(OperatorExecutor):
    op: t.Union[CsvReader, JsonReader]
    dataset: pl.DataFrame
    rows_read: int

    def __init__(self, op: t.Union[CsvReader, JsonReader]):
        self.op = op
        self.rows_read = 0
        if isinstance(self.op, CsvReader):
            self.dataset = pl.read_csv(self.op.fpath)
        elif isinstance(self.op, JsonReader):
            self.dataset = pl.read_ndjson(self.op.fpath)

    def is_incremental(self) -> bool:
        return self.op.batch_size is not None

    def run(self) -> TYPE_OP_OUTPUT:
        if self.op.batch_size is None:
            data = self.dataset
        elif self.rows_read >= len(self.dataset):
            data = None
        else:
            self.rows_read += self.op.batch_size
            data = self.dataset.slice(self.rows_read, self.op.batch_size)
        return {"output": data}


# -----------------------------------------------------------
# Read from a Delta Table, which uses parquet files under the hood
# -----------------------------------------------------------


@register_op
class DeltaReader(BaseModel):
    fpath: str
    batch_split: bool = False  # whether we want to read one record batch at a time

    def make_executor(self, settings: t.Optional[Settings] = None):
        return DeltaReaderExecutor(self)


class DeltaReaderExecutor(OperatorExecutor):
    op: DeltaReader
    _dataset: t.Any  # pyarrow dataset
    _batch_generator: t.Optional[t.Iterator[t.Any]]  # record batch generator

    def __init__(self, op: DeltaReader):
        self.op = op
        self._dataset = dl.DeltaTable(self.op.fpath).to_pyarrow_dataset()
        if self.is_incremental():
            self._batch_generator = iter(self._dataset.to_batches())

    def is_incremental(self) -> bool:
        return self.op.batch_split is True

    def run(self) -> TYPE_OP_OUTPUT:
        if not self.is_incremental():
            data = pl.from_arrow(self._dataset.to_table())
        else:
            try:
                data = pl.from_arrow(next(self._batch_generator))  # type: ignore
            except StopIteration:
                data = None

        if data is not None:
            assert isinstance(data, pl.DataFrame)
        return {"output": data}
