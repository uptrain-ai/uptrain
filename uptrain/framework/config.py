import typing as t
from functools import partial

from pydantic import BaseModel, BaseSettings, Field
from uptrain.operators.base import Operator

# -----------------------------------------------------------
# Create a registry for operators defined through the Uptrain
# library. This lets us load the corresponding operator from
# the serialized config.
# -----------------------------------------------------------


class OperatorRegistry:
    _registry: dict[str, t.Type[Operator]] = {}

    @classmethod
    def register_operator(cls, name: str, operator_klass: t.Any):
        if not issubclass(operator_klass, Operator):
            raise ValueError(
                f"{operator_klass.__name__} doesn't follow the Operator protocol."
            )
        cls._registry[name] = operator_klass

    @classmethod
    def get_operator(cls, name: str):
        operator_klass = cls._registry.get(name)
        if operator_klass is None:
            raise ValueError(f"No operator registered with name {name}")
        return operator_klass


def _register_operator(
    cls: t.Type[Operator], namespace: t.Optional[str]
) -> t.Type[Operator]:
    key = cls.__name__
    if namespace is not None:
        key = f"{namespace}:{key}"
    OperatorRegistry.register_operator(key, cls)
    return cls


def register_operator(namespace: t.Optional[str] = None):
    """Decorator to register an operator with Uptrain's registry.

    Args:
        namespace (t.Optional[str], optional): Namespace to register the operator under. Defaults to None.
    """
    return partial(_register_operator, namespace=namespace)


class Pipeline(BaseModel):
    elements: list[t.Union[Operator, list[Operator]]]

    def check_elements(cls, values):
        elements = values["elements"]
        if len(elements) == 0:
            raise ValueError("Expected at least one element in the pipeline")
        for i, elem in enumerate(elements):
            if i != len(elements) - 1:
                if not isinstance(elem, Operator):
                    raise ValueError(
                        f"Expected elements of the pipeline besides the end to be of type `Operator`"
                    )
        return values


class Settings(BaseSettings):
    # general
    logs_folder: str

    # external api auth
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")


class Config:
    checks: list[list[t.Union[Operator, tuple[Operator]]]]
    settings: Settings
