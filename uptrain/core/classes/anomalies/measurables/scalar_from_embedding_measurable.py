from uptrain.core.classes.anomalies.measurables import (
    Measurable,
    InputFeatureMeasurable,
)


class ScalarFromEmbeddingMeasurable(Measurable):
    def __init__(self, framework, idx, extract_from_args) -> None:
        super().__init__(framework)
        self.idx = idx
        self.extract_from = InputFeatureMeasurable(
            framework, extract_from_args["feature_name"]
        )

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        return self.extract_from._compute(
            inputs=inputs, outputs=outputs, gts=gts, extra=extra
        )[self.idx]

    def col_name(self):
        return (
            "Measurable: Scalar [Index:"
            + str(self.idx)
            + "] from Embedding: "
            + str(self.extract_from.col_name())
        )

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        return self.extract_from.extract_val_from_training_data(x)[self.idx]
