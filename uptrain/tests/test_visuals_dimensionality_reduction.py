import numpy as np
import uptrain


def test_visuals_dimensionality_reduction():
    """Test Visuals Dimensionality Reduction.
    
    The test creates a dataset with 4 types of data points. Each type is
    represented by a normal distribution with a mean of 0, 1, 2, 3. The data
    points are randomly assigned to one of the 4 types. The test then creates
    a UMAP and TSNE visualisation of the data points in 2D and 3D for both.

    The test passes if the UMAP and TSNE visualisations are created and the
    clusters are clearly visible in the 2D and 3D visualisations.
    """

    random_state = np.random.RandomState(seed=1337)

    # Set the size of the dataset, the number of types and generate the proportions of each type
    n = 200
    type_count = 4
    p = random_state.randn(type_count)
    p /= np.sum(p)
    
    # Randomly assign labels to the data points based on the proportions
    labels = random_state.choice(np.arange(type_count), size=n, p=p)
    data = []

    # Create a dataset based on the randomly assigned labels
    # and random normal distributions
    for label in labels:
        data.append(random_state.normal(np.full(n, label), 1, n))
    
    # Set the parameters for UMAP
    umap_cfg = {
        "type": uptrain.Visual.UMAP,
        "measurable_args": {
            "type": uptrain.MeasurableType.INPUT_FEATURE,
            "feature_name": "data"
        },
        "label_args": {
            "type": uptrain.MeasurableType.INPUT_FEATURE,
            "feature_name": "labels"
        },
        "min_dist": 0.01,
        "n_neighbors": 20,
        "metric": "euclidean",
        "update_freq": 1
    }

    # Set the parameters for t-SNE
    tsne_cfg = {
        "type": uptrain.Visual.TSNE,
        "measurable_args": {
            "type": uptrain.MeasurableType.INPUT_FEATURE,
            "feature_name": "data"
        },
        "label_args": {
            "type": uptrain.MeasurableType.INPUT_FEATURE,
            "feature_name": "labels"
        },
        "update_freq": 1,
        "perplexity": 10
    }

    cfg = {
        "checks": [
            {
                **umap_cfg,
                "dim": "3D",
                "dashboard_name": "umap_3d"
            },
            # {
            #     **umap_cfg,
            #     "dim": "2D",
            #     "dashboard_name": "umap_2d"
            # },
            {
                **tsne_cfg,
                "dim": "3D",
                "dashboard_name": "tsne_3d"
            },
            # {
            #     **tsne_cfg,
            #     "dim": "2D",
            #     "dashboard_name": "tsne_2d"
            # }
        ],

        "logging_args": {
            "log_folder": "uptrain_logs_dimensionality_reduction",
            "st_logging": True
        }
    }

    # Set up the framework using the configurations
    framework = uptrain.Framework(cfg)

    # Log the inputs
    framework.log(inputs = {
        "data": data,
        "labels": labels
    })
