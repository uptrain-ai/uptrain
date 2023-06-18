import numpy as np

from typing import List, Union

from uptrain.v0.core.classes.distances import AbstractDistance


class NormRatio(AbstractDistance):
    """Class that computes the normalized ratio between base and reference vectors."""

    def __init__(self, norm_min: float = 1e-6):
        self.norm_min = norm_min

    def calculate_norm(self, vector) -> float:
        if len(vector.shape) > 1:
            return np.linalg.norm(vector, axis=1)
        return np.abs(vector)

    def compute_distance(
        self, base: Union[List, np.ndarray], reference: Union[List, np.ndarray]
    ) -> np.ndarray:
        """Compute the norm ratio between base and reference vectors.

        Parameters
        ----------
        base
            It is the base vector for norm ratio computation.
        reference
            It is the reference vector for norm ratio computation.

        Returns
        -------
        np.ndarray
            The norm ratio between base and reference.
        """

        base = np.array(base)
        reference = np.array(reference)

        self.check_compatibility(base, reference)

        base_norm = self.calculate_norm(base)
        ref_norm = self.calculate_norm(reference)

        return base_norm / np.maximum(ref_norm, self.norm_min)
