import numpy as np

from uptrain.core.classes.monitors import AbstractMonitor
from uptrain.core.classes.algorithms import PopularityBias
from uptrain.constants import BiasAlgo, Monitor


class RecommendationBias(AbstractMonitor):
    dashboard_name = "popularity_bias"
    monitor_type = Monitor.POPULARITY_BIAS

    def __init__(self, fw, check):
        self.log_handler = fw.log_handler
        self.acc_arr = []
        if check["algorithm"] == BiasAlgo.POPULARITY_BIAS:
            sessions = check.get("sessions", None)
            self.algo = PopularityBias(sessions)
        else:
            raise Exception("Recommendation bias type not supported")

    def need_ground_truth(self):
        return False

    def check(self, inputs, outputs, gts=None, extra_args={}):
        for y_pred in outputs:
            self.algo.add_prediction(y_pred)
            pop_arr = self.algo.all_popularity
            self.log_handler.add_histogram(
                "popularity_bias", pop_arr, self.dashboard_name
            )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"]))
