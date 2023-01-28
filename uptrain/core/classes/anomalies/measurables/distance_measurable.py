import numpy as np

from uptrain.core.classes.anomalies.measurables import Measurable
from uptrain.core.classes.anomalies.measurables import InputFeatureMeasurable


class DistanceMeasurable(Measurable):
    def __init__(self, framework, base, reference) -> None:
        super().__init__(framework)
        self.base = InputFeatureMeasurable(framework, base['feature_name'])
        self.reference = reference
        self.ref_val = None

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        base_val = self.base.compute_and_log(inputs=inputs, outputs=outputs, gts=gts, extra=extra)
        if self.ref_val is None:
            self.ref_val = base_val

        dist = self._compute_distance(base_val, self.ref_val)

        if self.reference == 'running_diff':
            self.ref_val = base_val
        return dist

    def _compute_distance(self, base, ref) -> float:
        raise Exception("Define distance for child classes")