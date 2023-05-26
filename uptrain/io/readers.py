from __future__ import annotations
import typing as t

from pydantic import BaseModel
import polars as pl
import deltalake as dl

# -----------------------------------------------------------
# Read from text file formats - csv and json
# -----------------------------------------------------------


class CsvReader(BaseModel):
    fpath: str
    batch_size: t.Optional[int] = None

    def make_executor(self):
        return TextReaderExecutor(self)


class JsonReader(BaseModel):
    fpath: str
    batch_size: t.Optional[int] = None

    def make_executor(self):
        return TextReaderExecutor(self)


class TextReaderExecutor:
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

    def run(self) -> t.Optional[pl.DataFrame]:
        if self.op.batch_size is None:
            return self.dataset
        elif self.rows_read >= len(self.dataset):
            return None
        else:
            self.rows_read += self.op.batch_size
            return self.dataset.slice(self.rows_read, self.op.batch_size)


# -----------------------------------------------------------
# Read from a Delta Table, which uses parquet files under the hood
# -----------------------------------------------------------


class DeltaReader(BaseModel):
    fpath: str
    batch_split: bool = False  # whether we want to read one record batch at a time

    def make_executor(self):
        return DeltaReaderExecutor(self)


class DeltaReaderExecutor:
    op: DeltaReader
    _dataset: t.Any  # pyarrow dataset
    _batch_generator: t.Iterator[t.Any]  # pyarrow record batch

    def __init__(self, op: DeltaReader):
        self.op = op
        self._dataset = dl.DeltaTable(self.op.fpath).to_pyarrow_dataset()
        self._batch_generator = iter(self._dataset.to_batches())

    def run(self) -> t.Optional[pl.DataFrame]:
        try:
            return pl.from_arrow(next(self._batch_generator))  # type: ignore
        except StopIteration:
            return None
