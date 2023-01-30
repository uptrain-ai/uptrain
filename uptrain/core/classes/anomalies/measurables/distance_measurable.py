import numpy as np

from uptrain.core.classes.anomalies.distances import DistanceResolver
from uptrain.core.classes.anomalies.measurables import Measurable
from uptrain.core.classes.anomalies.measurables import InputFeatureMeasurable

class DistanceMeasurable(Measurable):
    def __init__(self, framework, base, reference, distance_types) -> None:
        super().__init__(framework)
        self.base = InputFeatureMeasurable(framework, base['feature_name'])
        self.reference = reference
        self.ref_val = None
        self.distance_types = distance_types
        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> any:
        base_val = self.base.compute_and_log(inputs=inputs, outputs=outputs, gts=gts, extra=extra)
        if self.ref_val is None:
            self.ref_val = base_val

        dists = dict(zip(self.distance_types, [x.compute_distance(base_val, self.ref_val) for x in self.dist_classes]))

        if self.reference == 'running_diff':
            self.ref_val = base_val
        return dists

    def col_name(self, return_str = True):
        col_names = [
            "Measurable: Distance "
            + str(self.base.col_name())
            + self.reference + str(x) for x in self.distance_types]
        if return_str:
            col_names = str(col_names)
        return col_names
