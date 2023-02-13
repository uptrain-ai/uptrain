import os
import subprocess

def download_dataset(data_file):    
    remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/NSL_KDD_binary.csv"

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
            if not os.path.exists("data.zip"):
                print("Downloading data from the remote server")
                file_downloaded_ok = subprocess.call("wget " + remote_url, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print("Data downloaded")
        except:
            print(e)
            print("Could not load training data")
            print("Please follow following steps to manually download data")
            print("Step 1: Open in browser: https://oodles-dev-training-data.s3.amazonaws.com/NSL_KDD_binary.csv")
            print("Step 2: Download and move the file to example location (i.e. uptrain/examples/2_cyber_attack_classification/")
    else:
        print("Data file exists. Skipping download.")

    print(str(data_file) + " dataset prepared successfully!")

def pretty(d, indent=0):
    if isinstance(d, list):
        for value in d:
            if isinstance(value, list):
                pretty(value, indent)
            elif isinstance(value, dict):
                pretty(value, indent)
            else:
                print('\t' * (indent) + str(value))
    else:
        for key, value in d.items():
            print('\t' * indent + "- " + str(key) + ":")
            if isinstance(value, list):
                pretty(value, indent+1)
            elif isinstance(value, dict):
                pretty(value, indent+1)
            else:
                print('\t' * (indent+1) + str(value))