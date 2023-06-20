import os
import json
import copy
import csv
import time
from typing import Optional
from datetime import datetime, timedelta, tzinfo
from collections import OrderedDict
import functools

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from uptrain.v0.core.encoders import UpTrainEncoder


def cluster_and_plot_data(
    data,
    num_clusters,
    cluster_plot_func=None,
    plot_save_name="",
    normalisation=None,
    compute_point_density=False,
):
    kmeans = KMeans(n_clusters=num_clusters, random_state=1, n_init=10)
    kmeans.fit(data)
    all_clusters = kmeans.cluster_centers_
    all_labels = kmeans.labels_

    counts = np.zeros(num_clusters)
    uniq_lbs, uniq_cts = np.unique(all_labels, return_counts=True)
    for idx in range(uniq_lbs.shape[0]):
        counts[uniq_lbs[idx]] = uniq_cts[idx]

    cluster_vars = []
    cluster_dictn = {}
    for idx in range(len(all_clusters)):
        this_elems = data[np.where(all_labels == idx)[0]]
        cluster_dictn.update({idx: this_elems})
        cluster_vars.append(
            np.mean(np.sum(np.abs(this_elems - all_clusters[idx]), axis=1))
        )

    density_arr = []
    if compute_point_density:
        min_var = np.min(cluster_vars)
        for idx in range(len(data)):
            cluster_centroid_dists = np.sum(np.abs(all_clusters - data[idx]), axis=1)
            closest_cluster_labels = np.where(cluster_centroid_dists < min_var * 4)
            num_close_points = 0
            for this_label in closest_cluster_labels[0]:
                this_elems = cluster_dictn[this_label]
                all_elems_dists = np.sum(np.abs(this_elems - data[idx]), axis=1)
                closest_points_idxs = np.where(all_elems_dists < 1.5 * min_var)
                num_close_points += len(closest_points_idxs[0])
            density_arr.append(num_close_points - 1)
    density_arr = np.array(density_arr)

    idxs_closest_to_cluster_centroids = {}
    for idx in range(len(all_clusters)):
        this_elems = cluster_dictn[idx]
        all_elems_dists = np.sum(np.abs(this_elems - all_clusters[idx]), axis=1)
        closest_idxs = np.argsort(all_elems_dists)[0:3]
        idxs_closest_to_cluster_centroids.update({idx: closest_idxs})

    dictn = []
    for idx in range(len(all_clusters)):
        dictn.append(
            {
                "cluster": all_clusters[idx],
                "count": counts[idx],
                "var": cluster_vars[idx],
                "idxs_closest": idxs_closest_to_cluster_centroids[idx],
            }
        )
    dictn.sort(key=lambda x: x["count"], reverse=True)

    all_clusters = np.array([x["cluster"] for x in dictn])
    counts = np.array([x["count"] for x in dictn])
    cluster_vars = np.array([x["var"] for x in dictn])
    idxs_closest_to_cluster_centroids = dict(
        zip(range(len(dictn)), [x["idxs_closest"] for x in dictn])
    )

    if normalisation is not None:
        all_clusters_renormalised = copy.deepcopy(all_clusters) * normalisation
    else:
        all_clusters_renormalised = all_clusters
    if cluster_plot_func is not None:
        cluster_plot_func(
            all_clusters_renormalised, counts, plot_save_name=plot_save_name
        )
    return (
        all_clusters,
        counts,
        cluster_vars,
        density_arr,
        idxs_closest_to_cluster_centroids,
    )


def add_data_to_warehouse(data, path_csv, row_update=False):
    """Stores the dictionary "data" at location path_csv"""

    for k in list(data.keys()):
        if row_update and k == "id":
            continue
        data[k] = [json.dumps(x, cls=UpTrainEncoder) for x in data[k]]
    if not os.path.exists(path_csv):
        pd.DataFrame(data).to_csv(path_csv, index=False)
    else:
        if row_update:
            df = pd.read_csv(path_csv)
            for k in list(data.keys()):
                if row_update and k == "id":
                    continue
                if k not in list(df.columns):
                    df[k] = None
                df.loc[get_df_indices_from_ids(df, data["id"]), k] = np.array(
                    data[k], dtype="object"
                )
            pd.DataFrame(df).to_csv(path_csv, index=False)
        else:
            pd.DataFrame(data).to_csv(path_csv, index=False, mode="a", header=False)


def combine_data_points_for_batch(data):
    # what could be the generic logic???
    if isinstance(data, list):
        joined = None
        for idx in range(len(data)):
            elem = data[idx]
            if isinstance(elem, dict):
                if joined is None:
                    joined = {}
                for key in list(elem.keys()):
                    if key not in joined:
                        joined.update({key: []})
                    joined[key].append(elem[key])
                    if idx == len(data) - 1:
                        joined[key] = np.squeeze(np.array(joined[key]), axis=1)
            elif isinstance(elem, list):
                if len(elem) == 1:
                    if joined is None:
                        joined = []
                    joined.append(np.array(elem))
                    if idx == len(data) - 1:
                        joined = np.squeeze(np.array(joined), axis=1)
                else:
                    print(data)
                    import pdb

                    pdb.set_trace()
                    raise Exception("Not implemented, please contact developers")
            elif isinstance(elem, np.ndarray):
                if joined is None:
                    joined = []
                joined.append(elem)
                joined = np.squeeze(np.array(joined), axis=1)
        return joined
    else:
        print(data)
        raise Exception("Not implemented, please contact developers")


