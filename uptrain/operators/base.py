"""Operators for the uptrain.core module. 

- Arrow/Numpy conversion utils - since we leverage duckdb as a cache and ray for execution, intermediate 
outputs are stored as Arrow batches. 
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
    "TYPE_COLUMN_OUTPUT",
    "Operator",
    "OpBaseModel",
    "ColumnOp",
    "TableOp",
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


class TYPE_COLUMN_OUTPUT(te.TypedDict):
    output: pl.Series | None
    extra: te.NotRequired[dict]


class Operator(t.Protocol):
    """All operator implementations must implement this protocol.

    An operator is usually defined as a pydantic model with the parameters
    necessary to run it. For ex,
    - params necessary to run an algorithm
    - columns required in the input dataset
    - columns that will be generated as output, etc.

    NOTE: An operator must also define `setup` and `run` methods like shown below.
    I can't make mypy happy with it yet though, so we just check for it inside the
    `register_op` decorator.
    """

    def dict(self) -> dict:
        """Serialize this operator to a json dictionary. The objective is to be able to
        recreate the operator from this dict.

        NOTE: If your operator is a pydantic model, pydantic handles this. Though for fields
        with custom non-python types, you MUST override and implement both a `dict` and a
        `from_dict` method.
        """
        ...

    def setup(self, settings: "Settings" | None = None) -> "Operator":
        """Setup the operator. This must be called before the operator is run."""
        ...

    # def run(self, *args: pl.DataFrame | None) -> t.Any:
    #     """Runs the operator."""
    #     ...


class OpBaseModel(BaseModel):
    """Base class you can use if constructing an operator using a pydantic
    model, to get around some of the sharp edges.

    Attributes:
        _state (dict): A dict you can use to store state values between multiple
            calls to the `run` method.
    """

    _state: dict = Field(default_factory=dict)

    class Config:
        smart_union = True
        underscore_attrs_are_private = True


class ColumnOp(OpBaseModel):
    def setup(self, settings: "Settings" | None = None) -> None:
        raise NotImplementedError

    def run(self, data: pl.DataFrame | None = None) -> TYPE_COLUMN_OUTPUT:
        """Runs the operator on the given data.

        Args:
            data (pl.DataFrame): A polars dataframe. It computes a function over one/multiple
                columns of it.

        Returns:
            A dictionary with the `output` key set to the computed Series/None. Any extra
                information can be put in the `extra` key.
        """
        raise NotImplementedError


class TableOp(OpBaseModel):
    def setup(self, _: "Settings" | None = None) -> None:
        raise NotImplementedError

    def run(self, *args: pl.DataFrame | None) -> TYPE_TABLE_OUTPUT:
        """Runs the operator on the given data.

        Args:
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

    def setup(self, settings: "Settings" | None = None) -> None:
        raise NotImplementedError

    def run(self, *args: pl.DataFrame | None) -> None:
        raise NotImplementedError(
            "This is only a placeholder since the operator: {self.op_name} is not registered with Uptrain. Import the module where it is defined and try again."
        )


@register_op
class SelectOp(TableOp):
    """Use this to combine the output from multiple `ColumnOp` operators."""

    columns: dict[str, ColumnOp]

    @root_validator
    def check_columns(cls, values: dict) -> dict:
        columns = values["columns"]
        for col_name, col_op in columns.items():
            if not isinstance(col_op, ColumnOp):
                raise ValueError(
                    f"Expected a ColumnOp for column: {col_name}, but got: {col_op}"
                )
        return values

    def dict(self) -> dict:
        return {
            "columns": {
                col_name: to_py_types(col_op)
                for col_name, col_op in self.columns.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SelectOp":
        columns = data["columns"]
        for col_name, col_op in columns.items():
            columns[col_name] = deserialize_operator(col_op)
        return cls(columns=columns)

    def setup(self, settings: Settings | None) -> None:
        for _, col_op in self.columns.items():
            col_op.setup(settings)
        return self

    def run(self, data: pl.DataFrame | None) -> TYPE_TABLE_OUTPUT:
        new_cols = []
        for col_name, col_op in self.columns.items():
            out_op = col_op.run(data)["output"]
            if out_op is not None:
                new_cols.append(out_op.alias(col_name))

        if data is None:
            return {"output": pl.DataFrame(data=[new_cols])}
        else:
            return {"output": data.with_columns(new_cols)}


# -----------------------------------------------------------
# TODO: Aggregate Ops. Not sure if needed.
# -----------------------------------------------------------

# class AggregateOp(OpBaseModel):
#     def setup(self, _: "Settings" | None = None) -> None:
#         raise NotImplementedError

#     def run(self, data: list[pl.DataFrame]) -> TYPE_COLUMN_OUTPUT:
#         """Runs the aggregation op on the given list of sub-dataframe.

#         Args:
#             data (pl.DataFrame): A polars dataframe, one for each group key values. It
#                 aggregates over each group to compute a single value, and returns a series of
#                 the same length as the input.

#         Returns:
#             A dictionary with the `output` key set to the computed Series/None. Any extra
#                 information can be put in the `extra` key.
#         """
#         raise NotImplementedError

# class GroupbyOp(TableOp):
#     """Groups the input dataframe by a set of columns, and computes aggregate operators
#     over the grouped data.
#     """

#     cols_groupby: list[str]
#     cols_agg: dict[str, AggregateOp]

#     def setup(self, settings: Settings | None) -> None:
#         for _, agg_op in self.cols_agg.items():
#             agg_op.setup(settings)

#     def run(self, data: pl.DataFrame | None) -> TYPE_TABLE_OUTPUT:
#         if data is None:
#             return {"output": None}

#         list_groups = list(data.groupby(self.cols_groupby))
#         new_cols = []
#         for col_name, agg_op in self.cols_agg.items():
#             out_op = agg_op.run(list_groups)["output"]
#             if out_op is not None:
#                 new_cols.append(out_op.alias(col_name))
