import numpy as np

from uptrain.v0.core.classes.measurables import Measurable


class AccuracyMeasurable(Measurable):
    """Class that computes the accuracy from predictions and ground truths.

    Returns a list of values where a value is:
    - True, if prediction equals ground truth
    - False, if prediction does not equal ground truth
    """

    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> np.ndarray:
        gts = np.array(gts)
        outputs = np.reshape(np.array(outputs), gts.shape)
        return np.equal(outputs, gts)

    def col_name(self) -> str:
        return "Accuracy"


class MAEMeasurable(Measurable):
    """Class that computes the Mean Absolute Error from predictions and ground truths.

    Returns a list of values where each value is the absolute value of the
    difference between corresponding prediction and ground truth.
    """

    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> np.ndarray:
        gts = np.array(gts)
        outputs = np.reshape(np.array(outputs), gts.shape)
        return np.squeeze(np.abs(outputs - gts))

    def col_name(self) -> str:
        return "MAE"


class MAPEMeasurable(Measurable):
    """Class that computes the Mean Absolute Percentage Error from predictions and ground truths.

    Returns a list of values where each value is the absolute percentage
    difference between corresponding prediction and ground truth,
    multiplied by 100 to express the result as a percentage.
    """
    
    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> np.ndarray:
        gts = np.array(gts)
        outputs = np.reshape(np.array(outputs), gts.shape)
        return 100 * np.squeeze(np.abs(np.divide(outputs - gts, gts)))

    def col_name(self) -> str:
        return "MAPE"
