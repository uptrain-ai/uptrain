import importlib.util
import os
import threading
import typing as t

from loguru import logger


class StreamlitRunner:
    log_folder: str
    launch_cmd: str

    def __init__(self, log_folder: str, port: t.Optional[int] = None):
        self.log_folder = log_folder
        if "config.json" not in os.listdir(self.log_folder):
            logger.warning("No Uptrain config found in the specified log folder.")

        path_uptrain_init: str = importlib.util.find_spec("uptrain").origin  # type: ignore
        path_st_run = os.path.join(
            os.path.dirname(path_uptrain_init), "dashboard", "st_run.py"
        )
        port_arg = "" if port is None else f"--server.port {port}"
        nowatch_arg = "--server.fileWatcherType none"
        self.launch_cmd = (
            f"streamlit run {path_st_run} {port_arg} {nowatch_arg} -- {self.log_folder}"
        )
        logger.info(f"Streamlit launch command: {self.launch_cmd}")

    def start(self):
        t = threading.Thread(target=lambda: os.system(self.launch_cmd), args=([]))
        t.start()
