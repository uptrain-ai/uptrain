from typing import Any, List, Union

from uptrain.v0.core.classes.distances import DistanceResolver
from uptrain.v0.core.classes.measurables import Measurable
from uptrain.v0.core.classes.measurables import InputFeatureMeasurable


class DistanceMeasurable(Measurable):
    """Class that computes and logs distance based on chosen distance metric."""

    def __init__(self, framework, base, reference, distance_types) -> None:
        """Constructor for DistanceMeasurable class.

        Parameters
        ----------
        framework
            UpTrain Framework object
        base
            TODO
        reference
            TODO
        distance_types
            The distance types to use for computation in the distance metric.
            Distance types must be from the list:
                ["cosine_distance", "l2_distance", "norm_ratio"]
        """

        super().__init__(framework)
        self.base = InputFeatureMeasurable(framework, base["feature_name"])
        self.reference = reference
        self.ref_val = None
        self.distance_types = distance_types
        self.dist_classes = [DistanceResolver().resolve(x) for x in self.distance_types]

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None) -> Any:
        base_val = self.base.compute_and_log(
            inputs=inputs, outputs=outputs, gts=gts, extra=extra
        )
        if self.ref_val is None:
            self.ref_val = base_val

        dists = dict(
            zip(
                self.distance_types,
                [x.compute_distance(base_val, self.ref_val) for x in self.dist_classes],
            )
        )

        if self.reference == "running":
            self.ref_val = base_val
        return dists

    def col_name(self, return_str: bool = True) -> Union[List[str], str]:
        col_names = [
            f"Distance {str(self.base.col_name())} {self.reference} {str(x)}"
            for x in self.distance_types
        ]
        if return_str:
            col_names = str(col_names)
        return col_names
