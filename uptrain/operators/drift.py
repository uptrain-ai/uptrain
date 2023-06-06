"""
Implement checks to detect drift in the data. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import BaseModel, root_validator
import polars as pl

try:
    import river
except ImportError:
    river = None

from uptrain.operators.base import *
from uptrain.utilities import dependency_required

if t.TYPE_CHECKING:
    from uptrain.framework.config import *


class ParamsDDM(BaseModel):
    warm_start: int = 500
    warn_threshold: float = 2.0
    alarm_threshold: float = 3.0


class ParamsADWIN(BaseModel):
    delta: float = 0.002
    clock: int = 32
    max_buckets: int = 5
    min_window_length: int = 5
    grace_period: int = 5


class SchemaDrift(BaseModel):
    in_col_measure: str = "metric"


@register_op
class ConceptDrift(BaseModel):
    algorithm: t.Literal["DDM", "ADWIN"]
    params: t.Union[ParamsDDM, ParamsADWIN]
    dataschema: SchemaDrift = SchemaDrift()

    @root_validator
    def check_params(cls, values):
        algo = values["algorithm"]
        params = values["params"]
        if algo == "DDM" and not isinstance(params, ParamsDDM):
            raise ValueError(
                f"Expected params to be of type {ParamsDDM} for algorithm - DDM"
            )
        elif algo == "ADWIN" and not isinstance(params, ParamsADWIN):
            raise ValueError(
                f"Expected params to be of type {ParamsADWIN} for algorithm - ADWIN"
            )
        return values

    def make_executor(self, settings: t.Optional[Settings] = None):
        return ConceptDriftExecutor(self)


@dependency_required(river, "river")
class ConceptDriftExecutor(OperatorExecutor):
    op: ConceptDrift
    algo: t.Any
    counter: int
    cuml_accuracy: float
    alert_info: t.Optional[dict]

    def __init__(self, op: ConceptDrift):
        import river.drift.binary
        import river.drift

        self.op = op
        if op.algorithm == "DDM":
            self.algo = river.drift.binary.DDM(**op.params.dict())
        elif op.algorithm == "ADWIN":
            self.algo = river.drift.ADWIN(**op.params.dict())
        self.counter = 0
        self.avg_accuracy = 0.0
        self.alert_info = None

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        ser = data.get_column(self.op.dataschema.in_col_measure)

        for val in ser:
            self.algo.update(val)
            if self.algo.drift_detected and self.alert_info is None:
                msg = f"Drift detected using {self.op.algorithm}!"
                self.alert_info = {"counter": self.counter, "msg": msg}
                logger.info(msg)

            self.counter += 1
            self.cuml_accuracy += val

        avg_accuracy = self.cuml_accuracy / self.counter if self.counter > 0 else 0.0
        return {
            "output": None,
            "extra": {
                "counter": self.counter,
                "avg_accuracy": avg_accuracy,
                "alert_info": self.alert_info,
            },
        }
