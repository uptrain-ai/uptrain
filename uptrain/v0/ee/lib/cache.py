"""Utility routines to help us use Duckdb, as storage for intermediate state when 
computing aggregations. 
"""

from __future__ import annotations
import os
from typing import Any, Type, Union
import uuid

import duckdb
import numpy as np
import pyarrow as pa

# -----------------------------------------------------------
# utility routines for converting between Arrow and Numpy
# -----------------------------------------------------------


def array_np_to_arrow(arr: np.ndarray) -> pa.Array:
    assert arr.ndim in (1, 2), "Only 1D and 2D arrays are supported."
    if arr.ndim == 1:
        return pa.array(arr)
    else:
        dim1, dim2 = arr.shape
        return pa.ListArray.from_arrays(
            np.arange(0, (dim1 + 1) * dim2, dim2), arr.ravel()
        )


def array_arrow_to_np(arr: pa.Array) -> np.ndarray:
    if isinstance(arr, pa.ChunkedArray):
        arr = arr.combine_chunks()

    if not pa.types.is_list(arr.type):
        return arr.to_numpy()  # assume a 1D array
    else:
        dim1 = len(arr)  # assume a 2D array
        return np.asarray(arr.values.to_numpy()).reshape(dim1, -1)


def arrow_batch_to_table(batch_or_tbl: Union[pa.Table, pa.RecordBatch]) -> pa.Table:
    if not isinstance(batch_or_tbl, pa.Table):
        return pa.Table.from_batches([batch_or_tbl])
    else:
        return batch_or_tbl


def table_arrow_to_np_arrays(tbl: pa.Table, cols: list[str]) -> list[np.ndarray]:
    return [array_arrow_to_np(tbl[c]) for c in cols]


def np_arrays_to_arrow_table(arrays: list[np.ndarray], cols: list[str]) -> pa.Table:
    return pa.Table.from_pydict(
        {c: array_np_to_arrow(arr) for c, arr in zip(cols, arrays)}
    )


# -----------------------------------------------------------
# State cache
# -----------------------------------------------------------


class DuckDBStateCache:
    """A state cache that uses DuckDB to store intermediate state."""

    def __init__(self, fw: Any, columns: dict[str, Type]):
        db_dir = os.path.join(fw.fold_name, "dbs")
        os.makedirs(db_dir, exist_ok=True)
        self.conn = duckdb.connect(os.path.join(db_dir, str(uuid.uuid4()) + ".db"))

        # create the table
        cols = {"id": "LONG PRIMARY KEY"}
        for col, col_type in columns.items():
            if col_type == np.ndarray:
                cols[col] = "FLOAT[]"
            elif col_type == float:
                cols[col] = "FLOAT"
            elif col_type == int:
                cols[col] = "LONG"
            elif col_type == str:
                cols[col] = "VARCHAR"
            else:
                raise ValueError(f"Unsupported type {col_type}")
        str_cols = ",".join([f"{col} {col_type}" for col, col_type in cols.items()])
        self.conn.execute(f"CREATE TABLE store ({str_cols})")

    def upsert_ids_n_col_values(
        self, ids: np.ndarray, col_values: dict[str, np.ndarray]
    ):
        tbl = pa.Table.from_pydict(
            {
                "id": array_np_to_arrow(ids),
                **{
                    col: array_np_to_arrow(values) for col, values in col_values.items()
                },
            }
        )
        # upserts don't work for List data types, so we do it in steps
        # conn.execute("INSERT OR REPLACE INTO store SELECT id, value FROM tbl")
        self.conn.execute(f"DELETE FROM store WHERE id IN (SELECT id FROM tbl)")
        str_col_names = ",".join(col_values.keys())
        self.conn.execute(f"INSERT INTO store SELECT id, {str_col_names} FROM tbl")

    def fetch_col_values_for_ids(
        self, ids: np.ndarray, col_names: list[str]
    ) -> list[dict]:
        id_tbl = pa.Table.from_pydict({"id": array_np_to_arrow(ids)})
        str_col_names = ",".join(col_names)
        self.conn.execute(
            f"SELECT id, {str_col_names} FROM store WHERE id IN (SELECT id FROM id_tbl)"
        )

        value_tbl = self.conn.fetch_arrow_table()
        if len(value_tbl) == 0:
            return [{} for _ in col_names]
        else:
            output = []
            _ids = array_arrow_to_np(value_tbl["id"])
            for col in col_names:
                _values = array_arrow_to_np(value_tbl[col])
                output.append({_id: value for _id, value in zip(_ids, _values)})
            return output
