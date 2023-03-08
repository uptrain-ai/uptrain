import os
import subprocess

'''
This function downloads a dataset from an S3 URL using wget if available, or 
provides instructions for manual download
'''
def download_dataset(s3_url, data_file):    
    remote_url = f"{s3_url}/{data_file}"

    if not os.path.exists(data_file):
        print("Installing wget to download dataset from remote")
        try:
            # Most Linux distributions have Wget installed by default.
            # Below command is to install wget for MacOS
            subprocess.call("brew install wget", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print("Successfully installed wget")
        except:
            print("Wget installation fails! Checking if data is manually downloaded")
        try:
            if not os.path.exists("data.zip"):
                print("Downloading data from the remote server")
                subprocess.call("wget " + remote_url, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print("Data downloaded")
        except Exception as e:
            print(e)
            print("Could not load training data")
            print("Please follow following steps to manually download data")
            print(f"Step 1: Open in browser: {remote_url}")
            print("Step 2: Download and move the file to example location (i.e. uptrain/examples/fraud_detection/")
    else:
        print("Data file exists. Skipping download.")

    print(str(data_file) + " dataset prepared successfully!")


'''
This function takes in a dictionary or a list of dictionaries and prints its keys 
and values in a pretty format, using the indent parameter to specify the number of 
tabs to be used for indentation.
'''
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
