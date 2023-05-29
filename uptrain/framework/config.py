import typing as t
from functools import partial

from pydantic import BaseSettings, Field

from uptrain.operators.base import Operator
from uptrain.utilities import jsonload, jsondump

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
        operator_klass._is_operator = True  # helps with deserialization

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


class Settings(BaseSettings):
    # uptrain stores logs in this folder
    logs_folder: str = "/tmp/uptrain_logs"

    # external api auth
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    def check_and_get(self, key: str) -> str:
        """Check if a value is present in the settings and return it."""
        value = getattr(self, key)
        if value is None:
            raise ValueError(f"Expected value for {key} to be present in the settings.")
        return value


class Config:
    checks: list[list[t.Union[Operator, tuple[Operator]]]]
    settings: Settings

    def __init__(self, checks: list[t.Any], settings: Settings):
        self.checks = checks
        self.settings = settings

    @classmethod
    def _deserialize_check(cls, step: dict) -> Operator:
        operator_klass = OperatorRegistry.get_operator(step["operator"])
        return operator_klass(**step["params"])  # type: ignore

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        checks = []
        for check in data.get("checks", []):
            steps = []
            num_steps = len(check)
            for i, step in check:
                if i == num_steps - 1:
                    if isinstance(step, (list, tuple)):
                        steps.append(
                            [cls._deserialize_check(sub_step) for sub_step in step]
                        )
                    else:
                        steps.append(cls._deserialize_check(step))
                else:
                    assert isinstance(
                        step, dict
                    ), "Only the last step of a check can be multiple operators"
                    steps.append(cls._deserialize_check(step))

        settings = Settings(**data["settings"])
        return cls(checks=checks, settings=settings)

    @classmethod
    def deserialize(cls, fpath: str) -> "Config":
        return cls.from_dict(jsonload(fpath))

    def serialize(self, fpath: str) -> None:
        jsondump({"checks": self.checks, "settings": self.settings}, fpath)
