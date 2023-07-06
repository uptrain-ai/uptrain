"""
Implement checks to test similarity between two pieces of text.

This module provides the `CosineSimilarity` class, which calculates the cosine similarity between two vectors representing text. The vectors can be columns in a DataFrame. The cosine similarity measures the similarity between two vectors based on the cosine of the angle between them.

"""

from __future__ import annotations
import typing as t

import numpy as np
from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class CosineSimilarity(ColumnOp):
    """
    Column operation to calculate the cosine similarity between two vectors representing text.

    Attributes:
        col_in_vector_1 (str): The name of the column containing the first vector.
        col_in_vector_2 (str): The name of the column containing the second vector.
        col_out (str): The name of the output column containing the cosine similarity scores.

    Returns:
        dict: A dictionary containing the cosine similarity scores.

    Example:
        ```
        import polars as pl
        import numpy as np
        from uptrain.operators import CosineSimilarity

        # Create a DataFrame
        df = pl.DataFrame({
            "vector_1": [np.array([0.1, 0.2, 0.3]), np.array([0.4, 0.5, 0.6])],
            "vector_2": [np.array([0.7, 0.8, 0.9]), np.array([0.2, 0.3, 0.4])]
        })

        # Create an instance of the CosineSimilarity class
        similarity_op = CosineSimilarity(col_in_vector_1="vector_1", col_in_vector_2="vector_2")

        # Calculate the cosine similarity between the two vectors
        result = similarity_op.run(df)
        similarity_scores = result["output"]

        # Print the similarity scores
        print(similarity_scores)
        ```

    Output:
        ```
        shape: (2,)
        Series: '_col_0' [f64]
        [
                1.861259
                0.288437
        ]
        ```

    """

    col_in_vector_1: str
    col_in_vector_2: str
    col_out: str = "cosine_similarity"

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        vector_1 = data.get_column(self.col_in_vector_1)
        vector_2 = data.get_column(self.col_in_vector_2)

        results = []
        for i in range(len(vector_1)):
            v1 = np.array(vector_1[i])
            v2 = np.array(vector_2[i])
            similarity_score = np.dot(v1, v2) / np.linalg.norm(v1) * np.linalg.norm(v2)
            results.append(similarity_score)

        return {"output": data.with_columns(pl.Series(results).alias(self.col_out))}
