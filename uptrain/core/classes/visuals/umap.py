import umap
import copy
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
        self.allowed_model_values = [x['allowed_values'] for x in check['model_args']]
        self.num_model_options = sum([len(x) > 1 for x in self.allowed_model_values])
        self.children = []

        if self.num_model_options > 0:
            for m in self.allowed_model_values[0]:
                check_copy = copy.deepcopy(check)
                check_copy['model_args'][0]['allowed_values'] = [m]
                check_copy['model_args'].append(copy.deepcopy(check_copy['model_args'][0]))
                del check_copy['model_args'][0]
                self.children.append(Umap(fw, check_copy))
        else:
            self.framework = fw
            self.log_handler = fw.log_handler
            self.log_handler.add_writer(self.dashboard_name)
            self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
            self.aggregate_measurable = MeasurableResolver(check["aggregate_args"]).resolve(
                fw
            )
            self.feature_measurables = [
                MeasurableResolver(x).resolve(fw) for x in check.get("feature_args", [])
            ]
            self.model_measurables = [
                MeasurableResolver(x).resolve(fw) for x in check.get("model_args", [])
            ]
            self.label_measurable = MeasurableResolver(check.get("label_args", None)).resolve(
                fw
            )
            self.model_names = [x.col_name() for x in self.model_measurables]
            self.feature_names = [x.col_name() for x in self.feature_measurables]

            self.count_checkpoints = check.get("count_checkpoints", ["all"])
            self.min_dist = check["min_dist"]
            self.n_neighbors = check["n_neighbors"]
            self.metric_umap = check["metric_umap"]
            self.dim = check.get("dim", '2D')
            self.clustering = check.get("clustering", False)
            self.min_samples = check.get("min_samples", 5)
            self.eps = check.get("eps", 2.0)
            self.total_count = 0
            self.prev_calc_at = 0
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
        if len(self.children) > 0:
            [x.check(inputs, outputs, gts, extra_args) for x in self.children]
        else:
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

            self.total_count += len(extra_args['id'])
            if not ((self.total_count - self.prev_calc_at) > self.umap_update_freq):
                return

            self.prev_calc_at = self.total_count
            models = dict(zip(['model_' + x for x in self.model_names], 
                [self.allowed_model_values[jdx][0] for jdx in range(len(self.model_names))]))
            for count in self.count_checkpoints:
                emb_list = np.array(self.get_data_for_umap(count))

                if emb_list.shape[0] > 10:
                    clusters = []
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
                        models = models,
                        file_name = str(count) + "_" + '_'.join(list(models.values()))
                    )


    def get_data_for_umap(self, count):
        if self.measurable is None:
            distribution_anomaly = list(
                filter(
                    lambda x: x.statistic_type == Statistic.DISTRIBUTION_STATS,
                    self.framework.check_manager.statistics_to_check,
                )
            )[0]
            data_dict = distribution_anomaly.get_feats_for_clustering(count, self.allowed_model_values)
            return data_dict.values()
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
