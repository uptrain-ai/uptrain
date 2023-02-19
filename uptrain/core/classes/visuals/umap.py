import umap
from sklearn.cluster import DBSCAN
import numpy as np

from uptrain.core.classes.visuals import AbstractVisual
from uptrain.constants import Visual, Statistic
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.core.lib.helper_funcs import read_json


class Umap(AbstractVisual):
    visual_type = Visual.UMAP
    dashboard_name = "umap_and_clusters"

    def __init__(self, fw, check):
        self.framework = fw
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.measurable = MeasurableResolver(check.get("measurable_args", None)).resolve(fw)
        self.aggregate_measurable = MeasurableResolver(check.get("aggregate_args", None)).resolve(
            fw
        )
        self.label_measurable = MeasurableResolver(check.get("label_args", None)).resolve(
            fw
        )
        self.item_counts = {}
        self.feats_dictn = {}
        self.distances_dictn = {}
        self.count_checkpoints = check.get("count_checkpoints", ["all"])
        self.min_dist = check["min_dist"]
        self.n_neighbors = check["n_neighbors"]
        self.metric_umap = check["metric_umap"]
        self.dim = check["dim"]
        self.min_samples = check.get("min_samples", 1)
        self.eps = check.get("eps", 0.1)
        self.emb_dict = {}
        self.measurable_dict = {}
        self.total_count = 0
        self.umap_update_freq = check.get('umap_update_freq', 10000)
        self.vals = []
        self.labels = []
        self.do_clustering = check.get("do_clustering", False)
        
        self.initial_dataset = check.get('initial_dataset', None)
        if self.initial_dataset is not None:
            data = read_json(self.initial_dataset)
            self.vals.extend(
                [self.measurable.extract_val_from_training_data(x) for x in data]
            )
            if self.label_measurable is not None:
                self.labels.extend(
                    [self.label_measurable.extract_val_from_training_data(x) for x in data]
                )


    def check(self, inputs, outputs, gts=None, extra_args={}):
        if self.measurable is not None:
            vals = self.measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            self.vals.extend(vals)
            if self.label_measurable is not None:
                labels = self.label_measurable.compute_and_log(
                    inputs, outputs, gts=gts, extra=extra_args
                )
                self.labels.extend(labels)

        self.total_count += 1
        if not (self.total_count % self.umap_update_freq == 0):
            return

        for count in self.count_checkpoints:
            emb_list = np.array(self.get_data_for_umap(count))

            if emb_list.shape[0] > 10:
                # emb_list = np.squeeze(np.array(list(data_dict.values())))
                umap_list, clusters = self.get_umap_and_labels(
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
                    "umap_and_clusters",
                    this_data,
                    self.dashboard_name,
                    count,
                )

    def get_data_for_umap(self, count):
        if self.measurable is None:
            distribution_anomaly = list(
                filter(
                    lambda x: x.statistic_type == Statistic.DISTRIBUTION_STATS,
                    self.framework.check_manager.statistics_to_check,
                )
            )[0]
            return distribution_anomaly.get_feats_for_clustering(count)
        else:
            return self.vals

    def get_umap_and_labels(
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

        umap_embeddings = umap.UMAP(
            n_neighbors=n_neighbors,
            n_components=n_components,
            min_dist=min_dist,
            metric=metric,
        ).fit_transform(emb_list)

        # Do DBSCAN clustering
        if self.do_clustering:
            clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(umap_embeddings)
            labels = clustering.labels_
        else:
            labels = self.labels
        return umap_embeddings, labels
