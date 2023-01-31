import numpy as np
from uptrain.core.classes.anomalies import AbstractAnomaly
from uptrain.constants import Anomaly


class CustomAnomaly(AbstractAnomaly):
    anomaly_type = Anomaly.CUSTOM_MONITOR

    def __init__(self, fw, check):
        self.dashboard_name = check.get("dashboard_name", "custom_measure")
        self.log_handler = fw.log_handler
        self.log_handler.add_writer(self.dashboard_name)
        self.check_func = check["check_func"]
        self.need_gt = check["need_gt"]

        initialize_func = check.get("initialize_func", None)
        if initialize_func is not None:
            initialize_func(self)

    def check(self, inputs, outputs, gts=None, extra_args={}):
        check_func = self.check_func
        return check_func(self, inputs, outputs, gts=gts, extra_args=extra_args)

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return np.array([False] * len(extra_args["id"]))

    def need_ground_truth(self):
        return self.need_gt
