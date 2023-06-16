"""
This module Implements storage backends for logs collected by the Uptrain package. 
For now, they all live on the local filesystem. 

- sqlite
- duckdb? (TODO)
"""

import sqlite3
from typing import Any, Sequence, Dict, List, Union, Callable

import numpy as np
import pandas as pd


def make_encoder(x: Any) -> Callable:
    """Create an encoder to encode all values with the same type as the one passed."""
    if isinstance(x, (int, float, str)):
        return lambda x: x
    elif isinstance(x, (np.integer, np.floating, np.bool_)):
        return lambda x: x.item()
    elif isinstance(x, np.ndarray):
        return lambda x: str(x.tolist())
    else:
        return lambda x: str(x)


def make_sqlite_type(x: Any) -> str:
    """Produce the sqlite type to map to for the given value."""
    if isinstance(x, (int, bool, np.integer, np.bool_)):
        return "INTEGER"
    elif isinstance(x, (float, np.floating)):
        return "REAL"
    elif isinstance(x, str):
        return "TEXT"
    else:
        return "BLOB"


class SqliteStore:
    """A sqlite based storage backend for model usage logs."""

    path_db: str
    conn: sqlite3.Connection
    _schema: Union[Dict[str, str], None]
    _encoders: List[Callable]

    def __init__(self, path: str):
        """Initializes a sqlite database at the given path. Removes the existing file if present.

        Args:
            path: path to the sqlite database file.
        """
        self.path_db = path if path == ":memory:" else f"{path}.db"
        self.conn = sqlite3.connect(self.path_db, isolation_level=None)
        with self.conn:
            self.conn.execute("PRAGMA journal_mode=WAL")

        self._schema = None
        self._encoders = []

    def __del__(self):
        self.conn.close()

    def _init_table(self, datapoint: Dict[str, Any]):
        """Infer the schema for the logs table from the first datapoint."""
        self._schema = dict()
        assert (
            "id" in datapoint
        ), "A column named `id` must be present in the logged data."
        for col, val in datapoint.items():
            self._schema[col] = make_sqlite_type(val)
            self._encoders.append(make_encoder(val))

        schema_str = ", ".join(f"{k} {v}" for k, v in self._schema.items())
        with self.conn:
            self.conn.execute(
                f"CREATE TABLE logs ({schema_str}, internal_ts INTEGER DEFAULT (strftime('%s','now')))"
            )

    def log(self, datapoint: Dict[str, Any]):
        """Logs a single datapoint."""
        if self._schema is None:
            self._init_table(datapoint)

        with self.conn:
            self.conn.execute(
                f"INSERT INTO logs ({','.join(datapoint.keys())}) VALUES ({','.join('?' * len(datapoint))})",
                list(self._encoders[i](x) for i, x in enumerate(datapoint.values())),
            )

    def log_many(self, datapoints: Dict[str, Sequence[Any]]):
        """Logs multiple datapoints."""
        if self._schema is None:
            self._init_table({k: v[0] for k, v in datapoints.items()})

        with self.conn:
            self.conn.executemany(
                f"INSERT INTO logs ({','.join(datapoints.keys())}) VALUES ({','.join('?' * len(datapoints))})",
                (
                    [self._encoders[i](x) for i, x in enumerate(ntuple)]
                    for ntuple in zip(*datapoints.values())
                ),
            )

    def fetch_all(self) -> "pd.DataFrame":
        return pd.read_sql_query("SELECT * FROM logs", self.conn)
