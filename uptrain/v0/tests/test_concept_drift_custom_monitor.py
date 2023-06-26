import os
import subprocess

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import uptrain.v0 as v0
from xgboost import XGBClassifier


def test_concept_drift_custom_monitor():
    data_file = "NSL_KDD_binary.csv"
    remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/NSL_KDD_binary.csv"

    if not os.path.exists(data_file):
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
            pass

        try:
            if not os.path.exists("data.zip"):
                file_downloaded_ok = subprocess.call(
                    "wget " + remote_url,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )
                print("Data downloaded")
        except:
            print("Could not load training data")
            print("Please follow following steps to manually download data")
            print(
                "Step 1: Open in browser: https://oodles-dev-training-data.s3.amazonaws.com/NSL_KDD_binary.csv"
            )
            print(
                "Step 2: Download and move the file to example location (i.e. uptrain/examples/2_cyber_attack_classification/"
            )
    else:
        print("Data file exists. Skipping download.")

    df = pd.read_csv(data_file)
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=0.1, test_size=0.9, random_state=0, shuffle=False
    )

    # Train the XGBoost classifier with training data
    classifier = XGBClassifier()
    classifier.fit(X_train, y_train)

    y_pred = classifier.predict(X_train)
    print("Training accuracy: " + str(100 * accuracy_score(y_train, y_pred)))

    """
    Defining a custom drift metric where
    the user just want to check if accuracy
    drops beyond a threshold.
    """

    def custom_initialize_func(self):
        self.initial_acc = None
        self.acc_arr = []
        self.count = 0
        self.thres = 0.02
        self.window_size = 200
        self.is_drift_detected = False

    def custom_check_func(self, inputs, outputs, gts=None, extra_args={}):
        batch_size = len(extra_args["id"])
        self.count += batch_size
        self.acc_arr.extend(list(np.equal(gts, outputs)))

        # Calculate initial performance of the model on first 200 points
        if (self.count >= self.window_size) and (self.initial_acc is None):
            self.initial_acc = (
                sum(self.acc_arr[0 : self.window_size]) / self.window_size
            )

        # Calculate the most recent accuracy and log it to dashboard.
        if self.initial_acc is not None:
            for i in range(self.count - batch_size, self.count, self.window_size):
                # Calculate the most recent accuracy
                recent_acc = (
                    sum(self.acc_arr[i : i + self.window_size]) / self.window_size
                )

                # Logging to UpTrain dashboard
                self.log_handler.add_scalars(
                    "custom_metrics",
                    {
                        "y_initial_acc": self.initial_acc,
                        "y_recent_acc": recent_acc,
                    },
                    i,
                    self.dashboard_name,
                )

                # Send an alert when recent model performance goes down
                if (self.initial_acc - recent_acc > self.thres) and (
                    not self.is_drift_detected
                ):
                    alert = f"Concept drift detected with custom metric at time: {i}"
                    print(alert)
                    self.log_handler.add_alert(
                        "Custom Concept Drift Alert", alert, self.dashboard_name
                    )
                    self.is_drift_detected = True

    checks = [
        {
            "type": v0.Monitor.CUSTOM_MONITOR,
            "initialize_func": custom_initialize_func,
            "check_func": custom_check_func,
            "need_gt": True,
        },
    ]

    cfg = {
        # Checks to identify concept drift
        "checks": checks,
        # Folder that stores data logged by UpTrain
        "retraining_folder": "uptrain_smart_data",
    }

    # Initialize the UpTrain framework
    framework = v0.Framework(cfg)
    batch_size = len(X_test)

    for i in range(int(len(X_test) / batch_size)):
        # Do model prediction
        inputs = {"feats": X_test[i * batch_size : (i + 1) * batch_size]}
        preds = classifier.predict(inputs["feats"])

        # Log model inputs and outputs to monitor concept drift
        ids = framework.log(inputs=inputs, outputs=preds)

        # Attach ground truth to corresponding predictions
        # in UpTrain framework and identify concept drift
        ground_truth = y_test[i * batch_size : (i + 1) * batch_size]
        framework.log(identifiers=ids, gts=ground_truth)
