import numpy as np
from uptrain.v0.core.classes.monitors import AbstractMonitor
from uptrain.v0.constants import Monitor


class CustomMonitor(AbstractMonitor):
    monitor_type = Monitor.CUSTOM_MONITOR

    def base_init(self, fw, check):
        self.dashboard_name = check.get("dashboard_name", "custom_measure")
        self.check_func = check["check_func"]
        self.need_gt = check["need_gt"]

        initialize_func = check.get("initialize_func", None)
        if initialize_func is not None:
            initialize_func(self)

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        check_func = self.check_func
        return check_func(self, inputs, outputs, gts=gts, extra_args=extra_args)

    def need_ground_truth(self):
        return self.need_gt
