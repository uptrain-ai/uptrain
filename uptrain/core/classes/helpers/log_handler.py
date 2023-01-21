import os
import shutil

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
            self.st_logs = StreamlitLogs()
            self.st_writer = self.st_logs

    def add_writer(self, dashboard_name):
        dashboard_name = self.make_name_fold_directory_friendly(dashboard_name)
        tb_writer = None
        if self.tb_logs:
            tb_writer = self.tb_logs.add_writer(dashboard_name)
        self.tb_writers.update({dashboard_name: tb_writer})
        # Do nothing for st logs?

    def add_scalars(self, plot_name, dictn, count, dashboard_name):
        if self.tb_logs:
            dashboard_name, plot_name = self.make_name_fold_directory_friendly([dashboard_name, plot_name])
            new_dictn = dict(zip(self.make_name_fold_directory_friendly(list(dictn.keys())), dictn.values()))
            if dashboard_name in self.tb_writers:
                self.tb_writers[dashboard_name].add_scalars(plot_name, new_dictn, count)
        if self.st_writer:
            self.st_writer.add_scalars(plot_name, new_dictn)

    def add_histogram(self, plot_name, arr, dashboard_name):
        if self.tb_logs:
            dashboard_name, plot_name = self.make_name_fold_directory_friendly([dashboard_name, plot_name])
            if dashboard_name in self.tb_writers:
                self.tb_writers[dashboard_name].add_histogram(plot_name, arr, len(arr))
        if self.st_writer:
            self.st_writer.add_histogram(plot_name, arr[-1])

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
        return txt
