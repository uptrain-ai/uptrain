import numpy as np

from uptrain.core.classes.measurables import Measurable


class InputFeatureMeasurable(Measurable):
    def __init__(self, framework, feature_name, dtype=None) -> None:
        super().__init__(framework)
        self.feature_name = feature_name
        # self.dtype = dtype

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        val = inputs[self.feature_name]
        if self.dtype:
            if self.dtype == int:
                val = [int(x) for x in list(val)]
            else:
                raise Exception("Invalid dtype")
        return val

    def col_name(self):
        return str(self.feature_name)

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        return x[self.feature_name]
