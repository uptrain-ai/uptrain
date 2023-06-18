import numpy as np

from typing import Any

from uptrain.v0.core.classes.measurables import Measurable


class RecHitRateMeasurable(Measurable):
    """Class that computes the recommendation hit-rate of a model's predictions."""

    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> Any:
        acc = [1 if gt in outputs[i] else 0 for i, gt in enumerate(gts)]
        return np.array(acc)

    def col_name(self) -> str:
        return "Hit-Rate"
