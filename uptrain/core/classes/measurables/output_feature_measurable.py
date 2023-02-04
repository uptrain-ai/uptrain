from uptrain.core.classes.anomalies.measurables import Measurable


class OutputFeatureMeasurable(Measurable):
    def __init__(self, framework, feature_name) -> None:
        super().__init__(framework)
        self.feature_name = feature_name

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        return outputs[self.feature_name]

    def col_name(self):
        return "Measurable: Output - " + str(self.feature_name)
