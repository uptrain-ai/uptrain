import numpy as np

from typing import List, Union

from uptrain.core.classes.distances import AbstractDistance


class HammingDistance(AbstractDistance):
    """Class that computes Hamming distance between base and reference vectors."""

    def compute_distance(
        self, base: Union[List, np.ndarray], reference: Union[List, np.ndarray]
    ) -> np.ndarray:
        """Compute the Hamming distance between base and reference vectors.

        Parameters
        ----------
        base
            It is the base vector for Hamming distance computation.
        reference
            It is the reference vector for Hamming distance computation.

        Returns
        -------
        np.ndarray
            The Hamming distance between base and reference.
        """

        base = np.array(base)
        reference = np.array(reference)

        self.check_compatibility(base, reference)

        return sum(abs(b - r) for b, r in zip(base, reference)) / len(base)
