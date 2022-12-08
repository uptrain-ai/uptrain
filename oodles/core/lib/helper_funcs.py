import os
import json
import csv 
import pandas as pd
import numpy as np
from collections import OrderedDict
from oodles.core.encoders.numpy_encoder import NumpyEncoder


def add_data_to_warehouse(data, path_csv):
        """Stores the dictionary "data" at location path_csv"""
        for k in list(data.keys()):
            data[k] = [json.dumps(x, cls=NumpyEncoder) for x in data[k]]    
        if not os.path.exists(path_csv):        
            pd.DataFrame(data).to_csv(path_csv, index=False)
        else:
            pd.DataFrame(data).to_csv(path_csv, index=False, mode='a', header=False)


def extract_data_point_from_batch(data, i):
        if isinstance(data, dict):
            this_data = {}
            for key in list(data.keys()):
                this_data.update(
                    {key: extract_data_point_from_batch(data[key], i)}
                )
            return this_data
        elif isinstance(data, np.ndarray):
            assert len(np.shape(data)) > 1, "Data point should be a multi-dimensional array"
            return np.array([data[i]])
        elif isinstance(data, list):
            return [data[i]]
        else:
            return data


def add_data_to_batch(data, this_data):
    """Add dat point this_data to data"""
    if isinstance(data, dict):
        assert isinstance(this_data, dict)
        for key, val in this_data.items():
            data.update({key: val})
        return data
    else:
        Exception("Invalid Data id type: %s" % type(data))

def get_df_indices_from_ids(df, ids):
    all_id_array = np.array(df['id'])
    sorter = None
    if not np.all(np.diff(all_id_array) >= 0):
        # ids are not sorted in this case
        sorter = np.argsort(all_id_array)
    return np.searchsorted(all_id_array, ids, sorter=sorter)


def read_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def write_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)

def write_csv_row(file_name, data):
    with open(file_name, 'a') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(data)
        f_object.close()

def read_csv(file_name):
    return pd.read_csv(file_name)
