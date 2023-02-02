import numpy as np

from uptrain.core.classes.anomalies.measurables import Measurable


class AccuracyMeasurable(Measurable):
    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        gts = np.array(gts)
        outputs = np.reshape(np.array(outputs), gts.shape)
        return np.equal(outputs, gts)

    def col_name(self):
        return "Measurable: Accuracy"
