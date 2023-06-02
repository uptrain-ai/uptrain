"""Operators for the uptrain.core module. 

- Arrow/Numpy conversion utils - since we leverage duckdb as a cache and ray for execution, intermediate 
outputs are stored as Arrow batches. 
"""

from __future__ import annotations
from functools import partial
import typing as t
import typing_extensions as te

from loguru import logger
from pydantic import BaseModel
import polars as pl


if t.TYPE_CHECKING:
    from uptrain.framework.config import Settings


__all__ = [
    "TYPE_OP_OUTPUT",
    "Operator",
    "OperatorExecutor",
    "PlaceholderOp",
    "register_op",
    "register_op_external",
    "deserialize_operator",
    "get_output_col_name_at",
    "check_req_columns_present",
    "add_output_cols_to_data",
]

# -----------------------------------------------------------
# Base classes for operators
# -----------------------------------------------------------


class TYPE_OP_OUTPUT(te.TypedDict):
    output: t.Optional[pl.DataFrame]
    extra: te.NotRequired[dict]


class Operator(t.Protocol):
    """Base class for all operators."""

    # optional attribute (not allowe in python protocols)
    # specifies all the input columns required by the operator
    # schema_data: t.Optional["BaseModel"]

    def make_executor(
        self, settings: t.Optional["Settings"] = None
    ) -> "OperatorExecutor":
        """Create an executor for this operator, which acutally takes the input data and
        runs the operator.
        """
        ...

    def dict(self) -> dict:
        """Serialize this operator to a dict."""
        ...


class OperatorExecutor(t.Protocol):
    """Base protocol class for all operator executors."""

    op: Operator

    def run(self, data: t.Optional[pl.DataFrame] = None) -> TYPE_OP_OUTPUT:
        ...


# -----------------------------------------------------------
# Create a registry for operators defined through the Uptrain
# library. This lets us load the corresponding operator from
# the serialized config.
# -----------------------------------------------------------


class OperatorRegistry:
    _registry: dict[str, t.Type[Operator]] = {}

    @classmethod
    def register_operator(cls, name: str, operator_klass: t.Any):
        cls._registry[name] = operator_klass
        # mark the class as an operator, helpful for (de)serialization later
        operator_klass._uptrain_op_name = name

    @classmethod
    def get_operator(cls, name: str):
        operator_klass = cls._registry.get(name)
        if operator_klass is None:
            raise ValueError(f"No operator registered with name {name}")
        return operator_klass

    @classmethod
    def has_operator(cls, name: str):
        return name in cls._registry


T = t.TypeVar("T")


def _register_operator(cls: T, namespace: str) -> T:
    assert isinstance(cls, type), "Can only register classes as Uptrain operators"
    key = f"{namespace}:{cls.__name__}"
    OperatorRegistry.register_operator(key, cls)
    return cls


def register_op(cls: T) -> T:
    """Decorator to register an operator with Uptrain's registry. Meant for internal use only."""
    return _register_operator(cls, namespace="uptrain")


def register_op_external(namespace: str):
    """Decorator to register custom operators with Uptrain's registry."""
    return partial(_register_operator, namespace=namespace)


def deserialize_operator(data: dict) -> Operator:
    """Deserialize an operator from a dict."""
    op_name = data["op_name"]
    if OperatorRegistry.has_operator(op_name):
        op = OperatorRegistry.get_operator(op_name)
    else:
        return PlaceholderOp(op_name=op_name, params=data["params"])

    if hasattr(op, "from_dict"):
        # likely a check object
        return op.from_dict(data)  # type: ignore
    else:
        # likely a pydantic model
        params = data["params"]
        return op(**params)  # type: ignore


# -----------------------------------------------------------
# Utility routines for operators
# -----------------------------------------------------------


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


@register_op
class PlaceholderOp(BaseModel):
    """A placeholder operator that does nothing. Used when deserializing an operator,
    that hasn't been registered."""

    op_name: str
    params: dict[str, t.Any]

    def make_executor(
        self, settings: t.Optional["Settings"] = None
    ) -> "PlaceholderOpExecutor":
        """Make an executor for this operator."""
        return PlaceholderOpExecutor(self)


class PlaceholderOpExecutor(OperatorExecutor):
    op: PlaceholderOp

    def __init__(self, op: PlaceholderOp) -> None:
        self.op = op

    def run(self, data: t.Optional[pl.DataFrame] = None) -> t.Optional[pl.DataFrame]:
        raise NotImplementedError(
            "This is only a placeholder since the operator: {self.op_name} is not registered with Uptrain. Import the module where it is defined and try again."
        )
