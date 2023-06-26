import numpy as np
import scipy
import pandas as pd

from uptrain.v0.core.classes.monitors import AbstractMonitor
from uptrain.v0.constants import Monitor
from uptrain.v0.core.lib.helper_funcs import read_json
from uptrain.v0.core.classes.algorithms import Clustering


class FeatureDrift(AbstractMonitor):
    dashboard_name = "feature_drift"

    def model_choices(self, check):
        return [{"is_embedding": False}]

    def base_init(self, fw, check):
        self.reference_dataset = check["reference_dataset"]
        self.NUM_BUCKETS = check.get("num_buckets", 10)
        self.psi_threshold = check.get("psi_threshold", 0.2)
        self.step = check.get("step", 2000)
        self.prod_dist_counts_arr = []
        self.all_count = 0
        self.plot_name = "Feature " + self.measurable.col_name()
        self.feats = np.array([])
        self.psis = []

        self.train_dist, self.train_bins = self.get_ref_data_stats()

        # convert the array self.train_bins into tuples of (min, max) values
        self.bar_vals = []
        for i in range(len(self.train_bins) - 1):
            start_str = "{:.2f}".format(self.train_bins[i])
            end_str = "{:.2f}".format(self.train_bins[i + 1])
            self.bar_vals.append(start_str + "-" + end_str)

    def check(self, inputs, outputs, gts=None, extra_args={}):
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
            prod_dist = prod_dist / sum(prod_dist)

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
                "psi",
                {"y_psi": psi},
                self.all_count,
                self.dashboard_name,
                file_name=self.measurable.col_name(),
            )
            feat_name = self.measurable.feature_name

            # High PSI alerts the user to a feature drift
            if psi > self.psi_threshold:
                alert = f"Feature Drift last detected at {self.all_count} for {feat_name} with PSI = {psi}"
                self.log_handler.add_alert(
                    f"Feature Drift Alert for {feat_name} 🚨", alert, self.dashboard_name
                )
            self.feats = np.array([])

    def get_ref_data_stats(self):
        """
        Find the bucketing scheme for data in ref_arr. The data can be numerical or categorical.
        """
        if self.reference_dataset.split(".")[-1] == "json":
            data = read_json(self.reference_dataset)
            all_inputs = np.array(
                [self.measurable.extract_val_from_training_data(x) for x in data]
            )
        elif self.reference_dataset.split(".")[-1] == "csv":
            data = pd.read_csv(self.reference_dataset).to_dict()
            for key in data:
                data[key] = list(data[key].values())
            all_inputs = np.array(self.measurable.extract_val_from_training_data(data))
        else:
            raise Exception("Reference data file type not recognized.")

        prob = np.linspace(0, 1, self.NUM_BUCKETS + 1)
        bins = scipy.stats.mstats.mquantiles(all_inputs, prob)
        vals, bins = np.histogram(all_inputs, bins=bins)
        return vals / sum(vals), bins

    def get_psi(self, ref_dist, prod_dist):
        """
        Find the population stability index between the two distributions.
        """
        return np.sum(
            np.where(
                ref_dist == 0, 0, (ref_dist - prod_dist) * np.log(ref_dist / prod_dist)
            )
        )
