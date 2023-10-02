"""
This module provides the Clustering operator that operate on embeddings.

Operators:
- `Clustering`: Performs the clustering on examples in embedding space.

NOTE: The above operators take embeddings as input. Refer uptrain.operators.language.embedding and uptrain.operators.embs to learn more.

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
        col_out_dist (str): The name of the column in the DataFrame to output the euclidean distance from its cluster centroid.
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

    algorithm: str = 'kmeans'
    n_clusters: int = 40
    col_in: str = 'umap_embedding'
    col_out: str = 'cluster_index'
    col_out_dist: str = 'cluster_index_distance'

    def setup(self, settings: Settings):
        if self.algorithm == "kmeans":
            self.algorithm_obj = nltk.cluster.KMeansClusterer(self.n_clusters, distance=nltk.cluster.util.cosine_distance,avoid_empty_clusters=True)
        else:
            raise Exception(f"{self.algorithm} is not supported yet.")
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:      
        embeddings = np.asarray(data[self.col_in])
        assigned_clusters = self.algorithm_obj.cluster(embeddings, assign_clusters=True)
        scores = []
        for index in range(len(embeddings)):
            scores.append(np.linalg.norm(embeddings[index] - self.algorithm_obj.means()[assigned_clusters[index]]))
        return {
            "output": 
                data.with_columns([
                        pl.Series(assigned_clusters).alias(self.col_out),
                        pl.Series(scores).alias(self.col_out_dist) 
                ])
        }


