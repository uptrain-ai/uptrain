import os
import shutil
import urllib3
import json

class LogHandler:
    def __init__(self, framework=None, cfg=None):
        self.fw = framework
        log_folder = cfg.logging_args.log_folder
        if os.path.exists(log_folder):
            print("Deleting the folder: ", log_folder)
            shutil.rmtree(log_folder)

        self.st_writer = None
        if cfg.st_logging:
            from uptrain.core.classes.logging.log_streamlit import StreamlitLogs

            self.st_log_folder = os.path.join(log_folder, "st_data")
            os.makedirs(self.st_log_folder, exist_ok=True)
            self.st_writer = StreamlitLogs(self.st_log_folder, port=cfg.logging_args.dashboard_port)

        # Get Webhook URL for alerting on slack
        self.webhook_url = cfg.logging_args.slack_webhook_url

        # Saving config to get model metadata
        cfg_metadata = {'model_args': None, 'feature_args': None}
        if len(cfg.checks) > 0:
            check = cfg.checks[0]
            cfg_metadata.update({'model_args': check.get('model_args', None)})
            cfg_metadata.update({'feature_args': check.get('feature_args', None)})
        if cfg.st_logging:
            metadata_file = os.path.join(self.st_log_folder, "metadata.json")
            with open(metadata_file, "w") as f:
                json.dump(cfg_metadata, f)

    def get_plot_save_name(self, plot_name, dashboard_name):
        if self.st_writer:
            return os.path.join(self.st_log_folder, dashboard_name, plot_name)
        else:
            return ""

    def add_scalars(self, plot_name, dictn, count, dashboard_name, features={}, models={}, file_name=None, update_val=False):
        if self.st_writer is None:
            return
        dashboard_name, plot_name = self.dir_friendly_name(
            [dashboard_name, plot_name]
        )
        dictn.update(features)
        dictn.update(models)
        new_dictn = dict(
            zip(
                self.dir_friendly_name(list(dictn.keys())),
                dictn.values(),
            )
        )
        dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
        plot_folder = os.path.join(dashboard_dir, "line_plots", plot_name)
        os.makedirs(plot_folder, exist_ok=True)
        new_dictn.update({"x_count": count})
        if file_name is None:
            file_name = plot_name
        self.st_writer.add_scalars(new_dictn, plot_folder, file_name=file_name, update_val=update_val)

    def add_histogram(self, plot_name, data, dashboard_name, features=None, models=None, file_name=None):
        dashboard_name, plot_name = self.dir_friendly_name(
            [dashboard_name, plot_name]
        )
        if self.st_writer:
            dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
            plot_folder = os.path.join(dashboard_dir, "histograms", plot_name)
            os.makedirs(plot_folder, exist_ok=True)
            if file_name is None:
                file_name = plot_name
            self.st_writer.add_histogram(data, plot_folder, features=features, models=models, file_name=file_name)

    def add_bar_graphs(self, plot_name, data, dashboard_name, count=-1):
        if self.st_writer is None:
            return
        dashboard_name, plot_name = self.dir_friendly_name(
            [dashboard_name, plot_name]
        )
        dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
        plot_folder = os.path.join(dashboard_dir, "bar_graphs", plot_name)
        os.makedirs(plot_folder, exist_ok=True)
        self.st_writer.add_bar_graphs(data, plot_folder, count)

    def dir_friendly_name(self, arr):
        if isinstance(arr, str):
            return self.dir_friendly_name([arr])[0]

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

    def add_alert(self, alert_name, alert, dashboard_name):
        if self.st_writer:
            dashboard_name = self.dir_friendly_name(dashboard_name)
            dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
            plot_folder = os.path.join(dashboard_dir, "alerts")
            os.makedirs(plot_folder, exist_ok=True)
            self.st_writer.add_alert(alert_name, alert, plot_folder)

        if self.webhook_url:
            message = f"Dashboard: {dashboard_name}, Alert name: {alert_name}, Alert: {alert}"
            self.slack_notification({'text': message})

    def slack_notification(self, message):
        try:
            http = urllib3.PoolManager()
            response = http.request('POST',
                                    self.webhook_url,
                                    body = json.dumps(message),
                                    headers = {'Content-Type': 'application/json'},
                                    retries = False)
        except Exception as e:
            print("Caught Exception")
            print(e)
