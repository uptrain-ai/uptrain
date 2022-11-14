import sys
import pdb
import os

sys.path.append(os.getcwd())
from contextlib import redirect_stdout
from datetime import datetime

import tensorflow as tf
from dataset import KpsDataset, read_json, ClassicalKpsDataset
from model import make_model
from sklearn.linear_model import LogisticRegression
import joblib
import pickle

def train_raw(training_file, model_save_name,logistic_reg=False):
    print(
        "Training on: ",
        training_file,
        " which has ",
        len(read_json(training_file)),
        " data-points",
    )
    if logistic_reg=False:
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
    else:
        print("Training on: ", training_file, " which has ",len(read_json(training_file)), " data-points")
        training_dataset = ClassicalKpsDataset(training_file, normalization=True)
        X_train, y_train = training_dataset.load_x_y_from_data()
        model= LogisticRegression()
        model.fit(X_train,y_train)
        if not os.path.exists('trained_models/'):
            os.mkdir('trained_models/')
        filename = "trained_models/" + model_save_name
        joblib.dump(model,filename)
        print("Model saved at: ", "trained_models/" + model_save_name)
        
       


def train_model(training_file, model_save_name,logistic_reg=False):
    if logistic_reg=False:
        print_training_info = True
        if not print_training_info:
            if not os.path.exists("training_logs"):
                os.mkdir("training_logs")
            with open("training_logs/" + str(datetime.now()) + ".txt", "w") as f:
                with redirect_stdout(f):
                    train_raw(training_file, model_save_name)
        else:
            train_raw(training_file, model_save_name)
    else:
        train_raw(training_file,model_save_name,logistic_reg=False)
        
      
