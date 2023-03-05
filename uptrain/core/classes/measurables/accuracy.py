import numpy as np

from uptrain.core.classes.measurables import Measurable


class AccuracyMeasurable(Measurable):
    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        gts = np.array(gts)
        outputs = np.reshape(np.array(outputs), gts.shape)
        return np.equal(outputs, gts)

    def col_name(self):
        return "Accuracy" 


class MAEMeasurable(Measurable):
    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        gts = np.array(gts)
        outputs = np.reshape(np.array(outputs), gts.shape)
        return np.squeeze(np.abs(outputs - gts))

    def col_name(self):
        return "MAE"


class MAPEMeasurable(Measurable):
    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        gts = np.array(gts)
        outputs = np.reshape(np.array(outputs), gts.shape)
        return 100*np.squeeze(np.abs(np.divide(outputs - gts, gts)))

    def col_name(self):
        return "MAPE"    
