import sys
import os
import subprocess
import zipfile
import numpy as np

import uptrain

sys.path.append("../examples/orientation_classification/")

from dataset import input_to_dataset_transformation, read_json, write_json, KpsDataset
from pushup_signal import pushup_signal
from contextlib import redirect_stdout

import joblib
import json

data_dir = "data"
remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/data.zip"
orig_training_file = "data/training_data.json"
if not os.path.exists(data_dir):
    try:
        file_downloaded_ok = subprocess.check_output("wget " + remote_url, shell=True)
    except:
        print("Could not load training data")
    with zipfile.ZipFile("data.zip", "r") as zip_ref:
        zip_ref.extractall("./")

    full_training_data = read_json(orig_training_file)
    np.random.seed(1)
    np.random.shuffle(full_training_data)
    reduced_training_data = full_training_data[0:1000]
    write_json(orig_training_file, reduced_training_data)

real_world_test_cases = "data/real_world_testing_data.json"
golden_testing_file = "data/golden_testing_data.json"
annotation_args = {"master_file": "data/master_annotation_data.json"}

# Defining the egde-case signal
pushup_edge_case = uptrain.Signal("Pushup", pushup_signal)
inference_batch_size = 1

from model_logistic_regression import get_accuracy_lr, train_model_lr

train_model_lr("data/training_data.json", "version_0")

cfg = {
    # Define your signal to identify edge cases
    "checks": [
        {"type": uptrain.Anomaly.EDGE_CASE, "signal_formulae": pushup_edge_case}
    ],
    "data_identifier": "id",
    # Connect training pipeline to annotate data and retrain the model
    "training_args": {
        "data_transformation_func": input_to_dataset_transformation,
        "annotation_method": {
            "method": uptrain.AnnotationMethod.MASTER_FILE,
            "args": annotation_args,
        },
        "training_func": train_model_lr,
        "fold_name": "uptrain_smart_data",
        "orig_training_file": orig_training_file,
    },
    # Connect evaluation pipeline to test retrained model against original model
    "evaluation_args": {
        "inference_func": get_accuracy_lr,
        "golden_testing_dataset": golden_testing_file,
        "metrics_to_check": ["accuracy"],
    },
}


# if __name__=="__main__":
def test_retrain_edge_cases():
    framework_lr = uptrain.Framework(cfg)

    testing_dataset = KpsDataset(real_world_test_cases, normalization=True)
    X_test, y_test, id = testing_dataset.load_x_y_from_data()
    model = joblib.load("trained_models_lr/" + "version_0")
    for i in range(int(np.ceil(len(X_test) / inference_batch_size))):

        elem = X_test[
            i * inference_batch_size : min((i + 1) * inference_batch_size, len(X_test))
        ]
        ids = id[
            i * inference_batch_size : min((i + 1) * inference_batch_size, len(X_test))
        ]

        # Do model prediction
        inputs = {"data": {"kps": elem}, "id": ids}
        preds = model.predict(inputs["data"]["kps"])
        idens = framework_lr.log(inputs=inputs, outputs=preds)

        # Attach Ground Truth
        gts = y_test[
            i * inference_batch_size : min((i + 1) * inference_batch_size, len(X_test))
        ]
        framework_lr.log(gts=gts, identifiers=idens)

        if framework_lr.version > 1:
            # Retrain only once
            break
