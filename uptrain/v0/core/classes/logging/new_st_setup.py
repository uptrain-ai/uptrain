import importlib.util
import os
import threading
from typing import Optional


class StreamlitRunner:
    log_folder: str
    launch_cmd: str

    def __init__(self, log_folder: str, port: Optional[int] = None):
        self.log_folder = log_folder

        path_uptrain_init: str = importlib.util.find_spec("uptrain").origin  # type: ignore
        path_st_run = os.path.join(
            os.path.dirname(path_uptrain_init), "v0/core/classes/logging/new_st_run.py"
        )
        port_arg = "" if port is None else f"--server.port {port}"
        self.launch_cmd = f"streamlit run {path_st_run} {port_arg} -- {self.log_folder}"

    def start(self):
        t = threading.Thread(target=lambda: os.system(self.launch_cmd), args=([]))
        t.start()
