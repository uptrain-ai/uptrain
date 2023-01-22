import numpy as np

from uptrain.core.classes.anomalies.measurables import Measurable
from uptrain.core.classes.anomalies.signals import SignalManager


class CustomMeasurable(Measurable):
    def __init__(self, framework, custom_args={}) -> None:
        super().__init__(framework)
        self._args = custom_args
        self.signal_manager = SignalManager()
        self.signal_manager.add_signal_formulae(self._args["signal_formulae"])

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        val = self.signal_manager.evaluate_signal(
            inputs, outputs, gts=gts, extra_args=extra
        )
        return val

    def col_name(self):
        return "Measurable: Custom(" + str(self.signal_manager) + ")"

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        fake_inputs = {}
        for key, val in x.items():
            fake_inputs.update({key: np.array([val])})
        return self.signal_manager.evaluate_signal(fake_inputs, None)
