import numpy as np
import pytest
import uptrain.v0 as v0
import json


@pytest.fixture(scope="module")
def random_state():
    return np.random.RandomState(seed=1337)


@pytest.fixture(scope="module")
def random_state2():
    return np.random.RandomState(seed=1000)


@pytest.fixture(scope="module")
def dataset(random_state):
    """Returns a dataset with 4 types of data points."""
    n = 200
    type_count = 4
    p = random_state.randn(type_count)
    p /= np.sum(p)
    labels = random_state.choice(np.arange(type_count), size=n, p=p)
    data = []
    for label in labels:
        data.append(random_state.normal(np.full(n, label), 1, n))
    return data, labels


@pytest.fixture(scope="module")
def dataset2(random_state2):
    """Returns a dataset with 4 types of data points."""
    n = 200
    type_count = 4
    labels = random_state2.choice(np.arange(type_count), size=n).tolist()
    data = []
    for label in labels:
        data.append(random_state2.normal(np.full(n, label), 1, n).tolist())
    return data, labels


@pytest.fixture(scope="module")
def umap_cfg():
    """Returns the parameters for UMAP."""
    return {
        "type": v0.Visual.UMAP,
        "measurable_args": {
            "type": v0.MeasurableType.INPUT_FEATURE,
            "feature_name": "data",
        },
        "label_args": [
            {
                "type": v0.MeasurableType.INPUT_FEATURE,
                "feature_name": "labels",
            }
        ],
        "min_dist": 0.01,
        "n_neighbors": 20,
        "metric": "euclidean",
        "update_freq": 1,
        "clustering_algorithm": v0.ClusteringAlgorithm.HDBSCAN,
    }


@pytest.fixture(scope="module")
def tsne_cfg():
    """Returns the parameters for t-SNE."""
    return {
        "type": v0.Visual.TSNE,
        "measurable_args": {
            "type": v0.MeasurableType.INPUT_FEATURE,
            "feature_name": "data",
        },
        "label_args": [
            {
                "type": v0.MeasurableType.INPUT_FEATURE,
                "feature_name": "labels",
            }
        ],
        "update_freq": 1,
        "perplexity": 10,
        "clustering_algorithm": v0.ClusteringAlgorithm.DBSCAN,
        "clustering_args": {
            "eps": 0.5,
            "min_samples": 5,
            "metric": "euclidean",
            "algorithm": "auto",
            "leaf_size": 30,
            "p": None,
            "n_jobs": None,
        },
    }


@pytest.fixture(scope="module")
def pca_cfg(dataset2):
    data, labels = dataset2
    train_data = []
    for i, d in enumerate(zip(data, labels)):
        train_data.append({"data": d[0], "labels": d[1], "id": i})

    with open("test_data.json", "w") as fp:
        json.dump(train_data, fp)

    """Returns the parameters for PCA."""
    return {
        "type": v0.Visual.PCA,
        "measurable_args": {
            "type": v0.MeasurableType.INPUT_FEATURE,
            "feature_name": "data",
        },
        "label_args": [
            {
                "type": v0.MeasurableType.INPUT_FEATURE,
                "feature_name": "labels",
            }
        ],
        "initial_dataset": "test_data.json",
        "update_freq": 1,
    }


def test_visuals_dimensionality_reduction(dataset, umap_cfg, tsne_cfg, pca_cfg):
    """Test Visuals Dimensionality Reduction.

    The test creates a UMAP and t-SNE visualisation of the data points in 2D
    and 3D. The test passes if the clusters are clearly visible in the visualisations.
    """
    data, labels = dataset

    cfg = {
        "checks": [
            {**umap_cfg, "dim": "3D", "dashboard_name": "umap_3d"},
            {**tsne_cfg, "dim": "3D", "dashboard_name": "tsne_3d"},
            {**pca_cfg, "dim": "3D", "dashboard_name": "pca_3d"},
            # {**umap_cfg, "dim": "2D", "dashboard_name": "umap_2d"},
            # {**tsne_cfg, "dim": "2D", "dashboard_name": "tsne_2d"},
            # {**pca_cfg, "dim": "2D", "dashboard_name": "pca_2d"},
        ],
        "logging_args": {
            "log_folder": "uptrain_logs_dimensionality_reduction_1",
            "st_logging": True,
        },
    }

    # Set up the framework using the configurations
    framework = v0.Framework(cfg)

    # Log the inputs
    framework.log(inputs={"data": data, "labels": labels})


def test_visuals_dimensionality_reduction_new_logging(
    dataset, umap_cfg, tsne_cfg, pca_cfg
):
    data, labels = dataset

    cfg = {
        "checks": [
            {**umap_cfg, "dim": "3D", "dashboard_name": "umap_3d"},
            {**tsne_cfg, "dim": "3D", "dashboard_name": "tsne_3d"},
            {**pca_cfg, "dim": "3D", "dashboard_name": "pca_3d"},
        ],
        "logging_args": {
            "log_folder": "uptrain_logs_dimensionality_reduction_2",
            "use_new_handler": True,
            "run_background_streamlit": False,
        },
    }

    # Set up the framework using the configurations
    framework = v0.Framework(cfg)

    # Log the inputs
    _ = framework.log(inputs={"data": data, "labels": labels})
