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
        col_aggs (list[str]): Optional, can be used to specify name of columns to aggregate by and run individual clustering, ex: if you want separate clustering for seperate organisations
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
    col_aggs: list[str] = []
    min_samples_each_cluster: int = 50

    def setup(self, settings: Settings):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:      

        self.cluster_centroids = {}
        unique_agg_keys = ['default']

        if len(self.col_aggs):
            # First aggregate by col_aggs
            agg_data = data.groupby(self.col_aggs).agg([pl.col(self.col_in).count().alias("num_rows_" + self.col_in)])
            agg_data = agg_data.drop("num_rows_" + self.col_in)
            unique_agg_keys = agg_data.to_dicts()

        res_data_arr = []
        for unique_agg_key in unique_agg_keys:
            cond = True
            if isinstance(unique_agg_key, dict):
                unique_agg_key = dict([(key, unique_agg_key[key]) for key in sorted(unique_agg_key)])
                for key,val in unique_agg_key.items():
                    cond = cond & (data[key] == val)
            data_subset = data.filter(cond)

            n_clusters = max(1, min(self.n_clusters, int(len(data_subset)/self.min_samples_each_cluster)))

            if self.algorithm == "kmeans":
                algorithm_obj = nltk.cluster.KMeansClusterer(n_clusters, distance=nltk.cluster.util.cosine_distance, avoid_empty_clusters=True)
            else:
                raise Exception(f"{self.algorithm} is not supported yet.")

            embeddings = np.asarray(data_subset[self.col_in])
            assigned_clusters = algorithm_obj.cluster(embeddings, assign_clusters=True)
            scores = []
            for index in range(len(embeddings)):
                scores.append(np.linalg.norm(embeddings[index] - algorithm_obj.means()[assigned_clusters[index]]))

            data_subset = data_subset.with_columns([
                        pl.Series(assigned_clusters).alias(self.col_out),
                        pl.Series(scores).alias(self.col_out_dist),
                        pl.Series([str(unique_agg_key)] * len(data_subset)).alias("_unique_agg_key_for_clustering")
                ])
            res_data_arr.append(data_subset)
            unique_assigned_clusters = np.unique(np.array(assigned_clusters))
            all_means = [list(x.astype(np.float64)) for x in list(algorithm_obj.means())]
            assigned_means = []
            for clus_idx in unique_assigned_clusters:
                assigned_means.append([round(y, 8) for y in all_means[clus_idx]])
            self.cluster_centroids[str(unique_agg_key)] = assigned_means

        return {
            "output": 
                pl.concat(res_data_arr)
        }


