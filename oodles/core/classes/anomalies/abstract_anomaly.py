import os
from tensorboardX import SummaryWriter

class AbstractAnomaly:
    dashboard_name = None

    def __init__(self, log_args={}):
        if "log_folder" in log_args:
            self.writer = SummaryWriter(
                os.path.join(log_args["log_folder"], self.dashboard_name)
            )

    def check(self, inputs, outputs, gts=None, extra_args={}):
        raise Exception("Should be defined for each class")

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        raise Exception("Should be defined for each class")

    def need_ground_truth(self):
        return False

    def plot_scalar(self, name, x, y):
        self.writer.add_scalar(name, x, y)

    def plot_scalars(self, name, x, y):
        self.writer.add_scalars(name, x, y)

    def plot_histogram(self, name, arr, t):
        self.writer.add_histogram(name, arr, t)
