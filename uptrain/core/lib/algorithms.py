import numpy as np


def estimate_earth_moving_cost(prod_dist, ref_dist, clusters):
    num_clusters = clusters.shape[0]
    cost = 0
    for jdx in range(num_clusters):
        dirt_required = prod_dist[jdx] - ref_dist[jdx]
        dictn = []
        for kdx in range(num_clusters):
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
