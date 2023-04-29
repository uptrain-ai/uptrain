import importlib.util
import os
import socket
import threading
from typing import Optional


def get_free_port(port):
    HOST = "localhost"
    # Creates a new socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        # Try to connect to the given host and port
        if sock.connect_ex((HOST, port)):
            sock.close()
            print(f"Dashboard available at port {port}.")
            return port
        else:
            print(f"Port {port} is in use, trying port {port+1}.")
            port += 1
            sock.close()


class StreamlitRunner:
    log_folder: str
    launch_cmd: str

    def __init__(self, log_folder: str, port: Optional[int] = None):
        self.log_folder = log_folder

        path_uptrain_init: str = importlib.util.find_spec("uptrain").origin  # type: ignore
        path_st_run = os.path.join(
            os.path.dirname(path_uptrain_init), "core/classes/logging/new_st_run.py"
        )
        port = get_free_port(int(8501 if port is None else port))
        self.launch_cmd = f"streamlit run {path_st_run} --server.port {str(port)} -- {self.log_folder}"

    def start(self):
        t = threading.Thread(target=lambda: os.system(self.launch_cmd), args=([]))
        t.start()
