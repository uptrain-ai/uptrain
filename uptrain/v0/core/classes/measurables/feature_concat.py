from typing import Any
import numpy as np

from uptrain.v0.core.classes.measurables import Measurable


class FeatureConcatMeasurable(Measurable):
    """Class that returns the input feature corresponding to the feature name."""

    def __init__(self, framework, feat_name_list) -> None:
        super().__init__(framework)
        self.feat_name_list = feat_name_list

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> Any:
        vals = [inputs[x] for x in self.feat_name_list]
        vals = np.transpose(vals)
        return vals

    def col_name(self) -> str:
        name = 'concat_' + '_'.join(self.feat_name_list)
        return name

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        vals = [x[y] for y in self.feat_name_list]
        return vals
