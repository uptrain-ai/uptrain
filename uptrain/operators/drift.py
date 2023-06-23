"""
Implement checks to detect drift in the data. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import root_validator
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

drift = lazy_load_dep("river.drift", "river")


class ParamsDDM(OpBaseModel):
    warm_start: int = 500
    warn_threshold: float = 2.0
    alarm_threshold: float = 3.0


class ParamsADWIN(OpBaseModel):
    delta: float = 0.002
    clock: int = 32
    max_buckets: int = 5
    min_window_length: int = 5
    grace_period: int = 5


@register_op
class ConceptDrift(ColumnOp):
    algorithm: t.Literal["DDM", "ADWIN"]
    params: t.Union[ParamsDDM, ParamsADWIN]
    col_in_measure: str = "metric"
    _algo_obj: t.Any
    _counter: int
    _cuml_accuracy: float
    _alert_info: t.Optional[dict]

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

    def setup(self, _: t.Optional[Settings] = None):
        if self.algorithm == "DDM":
            self._algo_obj = drift.DDM(**self.params.dict())  # type: ignore
        elif self.algorithm == "ADWIN":
            self._algo_obj = drift.ADWIN(**self.params.dict())  # type: ignore
        self._counter = 0
        self._avg_accuracy = 0.0
        self._alert_info = None

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        ser = data.get_column(self.col_in_measure)

        for val in ser:
            self._algo_obj.update(val)
            if self._algo_obj.drift_detected and self._alert_info is None:
                msg = f"Drift detected using {self.algorithm}!"
                self._alert_info = {"counter": self._counter, "msg": msg}
                logger.info(msg)

            self._counter += 1
            self._cuml_accuracy += val

        avg_accuracy = self._cuml_accuracy / self._counter if self._counter > 0 else 0.0
        return {
            "output": None,
            "extra": {
                "counter": self._counter,
                "avg_accuracy": avg_accuracy,
                "alert_info": self._alert_info,
            },
        }
