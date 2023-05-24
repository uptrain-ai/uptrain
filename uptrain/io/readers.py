from __future__ import annotations
import typing as t

from pydantic import BaseModel
import pyarrow as pa
import pyarrow.dataset
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
    dataset: pa.Table
    rows_read: int

    def __init__(self, op: t.Union[CsvReader, JsonReader]):
        self.op = op
        self.rows_read = 0
        if isinstance(self.op, CsvReader):
            import pyarrow.csv

            self.dataset = pa.csv.read_csv(self.op.fpath)
        elif isinstance(self.op, JsonReader):
            import pyarrow.json

            self.dataset = pa.json.read_json(self.op.fpath)

    def run(self) -> t.Optional[pa.Table]:
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
    filter_query: t.Optional[str] = None

    def make_executor(self):
        return DeltaReaderExecutor(self)


class DeltaReaderExecutor:
    op: DeltaReader
    dataset: "pa._dataset.Dataset"
    _delta_table: "dl.DeltaTable"
    _batch_generator: t.Iterator[pa.Table]

    def __init__(self, op: DeltaReader):
        self.op = op
        self._delta_table = dl.DeltaTable(self.op.fpath)
        self.dataset = self._delta_table.to_pyarrow_dataset()
        self._batch_generator = iter(
            self.dataset.to_batches(filter=self.op.filter_query)
        )

    def run(self) -> t.Optional[pa.Table]:
        try:
            return next(self._batch_generator)
        except StopIteration:
            return None
