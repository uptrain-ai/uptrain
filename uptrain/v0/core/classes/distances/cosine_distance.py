import numpy as np

from typing import List, Union

from uptrain.v0.core.classes.distances import AbstractDistance


class CosineDistance(AbstractDistance):
    """Class that computes cosine distance between base and reference vectors."""

    def calculate_norm(self, vector) -> float:
        if len(vector.shape) > 1:
            return np.linalg.norm(vector, axis=1)
        return np.abs(vector)

    def compute_distance(
        self, base: Union[List, np.ndarray], reference: Union[List, np.ndarray]
    ) -> np.ndarray:
        """Compute the cosine distance between base and reference.

        The cosine distance between vectors x and y is defined as:
            1 - cosine_similarity(x, y)
        The cosine similarity can be computed as:
            dot_product(x, y) / (normalized(x) * normalized(y))

        For further reading, check [this](https://en.wikipedia.org/wiki/Cosine_similarity) out.

        Parameters
        ----------
        base
            x in the above equations.
            It is the base vector for cosine distance computation.
        reference
            y in the above equations.
            It is the reference vector for cosine distance computation.

        Returns
        -------
        np.ndarray
            The cosine distance between base and reference.
        """
        base = np.array(base)
        reference = np.array(reference)

        self.check_compatibility(base, reference)

        base_norm = self.calculate_norm(base)
        ref_norm = self.calculate_norm(reference)

        return np.array(
            [
                1 - np.dot(base[i], reference[i]) / (base_norm[i] * ref_norm[i])
                for i in range(base.shape[0])
            ]
        )
