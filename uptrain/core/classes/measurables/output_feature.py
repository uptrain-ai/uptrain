from uptrain.core.classes.measurables import Measurable


class OutputFeatureMeasurable(Measurable):
    def __init__(self, framework, feature_name) -> None:
        super().__init__(framework)
        self.feature_name = feature_name

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        return outputs

    def col_name(self):
        return str(self.feature_name)

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        return x[self.feature_name]
