import os
import shutil
import numpy as np


class LogHandler:
    def __init__(self, framework=None, cfg=None):
        self.fw = framework
        if os.path.exists(cfg.log_folder):
            print("Deleting the folder: ", cfg.log_folder)
            shutil.rmtree(cfg.log_folder)

        self.tb_writers = {}
        self.tb_logs = None
        if cfg.tb_logging:
            from uptrain.core.classes.logging.log_tensorboard import TensorboardLogs

            self.tb_logs = TensorboardLogs(cfg.log_folder)

        self.st_writer = None
        if cfg.st_logging:
            from uptrain.core.classes.logging.log_streamlit import StreamlitLogs

            self.st_log_folder = os.path.join(cfg.log_folder, "st_data")
            os.makedirs(self.st_log_folder, exist_ok=True)
            self.st_writer = StreamlitLogs(self.st_log_folder)
            self.st_log_folders_all = {}

    def add_writer(self, dashboard_name):
        dashboard_name = self.make_name_fold_directory_friendly(dashboard_name)
        tb_writer = None
        if self.tb_logs:
            tb_writer = self.tb_logs.add_writer(dashboard_name)
            self.tb_writers.update({dashboard_name: tb_writer})

    def add_scalars(self, plot_name, dictn, count, dashboard_name):
        dashboard_name, plot_name = self.make_name_fold_directory_friendly(
            [dashboard_name, plot_name]
        )
        new_dictn = dict(
            zip(
                self.make_name_fold_directory_friendly(list(dictn.keys())),
                dictn.values(),
            )
        )
        if self.tb_logs:
            if dashboard_name in self.tb_writers:
                self.tb_writers[dashboard_name].add_scalars(plot_name, new_dictn, count)
        if self.st_writer:
            dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
            plot_folder = os.path.join(dashboard_dir, "line_plots", plot_name)
            os.makedirs(plot_folder, exist_ok=True)
            dictn.update({"count": count})
            self.st_writer.add_scalars(dictn, plot_folder)

    def add_histogram(self, plot_name, data, dashboard_name, count=-1):
        dashboard_name, plot_name = self.make_name_fold_directory_friendly(
            [dashboard_name, plot_name]
        )
        if not isinstance(data, dict):
            if isinstance(data, list) or isinstance(data, np.ndarray):
                if dashboard_name in self.tb_writers:
                    self.tb_writers[dashboard_name].add_histogram(plot_name, data, count)
        if self.st_writer:
            dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
            plot_folder = os.path.join(dashboard_dir, "histograms", plot_name)
            os.makedirs(plot_folder, exist_ok=True)
            self.st_writer.add_histogram(data, plot_folder, count)

    def add_alert(self, alert_name, alert, dashboard_name):
        # dashboard_name = self.make_name_fold_directory_friendly(
        #     [dashboard_name]
        # )
        if self.st_writer:
            dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
            plot_folder = os.path.join(dashboard_dir, "alerts")
            os.makedirs(plot_folder, exist_ok=True)
            self.st_writer.add_alert(alert_name, alert, plot_folder)

    def add_bar_graphs(self, plot_name, data, dashboard_name, count=-1):
        dashboard_name, plot_name = self.make_name_fold_directory_friendly(
            [dashboard_name, plot_name]
        )
        if self.st_writer:
            dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
            plot_folder = os.path.join(dashboard_dir, "bar_graphs", plot_name)
            os.makedirs(plot_folder, exist_ok=True)
            self.st_writer.add_bar_graphs(data, plot_folder, count)

    def make_name_fold_directory_friendly(self, arr):
        if isinstance(arr, str):
            return self.make_name_fold_directory_friendly([arr])[0]

        new_arr = [self.convert_str(x) for x in arr]
        return new_arr

    def convert_str(self, txt):
        txt = txt.replace("(", "_")
        txt = txt.replace(")", "_")
        txt = txt.replace(":", "_")
        txt = txt.replace(" ", "_")
        txt = txt.replace(",", "_")
        txt = txt.replace(">", "_")
        txt = txt.replace("<", "_")
        txt = txt.replace("=", "_")
        txt = txt.replace("-", "_")
        return txt
