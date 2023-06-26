import numpy as np
import copy
import pandas as pd

from uptrain.v0.core.classes.monitors import AbstractMonitor
from uptrain.v0.constants import Monitor
from uptrain.v0.core.lib.helper_funcs import read_json
from uptrain.v0.core.lib.algorithms import estimate_earth_moving_cost
from uptrain.v0.core.classes.measurables import MeasurableResolver
from uptrain.v0.core.classes.algorithms import Clustering


class DataDrift(AbstractMonitor):
    dashboard_name = "data_drift"
    monitor_type = Monitor.DATA_DRIFT
    is_embedding = None
    mode = None
    NUM_BUCKETS = 20
    INITIAL_SKIP = 2000

    def model_choices(self, check):
        self.is_embedding = check.get("is_embedding", None)
        if self.is_embedding == None:
            return [{"is_embedding": False}, {"is_embedding": True}]
        else:
            return [{"is_embedding": check["is_embedding"]}]

    def base_init(self, fw, check):
        self.reference_dataset = check["reference_dataset"]
        self.cluster_plot_func = fw.dataset_handler.cluster_plot_func
        self.save_edge_cases = check.get("save_edge_cases", True)
        self.NUM_BUCKETS = check.get("num_buckets", self.NUM_BUCKETS)

        # Also the step in calculating drift
        self.INITIAL_SKIP = check.get("initial_skip", self.INITIAL_SKIP)
        self.outlier_idxs = check.get("outlier_idxs", [])
        self.do_low_density_check = check.get("do_low_density_check", False)
        self.hover_measurable = MeasurableResolver(
            check.get("hover_label_args", None)
        ).resolve(fw)
        self.count = 0
        self.bucket_labelling_info = {
            "latest_idxs_added_to_clusters": np.array([None] * self.NUM_BUCKETS),
            "idxs_closest_to_clusters": np.array([None] * self.NUM_BUCKETS),
            "closest_idxs_distance": np.array([None] * self.NUM_BUCKETS),
            "hover_vals_for_reference_clusters": np.array([" "] * self.NUM_BUCKETS),
            "hover_vals_for_production_clusters": np.array([" "] * self.NUM_BUCKETS),
        }
        self.prod_dist_counts_arr = []
        clustering_args = {
            "num_buckets": self.NUM_BUCKETS,
            "is_embedding": self.is_embedding,
            "plot_save_name": self.log_handler.get_plot_save_name(
                "training_dataset_clusters.png", self.dashboard_name
            ),
            "cluster_plot_func": self.cluster_plot_func,
            "find_low_density_regions": self.do_low_density_check,
        }
        self.clustering_helper = Clustering(clustering_args)
        if self.is_embedding:
            self.plot_name = "Embeddings_" + self.measurable.col_name()
            self.emd_threshold = check.get("emd_threshold", 1)
        else:
            self.plot_name = "Scalar_" + self.measurable.col_name()
        self.bucket_reference_dataset()
        self.outliers = check.get("outlier_data", [])
        if len(self.outliers):
            self.outliers = np.array(self.outliers) / self.max_along_axis

    def need_ground_truth(self):
        return False

    def check(self, inputs, outputs, gts=None, extra_args={}):
        if len(self.children) > 0:
            feats = self.measurable.compute_and_log(
                inputs=inputs, outputs=outputs, gts=gts, extra=extra_args
            )
            if sum(list(feats.shape)[1:]) / max(1, len(list(feats.shape)[1:])) <= 1:
                self.children = [self.children[0]]
            [
                x.check(inputs, outputs, gts=gts, extra_args=extra_args)
                for x in self.children
            ]
        else:
            self.count += len(extra_args["id"])

            self.feats = self.measurable.compute_and_log(
                inputs=inputs, outputs=outputs, gts=gts, extra=extra_args
            )
            feats_shape = list(self.feats.shape)
            feats_shape.insert(1, 1)
            if len(feats_shape) == 2:
                feats_shape.insert(2, 1)
            self.feats = np.reshape(self.feats, tuple(feats_shape))

            if self.is_embedding:
                self.feats = self.feats / np.expand_dims(self.max_along_axis, 0)

            (
                self.this_datapoint_cluster,
                self.prod_dist_counts,
            ) = self.clustering_helper.infer_cluster_assignment(
                self.feats, self.prod_dist_counts
            )
            # TODO: Extend for feature-wise clusters
            if (self.hover_measurable is not None) and self.is_embedding:
                hover_measurable_vals = np.array(
                    self.hover_measurable.compute_and_log(
                        inputs=inputs, outputs=outputs, gts=gts, extra=extra_args
                    )
                )
                uniq_clusters, uniq_indexs = np.unique(
                    self.this_datapoint_cluster, return_index=True
                )
                query_indexs = np.zeros(self.NUM_BUCKETS)
                self.bucket_labelling_info["latest_idxs_added_to_clusters"][
                    uniq_clusters
                ] = uniq_indexs
                query_indexs[uniq_clusters] = uniq_indexs
                query_indexs = np.array(query_indexs, dtype=int)
                self.bucket_labelling_info[
                    "hover_vals_for_production_clusters"
                ] = hover_measurable_vals[query_indexs]

            self.prod_dist_counts_arr.append(self.prod_dist_counts.copy())

            self.prod_dist = (
                self.prod_dist_counts_arr[-1]
                - self.prod_dist_counts_arr[
                    int(max(self.count - self.INITIAL_SKIP, 0) / len(extra_args["id"]))
                ]
            ) / min(self.count, self.INITIAL_SKIP)

            if self.ref_dist.shape[0] == 1:
                if self.is_embedding:
                    bar_graph_buckets = [
                        "cluster_" + str(idx)
                        for idx in range(len(list(np.reshape(self.clusters, -1))))
                    ]
                else:
                    bar_graph_buckets = list(np.reshape(self.clusters, -1))

                self.log_handler.add_bar_graphs(
                    self.plot_name,
                    {
                        "reference": dict(
                            zip(
                                bar_graph_buckets,
                                list(np.reshape(np.array(self.ref_dist[0]), -1)),
                            )
                        ),
                        "production": dict(
                            zip(
                                bar_graph_buckets,
                                list(np.reshape(np.array(self.prod_dist[0]), -1)),
                            )
                        ),
                    },
                    self.dashboard_name,
                    hover_data={
                        "reference": dict(
                            zip(
                                bar_graph_buckets,
                                list(
                                    self.bucket_labelling_info[
                                        "hover_vals_for_reference_clusters"
                                    ]
                                ),
                            )
                        ),
                        "production": dict(
                            zip(
                                bar_graph_buckets,
                                list(
                                    self.bucket_labelling_info[
                                        "hover_vals_for_production_clusters"
                                    ]
                                ),
                            )
                        ),
                    },
                )

            if self.count < self.INITIAL_SKIP:
                self.drift_detected = False
                return
            else:
                self.psis = np.zeros(self.ref_dist.shape[0])
                self.costs = np.zeros(self.ref_dist.shape[0])
                drift_detected = False
                for idx in range(self.ref_dist.shape[0]):
                    if self.is_embedding:
                        self.costs[idx] = estimate_earth_moving_cost(
                            self.prod_dist[idx], self.ref_dist[idx], self.clusters[idx]
                        )
                        drift_detected = drift_detected or (
                            self.costs[idx] > self.emd_threshold
                        )
                    else:
                        this_psi = sum(
                            [
                                (self.prod_dist[idx][jdx] - self.ref_dist[idx][jdx])
                                * np.log(
                                    max(self.prod_dist[idx][jdx], 0.0001)
                                    / self.ref_dist[idx][jdx]
                                )
                                for jdx in range(self.ref_dist.shape[1])
                            ]
                        )
                        self.psis[idx] = this_psi
                        drift_detected = drift_detected or (this_psi > 0.3)
                self.drift_detected = drift_detected
                if self.drift_detected:
                    alert = (
                        "Data Drift last detected at "
                        + str(self.count)
                        + " for Embeddings with Earth moving distance = "
                        + str(float(self.costs[0]))
                    )
                    self.log_handler.add_alert(
                        "Data Drift Alert 🚨", alert, self.dashboard_name
                    )

            if self.is_embedding:
                dict_emc = dict(
                    zip(
                        [
                            "y_" + self.measurable.col_name()
                            for x in range(self.costs.shape[0])
                        ],
                        [float(x) for x in list(self.costs)],
                    )
                )
                # dict_emc.update({"threshold": self.emd_threshold})
                self.log_handler.add_scalars(
                    self.measurable.col_name() + " - earth_moving_costs",
                    dict_emc,
                    self.count,
                    self.dashboard_name,
                    file_name="embeddings",
                )
                self.log_handler.add_scalars(
                    self.measurable.col_name() + " - earth_moving_costs",
                    {list(dict_emc.keys())[0]: self.emd_threshold},
                    self.count,
                    self.dashboard_name,
                    file_name="threshold",
                )
            else:
                dict_psi = dict(
                    zip(
                        [
                            "y_" + self.measurable.col_name() + "_" + str(x)
                            for x in range(self.psis.shape[0])
                        ],
                        [float(x) for x in list(self.psis)],
                    )
                )
                dict_psi.update({"threshold": 0.3})
                self.log_handler.add_scalars(
                    self.measurable.col_name() + " - population_stability_index_scalar",
                    dict_psi,
                    self.count,
                    self.dashboard_name,
                )

    def base_is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        is_interesting = np.array([False] * len(extra_args["id"]))
        reasons = ["None"] * len(extra_args["id"])

        if self.do_low_density_check and (len(self.low_density_regions) > 0):
            dists_from_low_density_regions = np.min(
                np.sum(
                    np.abs(
                        self.feats - np.expand_dims(self.low_density_regions, axis=0)
                    ),
                    axis=2,
                ),
                axis=1,
            )
            min_cluster_var = np.min(self.cluster_vars)
            is_close = dists_from_low_density_regions < min_cluster_var
            is_interesting = np.logical_or(is_close, is_interesting)
            for lkdx in range(len(is_close)):
                if is_close[lkdx]:
                    reasons[
                        lkdx
                    ] = "Lies_to_Low_Density_Regions_In_Training_Distribution"

        if len(self.outliers):
            dists_from_outliers = np.min(
                np.sum(
                    np.abs(self.feats - np.expand_dims(self.outliers, axis=0)), axis=2
                ),
                axis=1,
            )
            min_cluster_var = np.min(self.cluster_vars)
            is_close = dists_from_outliers < 0.5 * min_cluster_var
            is_interesting = np.logical_or(is_close, is_interesting)
            for lkdx in range(len(is_close)):
                if is_close[lkdx]:
                    if dists_from_outliers[lkdx] < 0.0000001:
                        reasons[lkdx] = "Outlier_annotated_by_the_user"
                    else:
                        reasons[lkdx] = "Close_to_User_annotated_Outliers"

        if (
            self.save_edge_cases
            and self.drift_detected
            and not isinstance(self.feats[0, 0, 0], str)
        ):
            feats_shape = list(self.feats.shape)
            del feats_shape[1]
            self.feats = np.reshape(self.feats, tuple(feats_shape))
            for idx in range(self.ref_dist.shape[0]):
                if self.is_embedding:
                    dist_from_cluster = (
                        np.sum(
                            np.abs(
                                self.clusters[idx][self.this_datapoint_cluster]
                                - self.feats
                            ),
                            axis=tuple(range(1, len(feats_shape))),
                        )
                        / self.cluster_vars[idx][self.this_datapoint_cluster]
                    )
                else:
                    dist_from_cluster = np.abs(
                        np.reshape(
                            self.clusters[idx][self.this_datapoint_cluster[idx]], -1
                        )
                        - self.feats[:, idx]
                    ) / np.reshape(
                        self.cluster_vars[idx][self.this_datapoint_cluster[idx]], -1
                    )
                for jdx in range(dist_from_cluster.shape[0]):
                    if dist_from_cluster[jdx] > 2:
                        if self.is_embedding:
                            min_dist_from_clusters = np.min(
                                np.sum(
                                    np.abs(self.clusters[idx] - self.feats[jdx]),
                                    axis=tuple(range(1, len(feats_shape))),
                                )
                                / self.cluster_vars[idx]
                            )
                        else:
                            min_dist_from_clusters = np.min(
                                np.abs(
                                    np.reshape(self.clusters[idx], -1)
                                    - self.feats[jdx, idx]
                                )
                                / np.reshape(self.cluster_vars[idx], -1)
                            )
                        is_interesting[jdx] = is_interesting[jdx] or (
                            min_dist_from_clusters > 1
                        )
                        if min_dist_from_clusters > 1:
                            reasons[jdx] = "Away_from_all_training_clusters"

        return is_interesting, reasons

    def bucket_reference_dataset(self):
        self.ref_dist = []
        self.prod_dist = []
        self.ref_dist_counts = []
        self.prod_dist_counts = []
        if self.reference_dataset.split(".")[-1] == "json":
            data = read_json(self.reference_dataset)
            all_inputs = np.array(
                [self.measurable.extract_val_from_training_data(x) for x in data]
            )
        elif self.reference_dataset.split(".")[-1] == "csv":
            data = pd.read_csv(self.reference_dataset).to_dict()
            for key in data:
                data[key] = list(data[key].values())
            all_inputs = np.array(self.measurable.extract_val_from_training_data(data))
        else:
            raise Exception("Reference data file type not recognized.")

        all_inputs_shape = list(all_inputs.shape)
        if len(all_inputs_shape) == 1:
            all_inputs_shape.insert(1, 1)
            all_inputs = np.reshape(all_inputs, all_inputs_shape)

        clustering_results = self.clustering_helper.cluster_data(all_inputs)

        self.buckets = np.array(clustering_results["buckets"])
        self.clusters = np.array(clustering_results["clusters"])
        self.cluster_vars = np.array(clustering_results["cluster_vars"])

        self.ref_dist = np.array(clustering_results["dist"])
        self.ref_dist_counts = np.array(clustering_results["dist_counts"])
        self.max_along_axis = clustering_results["max_along_axis"]
        self.low_density_regions = clustering_results["low_density_regions"]

        if self.hover_measurable is not None:
            all_hover_vals = np.array(
                [self.hover_measurable.extract_val_from_training_data(x) for x in data]
            )
            hover_label_idxs = [
                x[0]
                for x in list(
                    clustering_results["idxs_closest_to_cluster_centroids"].values()
                )
            ]
            self.bucket_labelling_info[
                "hover_vals_for_reference_clusters"
            ] = all_hover_vals[hover_label_idxs]

        self.prod_dist = np.zeros(self.ref_dist.shape)
        self.prod_dist_counts = np.zeros(self.ref_dist_counts.shape)

        self.prod_dist_counts_arr.append(copy.deepcopy(self.prod_dist_counts))
        if len(self.outlier_idxs):
            self.outliers = all_inputs[np.array(self.outlier_idxs)]
