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
class DuckDBReader(TransformOp):
    """Read data from a Duckdb table.

    Attributes:
        fpath (str): Path to the Duckdb file.
        query (str): Query to run against the duckdb database.
        col_timestamp (str): Column name to use as the timestamp column. Only used in the context of monitoring.

    Example:
        ```python
        from uptrain.operators.io import DuckDBReader

        reader = DuckDBReader(
            fpath="data/duckdb.db",
            query="SELECT * FROM my_table",
            col_timestamp="timestamp",
        )
        output = reader.setup().run()["output"]
        ```
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
