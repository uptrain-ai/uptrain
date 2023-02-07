import numpy as np

from uptrain.core.classes.measurables import Measurable


class RecHitRateMeasurable(Measurable):
    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        acc = [1 if gt in outputs[i] else 0 for i,gt in enumerate(gts)]
        return np.array(acc)

    def col_name(self):
        return "Measurable: Hit-Rate"