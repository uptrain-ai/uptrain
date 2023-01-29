import os
import csv
import threading


class StreamlitLogs:

    def __init__(self, log_folder, log_every=10):
        self.log_every = log_every
        self.placeholders = {}
        self.prev_values = {}
        self.dfs = {}
        self.counts = {}
        self.log_folder = log_folder

        remote_st_py_file = 'https://raw.githubusercontent.com/uptrain-ai/uptrain/vipul/uptrain/core/classes/logging/st_run.py'
        cmd = "streamlit run " + remote_st_py_file + " -- " + self.log_folder
        launch_st = lambda: os.system(cmd)
        t = threading.Thread(target=launch_st, args=([]))
        t.start()


    def add_scalars(self, name, dict, folder):
        # list of column names
        field_names = dict.keys()

        # CSV file that includes the data 
        file_name = os.path.join(folder, name + '.csv')
        if not os.path.isfile(file_name):
            with open(file_name, 'w', newline='') as f_object:
                writer = csv.writer(f_object)
                writer.writerow(field_names)
        
        with open(file_name, 'a') as f_object:
            dictwriter_object = csv.DictWriter(f_object, fieldnames=field_names)
            dictwriter_object.writerow(dict)
            f_object.close()


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
