import os
from tensorboardX import SummaryWriter


class TensorboardLogs():
    def __init__(self, log_folder):
        self.log_folder = log_folder

    def add_writer(self, dashboard_name="UpTrain AI Logs"):
        return SummaryWriter(
            os.path.join(
                self.log_folder, 
                dashboard_name
            )
        )