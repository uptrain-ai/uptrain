from oodles.core.classes.anomalies.abstract_anomaly import AbstractAnomaly


class CustomAnomaly(AbstractAnomaly):
    def __init__(self, check, log_args={}):
        self.dashboard_name = check.get("dashboard_name", "custom_measure")
        super().__init__(log_args=log_args)
        self.check_func = check["check_func"]
        self.need_gt = check["need_gt"]

        initialize_func = check.get("initialize_func", None)
        if initialize_func is not None:
            initialize_func(self)

    def check(self, inputs, outputs, gts=None, extra_args={}):
        check_func = self.check_func
        return check_func(self, inputs, outputs, gts=gts, extra_args=extra_args)

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return False

    def need_ground_truth(self):
        return self.need_gt
