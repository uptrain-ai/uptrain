"""
Here, we implement data-preprocessing for the 
publicly available NSL-KDD dataset: 
https://www.unb.ca/cic/datasets/nsl.html
"""

import pandas as pd
import numpy as np

# Assign column names
col_names = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
    "difficulty",
]

# Read the NSL-KDD dataset original training and test sets
df1 = pd.read_csv("data/NSL-KDD/KDDTrain+.txt", header=None, names=col_names)
df2 = pd.read_csv("data/NSL-KDD/KDDTest+.txt", header=None, names=col_names)

df1.drop(["difficulty"], axis=1, inplace=True)
df2.drop(["difficulty"], axis=1, inplace=True)

"""
Transform the NSL-KDD dataset to binary dataset (normal & attack).
"normal" label is set to 0, all attack labels are set to 1
"""
df1["label"][df1["label"] == "normal"] = 0
df1["label"][df1["label"] != 0] = 1
df2["label"][df2["label"] == "normal"] = 0
df2["label"][df2["label"] != 0] = 1

# Using Label encoder to transform string features to numerical features
from sklearn.preprocessing import LabelEncoder


def Encoding(df):
    cat_features = [x for x in df.columns if df[x].dtype == "object"]
    le = LabelEncoder()
    for col in cat_features:
        if col in df.columns:
            i = df.columns.get_loc(col)
            df.iloc[:, i] = df.apply(
                lambda i: le.fit_transform(i.astype(str)), axis=0, result_type="expand"
            )
    return df


df1 = Encoding(df1)
df2 = Encoding(df2)
df = df1.append(df2)

import os

data_loc = os.getcwd() + "/data/NSL-KDD"
os.makedirs(data_loc, exist_ok=True)
print("Saving to location:", data_loc)
df1.to_csv(data_loc + "/binary_train.csv", index=0)
df2.to_csv(data_loc + "/binary_test.csv", index=0)
df.to_csv(data_loc + "/binary_train_test.csv", index=0)
