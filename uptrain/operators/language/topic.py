"""
This module provides the Topic Assignment operators that help to assign topics based on input queries.

Operators:
- `TopicAssignmentviaCluster`: Assigns topics based on clustering performed on embeddings.

"""

from __future__ import annotations
import typing as t

from loguru import logger
import numpy as np
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep


@register_op
class TopicAssignmentviaCluster(ColumnOp):

    """
    Operator for assigning topics based on cluster assignments. Note, you should run Clustering operator before using this.

    Attributes:
        cluster_centroids (dict): Dictionary of centroids for each cluster for each aggregation. Extracted from 'Clustering' operator.
        topics (dict): Dictionary of topics for each cluster for each aggregation. Extracted from 'TopicGeneration' operator.
        col_embeddings (str):  The name of the column which contains embeddings - It will be compared against centroids to determine cluster.
        col_out (str):  The name of the column in the DataFrame to output the assigned topic.
        col_out_cluster (str): The name of the column in the DataFrame to output the assigned cluster index.
        col_out_dist (str): The name of the column in the DataFrame to output the euclidean distance from its cluster centroid.
        col_aggs (list[str]): Optional,pecify name of columns to aggregate by which was used during clustering, ex: if you ran separate clustering for seperate organisations
    """

    cluster_centroids: dict
    topics: dict
    col_embeddings: str = 'embedding'
    col_out: str = 'topic'
    col_out_cluster: str = "cluster_index"
    col_out_dist: str = 'cluster_index_distance'
    col_aggs: list[str] = []

    def setup(self, settings: Settings):
        assert len(self.topics) > 0, "Topic list should not be empty"
        assert len(self.topics) == len(self.cluster_centroids), "Each group should have a topic"
        for key in self.topics.keys():
            assert len(self.topics[key]) == len(self.cluster_centroids[key]), "Each cluster should have a topic"
            self.cluster_centroids[key] = np.array(self.cluster_centroids[key])
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:      
        res_data_arr = []

        unique_agg_keys = ['default']
        if len(self.col_aggs):
            # First aggregate by col_aggs
            agg_data = data.groupby(self.col_aggs).agg([pl.col(self.col_embeddings).count().alias("num_rows_" + self.col_embeddings)])
            agg_data = agg_data.drop("num_rows_" + self.col_embeddings)
            unique_agg_keys = agg_data.to_dicts()

        for unique_agg_key in unique_agg_keys:
            cond = True
            if isinstance(unique_agg_key, dict):
                unique_agg_key = dict([(key, unique_agg_key[key]) for key in sorted(unique_agg_key)])
                for key,val in unique_agg_key.items():
                    cond = cond & (data[key] == val)
            data_subset = data.filter(cond)
            embeddings = np.asarray(data_subset[self.col_embeddings])

            if str(unique_agg_key) not in self.cluster_centroids:
                cluster_centroids = None
                topics = ['Not Defined']
            else:
                cluster_centroids = np.array(self.cluster_centroids[str(unique_agg_key)])
                topics = self.topics[str(unique_agg_key)]

            assigned_topics = []
            assigned_clusters = []
            cluster_index_distances = []
            for index in range(len(embeddings)):
                if cluster_centroids is None:
                    cluster_index_distances.append(float(-1))
                    assigned_topics.append(topics[0])
                    assigned_clusters.append(-1)
                else:
                    dists = np.linalg.norm(embeddings[index] - cluster_centroids, axis=1)
                    assigned_cluster = np.argmin(dists)
                    cluster_index_distances.append(np.min(dists))
                    assigned_topics.append(topics[assigned_cluster])
                    assigned_clusters.append(assigned_cluster)

            data_subset = data_subset.with_columns([
                    pl.Series(assigned_topics).alias(self.col_out),
                    pl.Series(assigned_clusters).alias(self.col_out_cluster),
                    pl.Series(cluster_index_distances).alias(self.col_out_dist),
            ])
            res_data_arr.append(data_subset)

        return {
            "output": pl.concat(res_data_arr)
        }

