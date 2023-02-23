import numpy as np
import copy

from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.constants import Anomaly
from uptrain.core.lib.helper_funcs import read_json
from uptrain.core.lib.algorithms import estimate_earth_moving_cost
from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.core.classes.algorithms import Clustering

class DataDrift(AbstractAnomaly):
    dashboard_name = "data_drift"
    anomaly_type = Anomaly.DATA_DRIFT
    is_embedding = None
    mode = None
    NUM_BUCKETS = 20
    INITIAL_SKIP = 2000

    def __init__(self, fw, check, is_embedding=None):
        self.measurable = None
        self.measurable = MeasurableResolver(check["measurable_args"]).resolve(fw)
        self.is_embedding = is_embedding
        if self.is_embedding == None:
            self.embedding_child_class = DataDrift(fw, check, is_embedding=True)
            self.scalar_child_class = DataDrift(fw, check, is_embedding=False)
        else:
            self.log_handler = fw.log_handler
            self.reference_dataset = check["reference_dataset"]
            self.cluster_plot_func = fw.dataset_handler.cluster_plot_func
            self.save_edge_cases = check.get("save_edge_cases", True)
            self.NUM_BUCKETS = check.get("num_buckets", self.NUM_BUCKETS)
            self.INITIAL_SKIP = check.get("initial_skip", self.INITIAL_SKIP)
            self.count = 0
            self.prod_dist_counts_arr = []
            clustering_args = {
                "num_buckets": self.NUM_BUCKETS,
                'is_embedding': self.is_embedding,
                'plot_save_name': "training_dataset_clusters.png",
                'cluster_plot_func': self.cluster_plot_func
            }
            self.clustering_helper = Clustering(clustering_args)
            if self.is_embedding:
                self.plot_name = "Embeddings_" + self.measurable.col_name()
                self.emd_threshold = check.get("emd_threshold", 1)
            else:
                self.plot_name = "Scalar_" + self.measurable.col_name()
            self.bucket_reference_dataset()

    def need_ground_truth(self):
        return False

    def check(self, inputs, outputs, gts=None, extra_args={}):
        if self.is_embedding == None:
            if self.mode == "check_both":
                self.embedding_child_class.check(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
                self.scalar_child_class.check(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
            elif self.mode == "check_scalar_only":
                self.scalar_child_class.check(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
            elif self.mode == "check_embeddings_only":
                self.scalar_child_class.check(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
            else:
                feats = self.measurable.compute_and_log(
                    inputs=inputs, outputs=outputs, gts=gts, extra=extra_args
                )
                if len(list(feats.shape)) > 2:
                    self.mode = "check_both"
                else:
                    self.mode = "check_scalar_only"
                self.check(inputs, outputs, gts=gts, extra_args=extra_args)
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

            self.this_datapoint_cluster, self.prod_dist_counts = self.clustering_helper.infer_cluster_assignment(self.feats, self.prod_dist_counts)
            self.prod_dist_counts_arr.append(self.prod_dist_counts.copy())

            self.prod_dist = (
                self.prod_dist_counts_arr[-1]
                - self.prod_dist_counts_arr[
                    int(max(self.count - self.INITIAL_SKIP, 0) / len(extra_args["id"]))
                ]
            ) / min(self.count, self.INITIAL_SKIP)

            if self.ref_dist.shape[0] == 1:
                if self.is_embedding:
                    bar_graph_buckets = ["cluster_" + str(idx) for idx in range(len(list(np.reshape(self.clusters,-1))))]
                else:
                    bar_graph_buckets = list(np.reshape(self.clusters,-1))

                self.log_handler.add_bar_graphs(
                    self.plot_name,
                    {
                        "reference": dict(zip(bar_graph_buckets, list(np.reshape(np.array(self.ref_dist[0]), -1)))),
                        "production": dict(zip(bar_graph_buckets, list(np.reshape(np.array(self.prod_dist[0]), -1)))),
                    },
                    self.dashboard_name,
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
                        drift_detected = drift_detected or (self.costs[idx] > self.emd_threshold)
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
                    alert = "Data Drift last detected at " + str(self.count) + " for Embeddings with Earth moving distance = " + str(float(self.costs[0]))
                    self.log_handler.add_alert(
                        "Data Drift Alert 🚨",
                        alert,
                        self.dashboard_name
                    )

            if self.is_embedding:
                dict_emc = dict(
                    zip(
                        ["y_" + self.measurable.col_name() for x in range(self.costs.shape[0])],
                        [float(x) for x in list(self.costs)],
                    )
                )
                dict_emc.update({"threshold": self.emd_threshold})
                self.log_handler.add_scalars(
                    self.measurable.col_name() + " - earth_moving_costs_embedding",
                    dict_emc,
                    self.count,
                    self.dashboard_name,
                )
            else:
                dict_psi = dict(
                    zip(
                        ["y_" + self.measurable.col_name() + "_" + str(x) for x in range(self.psis.shape[0])],
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

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        if self.is_embedding == None:
            if self.mode == "check_both":
                arr1 = self.embedding_child_class.is_data_interesting(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
                arr2 = self.scalar_child_class.is_data_interesting(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
                return np.logical_or(np.array(arr1), np.array(arr2))
            elif self.mode == "check_scalar_only":
                return self.scalar_child_class.is_data_interesting(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
            elif self.mode == "check_embeddings_only":
                return self.scalar_child_class.is_data_interesting(
                    inputs, outputs, gts=gts, extra_args=extra_args
                )
            else:
                raise Exception("Mode for data drift should be set in check func")
        else:
            is_interesting = np.array([False] * len(extra_args["id"]))
            if self.save_edge_cases and self.drift_detected and not isinstance(self.feats[0,0,0], str):
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
            return is_interesting


    def bucket_reference_dataset(self):
        self.ref_dist = []
        self.prod_dist = []
        self.ref_dist_counts = []
        self.prod_dist_counts = []
        data = read_json(self.reference_dataset)
        all_inputs = np.array(
            [self.measurable.extract_val_from_training_data(x) for x in data]
        )
        all_inputs_shape = list(all_inputs.shape)
        if len(all_inputs_shape) == 1:
            all_inputs_shape.insert(1, 1)
            all_inputs = np.reshape(all_inputs, all_inputs_shape)

        clustering_results = self.clustering_helper.cluster_data(all_inputs)

        self.buckets = np.array(clustering_results['buckets'])
        self.clusters = np.array(clustering_results['clusters'])
        self.cluster_vars = np.array(clustering_results['cluster_vars'])

        self.ref_dist = np.array(clustering_results['dist'])
        self.ref_dist_counts = np.array(clustering_results['dist_counts'])
        self.max_along_axis = clustering_results['max_along_axis']

        self.prod_dist = np.zeros((1, self.NUM_BUCKETS))
        self.prod_dist_counts = np.zeros((1, self.NUM_BUCKETS))

        self.prod_dist_counts_arr.append(copy.deepcopy(self.prod_dist_counts))