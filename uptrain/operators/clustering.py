"""
This module provides the following Distribution and UMAP operators that operate on embeddings:

Operators:
- `Distribution`: Computes the distribution of similarity metrics.
- `UMAP`: Performs UMAP dimensionality reduction.

NOTE: The above operators only take embeddings as input. Refer uptrain.operators.language.embedding to learn more.

"""

from __future__ import annotations
import typing as t

from loguru import logger
import numpy as np
import polars as pl
from pydantic import root_validator

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

nltk = lazy_load_dep("nltk", "nltk")



@register_op
class Clustering(ColumnOp):
    """
    Operator for performing Kmeans clustering.

    Attributes:
        algorithm (str): algorithm to perform clustering.
        n_clusters (int): number of clusters.
        col_in (str):  The name of the column in the DataFrame where clustering needs to be performed.
        col_out (str):  The name of the column in the DataFrame to output the assigned cluster index.
    Example:
        ```
        import polars as pl
        from uptrain.operators import Clustering

        # Create an instance of the UMAP operator
        op = Clustering(
                algorithm="kmeans",
                n_clusters=40, 
                col_in = 'umap_embedding',
                col_out = 'cluster_index'
            )

        # Set up the operator
        op.setup()

        # Run the operator on the input data
        input_data = pl.DataFrame(...)
        output = op.run(input_data)

        # Get the output DataFrame
        assigned_clusters = output["output"]
        ```
    """

    algorithm: str
    n_clusters: int
    col_in: str = 'umap_embedding'
    col_out: str = 'cluster_index'

    def setup(self, settings: Settings):
        if self.algorithm == "kmeans":
            self.algorithm_obj = nltk.cluster.KMeansClusterer(self.n_clusters, distance=nltk.cluster.util.cosine_distance,avoid_empty_clusters=True)
        else:
            raise Exception(f"{self.algorithm} is not supported yet.")
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:      
        embs_1 = np.asarray(data[self.col_in])
        assigned_clusters = self.algorithm_obj.cluster(embs_1, assign_clusters=True)
        return {"output": data.with_columns([pl.Series(assigned_clusters).alias(self.col_out)])}


