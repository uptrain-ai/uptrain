import umap
from sklearn.cluster import DBSCAN
import numpy as np

from uptrain.core.classes.visuals import AbstractVisual
from uptrain.constants import Visual, Statistic
from uptrain.core.classes.measurables import MeasurableResolver


class Umap(AbstractVisual):
    visual_type = Visual.UMAP
    dashboard_name = "umap_and_clusters"

    def __init__(self, fw, check):
        self.framework = fw
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
            fw
        )
        self.item_counts = {}
        self.feats_dictn = {}
        self.distances_dictn = {}
        self.count_checkpoints = check["count_checkpoints"]
        self.min_dist = check["min_dist"]
        self.n_neighbors = check["n_neighbors"]
        self.metric_umap = check["metric_umap"]
        self.dim = check["dim"]
        self.min_samples = check["min_samples"]
        self.eps = check["eps"]
        self.emb_dict = {}
        self.total_count = 0

    def check(self, inputs, outputs, gts=None, extra_args={}):
        self.total_count += 1
        if not (self.total_count % 10000 == 0):
            return

        for count in self.count_checkpoints:
            data_dict = self.get_data_for_umap(count)

            if len(data_dict) > 10:
                emb_list = np.squeeze(np.array(list(data_dict.values())))
                umap_list, clusters = self.get_umap_and_clusters(
                    emb_list,
                    self.dim,
                    self.n_neighbors,
                    self.min_dist,
                    self.metric_umap,
                    self.eps,
                    self.min_samples,
                )
                this_data = {"umap": umap_list, "clusters": clusters}
                self.log_handler.add_histogram(
                    self.dashboard_name,
                    this_data,
                    self.dashboard_name,
                    count,
                )

    def get_data_for_umap(self, count):
        distribution_anomaly = list(
            filter(
                lambda x: x.statistic_type == Statistic.DISTRIBUTION_STATS,
                self.framework.check_manager.statistics_to_check,
            )
        )[0]
        return distribution_anomaly.get_feats_for_clustering(count)

    def get_umap_and_clusters(
        self,
        emb_list,
        dim,
        n_neighbors,
        min_dist,
        metric,
        eps,
        min_samples,
    ):
        if dim == "2D":
            n_components = 2
        else:
            n_components = 3

        try:
            umap_embeddings = umap.UMAP(
                n_neighbors=n_neighbors,
                n_components=n_components,
                min_dist=min_dist,
                metric=metric,
            ).fit_transform(emb_list)
        except:
            import pdb

            pdb.set_trace()

        # Do DBSCAN clustering
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(umap_embeddings)
        return umap_embeddings, clustering.labels_
