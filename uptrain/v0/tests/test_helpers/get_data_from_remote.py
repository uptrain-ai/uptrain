import os
import subprocess
import zipfile
import numpy as np
from . import read_json, write_json 

def get_data_from_remote():

    data_dir = "data"
    remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/data.zip"
    orig_training_file = 'data/training_data.json'
    if not os.path.exists(data_dir):
        try:
            # Most Linux distributions have Wget installed by default.
            # Below command is to install wget for MacOS
            wget_installed_ok = subprocess.call("brew install wget", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print("Successfully installed wget")
        except:
            dummy = 1
        try:
            if not os.path.exists("data.zip"):
                file_downloaded_ok = subprocess.call("wget " + remote_url, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print("Data downloaded")
            with zipfile.ZipFile("data.zip", 'r') as zip_ref:
                zip_ref.extractall("./")
            full_training_data = read_json(orig_training_file)
            np.random.seed(1)
            np.random.shuffle(full_training_data)
            reduced_training_data = full_training_data[0:1000]
            write_json(orig_training_file, reduced_training_data)
            print("Prepared Example Dataset")
            os.remove("data.zip")
        except Exception as e:
            print(e)
            print("Could not load training data")
