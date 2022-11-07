import sys
import pdb
import os

sys.path.append(os.getcwd())
from contextlib import redirect_stdout
from datetime import datetime

import tensorflow as tf
from dataset import KpsDataset, read_json
from model import make_model


def train_raw(training_file, model_save_name):
    print(
        "Training on: ",
        training_file,
        " which has ",
        len(read_json(training_file)),
        " data-points",
    )
    training_dataset = KpsDataset(training_file, shuffle=True, augmentations=True)
    model = make_model(input_shape=34)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=5e-4),
        loss="binary_crossentropy",
        metrics=tf.keras.metrics.BinaryAccuracy(),
    )
    model.fit(training_dataset, epochs=10)
    model.save("trained_models/" + model_save_name)
    print("Model saved at: ", "trained_models/" + model_save_name)


def train_model(training_file, model_save_name):
    print_training_info = True
    if not print_training_info:
        if not os.path.exists("training_logs"):
            os.mkdir("training_logs")
        with open("training_logs/" + str(datetime.now()) + ".txt", "w") as f:
            with redirect_stdout(f):
                train_raw(training_file, model_save_name)
    else:
        train_raw(training_file, model_save_name)
