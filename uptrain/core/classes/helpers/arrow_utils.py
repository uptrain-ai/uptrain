"""Utility routines to help us use Duckdb, as storage for intermediate state when 
computing aggregations. 
"""

from __future__ import annotations
from typing import Any, Union

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


def upsert_ids_n_values(conn: Any, tbl_name: str, ids: np.ndarray, values: np.ndarray):
    tbl = pa.Table.from_pydict(
        {
            "id": array_np_to_arrow(ids),
            "value": array_np_to_arrow(values),
        }
    )
    # upserts don't work for List data types, so we do it in steps
    # conn.execute("INSERT OR REPLACE INTO intermediates SELECT id, value FROM tbl")
    conn.execute(f"DELETE FROM {tbl_name} WHERE id IN (SELECT id FROM tbl)")
    conn.execute(f"INSERT INTO {tbl_name} SELECT id, value FROM tbl")


def fetch_values_for_ids(conn: Any, tbl_name: str, id_list: np.ndarray) -> dict:
    id_tbl = pa.Table.from_pydict({"id": array_np_to_arrow(id_list)})
    conn.execute(
        f"SELECT id, value FROM {tbl_name} where id IN (SELECT id FROM id_tbl)"
    )
    value_tbl = conn.fetch_arrow_table()
    _ids, _values = table_arrow_to_np_arrays(value_tbl, ["id", "value"])
    return {_id: value for _id, value in zip(_ids, _values)}
