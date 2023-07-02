import os
import shutil
import urllib3
import json

from uptrain.v0.core.lib.helper_funcs import clear_directory


class LogHandler:
    def __init__(self, framework=None, cfg=None):
        self.fw = framework
        log_folder = cfg.logging_args.log_folder
        self.path_all_data = framework.path_all_data

        if os.path.exists(log_folder):
            print("Deleting contents of the folder: ", log_folder)
            clear_directory(log_folder)

        self.st_writer = None
        self.postgres_writer = None
        if cfg.logging_args.st_logging:
            from uptrain.v0.core.classes.logging.log_streamlit import StreamlitLogs

            self.st_log_folder = os.path.join(log_folder, "st_data")
            os.makedirs(self.st_log_folder, exist_ok=True)
            self.st_writer = StreamlitLogs(
                self.st_log_folder, port=cfg.logging_args.dashboard_port
            )
        elif cfg.logging_args.postgres_logging:
            from uptrain.v0.core.classes.logging.log_postgres import PostgresLogs

            self.postgres_database = cfg.logging_args.database
            self.postgres_writer = PostgresLogs(
                self.postgres_database
            )

        # Get Webhook URL for alerting on slack
        self.webhook_url = cfg.logging_args.slack_webhook_url

        # Saving config to get model metadata
        self.cfg_metadata = {}
        if len(cfg.checks) > 0:
            check = cfg.checks[0]
            self.add_st_metadata(
                {
                    "model_args": check.get("model_args", None),
                    "feature_args": check.get("feature_args", None),
                }
            )
        else:
            self.add_st_metadata({"model_args": None, "feature_args": None})

    def add_st_metadata(self, new_dict):
        if self.st_writer is None:
            return
        self.cfg_metadata.update(new_dict)
        metadata_file = os.path.join(self.st_log_folder, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(self.cfg_metadata, f)

    def add_dashboard_metadata(self, mt_dict, dashboard_name):
        if self.st_writer is None:
            return
        dir_name = os.path.join(self.st_log_folder, dashboard_name)
        os.makedirs(dir_name, exist_ok=True)
        metadata_file = os.path.join(dir_name, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(mt_dict, f)

    def get_plot_save_name(self, plot_name, dashboard_name):
        if self.st_writer:
            dir_name = os.path.join(self.st_log_folder, dashboard_name)
            os.makedirs(dir_name, exist_ok=True)
            return os.path.join(dir_name, plot_name)
        else:
            return ""

    def add_scalars(
        self,
        plot_name,
        dictn,
        count,
        dashboard_name,
        features={},
        models={},
        file_name=None,
        update_val=False,
    ):
        dashboard_name, plot_name = self.dir_friendly_name([dashboard_name, plot_name])
        dictn.update(features)
        dictn.update(models)
        new_dictn = dict(
            zip(
                self.dir_friendly_name(list(dictn.keys())),
                dictn.values(),
            )
        )
        new_dictn.update({"x_count": count})

        if self.st_writer is not None:
            dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
            plot_folder = os.path.join(dashboard_dir, "line_plots", plot_name)
            os.makedirs(plot_folder, exist_ok=True)
            if file_name is None:
                file_name = plot_name
            if self.st_writer is not None:
                self.st_writer.add_scalars(
                    new_dictn, plot_folder, file_name=file_name, update_val=update_val
                )
        if self.postgres_writer is not None:
            plot_table = dashboard_name + "_line_plots_" + plot_name
            self.postgres_writer.add_scalars(
                new_dictn, plot_table, update_val=update_val
            )

    def add_histogram(
        self,
        plot_name,
        data,
        dashboard_name,
        features=None,
        models=None,
        file_name=None,
    ):
        if self.postgres_writer is not None:
            raise Exception("Postgres Log writer not supported for Histogram")
        dashboard_name, plot_name = self.dir_friendly_name([dashboard_name, plot_name])
        if self.st_writer:
            dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
            plot_folder = os.path.join(dashboard_dir, "histograms", plot_name)
            os.makedirs(plot_folder, exist_ok=True)
            if file_name is None:
                file_name = plot_name
            self.st_writer.add_histogram(
                data, plot_folder, features=features, models=models, file_name=file_name
            )

    def add_bar_graphs(self, plot_name, data, dashboard_name, count=-1, hover_data={}):
        if self.postgres_writer is not None:
            raise Exception("Postgres Log writer not supported for Bar Graphs")
        if self.st_writer is None:
            return
        dashboard_name, plot_name = self.dir_friendly_name([dashboard_name, plot_name])
        dashboard_dir = os.path.join(self.st_log_folder, dashboard_name)
        plot_folder = os.path.join(dashboard_dir, "bar_graphs", plot_name)
        os.makedirs(plot_folder, exist_ok=True)
        self.st_writer.add_bar_graphs(data, plot_folder, count, hover_data=hover_data)

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
            message = (
                f"Dashboard: {dashboard_name}, Alert name: {alert_name}, Alert: {alert}"
            )
            self.slack_notification({"text": message})

    def slack_notification(self, message):
        try:
            http = urllib3.PoolManager()
            response = http.request(
                "POST",
                self.webhook_url,
                body=json.dumps(message),
                headers={"Content-Type": "application/json"},
                retries=False,
            )
        except Exception as e:
            print("Caught Exception")
            print(e)
