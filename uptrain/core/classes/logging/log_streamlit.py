import os
import csv
import threading
import json
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class StreamlitLogs:
    def __init__(self, log_folder, log_every=10):
        self.log_every = log_every
        self.placeholders = {}
        self.prev_values = {}
        self.dfs = {}
        self.counts = {}
        self.log_folder = log_folder

        remote_st_py_file = "https://raw.githubusercontent.com/uptrain-ai/uptrain/dashboard/uptrain/core/classes/logging/st_run.py"
        # remote_st_py_file = "../../uptrain/core/classes/logging/st_run.py"
        cmd = "streamlit run " + remote_st_py_file + " -- " + self.log_folder
        launch_st = lambda: os.system(cmd)
        t = threading.Thread(target=launch_st, args=([]))
        t.start()

    def add_scalars(self, dict, folder):
        # CSV file that includes the data
        for key in dict.keys():
            if key == "count":
                continue
            file_name = os.path.join(folder, key + ".csv")
            if not os.path.isfile(file_name):
                with open(file_name, "w", newline="") as f_object:
                    writer = csv.writer(f_object)
                    writer.writerow([key, "count"])
                    f_object.close()

            with open(file_name, "a") as f_object:
                writer_object = csv.writer(f_object)
                writer_object.writerow([dict[key], dict["count"]])
                f_object.close()

    def add_histogram(self, data, folder, count=-1):
        file_name = os.path.join(folder, str(count) + ".json")
        with open(file_name, "w") as f:
            json.dump(data, f, cls=NumpyEncoder)

    def add_alert(self, alert_name, alert, folder):
        file_name = os.path.join(folder, str(alert_name) + ".json")
        with open(file_name, "w") as f:
            json.dump(alert, f)

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
    #         help="Check anomalies for this function",
    #     )
    #     # on_click=button_callback)
    #     if button:
    #         fw.feat_slicing(relevant_feat_list, limit_list)
