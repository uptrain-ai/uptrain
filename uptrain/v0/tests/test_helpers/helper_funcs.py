import numpy as np
import pandas as pd
from sklearn import preprocessing
import os
import subprocess

def process(data): 
    data["diff_lat"] = abs(data["pickup_latitude"] - data["dropoff_latitude"])
    data["diff_lon"] = abs(data["pickup_longitude"] - data["dropoff_longitude"])
    
    data["dist"] = np.sqrt(np.power(data["diff_lat"],2) + np.power(data["diff_lon"],2))

    data["pickup_datetime"] = pd.to_datetime(data["pickup_datetime"])
    
    data["pickup_year"] = data["pickup_datetime"].dt.year
    data["pickup_month"] = data["pickup_datetime"].dt.month
    data["pickup_day"] = data["pickup_datetime"].dt.day
    data["pickup_dow"] = data["pickup_datetime"].dt.dayofweek
    data["pickup_hour"] = data["pickup_datetime"].dt.hour
    data["pickup_min"] = data["pickup_datetime"].dt.minute
    data["pickup_sec"] = data["pickup_datetime"].dt.second
    
    data = data.drop(["diff_lat", "diff_lon", "pickup_longitude", "pickup_latitude", "dropoff_latitude", "dropoff_longitude", "id", "pickup_datetime"], axis = 1)
    data = data.drop(["dropoff_datetime"], axis = 1)

    le = preprocessing.LabelEncoder()
    data["store_and_fwd_flag"] = le.fit_transform(data["store_and_fwd_flag"])
    return data


def download_dataset(data_file):    
    remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/trip_duration_dataset.csv"

    if not os.path.exists(data_file):
        print("Installing wget to download dataset from remote")
        try:
            # Most Linux distributions have Wget installed by default.
            # Below command is to install wget for MacOS
            wget_installed_ok = subprocess.call("brew install wget", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print("Successfully installed wget")
        except:
            print("Wget installation fails! Checking if data is manually downloaded")
            dummy = 1
        try:
            print("Downloading data from the remote server")
            file_downloaded_ok = subprocess.call("wget " + remote_url, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print("Data downloaded")
        except Exception as e:
            print(e)
            print("Could not load training data")
            print("Please follow following steps to manually download data")
            print(f"Step 1: Open in browser: {remote_url}")
            print("Step 2: Download and move the file to the example location (i.e. uptrain/examples/ride_time_estimation/")
    else:
        print("Data file exists. Skipping download.")
