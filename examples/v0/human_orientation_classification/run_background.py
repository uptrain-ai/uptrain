#!pip install torch imgaug

import os
import subprocess
import zipfile
import numpy as np
import torch
import uptrain.v0 as v0
import time

from helper_files import read_json, KpsDataset
from helper_files import plot_all_cluster, body_length_from_kps

data_dir = "data"
remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/data.zip"
orig_training_file = "data/training_data.json"
if not os.path.exists(data_dir):
    print("Starting to download example dataset...")
    try:
        # Most Linux distributions have Wget installed by default.
        # Below command is to install wget for MacOS
        wget_installed_ok = subprocess.call(
            "brew install wget",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        print("Successfully installed wget")
    except:
        dummy = 1
    try:
        if not os.path.exists("data.zip"):
            file_downloaded_ok = subprocess.call(
                "wget " + remote_url,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            print("Data downloaded")
        with zipfile.ZipFile("data.zip", "r") as zip_ref:
            zip_ref.extractall("./")
        print("Prepared Example Dataset")
        os.remove("data.zip")
    except Exception as e:
        print(e)
        print("Could not load training data")
        print("Please follow following steps to manually download data")
        print(
            "Step 1: Paste the link https://oodles-dev-training-data.s3.amazonaws.com/data.zip in your browser"
        )
        print(
            "Step 2: Once the zip file is downloaded, unzip it here (i.e. YOUR_LOC/uptrain/examples/1_orientation_classification/"
        )
else:
    print("Example dataset already present")

training_file = "data/training_data.json"

# A testing dataset to evaluate model performance
golden_testing_file = "data/golden_testing_data.json"

# The data-points which the models sees in production
real_world_test_cases = "data/real_world_testing_data.json"

# To annotate the collected data points, we extract the ground truth from a master annotation file
# (we can also import from any other annotation pipelines such as an annotation job on Mechanical turk).
annotation_args = {"master_file": "data/master_annotation_data.json"}

# Let's visualize some of the training examples
training_data = read_json(training_file, dataframe=True)
training_data.head()

from helper_files import get_accuracy_torch, train_model_torch, BinaryClassification

train_model_torch(training_file, "version_0")

checks = [
    {
        "type": v0.Monitor.DATA_DRIFT,
        "reference_dataset": orig_training_file,
        "is_embedding": True,
        "measurable_args": {
            "type": v0.MeasurableType.INPUT_FEATURE,
            "feature_name": "kps",  # keypoints
        },
    }
]

print("Data Drift checks: ", checks)

# Define the training pipeline to annotate collected edge cases and retrain the model automatically
training_args = {
    "annotation_method": {
        "method": v0.AnnotationMethod.MASTER_FILE,
        "args": annotation_args,
    },
    "training_func": train_model_torch,
    "orig_training_file": orig_training_file,
}

# Define evaluation pipeline to test retrained model against original model
evaluation_args = {
    "inference_func": get_accuracy_torch,
    "golden_testing_dataset": golden_testing_file,
}

print("Training Pipelines: ", training_args, "\n")
print("Evaluation Pipelines: ", evaluation_args)

# ### Step 4: Initialize the UpTrain Framework

cfg = {
    "checks": checks,
    "training_args": training_args,
    "evaluation_args": evaluation_args,
    # Don't retrain
    "retrain_after": 300,
    # A local folder to store the retraining dataset
    "retraining_folder": "uptrain_smart_data",
    # A function to visualize clusters in the data
    "cluster_visualize_func": plot_all_cluster,
    "logging_args": {"st_logging": True},
    "run_background_log_consumer": True,
}

# Initialize the UpTrain framework object with config
framework = v0.Framework(cfg)
print("Successfully Initialized UpTrain Framework")

inference_batch_size = 16
model_dir = "trained_models_torch/"
model_save_name = "version_0"
real_world_dataset = KpsDataset(
    real_world_test_cases, batch_size=inference_batch_size, is_test=True
)
model = BinaryClassification()
model.load_state_dict(torch.load(model_dir + model_save_name))
model.eval()

for i, elem in enumerate(real_world_dataset):
    # Do model prediction
    inputs = {"kps": elem[0]["kps"], "id": elem[0]["id"]}
    x_test = torch.tensor(inputs["kps"]).type(torch.float)
    test_logits = model(x_test).squeeze()
    preds = torch.round(torch.sigmoid(test_logits)).detach().numpy()

    # Log model inputs and outputs to the uptrain Framework to monitor data drift
    idens = framework.log(inputs=inputs, outputs=preds)
    time.sleep(0.01)
