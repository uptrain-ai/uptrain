import os
from tensorboardX import SummaryWriter
import threading


class TensorboardLogs:
    def __init__(self, log_folder):
        self.log_folder = os.path.join(log_folder, "tb_data")
        os.makedirs(self.log_folder, exist_ok=True)
        launch_tb = lambda: os.system("tensorboard --logdir=" + self.log_folder)
        t = threading.Thread(target=launch_tb, args=([]))
        t.start()

    def add_writer(self, dashboard_name="UpTrain AI Logs"):
        return SummaryWriter(os.path.join(self.log_folder, dashboard_name))
