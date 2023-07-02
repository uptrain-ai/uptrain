from typing import Any

from uptrain.v0.core.classes.measurables import Measurable


class OutputFeatureMeasurable(Measurable):
    """Class that returns the output feature corresponding to the feature name."""

    def __init__(self, framework) -> None:
        super().__init__(framework)

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> Any:
        return outputs

    def col_name(self) -> str:
        return str("prediction")

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        return x
