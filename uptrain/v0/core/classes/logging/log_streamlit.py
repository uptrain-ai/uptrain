import os
import csv
import threading
import json
import numpy as np
import pandas as pd
import socket
import importlib.util


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


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


class StreamlitLogs:
    def __init__(self, log_folder, port=None):
        self.placeholders = {}
        self.prev_values = {}
        self.dfs = {}
        self.counts = {}
        self.log_folder = log_folder

        # remote_st_py_file = "https://raw.githubusercontent.com/uptrain-ai/uptrain/main/uptrain/core/classes/logging/st_run.py"
        # remote_st_py_file = "../../uptrain/core/classes/logging/st_run.py"

        path_uptrain_init: str = importlib.util.find_spec("uptrain").origin  # type: ignore
        remote_st_py_file = os.path.join(
            os.path.dirname(path_uptrain_init), "v0/core/classes/logging/st_run.py"
        )

        if port is None:
            cmd = "streamlit run " + remote_st_py_file + " -- " + self.log_folder
        else:
            port = get_free_port(int(port))
            cmd = (
                "streamlit run "
                + remote_st_py_file
                + f" --server.port {str(port)} "
                + " -- "
                + self.log_folder
            )
        launch_st = lambda: os.system(cmd)
        t = threading.Thread(target=launch_st, args=([]))
        t.start()

    def add_scalars(self, dict, folder, file_name="", update_val=False):
        # CSV file that includes the data
        file_name = os.path.join(folder, file_name + ".csv")
        if not os.path.isfile(file_name):
            with open(file_name, "w", newline="") as f_object:
                writer = csv.writer(f_object)
                writer.writerow(list(dict.keys()))
                f_object.close()

        if update_val:
            df = pd.read_csv(file_name)
            cond = None
            keys = list(dict.keys())
            for key in keys:
                if key[0:2] == "y_":
                    continue
                if cond is None:
                    cond = df[key] == dict[key]
                else:
                    cond = cond & (df[key] == dict[key])
            if len(df[cond]):
                for key in keys:
                    df.loc[cond, key] = dict[key]
            else:
                df = pd.concat([df, pd.DataFrame([dict])], ignore_index=True)
                for key in keys:
                    if key[0:2] == "x_":
                        df = df.sort_values(by=[key])
            df.to_csv(file_name, index=False)
        else:
            with open(file_name, "a") as f_object:
                writer_object = csv.writer(f_object)
                writer_object.writerow(list(dict.values()))
                f_object.close()

    def add_histogram(self, data, folder, models=None, features=None, file_name=""):
        if isinstance(data, dict):
            file_name = os.path.join(folder, file_name + ".json")
            if models is not None:
                data.update(models)
            if features is not None:
                data.update(features)
            with open(file_name, "w") as f:
                json.dump(data, f, cls=NumpyEncoder)
        else:
            file_name = os.path.join(folder, file_name + ".csv")
            if not os.path.isfile(file_name):
                with open(file_name, "w", newline="") as f_object:
                    writer = csv.writer(f_object)
                    all_keys = ["y_points"]
                    if models is not None:
                        all_keys.extend(list(models[0].keys()))
                    if features is not None:
                        all_keys.extend(list(features[0].keys()))
                    writer.writerow(all_keys)
                    f_object.close()

            with open(file_name, "a") as f_object:
                writer_object = csv.writer(f_object)
                for idx in range(len(data)):
                    this_point = [data[idx]]
                    if models is not None:
                        this_point.extend(list(models[idx].values()))
                    if features is not None:
                        this_point.extend(list(features[idx].values()))
                    writer_object.writerow(this_point)
                f_object.close()

    def add_alert(self, alert_name, alert, folder):
        file_name = os.path.join(folder, str(alert_name) + ".json")
        with open(file_name, "w") as f:
            json.dump(alert, f)

    def add_bar_graphs(self, data, folder, count=-1, hover_data={}):
        file_name = os.path.join(folder, str(count) + ".json")
        if len(hover_data):
            data.update({"hover_text": hover_data})
        with open(file_name, "w") as f:
            json.dump(data, f, cls=NumpyEncoder)

    # def feat_slicing(self, fw):
    #     relevant_feat_list = st.sidebar.multiselect(
    #         "Select features", fw.feat_name_list, fw.feat_name_list[0]
    #     )
    #     scol1, scol2 = st.sidebar.columns(2)
    #     limit_list = []
    #     for feat in relevant_feat_list:
    #         with scol1:
    #             lower_limit = st.sidebar.slider(f"Lower limit for {feat}", value=0.5)
    #         with scol2:
    #             upper_limit = st.sidebar.slider(f"Upper limit for {feat}", value=0.55)
    #         limit_list.append((lower_limit, upper_limit))
    #     # button_callback = lambda : fw.feat_slicing(relevant_feat_list, limit_list)

    #     # TODO: Function is run from top every time the button is clicked
    #     button = st.sidebar.button(
    #         "Check",
    #         help="Check monitors for this function",
    #     )
    #     # on_click=button_callback)
    #     if button:
    #         fw.feat_slicing(relevant_feat_list, limit_list)
