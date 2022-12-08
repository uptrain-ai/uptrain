import json
import numpy as np
from sklearn.cluster import KMeans


def cluster_and_plot_data(data, num_clusters, cluster_plot_func=None):
    kmeans = KMeans(n_clusters=num_clusters, random_state=1)
    kmeans.fit(data)
    all_clusters = kmeans.cluster_centers_
    all_labels = kmeans.labels_

    counts = np.zeros(num_clusters)
    uniq_lbs, uniq_cts = np.unique(all_labels, return_counts=True)
    for idx in range(uniq_lbs.shape[0]):
        counts[uniq_lbs[idx]] = uniq_cts[idx]

    cluster_vars = []
    for idx in range(len(all_clusters)):
        this_elems = data[np.where(all_labels == idx)[0]]
        cluster_vars.append(np.mean(np.sum(np.abs(this_elems-all_clusters[idx]), axis=1)))

    dictn = []
    for idx in range(len(all_clusters)):
        dictn.append({'cluster': all_clusters[idx], 'count': counts[idx], 'var': cluster_vars[idx]})
    dictn.sort(key=lambda x: x['count'], reverse=True)

    all_clusters = np.array([x['cluster'] for x in dictn])
    counts = np.array([x['count'] for x in dictn])
    cluster_vars = np.array([x['var'] for x in dictn])

    if cluster_plot_func is not None:
        cluster_plot_func(all_clusters, counts)
    return all_clusters, counts, cluster_vars


def read_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def write_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)
