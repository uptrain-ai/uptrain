"""
Operators for the uptrain.core module. 
"""

from __future__ import annotations
import importlib
import typing as t
import typing_extensions as te

from loguru import logger
from pydantic import BaseModel, Field, root_validator
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.utilities import to_py_types


__all__ = [
    "TYPE_TABLE_OUTPUT",
    "Operator",
    "OpBaseModel",
    "ColumnOp",
    "TransformOp",
    "PlaceholderOp",
    "register_op",
    "deserialize_operator",
    "get_output_col_name_at",
]

# -----------------------------------------------------------
# Base classes for operators
# -----------------------------------------------------------


class TYPE_TABLE_OUTPUT(te.TypedDict):
    output: pl.DataFrame | None
    extra: te.NotRequired[dict]


class Operator(t.Protocol):
    """
    All operator implementations must implement this protocol.

    An operator is usually defined as a pydantic model with the parameters
    necessary to run it. For ex,
    - params necessary to run an algorithm
    - columns required in the input dataset
    - columns that will be generated as output, etc.


    `Setup`: The `setup` method is called before the operator is run. This is where you
    can do any setup work, like loading models, settin up file addresses, etc.

    `Run`: The `run` method is called to run the operator. It takes 0 or more polars
    dataframes as input, and returns a dictionary with the `output` key set to the
    computed dataframe/None. Any extra information can be put in the `extra` key.
    """

    def dict(self) -> dict:
        """
        Serialize this operator to a json dictionary. The objective is to be able to
        recreate the operator from this dict.

        NOTE: If your operator is a pydantic model, pydantic handles this. Though if you
        have fields with custom non-python types, you MUST override and implement both a
        `dict` and a`from_dict` method.
        """
        ...

    def setup(self, settings: "Settings") -> "Operator":
        """Setup the operator. This must be called before the operator is run."""
        ...

    run: t.Callable[..., TYPE_TABLE_OUTPUT]  # runs the operator


class OpBaseModel(BaseModel):
    """
    Base class you can use if constructing an operator using a pydantic
    model, to get around some of the sharp edges.

    Attributes:
        _state (dict): A dict you can use to store state values between multiple
            calls to the `run` method.

    """

    _state: dict = Field(default_factory=dict)

    class Config:
        extra = "allow"
        smart_union = True
        underscore_attrs_are_private = True


class ColumnOp(OpBaseModel):
    """Represents operations that append columns to the input dataset, and
    return it as is.
    """

    def setup(self, settings: "Settings"):
        raise NotImplementedError

    def run(self, *args: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        """
        Runs the operator on the input dataset, and returns it with new columns added.

        Args:
            data (pl.DataFrame): Zero or one dataframe as input.

        Returns:
            A dictionary with the `output` key set to the computed Table. Any extra
                information can be put in the `extra` key.
        """
        raise NotImplementedError


class TransformOp(OpBaseModel):
    """Represents operations that transform the input dataset into another.
    For things like filtering, aggregation, etc.
    """

    def setup(self, settings: Settings):
        raise NotImplementedError

    def run(self, *args: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        """Runs the operator on the input dataset, and returns the transformed dataset.

        Attributes:
            *args (pl.DataFrame): Zero or more dataframes as inputs.

        Returns:
            A dictionary with the `output` key set to the computed dataframe/None. Any extra
                information can be put in the `extra` key.
        """
        raise NotImplementedError


T = t.TypeVar("T")


def register_op(cls: T) -> T:
    """Decorator that marks the class as an Uptrain operator. Useful for (de)serialization."""
    assert isinstance(cls, type), "Only classes can be registered as Uptrain operators"
    assert hasattr(cls, "setup") and hasattr(
        cls, "run"
    ), "All Uptrain operators must define a `setup` and a `run` method."
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
class PlaceholderOp(OpBaseModel):
    """A placeholder operator that does nothing. Used when deserializing an operator,
    that hasn't been registered."""

    op_name: str
    params: dict[str, t.Any]

    def setup(self, settings: "Settings"):
        raise NotImplementedError

    def run(self, *args: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        raise NotImplementedError(
            "This is only a placeholder since the operator: {self.op_name} is not registered with Uptrain. Import the module where it is defined and try again."
        )
