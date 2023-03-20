import numpy as np

from typing import List, Union

from uptrain.core.classes.distances import AbstractDistance


class CosineDistance(AbstractDistance):
    """Class that computes cosine distance between base and reference vectors."""

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

        if base.shape != reference.shape:
            raise Exception("Incompatible shapes for base and reference")

        if len(base.shape) > 1:
            base_norm = np.linalg.norm(base, axis=1)
        else:
            base_norm = np.abs(base)
        if len(reference.shape) > 1:
            ref_norm = np.linalg.norm(reference, axis=1)
        else:
            ref_norm = np.abs(reference)

        return np.array(
            [
                1 - np.dot(base[i], reference[i]) / (base_norm[i] * ref_norm[i])
                for i in range(base.shape[0])
            ]
        )
