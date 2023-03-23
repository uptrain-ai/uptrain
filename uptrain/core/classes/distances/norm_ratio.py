import numpy as np

from typing import List, Union

from uptrain.core.classes.distances import AbstractDistance


class NormRatio(AbstractDistance):
    """Class that computes the normalized ratio between base and reference vectors."""

    NORM_MIN = 1e-6

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

        if len(base.shape) > 1:
            base_norm = np.linalg.norm(base, axis=1)
        else:
            base_norm = np.abs(base)
        if len(reference.shape) > 1:
            ref_norm = np.linalg.norm(reference, axis=1)
        else:
            ref_norm = np.abs(reference)

        return base_norm / np.maximum(ref_norm, self.NORM_MIN)
