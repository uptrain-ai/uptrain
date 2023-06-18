from __future__ import annotations
import csv, _csv
import os
import shutil
import json
from typing import IO, TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from uptrain.v0.core.classes.framework import Framework
    from uptrain.v0.core.classes.helpers.config_handler import Config

from uptrain.v0.core.lib.helper_funcs import make_dir_friendly_name, clear_directory
from uptrain.v0.core.encoders import NumpyEncoder
from uptrain.v0.core.classes.logging.new_st_setup import StreamlitRunner


# -----------------------------------------------------------
# Implement LogWriters for different file formats
# -----------------------------------------------------------
def get_logs_addr_for_check(
    log_folder: str, dashboard_name: str, distance_type: str, reference: str
) -> str:
    """get the path to the log file for the dashboard."""
    dashboard_name = make_dir_friendly_name(dashboard_name)
    plot_name = make_dir_friendly_name(distance_type + "_" + str(reference))
    return os.path.join(log_folder, dashboard_name, f"{plot_name}.csv")


class LogWriter(Protocol):
    def log(self, data: dict):
        """Write data to a log file. Expects to get called multiple times."""
        ...


class CsvWriter(LogWriter):
    """
    NOTE: does this definitely work for multiple classes with a handle to the same CSV file?
    # RESPONSE: No, it didn't. Flushing after each write still leaves blank lines in the CSV.
    # SOLVED using memoization on the `make_logger` method, one file for each set of unique args to it.
    """

    file_handle: IO[str]
    writer: "_csv._writer"
    headers: list[str]
    initialized: bool

    def __init__(self, fname: str) -> None:
        self.file_handle = open(fname, "a")
        self.writer = csv.writer(self.file_handle)
        self.initialized = False
        self.headers = []

    def __del__(self):
        self.file_handle.close()

    def log(self, data: dict):
        """Create a csv file and write the header to it if it doesn't exist.
        Post that, write the data to the file.
        """
        if not self.initialized:
            self.initialized = True
            self.headers = list(data.keys())
            self.writer.writerow(self.headers)
        self.writer.writerow([data[k] for k in self.headers])


class JsonWriter(LogWriter):
    fname: str

    def __init__(self, fname: str) -> None:
        self.fname = fname

    def log(self, data: dict):
        """create a json file and write the data to it. Or append if it already exists."""
        with open(self.fname, "a") as f:
            json.dump(data, f, cls=NumpyEncoder)
            f.write("\n")


# -----------------------------------------------------------
# LogHandler object
# -----------------------------------------------------------


class LogHandler:
    list_writers: dict[str, "LogWriter"]  # cache writer objects for each file

    def __init__(self, framework: "Framework", cfg: "Config"):
        self.fw = framework
        self.path_all_data = framework.path_all_data

        self.log_folder = cfg.logging_args.log_folder
        if os.path.exists(self.log_folder):
            print(f"Deleting contents of the log folder at: {self.log_folder}")
            clear_directory(self.log_folder)
        else:
            print(f"Creating the log folder at: {self.log_folder}")
            os.makedirs(self.log_folder, exist_ok=True)
        self.list_writers = dict()

        # serialize the config to a json file so the consumers can read it
        cfg_file = os.path.join(self.log_folder, "config.json")
        with open(cfg_file, "w") as f:
            f.write(cfg.json())

        # initialize the streamlit dashboard
        self.st_runner = StreamlitRunner(self.log_folder, cfg.logging_args.dashboard_port)
        if cfg.logging_args.run_background_streamlit:
            self.st_runner.start()
        else:
            print(
                "To start the streamlit dashboard, run the following command: ",
                self.st_runner.launch_cmd,
            )

        # Get Webhook URL for alerting on slack
        self.webhook_url = cfg.logging_args.slack_webhook_url

    def make_logger(
        self, dashboard_name: str, plot_name: str, fmt: str = "csv"
    ) -> LogWriter:
        """Initialize a CSV logger that the `check` object can write data to."""
        dashboard_name = make_dir_friendly_name(dashboard_name)
        plot_name = make_dir_friendly_name(plot_name)

        dir_name = os.path.join(self.log_folder, dashboard_name)
        os.makedirs(dir_name, exist_ok=True)
        fname = os.path.join(dir_name, f"{plot_name}.{fmt}")

        if fname not in self.list_writers:
            if fmt == "json":
                self.list_writers[fname] = JsonWriter(fname)
            elif fmt == "csv":
                self.list_writers[fname] = CsvWriter(fname)
            else:
                raise ValueError(f"Unknown format for the log-file: {fmt}")
        return self.list_writers[fname]

    def add_alert(self, alert_name, alert, dashboard_name):
        dashboard_name = make_dir_friendly_name(dashboard_name)
        dashboard_dir = os.path.join(self.log_folder, dashboard_name)
        plot_folder = os.path.join(dashboard_dir, "alerts")
        os.makedirs(plot_folder, exist_ok=True)

        file_name = os.path.join(plot_folder, str(alert_name) + ".json")
        with open(file_name, "w") as f:
            json.dump(alert, f)

        if self.webhook_url:
            message = (
                f"Dashboard: {dashboard_name}, Alert name: {alert_name}, Alert: {alert}"
            )
            self.slack_notification({"text": message})

    def slack_notification(self, message):
        import urllib3

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
