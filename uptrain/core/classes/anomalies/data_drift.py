import numpy as np

from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.constants import Anomaly
from uptrain.core.lib.helper_funcs import read_json, cluster_and_plot_data
from uptrain.core.classes.anomalies.measurables import MeasurableResolver


class DataDrift(AbstractAnomaly):
    dashboard_name = "data_drift"
    anomaly_type = Anomaly.DATA_DRIFT
    is_embedding = None
    mode = None
    NUM_BUCKETS = 20

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
            self.count = 0
            self.prod_dist_counts_arr = []
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
            if self.count == 0:
                self.log_handler.add_writer(self.dashboard_name)

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
                selected_cluster = np.argmin(
                    np.sum(
                        np.abs(self.clusters[0] - self.feats),
                        axis=tuple(range(2, len(feats_shape))),
                    ),
                    axis=1,
                )
                for clus in selected_cluster:
                    self.prod_dist_counts[0][clus] += 1
                self.this_datapoint_cluster = selected_cluster
                self.prod_dist_counts_arr.append(self.prod_dist_counts.copy())
            else:
                this_datapoint_cluster = []
                for idx in range(self.feats.shape[2]):
                    bucket_idx = np.searchsorted(
                        self.buckets[idx], self.feats[:, :, idx]
                    )[:, 0]
                    this_datapoint_cluster.append(bucket_idx)
                    self.prod_dist_counts[idx][bucket_idx] += 1
                self.prod_dist_counts_arr.append(self.prod_dist_counts.copy())
                self.this_datapoint_cluster = np.array(this_datapoint_cluster)

            if self.count < 1000:
                self.drift_detected = False
                return
            else:
                self.prod_dist = (
                    self.prod_dist_counts_arr[-1]
                    - self.prod_dist_counts_arr[
                        int(max(self.count - 2000, 0) / len(extra_args["id"]))
                    ]
                ) / min(self.count, 2000)
                self.psis = np.zeros(self.ref_dist.shape[0])
                self.costs = np.zeros(self.ref_dist.shape[0])
                drift_detected = False
                for idx in range(self.ref_dist.shape[0]):
                    if self.is_embedding:
                        self.costs[idx] = self.estimate_earth_moving_cost(
                            self.prod_dist[idx], self.ref_dist[idx], self.clusters[idx]
                        )
                        drift_detected = drift_detected or (self.costs[idx] > 300)
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

            if self.is_embedding:
                dict_emc = dict(
                    zip(
                        ["feat_" + str(x) for x in range(self.costs.shape[0])],
                        [float(x) for x in list(self.costs)],
                    )
                )
                dict_emc.update({"threshold": 300})
                self.log_handler.add_scalars(
                    self.measurable.col_name() + " - earth_moving_costs_embedding",
                    dict_emc,
                    self.count,
                    self.dashboard_name,
                )
            else:
                dict_psi = dict(
                    zip(
                        ["feat_" + str(x) for x in range(self.psis.shape[0])],
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
            if self.save_edge_cases and self.drift_detected:
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

    def estimate_earth_moving_cost(self, prod_dist, ref_dist, clusters):
        cost = 0
        for jdx in range(self.ref_dist.shape[1]):
            dirt_required = prod_dist[jdx] - ref_dist[jdx]
            dictn = []
            for kdx in range(self.clusters.shape[1]):
                if jdx == kdx:
                    dirt_can_be_transported = 0
                else:
                    dirt_can_be_transported = prod_dist[kdx] - ref_dist[kdx]
                this_dirt = -dirt_can_be_transported
                if this_dirt * dirt_required < 0:
                    cost_per_dirt = 1000000000
                else:
                    cost_per_dirt = np.sum(np.abs(clusters[kdx] - clusters[jdx]))
                dictn.append(
                    {
                        "dirt": np.abs(this_dirt),
                        "idx": kdx,
                        "cost_per_dirt": cost_per_dirt,
                    }
                )
            dictn = sorted(dictn, key=lambda x: x["cost_per_dirt"])
            this_cost = 0
            dirt_required = np.abs(dirt_required)
            for kdx in range(len(dictn)):
                if dirt_required > 0:
                    this_cost += (
                        min(dictn[kdx]["dirt"], dirt_required)
                        * dictn[kdx]["cost_per_dirt"]
                    )
                    dirt_required -= min(dictn[kdx]["dirt"], dirt_required)
                else:
                    break
            cost += this_cost
        return cost

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

        if self.is_embedding:
            self.bucket_vector(all_inputs)
        else:
            buckets = []
            clusters = []
            cluster_vars = []
            for idx in range(all_inputs.shape[1]):
                this_inputs = all_inputs[:, idx]
                this_buckets, this_clusters, this_cluster_vars = self.bucket_scalar(
                    this_inputs
                )
                buckets.append(this_buckets)
                clusters.append(this_clusters)
                cluster_vars.append(this_cluster_vars)
            self.buckets = np.array(buckets)
            self.clusters = np.array(clusters)
            self.cluster_vars = np.array(cluster_vars)

        self.ref_dist = np.array(self.ref_dist)
        self.ref_dist_counts = np.array(self.ref_dist_counts)
        self.prod_dist = np.array(self.prod_dist)
        self.prod_dist_counts = np.array(self.prod_dist_counts)

    def bucket_scalar(self, arr):
        sorted_arr = np.sort(arr)
        buckets = []
        clusters = []
        cluster_vars = []
        for idx in range(0, self.NUM_BUCKETS):
            if idx > 0:
                buckets.append(
                    sorted_arr[int(idx * (len(sorted_arr) - 1) / self.NUM_BUCKETS)]
                )
            this_bucket_elems = sorted_arr[
                int((idx) * (len(sorted_arr) - 1) / self.NUM_BUCKETS) : int(
                    (idx + 1) * (len(sorted_arr) - 1) / self.NUM_BUCKETS
                )
            ]
            gaussian_mean = np.mean(this_bucket_elems)
            gaussian_var = np.var(this_bucket_elems)
            clusters.append([gaussian_mean])
            cluster_vars.append([gaussian_var])

        self.ref_dist.append([[1 / self.NUM_BUCKETS] for x in range(self.NUM_BUCKETS)])
        self.ref_dist_counts.append(
            [[int(len(sorted_arr) / self.NUM_BUCKETS)] for x in range(self.NUM_BUCKETS)]
        )
        self.prod_dist.append([[0] for x in range(self.NUM_BUCKETS)])
        self.prod_dist_counts.append([[0] for x in range(self.NUM_BUCKETS)])
        return np.array(buckets), np.array(clusters), np.array(cluster_vars)

    def bucket_vector(self, data):

        all_clusters, counts, cluster_vars = cluster_and_plot_data(
            data,
            self.NUM_BUCKETS,
            cluster_plot_func=self.cluster_plot_func,
            plot_save_name="training_dataset_clusters.png",
        )

        self.clusters = np.array([all_clusters])
        self.cluster_vars = np.array([cluster_vars])

        self.ref_dist_counts = np.array([counts])
        self.ref_dist = self.ref_dist_counts / data.shape[0]
        self.prod_dist = np.zeros((1, self.NUM_BUCKETS))
        self.prod_dist_counts = np.zeros((1, self.NUM_BUCKETS))
