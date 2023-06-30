import numpy as np

from typing import Any, List, Tuple, Union

from uptrain.v0.core.lib.helper_funcs import cluster_and_plot_data


class Clustering:
    def __init__(self, args) -> None:
        """
        Initializes the Clustering object with the specified arguments.

        Parameters
        ----------
        args
            A dictionary containing the following keys:
                - num_buckets: the number of buckets to use when clustering
                - is_embedding: a boolean indicating whether the data is an embedding
                - plot_save_name: a string indicating the name of the plot file to save
                - cluster_plot_func: a function that can be used to plot the clustering results
        """

        self.NUM_BUCKETS = args["num_buckets"]
        self.is_embedding = args["is_embedding"]
        self.plot_save_name = args.get("plot_save_name", "")
        self.cluster_plot_func = args.get("cluster_plot_func", None)
        self.find_low_density_regions = args.get("find_low_density_regions", False)
        self.dist = []
        self.dist_counts = []
        self.max_along_axis = []
        self.low_density_regions = []
        self.idxs_closest_to_cluster_centroids = {}

    def cluster_data(self, data: np.ndarray) -> dict:
        """
        Clusters the specified data and returns the results.

        Parameters
        ----------
        data
            The data to be clustered.

        Returns
        -------
        dict
            A dictionary containing the following keys:
                - buckets: the bucket assignments for each data point
                - clusters: the cluster assignments for each data point
                - cluster_vars: the cluster variances for each bucket
                - dist: the distance matrix between each pair of buckets
                - dist_counts: the number of points in each pair of buckets
                - max_along_axis: the maximum value along each axis
                - low_density_regions: the low density regions of the data
                - idxs_closest_to_cluster_centroids: the indices of the data points closest to each cluster centroid
        """

        if self.is_embedding:
            self.bucket_vector(data)
        else:
            buckets = []
            clusters = []
            cluster_vars = []
            for idx in range(data.shape[1]):
                this_inputs = data[:, idx]
                this_buckets, this_clusters, this_cluster_vars = self.bucket_scalar(
                    this_inputs
                )
                buckets.append(this_buckets)
                clusters.append(this_clusters)
                cluster_vars.append(this_cluster_vars)
            self.buckets = np.array(buckets)
            self.clusters = np.array(clusters)
            self.cluster_vars = np.array(cluster_vars)

        self.dist = np.array(self.dist)
        self.dist_counts = np.array(self.dist_counts)

        clustering_results = {
            "buckets": self.buckets,
            "clusters": self.clusters,
            "cluster_vars": self.cluster_vars,
            "dist": self.dist,
            "dist_counts": self.dist_counts,
            "max_along_axis": self.max_along_axis,
            "low_density_regions": self.low_density_regions,
            "idxs_closest_to_cluster_centroids": self.idxs_closest_to_cluster_centroids,
        }

        return clustering_results

    def bucket_scalar(
        self, arr: Union[List[Any], np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Buckets a one-dimensional array.

        Parameters
        ----------
        arr
            The array to be bucketed.

        Returns
        -------
        tuple
            A tuple containing the following elements:
                - buckets: the bucket assignments for each data point
                - clusters: the cluster assignments for each data point
                - cluster_vars: the cluster variances for each bucket
        """

        if isinstance(arr[0], str):
            uniques, counts = np.unique(np.array(arr), return_counts=True)
            buckets = uniques
            self.NUM_BUCKETS = len(buckets)
            clusters = uniques
            cluster_vars = [None] * self.NUM_BUCKETS
            self.ref_dist.append(
                [[counts[x] / len(arr)] for x in range(self.NUM_BUCKETS)]
            )
            self.ref_dist_counts.append([[counts[x]] for x in range(self.NUM_BUCKETS)])
        else:
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

        self.dist.append([[1 / self.NUM_BUCKETS] for x in range(self.NUM_BUCKETS)])
        self.dist_counts.append(
            [[int(len(sorted_arr) / self.NUM_BUCKETS)] for x in range(self.NUM_BUCKETS)]
        )
        return np.array(buckets), np.array(clusters), np.array(cluster_vars)

    def bucket_vector(self, data: np.ndarray) -> None:
        """
        This function takes in an array of vectors and performs bucketing on the data.

        Parameters
        ----------
        data
            A 2D numpy array where each row is a vector to be bucketed.
        """
        abs_data = np.abs(data)
        self.max_along_axis = np.max(abs_data, axis=0)
        data = data / self.max_along_axis

        (
            all_clusters,
            counts,
            cluster_vars,
            density_around_points,
            idxs_closest_to_cluster_centroids,
        ) = cluster_and_plot_data(
            data,
            self.NUM_BUCKETS,
            cluster_plot_func=self.cluster_plot_func,
            plot_save_name=self.plot_save_name,
            normalisation=self.max_along_axis,
            compute_point_density=self.find_low_density_regions
        )


        self.clusters = np.array([all_clusters])
        self.cluster_vars = np.array([cluster_vars])
        self.buckets = self.clusters

        if self.find_low_density_regions:
            low_density_regions = data[
                np.where(
                    density_around_points < np.ceil(len(density_around_points) * 0.002)
                )[0]
            ]
            self.low_density_regions = low_density_regions

        self.density_around_points = density_around_points
        self.idxs_closest_to_cluster_centroids = idxs_closest_to_cluster_centroids

        self.dist_counts = np.array([counts])
        self.dist = self.dist_counts / data.shape[0]

    def infer_cluster_assignment(
        self, feats: np.ndarray, prod_dist_counts: np.ndarray = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Infers the cluster assignments for the given input features.

        Parameters
        ----------
        feats
            The input features for which the cluster assignments are to be inferred.
        prod_dist_counts
            A matrix containing the product of the pairwise distances between each pair
            of buckets and the number of points in each pair of buckets, by default None.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            A tuple containing the inferred cluster assignments for the input features
            and the updated matrix of product of pairwise distances between each pair
            of buckets and number of points in each pair of buckets.
        """

        if prod_dist_counts is None:
            prod_dist_counts = np.zeros((feats.shape[1], self.NUM_BUCKETS))

        if self.is_embedding:
            selected_cluster = np.argmin(
                np.sum(
                    np.abs(self.clusters[0] - feats),
                    axis=tuple(range(2, len(feats.shape))),
                ),
                axis=1,
            )
            for clus in selected_cluster:
                prod_dist_counts[0][clus] += 1
            this_datapoint_cluster = selected_cluster
        else:
            this_datapoint_cluster = []
            for idx in range(feats.shape[2]):
                if isinstance(feats[0, 0, idx], str):
                    try:
                        bucket_idx = np.array(
                            [
                                list(self.buckets[idx]).index(feats[x, 0, idx])
                                for x in range(feats.shape[0])
                            ]
                        )
                    except:
                        # TODO: This logic is not completely tested yet. Contact us if you are facing issues
                        # If given data-point is not present -> add a new bucket
                        temp_buckets = list(self.buckets[idx])
                        num_added = 0

                        for x in range(feats.shape[0]):
                            if feats[x, 0, idx] not in temp_buckets:
                                temp_buckets.append(feats[x, 0, idx])
                                num_added += 1

                        self.buckets[idx] = np.array(temp_buckets)
                        bucket_idx = np.array(
                            [
                                list(self.buckets[idx]).index(feats[x, 0, idx])
                                for x in range(feats.shape[0])
                            ]
                        )
                else:
                    bucket_idx = np.searchsorted(self.buckets[idx], feats[:, :, idx])[
                        :, 0
                    ]
                this_datapoint_cluster.append(bucket_idx)
                for clus in bucket_idx:
                    prod_dist_counts[idx][clus] += 1
            this_datapoint_cluster = np.array(this_datapoint_cluster)
        return this_datapoint_cluster, prod_dist_counts
