"""Operators for the uptrain.core module. 

- Arrow/Numpy conversion utils - since we leverage duckdb as a cache and ray for execution, intermediate 
outputs are stored as Arrow batches. 
"""

from __future__ import annotations
import typing as t
import typing_extensions as te

from pydantic import BaseModel
import polars as pl

__all__ = [
    "TYPE_OP_INPUT",
    "TYPE_OP_OUTPUT",
    "check_req_columns_present",
]

# -----------------------------------------------------------
# base classes for operators
# -----------------------------------------------------------

TYPE_OP_INPUT = t.Union[pl.DataFrame, pl.Series]


class TYPE_OP_OUTPUT(te.TypedDict):
    output: t.Union[None, pl.DataFrame, pl.Series]
    extra: te.NotRequired[dict]


@t.runtime_checkable
class Operator(t.Protocol):
    """Base class for all operators."""

    schema_data: "BaseModel"  # both input and output columns are specified here

    def make_executor(self) -> "OperatorExecutor":
        """Create a Ray actor for this operator."""
        raise NotImplementedError


@t.runtime_checkable
class OperatorExecutor(t.Protocol):
    """Base class for all operator executors."""

    op: Operator

    def _validate_data(self, data: pl.DataFrame) -> None:
        """Validate that the input data is compatible with this operator."""
        raise NotImplementedError

    def run(self, data: pl.DataFrame, **kwargs) -> TYPE_OP_OUTPUT:
        raise NotImplementedError


def check_req_columns_present(
    data: pl.DataFrame, schema: BaseModel, exclude: t.Optional[list[str]] = None
) -> None:
    for attr, col in schema.dict().items():
        if exclude is not None and attr in exclude:
            continue
        assert (
            col in data.columns
        ), f"Column: {col} for attribute: {attr} not found in input data."
