import numpy as np

from uptrain.v0.core.classes.monitors import AbstractMonitor
from uptrain.v0.core.classes.algorithms import PopularityBias
from uptrain.v0.constants import BiasAlgo, Monitor


class ModelBias(AbstractMonitor):
    dashboard_name = "popularity_bias"
    monitor_type = Monitor.POPULARITY_BIAS

    def base_init(self, fw, check):
        self.acc_arr = []
        if check["algorithm"] == BiasAlgo.POPULARITY_BIAS:
            sessions = check.get("sessions", None)
            self.algo = PopularityBias(sessions)
        else:
            raise Exception("Model bias type not supported")

    def need_ground_truth(self):
        return False

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        for y_pred in outputs:
            self.algo.add_prediction(y_pred)
            pop_arr = self.algo.all_popularity
            self.log_handler.add_histogram(
                "popularity_bias", pop_arr, self.dashboard_name
            )
