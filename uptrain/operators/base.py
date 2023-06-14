"""Operators for the uptrain.core module. 

- Arrow/Numpy conversion utils - since we leverage duckdb as a cache and ray for execution, intermediate 
outputs are stored as Arrow batches. 
"""

from __future__ import annotations
import importlib
import inspect
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
    "deserialize_operator",
    "get_output_col_name_at",
]

# -----------------------------------------------------------
# Base classes for operators
# -----------------------------------------------------------


class TYPE_OP_OUTPUT(te.TypedDict):
    output: t.Optional[pl.DataFrame]
    extra: te.NotRequired[dict]


class Operator(t.Protocol):
    """All operator implementations must implement this protocol.

    An operator is defined as a pydantic model with the parameters necessary to run it. For ex,
    - params necessary to run an algorithm
    - input columns required by the operator
    - output columns produced by the operator
    """

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
    """Protocol to be implemented by all operator executors."""

    op: Operator

    def run(self, data: t.Optional[pl.DataFrame] = None, **kwargs) -> TYPE_OP_OUTPUT:
        """Runs the operator on the given data. An oeprator can receive multiple inputs but
        all of them must be a polars DataFrame.
        """
        ...


T = t.TypeVar("T")


def register_op(cls: T) -> T:
    """Decorator that marks the class as an Uptrain operator. Useful for (de)serialization."""
    assert isinstance(cls, type), "Only classes can be registered as Uptrain operators"
    op_name = f"{cls.__module__}:{cls.__name__}"
    cls._uptrain_op_name = op_name  # type: ignore
    return cls


def deserialize_operator(data: dict) -> Operator:
    """Deserialize an operator from the serialized dict."""
    op_name = data["op_name"]
    mod_name, cls_name = op_name.split(":")
    try:
        mod = importlib.import_module(mod_name)
        op = getattr(mod, cls_name)
    except (ModuleNotFoundError, AttributeError) as exc:
        logger.error(
            f"Error when trying to fetch the operator: \n{exc}\n Creating a placeholder op for {op_name}."
        )
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
