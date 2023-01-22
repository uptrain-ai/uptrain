from uptrain.core.classes.anomalies.measurables import (
    Measurable,
    InputFeatureMeasurable,
    OutputFeatureMeasurable,
)


class FeatureMeasurable(Measurable):
    def __init__(self, framework, feature_name, dictn_type) -> None:
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

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        return self.helper._compute(
            inputs=inputs, outputs=outputs, gts=gts, extra=extra
        )

    def col_name(self):
        return self.helper.col_name()

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        return self.helper.extract_val_from_training_data(x)
