import typing as t
from functools import partial

import polars as pl
from pydantic import BaseModel, BaseSettings, Field

from uptrain.operators.base import *
from uptrain.utilities import jsonload, jsondump, to_py_types

__all__ = [
    "register_op",
    "register_op_external",
    "Config",
    "Settings",
]

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


T = t.TypeVar("T")


def _register_operator(cls: T, namespace: t.Optional[str] = None) -> T:
    key = cls.__name__  # type: ignore
    if namespace is not None:
        key = f"{namespace}:{key}"
    OperatorRegistry.register_operator(key, cls)
    return cls


def register_op(cls: T) -> T:
    """Decorator to register an operator with Uptrain's registry. Meant for internal use only."""
    return _register_operator(cls, namespace="uptrain")


def register_op_external(namespace: str):
    """Decorator to register custom operators with Uptrain's registry."""
    return partial(_register_operator, namespace=namespace)


def _deserialize_operator(data: dict) -> Operator:
    """Deserialize an operator from a dict."""
    op_name = data["op_name"]
    op = OperatorRegistry.get_operator(op_name)
    params = data["params"]
    return op(**params)  # type: ignore


# -----------------------------------------------------------
# User facing framework objects
# -----------------------------------------------------------


class TypeComputeOp(t.TypedDict):
    output_cols: list[str]
    operator: Operator


class TypeComputeOpExec(t.TypedDict):
    output_cols: list[str]
    operator: OperatorExecutor


class Check:
    # specify the sequence of operators to run, and name(s) for the output columns from each
    compute: list[TypeComputeOp]
    # specify the source of the data, if absent, data must be passed at runtime manually
    source: t.Optional[Operator] = None
    # specify the sinks to write the data to
    sinks: list[Operator]
    # specify the alerts to generate
    alerts: list[Operator]

    def __init__(
        self,
        compute: list[TypeComputeOp],
        source: t.Optional[Operator] = None,
        sinks: t.Optional[list[Operator]] = None,
        alerts: t.Optional[list[Operator]] = None,
    ):
        self.compute = compute
        self.source = source
        self.sinks = sinks or []
        self.alerts = alerts or []

    def make_executor(self, settings: "Settings") -> "CheckExecutor":
        """Make an executor for this check."""
        return CheckExecutor(check=self, settings=settings)

    @classmethod
    def from_dict(cls, data: dict) -> "Check":
        """Deserialize a check from a dict."""
        compute = []
        for elem in data["compute"]:
            compute.append(
                {
                    "output_cols": elem["output_cols"],
                    "operator": _deserialize_operator(elem["operator"]),
                }
            )
        if data.get("source"):
            source = _deserialize_operator(data["source"])
        else:
            source = None
        sinks = [_deserialize_operator(sink) for sink in data.get("sinks", [])]
        alerts = [_deserialize_operator(alert) for alert in data.get("alerts", [])]

        return cls(compute=compute, source=source, sinks=sinks, alerts=alerts)

    def to_dict(self) -> dict:
        """Serialize this check to a dict."""
        return {
            "compute": [
                {
                    "output_cols": op["output_cols"],
                    "operator": to_py_types(op["operator"]),
                }
                for op in self.compute
            ],
            "source": to_py_types(self.source),
            "sinks": [to_py_types(sink) for sink in self.sinks],
            "alerts": [to_py_types(alert) for alert in self.alerts],
        }


class CheckExecutor:
    """Executor for a check."""

    check: Check
    exec_source: t.Optional[OperatorExecutor]
    exec_compute: list[TypeComputeOpExec]
    exec_sinks: list[OperatorExecutor]
    exec_alerts: list[OperatorExecutor]

    def __init__(self, check: Check, settings: "Settings"):
        self.check = check
        self.exec_source = (
            check.source.make_executor(settings) if check.source else None
        )
        self.exec_sinks = [sink.make_executor(settings) for sink in check.sinks]
        self.exec_alerts = [alert.make_executor(settings) for alert in check.alerts]
        self.exec_compute = [
            {
                "output_cols": op["output_cols"],
                "operator": op["operator"].make_executor(settings),
            }
            for op in check.compute
        ]

    def run(self, data: t.Optional[pl.DataFrame] = None) -> t.Optional[pl.DataFrame]:
        """Run this check on the given data."""
        # run the source else use the provided data
        if data is None:
            assert (
                self.exec_source is not None
            ), "No source provided for this check, so data must be provided manually."
            data = self.exec_source.run()  # type: ignore
        assert data is not None

        # run the compute operations in sequence, passing the output of one to the next
        for compute_op in self.exec_compute:
            op = compute_op["operator"]
            col_names = compute_op["output_cols"]

            res = op.run(data)
            assert isinstance(res["output"], pl.DataFrame)
            rename_mapping = {
                get_output_col_name_at(i): name for i, name in enumerate(col_names)
            }
            data = res["output"].rename(rename_mapping)

        # run the sinks
        for sink in self.exec_sinks:
            sink.run(data)

        # run the alerts
        for alert in self.exec_alerts:
            alert.run(data)

        return data


class Settings(BaseSettings):
    # uptrain stores logs in this folder
    logs_folder: str = "/tmp/uptrain_logs"

    # external api auth
    openai_api_key: str = Field("", env="OPENAI_API_KEY")

    def check_and_get(self, key: str) -> str:
        """Check if a value is present in the settings and return it."""
        value = getattr(self, key)
        if value is None:
            raise ValueError(f"Expected value for {key} to be present in the settings.")
        return value


class Config:
    checks: list[Check]
    settings: Settings

    def __init__(self, checks: list[t.Any], settings: Settings):
        self.checks = checks
        self.settings = settings

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        check_objects = []
        for check in data.get("checks", []):
            check_objects.append(Check.from_dict(check))

        settings = Settings(**data["settings"])
        return cls(checks=check_objects, settings=settings)

    def to_dict(self) -> dict:
        return {
            "checks": [check.to_dict() for check in self.checks],
            "settings": self.settings.dict(),
        }

    @classmethod
    def deserialize(cls, fpath: str) -> "Config":
        return cls.from_dict(jsonload(fpath))

    def serialize(self, fpath: str) -> None:
        jsondump(self.to_dict(), fpath)
