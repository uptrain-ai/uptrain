from oodles.core.classes.anomalies.abstract_anomaly import AbstractAnomaly


class CustomAnomaly(AbstractAnomaly):
    def __init__(self, monitoring_func, need_gt=False, log_args={}, dashboard_name='custom_measure'):
        self.dashboard_name = dashboard_name
        super().__init__(log_args=log_args)
        self.monitoring_func = monitoring_func
        self.need_gt = need_gt
        self.initialise_anomaly()

    def initialise_anomaly(self):
        return

    def check(self, inputs, outputs, gts=None, extra_args={}):
        return self.monitoring_func(inputs, outputs, extra_args=extra_args)

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        return False

    def need_ground_truth(self):
        return self.need_gt
