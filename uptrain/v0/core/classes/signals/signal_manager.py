from uptrain.v0.core.classes.signals import Signal
from uptrain.v0.constants import ModelSignal


class SignalManager:
    """
    Manager class to help with signal evalutions

    ...
    Attributes
    ----------
    formulae : Signal
        Signal used to identify interesting data-points

    Methods
    -------
    add_signal_formulae(formulae):
        Attach the defined signal formulae to identify interesting data-points
    evaluate_signal(inputs, outputs, extra_args={}):
        Evaluate the defined signal formulae on given inputs and outputs
    """

    def __init__(self):
        """Initialise with default ie pass all signal"""

        self.formulae = Signal(ModelSignal.DEFAULT, is_model_signal=True)

    def add_signal_formulae(self, formulae):
        """Attach the defined signal formulae to identify interesting data-points"""

        self.formulae = formulae

    def evaluate_signal(self, inputs, outputs, gts=None, extra_args={}):
        """Evaluate the defined signal formulae on given inputs and outputs"""
        return self.formulae.evaluate(inputs, outputs, gts=None, extra_args=extra_args)

    def __str__(self) -> str:
        return str(self.formulae)
