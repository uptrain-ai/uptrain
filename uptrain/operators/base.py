"""Operators for the uptrain.core module. 

- Arrow/Numpy conversion utils - since we leverage duckdb as a cache and ray for execution, intermediate 
outputs are stored as Arrow batches. 
"""

from __future__ import annotations
import typing as t
import typing_extensions as te

from pydantic import BaseModel
import pyarrow as pa

# -----------------------------------------------------------
# base classes for operators
# -----------------------------------------------------------


class TYPE_OP_OUTPUT(te.TypedDict):
    output: pa.Table
    state: te.NotRequired[te.Any]
    aux_output: te.NotRequired[dict]


@t.runtime_checkable
class Operator(t.Protocol):
    """Base class for all operators."""

    data_schema: "BaseModel"

    def make_executor(self) -> "OperatorExecutor":
        """Create a Ray actor for this operator."""
        raise NotImplementedError


@t.runtime_checkable
class OperatorExecutor(t.Protocol):
    """Base class for all operator executors."""

    op: Operator

    def _validate_data(self, data: pa.Table) -> None:
        """Validate that the input data is compatible with this operator."""
        raise NotImplementedError

    def run(self, data: pa.Table, **kwargs) -> TYPE_OP_OUTPUT:
        raise NotImplementedError


def check_req_columns_present(data: pa.Table, schema: BaseModel) -> None:
    for attr, col in schema.dict().items():
        assert (
            col in data.column_names
        ), f"Column: {col} for attribute: {attr} not found in input data."
