"""A pytest module to test that the SQLite datastore works as expected.
"""

import os
import sqlite3
import tempfile

import pytest
import numpy as np

from uptrain.v0.core.lib.datastores import SqliteStore


@pytest.fixture
def sqlite_store():
    """Fixture to create a temporary SQLite datastore."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test")
        yield SqliteStore(path)


def test_table_created(sqlite_store: SqliteStore):
    """Test that the SQLite datastore works as expected."""
    datapoint = {"id": 1, "val": 2.0, "name": "test"}
    sqlite_store.log(datapoint)

    with sqlite3.connect(sqlite_store.path_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, val, name FROM logs")
        assert cursor.fetchone() == (1, 2.0, "test")

        res = cursor.execute("SELECT NAME FROM PRAGMA_TABLE_INFO('logs')")
        assert res.fetchall() == [("id",), ("val",), ("name",), ("internal_ts",)]


def test_batch_logging(sqlite_store: SqliteStore):
    """Test logging a batch of data at once works as expected."""
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    datapoints = {
        "id": np.arange(1000),  # int
        "feat_1": np.random.randn(1000),  # float
        "feat_2": ["".join(x) for x in np.random.choice(alphabet, (1000, 5))],  # str
        "feat_3": np.random.choice([True, False], 1000),  # bool
        "feat_4": np.arange(6000).reshape(1000, 6),  # np.ndarray
    }
    sqlite_store.log_many(datapoints)
    sqlite_store.log_many(datapoints)

    with sqlite3.connect(sqlite_store.path_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, feat_1, feat_2, feat_3, feat_4 FROM logs")
        res = cursor.fetchall()
        assert len(res) == 2000
