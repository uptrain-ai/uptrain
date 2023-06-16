from abc import ABC
from typing import Any


class AbstractMeasurable(ABC):
    """Abstract base class for objects that can be measured or evaluated.

    This abstract class provides a template for defining objects that can
    be evaluated in some way. Subclasses of  AbstractMeasurable should
    implement the `_compute` method, which performs the actual computation.
    """

    def __init__(self) -> None:
        super().__init__()

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> Any:
        """Computes the measurement or evaluation of this object.

        This method should be overridden by subclasses to perform the actual
        computation of the measurement or evaluation. The inputs, outputs and
        gts parameters can be used in the computation. The extra parameter can
        be used to provided additional information for the computation.

        Parameters
        ----------
        inputs
            Inputs values to use in the computation
        outputs
            Outputs values to use in the computation
        gts
            Ground truth values to use in the computation
        extra
            Additional information to use in the computation

        Returns
        -------
        Any
            Result of the computation
        """
        raise Exception("Should be defined for each individual class")

    def col_name (self) -> str:
        """Returns the column name of the Measurable"""
        raise Exception("Should be defined for each individual class")
