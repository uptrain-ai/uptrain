import numpy as np

from typing import Any, Dict

from uptrain.v0.core.classes.measurables import Measurable
from uptrain.v0.core.classes.signals import SignalManager


class CustomMeasurable(Measurable):
    """Class that computes a custom metric measurable using a user-defined signal formula."""

    def __init__(self, framework, custom_args: Dict[str, Any] = {}) -> None:
        """Constructor for CustomMeasurable class.

        Parameters
        ----------
        framework
            UpTrain framework object
        custom_args
            A dictionary containing custom arguments for usage in computation.
            The dictionary must contain "signal_formulae" as key which maps to
            a callback that takes in inputs, outputs, gts and extra_args, and
            returns a boolean value as the signal measure.
        """
        super().__init__(framework)
        self._args = custom_args
        self.signal_manager = SignalManager()
        self.signal_manager.add_signal_formulae(self._args["signal_formulae"])

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> np.ndarray:
        val = self.signal_manager.evaluate_signal(
            inputs, outputs, gts=gts, extra_args=extra
        )
        return val

    def col_name(self) -> str:
        return str(self.signal_manager)

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        fake_inputs = {}
        for key, val in x.items():
            fake_inputs.update({key: np.array([val])})
        return self.signal_manager.evaluate_signal(fake_inputs, None)
