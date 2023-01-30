import os


class AbstractAnomaly:
    anomaly_type = None

    def check(self, inputs, outputs, gts=None, extra_args={}):
        raise Exception("Should be defined for each class")

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        raise Exception("Should be defined for each class")

    def need_ground_truth(self):
        return False
