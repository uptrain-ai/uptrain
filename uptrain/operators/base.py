"""Operators for the uptrain.core module. 

- Arrow/Numpy conversion utils - since we leverage duckdb as a cache and ray for execution, intermediate 
outputs are stored as Arrow batches. 
"""

from __future__ import annotations
import importlib
import typing as t
import typing_extensions as te

from loguru import logger
from pydantic import BaseModel
import polars as pl


if t.TYPE_CHECKING:
    from uptrain.framework import Settings


__all__ = [
    "TYPE_TABLE_OP_OUTPUT",
    "TYPE_SCALAR_OP_OUTPUT",
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


class TYPE_TABLE_OP_OUTPUT(te.TypedDict):
    output: pl.DataFrame | None
    extra: te.NotRequired[dict]


class TYPE_SCALAR_OP_OUTPUT(te.TypedDict):
    output: pl.Series | None
    extra: te.NotRequired[dict]


class Operator(t.Protocol):
    """All operator implementations must implement this protocol.

    An operator is usually defined as a pydantic model with the parameters necessary to
    run it. For ex,
    - params necessary to run an algorithm
    - columns required in the input dataset
    - columns that will be generated as output, etc.

    For attributes that are specific to each execution (settings, current state), declare
    them as private attributes, so pydantic doesn't try to serialize them.
    """

    kind: t.ClassVar[t.Literal["select", "aggregate", "table"]]

    def dict(self) -> dict:
        """Serialize this operator to a json dictionary. The objective is to be able to
        recreate the operator from this dict.

        NOTE: If your operator is a pydantic model, pydantic handles this. Though for fields
        with custom non-python types, you need to override and implement this yourself.
        """
        ...

    def setup(self, settings: "Settings" | None = None) -> None:
        """Setup the operator. This must be called before the operator is run."""
        ...


class SelectOp(Operator, t.Protocol):
    kind = "select"

    def run(self, data: pl.DataFrame) -> TYPE_SCALAR_OP_OUTPUT:
        """Runs the operator on the given data.

        Args:
            A Select operator takes a single dataframe as input, and compute a function over
            one/multiple columns of it.

        Returns:
            A dictionary with the `output` key as a polars Series. Any extra information can
            be put in the `extra` key.
        """
        ...


class AggregateOp(Operator, t.Protocol):
    kind = "aggregate"

    def run(self, data: list[pl.DataFrame]) -> TYPE_SCALAR_OP_OUTPUT:
        """Runs the operator on the given data.

        Args:
            An Aggregation operator takes a list of dataframes as input, one for each group,
            aggregates over each to compute a single value, and returns a series of the same
            length as the input.

        Returns:
            A dictionary with the `output` key as a polars Series. Any extra information can
            be put in the `extra` key.
        """
        ...


class TableOp(Operator, t.Protocol):
    kind = "table"

    def run(self, *args: pl.DataFrame | None) -> TYPE_TABLE_OP_OUTPUT:
        """Runs the operator on the given data.

        Args:
            A Table operator takes one/multiple dataframes as input.

        Returns:
            A dictionary with the `output` key as a single dataframe. Any extra information
            can be put in the `extra` key.
        """
        ...


T = t.TypeVar("T")


def register_op(cls: T) -> T:
    """Decorator that marks the class as an Uptrain operator. Useful for (de)serialization."""
    assert isinstance(cls, type), "Only classes can be registered as Uptrain operators"
    assert hasattr(cls, "kind"), "An Operator class must define the `kind` attribute"
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

    params = data["params"]
    if hasattr(op, "from_dict"):
        # not a pydantic model, so a class implemented by uptrain
        return op.from_dict(params)  # type: ignore
    else:
        # likely a pydantic model
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
