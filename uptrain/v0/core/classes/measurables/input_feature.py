from typing import Any

from uptrain.v0.core.classes.measurables import Measurable


class InputFeatureMeasurable(Measurable):
    """Class that returns the input feature corresponding to the feature name."""

    def __init__(self, framework, feature_name) -> None:
        super().__init__(framework)
        self.feature_name = feature_name

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> Any:
        return inputs[self.feature_name]

    def col_name(self) -> str:
        return str(self.feature_name)

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        return x[self.feature_name]
