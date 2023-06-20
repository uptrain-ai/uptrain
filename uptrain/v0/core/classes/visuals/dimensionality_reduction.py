from typing import Optional, Union, TYPE_CHECKING

try:
    import umap
except:
    umap = None
import numpy as np
from sklearn.manifold import TSNE

from uptrain.v0.core.lib.helper_funcs import cluster_and_plot_data
from uptrain.v0.core.classes.visuals import AbstractVisual, ClusteringResolver
from uptrain.v0.constants import Visual, Statistic, MeasurableType, ClusteringAlgorithm
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.core.lib.helper_funcs import read_json, dependency_required

if TYPE_CHECKING:
    from uptrain.v0.core.classes.logging.new_log_handler import (
        LogHandler as NewLogHandler,
        LogWriter,
    )
    from uptrain.v0.core.classes.logging.log_handler import LogHandler


@dependency_required(umap, "umap-learn")
class DimensionalityReduction(AbstractVisual):
    log_handler: Union["LogHandler", "NewLogHandler"]
    log_writer: Optional["LogWriter"]

    def base_init(self, fw, check):
        self.visual_type = check["type"]
        self.dashboard_name = check.get("dashboard_name", "visual")
        if self.visual_type == Visual.UMAP:
            self.umap_init(check)
        elif self.visual_type == Visual.TSNE:
            self.tsne_init(check)
        else:
            raise Exception("Dimensionality reduction type undefined.")
        self.framework = fw
        self.clustering_algorithm = ClusteringResolver(
            check.get("clustering_algorithm", ClusteringAlgorithm.HDBSCAN)
        ).resolve(check.get("clustering_args", {}))
        self.label_measurables = [
            MeasurableResolver(x).resolve(fw) for x in check.get("label_args", [])
        ]
        label_names = [x.col_name() for x in self.label_measurables]
        self.labels = {"clusters": []}
        for label_name in label_names:
            self.labels[label_name] = []
        self.hover_measurables = [
            MeasurableResolver(x).resolve(fw) for x in check.get("hover_args", [])
        ]
        self.hover_names = [x.col_name() for x in self.hover_measurables]
        if "id" not in self.hover_names:
            id_args = {"type": MeasurableType.INPUT_FEATURE, "feature_name": "id"}
            self.hover_measurables.append(MeasurableResolver(id_args).resolve(fw))
            self.hover_names.append("id")
        self.count_checkpoints = check.get("count_checkpoints", ["all"])
        self.dim = check.get("dim", "2D")

        self.total_count = 0
        self.prev_calc_at = 0
        self.update_freq = check.get("update_freq", 10000)
        self.vals = []
        self.hover_texts = []
        self.feature_dictn = {}

        # get handles to the log writer object
        if hasattr(self.log_handler, "make_logger"):
            self.log_writer = self.log_handler.make_logger(
                self.dashboard_name, self.visual_type, fmt="json"
            )
        else:
            self.log_writer = None

        self.initial_dataset = check.get("initial_dataset", None)
        if self.initial_dataset is not None:
            data = read_json(self.initial_dataset)
            self.vals.extend(
                [self.measurable.extract_val_from_training_data(x) for x in data]
            )

            for label_measurable in self.label_measurables:
                label_data = [
                    label_measurable.extract_val_from_training_data(x) for x in data
                ]
                self.labels[label_measurable.col_name()] = label_data
            if len(self.hover_measurables):
                offset = 0
                for data_point in data:
                    this_hovers = [
                        x.extract_val_from_training_data(data_point)
                        for x in self.hover_measurables
                    ]
                    self.hover_texts.append(dict(zip(self.hover_names, this_hovers)))
                    # self.hover_texts[offset].update({"Training Density": int(points_density[offset])})
                    self.hover_texts[offset].update({"idx": offset})
                    offset += 1
            if len(self.feature_measurables):
                all_features = [
                    list(
                        np.reshape(
                            [
                                feature_measurable.extract_val_from_training_data(x)
                                for x in data
                            ],
                            -1,
                        )
                    )
                    for feature_measurable in self.feature_measurables
                ]
                this_dict = dict(
                    zip(["feature_" + x for x in self.feature_names], all_features)
                )
                for key in this_dict.keys():
                    if key in self.feature_dictn:
                        self.feature_dictn[key].extend(this_dict[key])
                    else:
                        self.feature_dictn.update({key: list(this_dict[key])})

    def umap_init(self, check):
        self.min_dist = check.get("min_dist", 0.01)
        self.n_neighbors = check.get("n_neighbors", 20)
        self.metric_umap = check.get("metric", "euclidean")

    def tsne_init(self, check):
        self.perplexity = check.get("perplexity", 30.0)
        self.early_exaggeration = check.get("early_exaggeration", 12.0)
        self.learning_rate = check.get("learning_rate", "auto")
        self.n_iter = check.get("n_iter", 1000)
        self.n_iter_without_progress = check.get("n_iter_without_progress", 300)
        self.min_grad_norm = check.get("min_grad_norm", 1e-7)
        self.metric_tsne = check.get("metric", "euclidean")
        self.metric_params = check.get("metric_params", None)
        self.init = check.get("init", "pca")
        self.verbose = check.get("verbose", 0)
        self.random_state = check.get("random_state", None)
        self.method = check.get("method", "barnes_hut")
        self.angle = check.get("angle", 0.5)
        self.n_jobs = check.get("n_jobs", None)

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        if self.measurable is not None:
            vals = self.measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            self.vals.extend(vals)

        for label_measurable in self.label_measurables:
            label_data = label_measurable.compute_and_log(
                inputs, outputs, gts=gts, extra=extra_args
            )
            self.labels[label_measurable.col_name()].extend(label_data)

        if len(self.feature_measurables):
            all_features = [
                x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
                for x in self.feature_measurables
            ]
            this_dict = dict(
                zip(["feature_" + x for x in self.feature_names], all_features)
            )
            for key in this_dict.keys():
                if key in self.feature_dictn:
                    self.feature_dictn[key].extend(this_dict[key])
                else:
                    self.feature_dictn.update({key: list(this_dict[key])})

        if len(self.hover_measurables):
            hover_values = [
                x.compute_and_log(inputs, outputs, gts=gts, extra=extra_args)
                for x in self.hover_measurables
            ]
            hover_table = np.array(hover_values).transpose()
            self.hover_texts.extend(
                [dict(zip(self.hover_names, values)) for values in hover_table]
            )

        self.total_count += len(extra_args["id"])
        if not ((self.total_count - self.prev_calc_at) >= self.update_freq):
            return

        self.prev_calc_at = self.total_count
        models = dict(
            zip(
                ["model_" + x for x in self.model_names],
                [
                    self.allowed_model_values[jdx][0]
                    for jdx in range(len(self.model_names))
                ],
            )
        )

        for count in self.count_checkpoints:
            emb_list, label_dict, hover_texts = self.get_high_dim_data(count)
            emb_list = np.array(emb_list)

            if emb_list.shape[0] > 10:
                clusters = []
                umap_list, clusters = self.get_embs_and_clusters(emb_list)
                this_data = {"umap": umap_list}
                label_dict["clusters"].extend(clusters)
                this_data.update({"labels": label_dict})
                if len(hover_texts) > 0:
                    this_data.update({"hover_texts": hover_texts})

                if self.log_writer is not None:
                    self.log_writer.log(
                        {
                            "count": str(count),
                            **this_data,
                            **models,
                            **self.feature_dictn,
                        }
                    )
                else:
                    self.log_handler.add_histogram(
                        self.visual_type,
                        this_data,
                        self.dashboard_name,
                        models=models,
                        features=self.feature_dictn,
                        file_name=self.dashboard_name
                        + "_"
                        + str(count)
                        + "_"
                        + "_".join(list(models.values())),
                    )

    def get_high_dim_data(self, count):
        if self.measurable is None:
            distribution_anomaly = list(
                filter(
                    lambda x: x.statistic_type == Statistic.DISTRIBUTION_STATS,
                    self.framework.check_manager.statistics_to_check,
                )
            )[0]
            data_dict = distribution_anomaly.get_feats_for_clustering(
                count, self.allowed_model_values
            )
            chosen_label_key = None
            chosen_hover_key = None
            if len(data_dict):
                temp_val = list(data_dict.values())[0]
                if len(temp_val):
                    temp_keys = list(temp_val.keys())
                    temp_keys = list(filter(lambda x: "visual_label_" in x, temp_keys))
                    if len(temp_keys) > 1:
                        print(
                            "Have multiple labels - "
                            + str(temp_keys)
                            + " .Using "
                            + temp_keys[0]
                            + " for labeling."
                        )
                    if len(temp_keys) > 0:
                        chosen_label_key = temp_keys[0]
                if len(temp_val):
                    temp_keys = list(temp_val.keys())
                    temp_keys = list(
                        filter(lambda x: "visual_hover_text_" in x, temp_keys)
                    )
                    if len(temp_keys) > 1:
                        print(
                            "Have multiple hover texts - "
                            + str(temp_keys)
                            + " .Using "
                            + temp_keys[0]
                            + " for hovering."
                        )
                    if len(temp_keys) > 0:
                        chosen_hover_key = temp_keys[0]
            vals = np.array([data_dict[x]["val"] for x in data_dict])
            if vals.shape[0] > 0:
                vals = np.squeeze(vals, axis=1)
            labels = []
            if chosen_label_key is not None:
                labels = [data_dict[x][chosen_label_key] for x in data_dict]

            hover_texts = []
            if chosen_hover_key is not None:
                hover_texts = [
                    {chosen_hover_key: data_dict[x][chosen_hover_key]}
                    for x in data_dict
                ]
            return vals, labels, hover_texts
        else:
            return self.vals, self.labels, self.hover_texts

    def get_embs_and_clusters(self, emb_list):
        if self.dim == "2D":
            n_components = 2
        else:
            n_components = 3

        if self.visual_type == Visual.UMAP:
            compressed_embeddings = umap.UMAP(
                n_neighbors=self.n_neighbors,
                n_components=n_components,
                min_dist=self.min_dist,
                metric=self.metric_umap,
            ).fit_transform(emb_list)
        elif self.visual_type == Visual.TSNE:
            compressed_embeddings = TSNE(
                n_components=n_components,
                perplexity=self.perplexity,
                early_exaggeration=self.early_exaggeration,
                learning_rate=self.learning_rate,
                n_iter=self.n_iter,
                n_iter_without_progress=self.n_iter_without_progress,
                min_grad_norm=self.min_grad_norm,
                metric=self.metric_tsne,
                init=self.init,
                verbose=self.verbose,
                random_state=self.random_state,
                method=self.method,
                angle=self.angle,
                n_jobs=self.n_jobs,
            ).fit_transform(emb_list)

        clustering = self.clustering_algorithm.fit(compressed_embeddings)
        labels = np.squeeze(np.array(clustering.labels_))
        return compressed_embeddings, labels
