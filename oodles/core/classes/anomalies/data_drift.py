import numpy as np
from sklearn.cluster import KMeans

from oodles.core.classes.anomalies.abstract_anomaly import AbstractAnomaly
from oodles.core.classes.anomalies.algorithms.data_drift_ddm import DataDriftDDM
from oodles.constants import DataDriftAlgo
from oodles.core.lib.helper_funcs import read_json

class DataDrift(AbstractAnomaly):
    dashboard_name = 'data_drift'
    is_embedding = True
    NUM_BUCKETS = 20

    def __init__(self, check, log_args={}):
        super().__init__(log_args=log_args)
        self.reference_dataset = check['reference_dataset']
        self.count = 0
        self.bucket_reference_dataset()
        if check["algorithm"] == DataDriftAlgo.DDM:
            warn_thres = check.get("warn_thres", 2)
            alarm_thres = check.get("alarm_thres", 3)
            self.algo = DataDriftDDM(warn_thres, alarm_thres)
        else:
            raise Exception("Data drift algo type not supported")

    def need_ground_truth(self):
        return False

    def check(self, inputs, outputs, gts=None, extra_args={}):
        self.count += 1
        feats = inputs['kps'][0]
        if self.is_embedding:
            selected_cluster = np.argmin(np.sum((self.clusters[0] - feats)*(self.clusters[0] - feats),axis=1))
            self.prod_dist_counts[0][selected_cluster] += 1
        else:
            for idx in range(feats.shape[0]):
                bucket_idx = np.searchsorted(self.buckets[idx], feats[idx])
                self.prod_dist_counts[idx][bucket_idx] += 1
        if self.count < 200:
            return
        else:
            self.prod_dist = self.prod_dist_counts/self.count
            self.psis = np.zeros(self.ref_dist.shape[0])
            self.costs = np.zeros(self.ref_dist.shape[0])
            for idx in range(self.ref_dist.shape[0]):
                self.costs[idx] = self.estimate_earth_moving_cost(self.prod_dist[idx], self.ref_dist[idx], self.clusters[idx])
                this_psi = sum([(self.prod_dist[idx][jdx] - self.ref_dist[idx][jdx]) * np.log(max(self.prod_dist[idx][jdx],0.0001)/self.ref_dist[idx][jdx]) for jdx in range(self.ref_dist.shape[1])])
                self.psis[idx] = this_psi
        self.plot_scalars('population stability index', dict(zip([str(x) for x in range(self.psis.shape[0])],[float(x) for x in list(self.psis)])), self.count)
        self.plot_scalars('earth moving costs', dict(zip([str(x) for x in range(self.costs.shape[0])],[float(x) for x in list(self.costs)])), self.count)
        self.plot_scalars('correlation bw psi and cost', dict(zip([str(x) for x in range(self.costs.shape[0])],[float(x) for x in list(100*self.psis/self.costs)])), self.count)

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return False

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
                dictn.append({'dirt': this_dirt, 'idx': kdx, 'cost_per_dirt': cost_per_dirt})
            dictn = sorted(dictn, key = lambda x: x['cost_per_dirt'])
            this_cost = 0
            for kdx in range(len(dictn)):
                if dirt_required > 0:
                    this_cost += min(dictn[kdx]['dirt'], dirt_required) * dictn[kdx]['cost_per_dirt']
                    dirt_required -= min(dictn[kdx]['dirt'], dirt_required)
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
        all_inputs = np.array([x['kps'] for x in data])

        if self.is_embedding:
            self.bucket_vector(all_inputs)
        else:
            buckets = []
            clusters = []
            cluster_vars = []
            for idx in range(all_inputs.shape[1]):
                this_inputs = all_inputs[:,idx]
                this_buckets, this_clusters, this_cluster_vars = self.bucket_scalar(this_inputs)
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
        for idx in range(0,self.NUM_BUCKETS):
            if idx > 0:
                buckets.append(sorted_arr[int(idx*(len(sorted_arr)-1)/self.NUM_BUCKETS)])
            this_bucket_elems = sorted_arr[int((idx)*(len(sorted_arr)-1)/self.NUM_BUCKETS):int((idx+1)*(len(sorted_arr)-1)/self.NUM_BUCKETS)]
            gaussian_mean = np.mean(this_bucket_elems)
            gaussian_var = np.var(this_bucket_elems)
            clusters.append([gaussian_mean])
            cluster_vars.append([gaussian_var])

        self.ref_dist.append([[1/self.NUM_BUCKETS] for x in range(self.NUM_BUCKETS)])
        self.ref_dist_counts.append([[int(len(sorted_arr)/self.NUM_BUCKETS)] for x in range(self.NUM_BUCKETS)])
        self.prod_dist.append([[0] for x in range(self.NUM_BUCKETS)])
        self.prod_dist_counts.append([[0] for x in range(self.NUM_BUCKETS)])
        return np.array(buckets), np.array(clusters), np.array(cluster_vars)

    def bucket_vector(self, data):
        self.ref_dist = np.zeros((1,self.NUM_BUCKETS))
        self.prod_dist = np.zeros((1,self.NUM_BUCKETS))
        self.ref_dist_counts = np.zeros((1,self.NUM_BUCKETS))
        self.prod_dist_counts = np.zeros((1,self.NUM_BUCKETS))

        kmeans = KMeans(n_clusters=self.NUM_BUCKETS)
        kmeans.fit(data)
        all_clusters = kmeans.cluster_centers_
        all_labels = kmeans.labels_

        # for idx in range(len(all_clusters)):
        #     frame = self.plot_kps_as_image(all_clusters[idx])
        #     cv2.imwrite(str(idx) + '.png', frame)
        # self.plot_cluster_as_image(self.NUM_BUCKETS)

        self.clusters = np.array([all_clusters])
        uniq_lbs, uniq_cts = np.unique(all_labels, return_counts=True)
        for idx in range(uniq_lbs.shape[0]):
            self.ref_dist_counts[0][uniq_lbs[idx]] = uniq_cts[idx]
        self.ref_dist = self.ref_dist_counts / data.shape[0]