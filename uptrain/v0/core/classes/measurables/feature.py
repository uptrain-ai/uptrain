from typing import Any

from uptrain.v0.core.classes.measurables import (
    Measurable,
    InputFeatureMeasurable,
    OutputFeatureMeasurable,
)


class FeatureMeasurable(Measurable):
    """Class that returns a feature as a result of computation."""

    def __init__(self, framework, feature_name, dictn_type: str) -> None:
        """Constructor for FeatureMeasurable class.
        
        Parameters
        ----------
        feature_name
            Name of the feature that is to be measured/evaluated
        dictn_type
            Must be "inputs" or "outputs" depending on which feature to
            measure/evaluate
        """
        super().__init__(framework)
        self.feature_name = feature_name
        self.dictn_type = dictn_type
        if self.dictn_type == "inputs":
            self.helper = InputFeatureMeasurable(framework, feature_name)
        elif self.dictn_type == "outputs":
            self.helper = OutputFeatureMeasurable(framework, feature_name)
        else:
            raise Exception(
                "Helper Measurable not defined for dictionary type %s" % self.dictn_type
            )

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> Any:
        return self.helper._compute(
            inputs=inputs, outputs=outputs, gts=gts, extra=extra
        )

    def col_name(self) -> str:
        return self.helper.col_name()

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        return self.helper.extract_val_from_training_data(x)