def extract_data_points_from_batch(data, idxs):
    if isinstance(data, dict):
        this_data = {}
        for key in list(data.keys()):
            this_data.update({key: extract_data_points_from_batch(data[key], idxs)})
        return this_data
    elif isinstance(data, np.ndarray):
        return np.array(data[np.array(idxs)])
    elif isinstance(data, list):
        if isinstance(idxs, int):
            return data[idxs]
        else:
            return [data[x] for x in list(idxs)]
    else:
        return data


def make_2d_np_array(data):
    data = np.asarray(data)
    if len(data.shape) == 1:
        return np.expand_dims(data, axis=0)
    elif len(data.shape) == 2:
        return data
    else:
        raise Exception("Invalid data shape: %s" % str(data.shape))


def get_feature_names_list(inputs):
    feat_name_list = []
    for k in list(inputs.keys()):
        if not (k == "id"):
            feat_name_list.append(k)
    return feat_name_list


def add_data_to_batch(data, this_data):
    """Add data point this_data to data"""
    if isinstance(data, dict):
        assert isinstance(this_data, dict)
        for key, val in this_data.items():
            data.update({key: val})
        return data
    else:
        Exception("Invalid Data id type: %s" % type(data))


def get_df_indices_from_ids(df, ids):
    if not isinstance(df["id"][0], str):
        all_id_array = np.array(df["id"])
        if np.all(np.diff(all_id_array) >= 0):
            return np.searchsorted(all_id_array, ids)
        else:
            sorter = np.argsort(all_id_array)
            return sorter[np.searchsorted(all_id_array, ids, sorter=sorter)]
    else:
        id_str_list = [eval(x) for x in df["id"]]
        sorter = np.argsort(id_str_list)
        return sorter[np.searchsorted(id_str_list, ids, sorter=sorter)]


def read_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def write_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)


def write_csv_row(file_name, data):
    with open(file_name, "a") as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(data)
        f_object.close()


def read_csv(file_name):
    return pd.read_csv(file_name)


def load_list_from_df(df, column):
    try:
        out = [json.loads(x) for x in list(df[column])]
    except:
        out_json = [json.dumps(x) for x in list(df[column])]
        out = [json.loads(x) for x in out_json]
    return out


def make_dir_friendly_name(txt: str) -> str:
    import re

    return re.sub(r"[^a-zA-Z0-9_]", "_", txt)


def clear_directory(dir_path: str):
    """Clears the directory at dir_path but without deleting the directory itself. `shutil.rmtree` will
    have difficulties with mounted volumes or network drives.
    """
    import shutil

    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


class Clock:
    """Makes testing easier by anchoring to an older time. This is helpful when
    testing with older datasets. While if initialized with no arguments, the clock
    starts at the current time.
    """

    behind_by: timedelta
    tzone: Optional[tzinfo]

    def __init__(self, init_at: datetime):
        tz = init_at.tzinfo
        if tz is None or tz.utcoffset(init_at) is None:
            self.tzone = None
            self.behind_by = datetime.now() - init_at
        else:
            self.tzone = tz
            self.behind_by = datetime.now(tz=tz) - init_at

    def now(self) -> datetime:
        """Return the current time, adjusted by the amount of time the clock is behind."""
        return datetime.now(tz=self.tzone) - self.behind_by

    def sleep(self, seconds: float):
        """If the clock is behind, catch up. Else, sleep for the given duration."""
        seconds_behind = self.behind_by.total_seconds()
        if seconds_behind > 0:
            print(f"advancing the clock by {seconds} seconds")
            self.behind_by = timedelta(seconds=max(seconds_behind - seconds, 0))
        else:
            print("sleeping for 60 seconds")
            time.sleep(seconds)


class Timer:
    """Context manager for timing code blocks"""

    time: float

    def __enter__(self):
        self.time = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = round(time.perf_counter() - self.time, 3)


def dependency_required(dependency_name, package_name: str):
    """Decorator for checks that need optional dependencies. If the dependency is not
    present, initializing the class will raise an error.
    """

    def class_decorator(cls):
        @functools.wraps(cls, updated=())
        class WrappedClass(cls):
            def __init__(self, *args, **kwargs):
                if dependency_name is None:
                    raise ImportError(
                        f"{package_name} is required to use {cls.__name__}. Please install it using: pip install {package_name}"
                    )
                super().__init__(*args, **kwargs)

        return WrappedClass

    return class_decorator


def fn_dependency_required(dependency_name, package_name: str):
    """Decorator for functions that need optional dependencies. If the dependency is not
    present, calling the function will raise an error.
    """

    def fn_decorator(fn):
        @functools.wraps(fn)
        def wrapped_fn(*args, **kwargs):
            if dependency_name is None:
                raise ImportError(
                    f"{package_name} is required to use {fn.__name__}. Please install it using: pip install {package_name}"
                )
            return fn(*args, **kwargs)

        return wrapped_fn

    return fn_decorator
