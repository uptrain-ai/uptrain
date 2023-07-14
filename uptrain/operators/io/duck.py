"""IO operators to read/write from/to Duckdb."""

from __future__ import annotations
import typing as t

import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep


duckdb = lazy_load_dep("duckdb", "duckdb")


@register_op
class DuckdbReader(TransformOp):
    """Read data from a Duckdb table.

    NOTE: To use this operator, you must include the GCP service account credentials in the settings.

    Attributes:
        fpath (str): Path to the Duckdb file.
        query (str): Query to run against the duckdb database.
        col_timestamp (str): Column name to use as the timestamp column. Only used in the context of monitoring.
    """

    fpath: str
    query: str
    col_timestamp: str = "timestamp"

    def setup(self, settings: Settings):
        self._conn = duckdb.connect(self.fpath)
        return self

    def run(self) -> TYPE_TABLE_OUTPUT:
        res = self._conn.query(self.query).to_arrow_table()
        return {"output": pl.from_arrow(res)}
