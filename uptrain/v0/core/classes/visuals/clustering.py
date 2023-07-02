from abc import ABC

try:
    import hdbscan
except:
    hdbscan = None
from sklearn.cluster import DBSCAN
from typing import Any, Dict, Union

from uptrain.v0.constants import ClusteringAlgorithm
from uptrain.v0.core.lib.helper_funcs import dependency_required


class Clustering(ABC):
    def __init__(self):
        super().__init__()

    def resolve(self, args: Dict[str, Any]) -> Any:
        raise NotImplementedError("Clustering.resolve() not implemented.")


class DBSCANClustering(Clustering):
    def __init__(self) -> None:
        super().__init__()

    # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html
    def resolve(self, args: Dict[str, Any]) -> DBSCAN:
        if not isinstance(args, dict):
            raise ValueError("args must be a dictionary.")

        valid_keys = {
            "eps",
            "min_samples",
            "metric",
            "metric_params",
            "algorithm",
            "leaf_size",
            "p",
            "n_jobs",
        }
        invalid_keys = set(args.keys()) - valid_keys

        if invalid_keys:
            raise ValueError(f"Invalid key(s) {invalid_keys} in args.")

        return DBSCAN(**args)


@dependency_required(hdbscan, "hdbscan")
class HDBSCANClustering(Clustering):
    def __init__(self) -> None:
        super().__init__()

    # https://hdbscan.readthedocs.io/en/latest/basic_hdbscan.html
    def resolve(self, args: Dict[str, Any]) -> "hdbscan.HDBSCAN":
        if not isinstance(args, dict):
            raise ValueError("args must be a dictionary.")

        valid_keys = {
            "algorithm",
            "alpha",
            "approx_min_span_tree",
            "gen_min_span_tree",
            "leaf_size",
            "memory",
            "metric",
            "min_cluster_size",
            "min_samples",
            "p",
        }
        invalid_keys = set(args.keys()) - valid_keys

        if invalid_keys:
            raise ValueError(f"Invalid key(s) {invalid_keys} in args.")

        return hdbscan.HDBSCAN(**args)


class ClusteringResolver:
    """Class that resolves a clustering key to a clustering class instance."""

    def __init__(self, algorithm: ClusteringAlgorithm) -> None:
        super().__init__()
        self.algorithm = algorithm

    def resolve(self, args: Dict[str, Any]) -> Union[DBSCAN, "hdbscan.HDBSCAN"]:
        if self.algorithm == ClusteringAlgorithm.DBSCAN:
            return DBSCANClustering().resolve(args)
        elif self.algorithm == ClusteringAlgorithm.HDBSCAN:
            return HDBSCANClustering().resolve(args)
        else:
            raise ValueError(f"Clustering algorithm {self.algorithm} not supported.")
