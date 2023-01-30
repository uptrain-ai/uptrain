import numpy as np

from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.core.classes.algorithms import PopularityBias
from uptrain.constants import BiasAlgo, Anomaly


class RecommendationBias(AbstractAnomaly):
    dashboard_name = "pop_bias"
    anomaly_type = Anomaly.POPULARITY_BIAS

    def __init__(self, fw, check):
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.acc_arr = []
        if check["algorithm"] == BiasAlgo.POPULARITY_BIAS:
            rec_list = check.get("rec_list", None)
            pop_map = check.get("pop_map", None)
            self.algo = PopularityBias(rec_list, pop_map)
        else:
            raise Exception("Recommendation bias type not supported")

    def need_ground_truth(self):
        return False

    def check(self, inputs, outputs, gts=None, extra_args={}):
        for y_pred in outputs:
            self.algo.add_prediction([y_pred])
            pop_arr = self.algo.all_popularity
            self.log_handler.add_histogram(
                "popularity_bias", pop_arr, self.dashboard_name
            )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"]))
