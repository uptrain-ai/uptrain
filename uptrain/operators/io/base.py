"""Basic IO operators for reading and writing data from Uptrain."""

from __future__ import annotations
import typing as t

import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

# -----------------------------------------------------------
# Read from text file formats - csv, json
# -----------------------------------------------------------


@register_op
class CsvReader(TransformOp):
    """Reads data from a csv file.

    Attributes:
        fpath (str): Path to the csv file.
        batch_size (Optional[int]): Number of rows to read at a time. Defaults to None, which reads the entire file.

    """

    fpath: str
    batch_size: t.Optional[int] = None

    def setup(self, settings: Settings):
        self._executor = TextReaderExecutor(self)
        return self

    def run(self) -> TYPE_TABLE_OUTPUT:
        return {"output": self._executor.run()}


@register_op
class JsonReader(TransformOp):
    """Reads data from a json file.

    Attributes:
        fpath (str): Path to the json file.
        batch_size (Optional[int]): Number of rows to read at a time. Defaults to None, which reads the entire file.

    """

    fpath: str
    batch_size: t.Optional[int] = None

    def setup(self, settings: Settings):
        self._executor = TextReaderExecutor(self)
        return self

    def run(self) -> TYPE_TABLE_OUTPUT:
        return {"output": self._executor.run()}


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

    @property
    def is_incremental(self) -> bool:
        return self.op.batch_size is not None

    def run(self) -> pl.DataFrame | None:
        if not self.is_incremental:
            data = self.dataset
        else:
            if self.rows_read >= len(self.dataset):
                data = None
            else:
                assert self.op.batch_size is not None
                self.rows_read += self.op.batch_size
                data = self.dataset.slice(self.rows_read, self.op.batch_size)
        return data


# -----------------------------------------------------------
# Read from a Delta Table, which uses parquet files under the hood
# -----------------------------------------------------------


@register_op
class DeltaReader(TransformOp):
    """Reads data from a Delta Lake table.

    Attributes:
        fpath (str): File path to the Delta Lake table.
        batch_split (bool): Whether to read the table in batches. Defaults to False.

    """

    fpath: str
    batch_split: bool = False
    _dataset: t.Any  # pyarrow dataset
    _batch_generator: t.Optional[t.Iterator[t.Any]]  # record batch generator

    def setup(self, settings: Settings):

        lazy_load_dep("pyarrow", "pyarrow>=10.0.0")
        dl = lazy_load_dep("deltatable", "deltalake>=0.9")

        self._dataset = dl.DeltaTable(self.fpath).to_pyarrow_dataset()
        if self.is_incremental:
            self._batch_generator = iter(self._dataset.to_batches())
        return self

    @property
    def is_incremental(self) -> bool:
        return self.batch_split is True

    def run(self) -> TYPE_TABLE_OUTPUT:
        if not self.is_incremental:
            data = pl.from_arrow(self._dataset.to_table())
        else:
            try:
                data = pl.from_arrow(next(self._batch_generator))  # type: ignore
            except StopIteration:
                data = None

        if data is not None:
            assert isinstance(data, pl.DataFrame)
        return {"output": data}


# -----------------------------------------------------------
# Writer objects
# -----------------------------------------------------------


@register_op
class DeltaWriter(OpBaseModel):
    fpath: str
    columns: t.Optional[list[str]] = None

    def setup(self, settings: Settings):
        dl = lazy_load_dep("deltatable", "deltalake>=0.9")

        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)
        data.write_delta(self.fpath, mode="append")
        return {"output": data}

    def to_reader(self):
        return DeltaReader(fpath=self.fpath)  # type: ignore


@register_op
class JsonWriter(OpBaseModel):
    fpath: str
    columns: t.Optional[list[str]] = None

    def setup(self, settings: Settings):
        return self

    def to_reader(self):
        return JsonReader(fpath=self.fpath)  # type: ignore

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        if self.columns is None:
            self.columns = list(data.columns)
        assert set(self.columns) == set(data.columns)
        with open(self.fpath, "a") as f:
            f.write(data.write_ndjson())
        return {"output": data}
