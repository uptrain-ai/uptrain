import numpy as np
import scipy
import pandas as pd

from uptrain.core.classes.monitors import AbstractMonitor
from uptrain.constants import Monitor
from uptrain.core.lib.helper_funcs import read_json
# from uptrain.core.lib.algorithms import estimate_earth_moving_cost
# from uptrain.core.classes.measurables import MeasurableResolver
from uptrain.core.classes.algorithms import Clustering


class FeatureDrift(AbstractMonitor):
    dashboard_name = "feature_drift"
    monitor_type = Monitor.FEATURE_DRIFT
    is_embedding = False
    mode = None
    INITIAL_SKIP = 2000

    def model_choices(self, check):
        return [{"is_embedding": False}]

    def base_init(self, fw, check):
        self.reference_dataset = check["reference_dataset"]
        self.NUM_BUCKETS = check.get("num_buckets", 10)
        self.psi_threshold = check.get("psi_threshold", 0.2)
        self.step = check.get("initial_skip", 2000)
        self.prod_dist_counts_arr = []
        self.all_count = 0
        self.plot_name = "Feature_" + self.measurable.col_name()
        self.feats = np.array([])
        self.psis = []

        # clustering_args = {
        #     "num_buckets": self.NUM_BUCKETS,
        #     'is_embedding': self.is_embedding,
        #     'plot_save_name': self.log_handler.get_plot_save_name("training_dataset_clusters.png", self.dashboard_name),
        #     'cluster_plot_func': self.cluster_plot_func,
        #     'find_low_density_regions': self.do_low_density_check
        # }
        # self.clustering_helper = Clustering(clustering_args)

        self.train_dist, self.train_bins = self.get_ref_data_stats()
        # convert the array self.train_bins into tuples of (min, max) values
        self.bar_vals = []
        for i in range(len(self.train_bins)-1):
            start_str = "{:.2f}".format(self.train_bins[i])
            end_str = "{:.2f}".format(self.train_bins[i+1])
            self.bar_vals.append(start_str + '-' + end_str)
            

    def check(self, inputs, outputs, gts=None, extra_args={}):
        if len(self.children) > 0:
            feats = self.measurable.compute_and_log(
                inputs=inputs, outputs=outputs, gts=gts, extra=extra_args
            )
            if sum(list(feats.shape)[1:])/max(1,len(list(feats.shape)[1:])) <= 1:
                self.children = [self.children[0]]
            [x.check(inputs, outputs, gts=gts, extra_args=extra_args) for x in self.children]
        else:
            """
            Find the population stability index between the reference and
            production distribtions by assigning them into 
            reference buckets. 
            """

            feats = self.measurable.compute_and_log(
                inputs=inputs, outputs=outputs, gts=gts, extra=extra_args
            )
            self.all_count += len(feats)
            self.feats = np.append(self.feats, np.squeeze(np.array(feats)))

            if len(self.feats) >= self.step:
                prod_dist, _ = np.histogram(self.feats, bins=self.train_bins)
                prod_dist = prod_dist/sum(prod_dist)

                # Find the PSI between the two distributions
                psi = self.get_psi(self.train_dist, prod_dist)
                self.psis.append(psi)

                self.log_handler.add_bar_graphs(
                    self.plot_name,
                    {
                        "reference": dict(zip(self.bar_vals, list(self.train_dist))),
                        "production": dict(zip(self.bar_vals, list(prod_dist))),
                    },
                    self.dashboard_name,
                )

                self.log_handler.add_scalars(
                    'psi',
                    {'y_psi': psi},
                    self.all_count,
                    self.dashboard_name,
                    file_name=self.measurable.col_name(),
                )

                # High PSI alerts the user to a feature drift
                if psi > self.psi_threshold:
                    alert = f"Feature Drift last detected at {self.all_count} for {self.measurable.feature_name} with PSI = {psi}"
                    self.log_handler.add_alert(
                            "Feature Drift Alert 🚨",
                            alert,
                            self.dashboard_name
                        )
                self.feats = np.array([])
        
    def get_ref_data_stats(self):
        """
        Find the bucketing scheme for data in ref_arr. The data can be numerical or categorical.
        """
        if self.reference_dataset.split('.')[-1] == 'json':
            data = read_json(self.reference_dataset)
            all_inputs = np.array(
                [self.measurable.extract_val_from_training_data(x) for x in data]
            )
        elif self.reference_dataset.split('.')[-1] == 'csv':
            data = pd.read_csv(self.reference_dataset).to_dict()
            for key in data:
                data[key] = list(data[key].values())
            all_inputs = np.array(self.measurable.extract_val_from_training_data(data))
        else:
            raise Exception("Reference data file type not recognized.")
        
        prob = np.linspace(0, 1, self.NUM_BUCKETS + 1)
        bins = scipy.stats.mstats.mquantiles(all_inputs, prob)
        vals, bins = np.histogram(all_inputs, bins=bins)
        return vals/sum(vals), bins
    
    def get_psi(self, ref_dist, prod_dist):
        """
        Find the population stability index between the two distributions.
        """
        return np.sum(np.where(
            ref_dist == 0, 0, (ref_dist - prod_dist) * np.log(ref_dist / prod_dist)
        ))