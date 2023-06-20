import numpy as np

from typing import List, Union

from uptrain.v0.core.classes.distances import AbstractDistance


class L2Distance(AbstractDistance):
    """Class that computes L2 distance between base and reference vectors."""

    def compute_distance(
        self, base: Union[List, np.ndarray], reference: Union[List, np.ndarray]
    ) -> np.ndarray:
        """Compute the L2 distance between base and reference vectors.

        Parameters
        ----------
        base
            It is the base vector for L2 distance computation.
        reference
            It is the reference vector for L2 distance computation.

        Returns
        -------
        np.ndarray
            The L2 distance between base and reference.
        """

        base = np.array(base)
        reference = np.array(reference)

        self.check_compatibility(base, reference)

        return np.sum(
            (base - reference) * (base - reference),
            axis=tuple(range(1, len(base.shape))),
        )
