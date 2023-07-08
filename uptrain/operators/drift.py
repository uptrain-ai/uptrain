"""
This module implements the ConceptDrift operator and its associated executor for detecting concept drift
using the DDM (Drift Detection Method) or ADWIN (Adaptive Windowing) algorithm.

The module provides the following classes:

- ParamsDDM: Parameters for the DDM algorithm.
- ParamsADWIN: Parameters for the ADWIN algorithm.
- ConceptDrift: Operator for detecting concept drift.
- ConceptDriftExecutor: Executor for the ConceptDrift operator.

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
    """
    Parameters for the DDM (Drift Detection Method) algorithm.

    Attributes:
        warm_start (int): The number of instances required before any drift detection.
        warning_threshold (float): The warning threshold value for the drift detection.
        drift_threshold (float): The alarm threshold value for the drift detection.

    """

    warm_start: int = 500
    warning_threshold: float = 2.0
    drift_threshold: float = 3.0


class ParamsADWIN(OpBaseModel):
    """
    Parameters for the ADWIN (Adaptive Windowing) algorithm.

    Attributes:
        delta (float): The delta value for the drift detection.
        clock (int): The clock value for the drift detection.
        max_buckets (int): The maximum number of buckets to keep for the drift detection.
        min_window_length (int): The minimum length of the window for the drift detection.
        grace_period (int): The grace period value for the drift detection.

    """

    delta: float = 0.002
    clock: int = 32
    max_buckets: int = 5
    min_window_length: int = 5
    grace_period: int = 5


@register_op
class ConceptDrift(ColumnOp):
    """
    Operator for detecting concept drift using the DDM (Drift Detection Method) or ADWIN (Adaptive Windowing) algorithm.

    Attributes:
        algorithm (Literal["DDM", "ADWIN"]): The algorithm to use for concept drift detection.
        params (Union[ParamsDDM, ParamsADWIN]): The parameters for the selected algorithm.
        col_in_measure (str): The name of the column in the input data representing the metric to measure concept drift.

    Raises:
        ValueError: If the specified algorithm does not match the type of the parameters.

    Example:
        ```py
        import polars as pl
        from uptrain.operators import ParamsDDM, ConceptDrift

        # Create an instance of the ParamsDDM class with the parameters

        params_ddm = ParamsDDM(
                        warm_start=500,
                        warn_threshold=2.0,
                        alarm_threshold=3.0
                    )

        # Create an instance of the ConceptDrift operator
        op = ConceptDrift(
                algorithm="DDM",
                params=params_ddm,
                col_in_measure="metric"
            )

        # Set up the operator
        op.setup()

        # Run the operator on the input data
        input_data = pl.DataFrame(...)
        output = op.run(input_data)["extra"]

        # Check the detected concept drift information
        if output["alert_info"] is not None:
            print("Counter:", output["alert_info"]["counter"])
        ```

    Output:
        ```
        INFO     | uptrain.operators.drift:run:181 - Drift detected using DDM!
        Counter: 129466
        ```
    """

    algorithm: t.Literal["DDM", "ADWIN"]
    params: t.Union[ParamsDDM, ParamsADWIN]
    col_in_measure: str = "metric"

    @root_validator
    def _check_params(cls, values):
        """
        Check if the parameters are valid for the specified algorithm.

        """
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

    def setup(self, settings: Settings):
        if self.algorithm == "DDM":
            self._algo_obj = drift.binary.DDM(**self.params.dict())  # type: ignore
        elif self.algorithm == "ADWIN":
            self._algo_obj = drift.ADWIN(**self.params.dict())  # type: ignore
        self._counter = 0
        self._avg_accuracy = 0.0
        self._cuml_accuracy = 0.0
        self._alert_info = None
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        ser = data.get_column(self.col_in_measure)

        for val in ser:
            self._algo_obj.update(val)
            if self._algo_obj.drift_detected and self._alert_info is None:
                msg = f"Drift detected using {self.algorithm}!"
                self._alert_info = {"counter": self._counter, "msg": msg}
                logger.info(msg)

            self._counter += 1
            self._cuml_accuracy += val

        self._avg_accuracy = (
            self._cuml_accuracy / self._counter if self._counter > 0 else 0.0
        )
        return {
            "output": None,
            "extra": {
                "counter": self._counter,
                "avg_accuracy": self._avg_accuracy,
                "alert_info": self._alert_info,
            },
        }
