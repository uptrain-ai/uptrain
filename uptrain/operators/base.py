"""Operators for the uptrain.core module. 

- Arrow/Numpy conversion utils - since we leverage duckdb as a cache and ray for execution, intermediate 
outputs are stored as Arrow batches. 
"""

from __future__ import annotations
import typing as t
import typing_extensions as te

from loguru import logger
from pydantic import BaseModel
import polars as pl


if t.TYPE_CHECKING:
    from uptrain.framework.config import Settings


__all__ = [
    "TYPE_OP_INPUT",
    "TYPE_OP_OUTPUT",
    "Operator",
    "OperatorExecutor",
    "get_output_col_name_at",
    "check_req_columns_present",
    "add_output_cols_to_data",
]

# -----------------------------------------------------------
# base classes for operators
# -----------------------------------------------------------

TYPE_OP_INPUT = t.Optional[pl.DataFrame]


class TYPE_OP_OUTPUT(te.TypedDict):
    output: t.Optional[pl.DataFrame]
    extra: te.NotRequired[dict]


class Operator(t.Protocol):
    """Base class for all operators."""

    # all required input columns must be specified in this attribute
    @property
    def schema_data(self) -> t.Optional["BaseModel"]:
        ...

    def make_executor(
        self, settings: t.Optional["Settings"] = None
    ) -> "OperatorExecutor":
        """Create an executor for this operator."""
        ...

    def dict(self) -> dict:
        """Serialize this operator to a dict."""
        ...


class OperatorExecutor(t.Protocol):
    """Base protocol class for all operator executors."""

    op: Operator

    def run(self, data: TYPE_OP_INPUT = None) -> TYPE_OP_OUTPUT:
        ...


def get_output_col_name_at(index: int) -> str:
    return f"_col_{index}"


def add_output_cols_to_data(
    data: pl.DataFrame, list_columns: list[pl.Series]
) -> pl.DataFrame:
    to_add = {}
    for i, col in enumerate(list_columns):
        col_name = get_output_col_name_at(i)
        if col_name in data.columns:
            logger.warning(f"Overwriting column {col_name} in the input data.")
        to_add[col_name] = col
    return data.with_columns(**to_add)


def check_req_columns_present(
    data: pl.DataFrame, schema: BaseModel, exclude: t.Optional[list[str]] = None
) -> None:
    for attr, col in schema.dict().items():
        if exclude is not None and attr in exclude:
            continue
        assert (
            col in data.columns
        ), f"Column: {col} for attribute: {attr} not found in input data."
