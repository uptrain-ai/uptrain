"""Operators for the uptrain.core module. 

- Arrow/Numpy conversion utils - since we leverage duckdb as a cache and ray for execution, intermediate 
outputs are stored as Arrow batches. 
"""

from __future__ import annotations
import typing as t
import typing_extensions as te

if t.TYPE_CHECKING:
    from uptrain.framework.config import Settings

from pydantic import BaseModel
import polars as pl

__all__ = [
    "TYPE_OP_INPUT",
    "TYPE_OP_OUTPUT",
    "Operator",
    "check_req_columns_present",
]

# -----------------------------------------------------------
# base classes for operators
# -----------------------------------------------------------

TYPE_OP_INPUT = t.Union[pl.DataFrame, pl.Series]


class TYPE_OP_OUTPUT(te.TypedDict):
    output: t.Union[None, pl.DataFrame, pl.Series]
    extra: te.NotRequired[dict]


class Operator(t.Protocol):
    """Base class for all operators."""

    # both input and output columns are specified here
    schema_data: t.Optional["BaseModel"]

    def make_executor(
        self, settings: t.Optional["Settings"] = None
    ) -> "OperatorExecutor":
        """Create am executor for this operator."""
        raise NotImplementedError


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
