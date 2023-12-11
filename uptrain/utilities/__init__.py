from __future__ import annotations
from datetime import datetime, timedelta, tzinfo
import dataclasses
import importlib
import importlib.util
import json
import typing as t
import os
import time

from lazy_loader import load as _lazy_load
from loguru import logger
import pydantic
import numpy as np
# import numpy.typing as npt
# import pyarrow as pa
import polars as pl
import datetime 


# -----------------------------------------------------------
# utility routines for JSON serialization - parts picked off
# from the openai-evals codebase
# -----------------------------------------------------------


def to_py_types(obj: t.Any) -> t.Any:
    import inspect

    # for nested dataclasses/pydantic models/operators
    if isinstance(obj, datetime.datetime):
        return str(obj)
    if isinstance(obj, dict):
        return {k: to_py_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_py_types(v) for v in obj]
    elif dataclasses.is_dataclass(obj):
        return to_py_types(dataclasses.asdict(obj))
    elif hasattr(obj, "_uptrain_op_name"):
        if hasattr(obj, "_uptrain_op_custom"):
            if hasattr(obj, "_uptrain_op_custom_source"):
                source = obj._uptrain_op_custom_source
            else:
                source = inspect.getsource(obj.__class__)
            return {
                "op_name": getattr(obj, "_uptrain_op_name"),
                "params": obj.dict(include=set(obj.__fields__)),
                "source": source,
            }
        else:
            return {
                "op_name": getattr(obj, "_uptrain_op_name"),
                "params": obj.dict(include=set(obj.__fields__)),
            }
    elif isinstance(obj, pydantic.BaseModel):
        return obj.dict()

    # for numpy types
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()

    return obj


class UpTrainEncoder(json.JSONEncoder):
    """Special json encoder for numpy types"""

    def default(self, obj: t.Any) -> str:
        return to_py_types(obj)


def jsondumps(obj: t.Any, **kwargs) -> str:
    return json.dumps(obj, cls=UpTrainEncoder, **kwargs)


def jsondump(obj: t.Any, fp: t.Any, **kwargs) -> None:
    json.dump(obj, fp, cls=UpTrainEncoder, **kwargs)


def jsonloads(s: str, **kwargs) -> t.Any:
    return json.loads(s, **kwargs)


def jsonload(fp: t.Any, **kwargs) -> t.Any:
    return json.load(fp, **kwargs)


# -----------------------------------------------------------
# utility routines for converting between Arrow and Numpy
# -----------------------------------------------------------


# def array_np_to_arrow(arr: npt.NDArray) -> pa.Array:
#     assert arr.ndim in (1, 2), "Only 1D and 2D arrays are supported."
#     if arr.ndim == 1:
#         return pa.array(arr)
#     else:
#         dim1, dim2 = arr.shape
#         return pa.ListArray.from_arrays(
#             np.arange(0, (dim1 + 1) * dim2, dim2), arr.ravel()
#         )


# def array_arrow_to_np(arr: pa.Array) -> npt.NDArray:
#     if isinstance(arr, pa.ChunkedArray):
#         arr = arr.combine_chunks()

#     if not pa.types.is_list(arr.type):
#         return arr.to_numpy(zero_copy_only=False)  # assume a 1D array
#     else:
#         dim1 = len(arr)  # assume a 2D array
#         return np.asarray(arr.values.to_numpy(zero_copy_only=False)).reshape(dim1, -1)


# def arrow_batch_to_table(batch_or_tbl: t.Union[pa.Table, pa.RecordBatch]) -> pa.Table:
#     if not isinstance(batch_or_tbl, pa.Table):
#         return pa.Table.from_batches([batch_or_tbl])
#     else:
#         return batch_or_tbl


# def table_arrow_to_np_arrays(
#     tbl: pa.Table, cols: list[t.Union[str, int]]
# ) -> list[np.ndarray]:
#     return [array_arrow_to_np(tbl.column(c)) for c in cols]


# def np_arrays_to_arrow_table(arrays: list[npt.NDArray], cols: list[str]) -> pa.Table:
#     return pa.Table.from_pydict(
#         {c: array_np_to_arrow(arr) for c, arr in zip(cols, arrays)}
#     )


def polars_to_pandas(data: pl.DataFrame):
    """Convert a polars dataframe to a pandas dataframe"""
    # FIXME: obscure error during pandas conversion through pyarrow for string columns, though
    # they already are utf-8 encoded by arrow/polars?? I tried pandas 1.5.3 and pyarrow>12,
    # as rec-d on github.
    import pandas as pd

    try:
        pd_data = data.to_pandas()
    except:
        # convert to python native types first and then to pandas
        logger.warning(
            "Error converting polars to pandas. Trying to convert to python native types first."
        )

        lazy_load_dep("pyarrow", "pyarrow>=10.0.0")

        # We can't iterate over polars as such, since rust panics can't be caught in python
        # convert to pyarrow first
        all_rows = []
        arrow_data = data.to_arrow()
        for row in range(len(data)):
            try:
                row_dict = {}
                for col in data.columns:
                    row_dict[col] = arrow_data[col][row].as_py()
                all_rows.append(row_dict)
            except Exception as e:
                logger.warning(f"Error converting row {row}: {e}")

        pd_data = pd.DataFrame(all_rows)
    return pd_data


# -----------------------------------------------------------
# routines for working with local files and directories
# -----------------------------------------------------------


def clear_directory(dir_path: str):
    """Clears the directory at dir_path but without deleting the directory itself. `shutil.rmtree` will
    have difficulties with mounted volumes or network drives.
    """
    import shutil

    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


# -----------------------------------------------------------
# routines to deal with time
# -----------------------------------------------------------


class Clock:
    """Makes testing easier by anchoring to an older time. This is helpful when
    testing with older datasets. While if initialized with no arguments, the clock
    starts at the current time.
    """

    behind_by: timedelta
    tzone: t.Optional[tzinfo]

    def __init__(self, init_at: datetime):
        tz = init_at.tzinfo
        if tz is None or tz.utcoffset(init_at) is None:
            self.tzone = None
            self.behind_by = datetime.now() - init_at
        else:
            self.tzone = tz
            self.behind_by = datetime.now(tz=tz) - init_at

    def now(self) -> datetime:
        """Return the current time, adjusted by the amount of time the clock is behind."""
        return datetime.now(tz=self.tzone) - self.behind_by

    def sleep(self, seconds: float):
        """If the clock is behind, catch up. Else, sleep for the given duration."""
        seconds_behind = self.behind_by.total_seconds()
        if seconds_behind > 0:
            print(f"advancing the clock by {seconds} seconds")
        else:
            print(f"sleeping for {seconds} seconds")
            time.sleep(seconds)
        self.behind_by = timedelta(seconds=max(seconds_behind - seconds, 0))


class Timer:
    """Context manager for timing code blocks"""

    time: float

    def __enter__(self):
        self.time = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = round(time.perf_counter() - self.time, 3)


# -----------------------------------------------------------
# routines to deal with optional dependencies
# -----------------------------------------------------------


def lazy_load_dep(import_name: str, package_name: str):
    """Helper function to lazily load optional dependencies. If the dependency is not
    present, the function will raise an error _when used_.

    NOTE: This wrapper adds a warning message at import time.
    """
    try:
        spec = importlib.util.find_spec(import_name)
    except:
        spec = None
    if spec is None:
        logger.warning(
            f"Optional feature dependent on missing package: {import_name} was initialized.\n"
            f"Use `pip install {package_name}` to install the package if running locally."
        )

    return _lazy_load(import_name)
