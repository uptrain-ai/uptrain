import numpy as np

from uptrain.core.classes.algorithms.clustering import Clustering


def test_bucket_scalar():
    """Test that the scalar bucketing algorithm works correctly.

    The test passes if the scalar bucketing algorithm works correctly and produces
    the expected results for `buckets`, `clusters`, and `cluster_vars`.
    """

    c = Clustering({"num_buckets": 3, "is_embedding": False})
    data = np.array([2, 4, 5, 6, 8, 9])
    buckets, clusters, cluster_vars = c.bucket_scalar(data)

    assert np.allclose(buckets, np.array([2, 5, 8]))
    assert np.allclose(clusters, np.array([[3], [5.5], [8.5]]))
    assert np.allclose(cluster_vars, np.array([[1], [0.25], [0.25]]))


def test_bucket_vector():
    """Test that the vector bucketing algorithm works correctly.

    The test passes if the vector bucketing algorithm works correctly and produces
    the expected results for `buckets`, `clusters`, and `cluster_vars`.
    """

    c = Clustering({"num_buckets": 2, "is_embedding": True})
    data = np.array([[1, 2], [2, 1], [5, 6], [7, 8], [6, 6]])
    c.bucket_vector(data)

    assert np.allclose(
        c.buckets, np.array([[0.857143, 0.833334], [0.214285, 0.187500]]), rtol=1e-4
    )
    assert np.allclose(
        c.clusters, np.array([[0.857143, 0.833334], [0.214285, 0.187500]]), rtol=1e-4
    )
    assert np.allclose(c.cluster_vars, np.array([[0.206349, 0.133928]]), rtol=1e-4)


def test_cluster_data():
    """Test that the clustering algorithm works correctly.

    The test passes if the clustering algorithm works correctly and produces
    the expected results for `buckets`, `clusters`, `cluster_vars`, `dist_counts`
    and `max_along_axis`.
    """
    c = Clustering({"num_buckets": 2, "is_embedding": True})
    data = np.array([[1, 2], [2, 1], [5, 6], [7, 8], [6, 6]])
    clustering_results = c.cluster_data(data)

    assert np.allclose(
        clustering_results["buckets"],
        np.array([[0.857143, 0.833334], [0.214285, 0.187500]]),
        rtol=1e-4,
    )
    assert np.allclose(
        clustering_results["clusters"],
        np.array([[0.857143, 0.833334], [0.214285, 0.187500]]),
        rtol=1e-4,
    )
    assert np.allclose(
        clustering_results["cluster_vars"], np.array([[0.206349, 0.133928]]), rtol=1e-4
    )
    assert np.array_equal(clustering_results["dist_counts"], np.array([[3, 2]]))
    assert np.array_equal(clustering_results["max_along_axis"], np.array([7, 8]))
