from oodles.core.classes.anomalies.abstract_anomaly import AbstractAnomaly


class CustomAnomaly(AbstractAnomaly):
    def __init__(self, monitoring_func):
        super().__init__()
        self.monitoring_func = monitoring_func

    def check(self, inputs, outputs, extra_args={}):
        return self.monitoring_func(inputs, outputs, extra_args=extra_args)

    def is_data_interesting(self, inputs, outputs, extra_args={}):
        return False