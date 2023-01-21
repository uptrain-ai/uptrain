import os
from sklearn.linear_model import LogisticRegression
import pickle

from helper_files import KpsDataset, read_json

import random
random.seed(42)


def get_accuracy_lr(testing_file, model_save_name, model_dir="trained_models_lr/"):
    testing_dataset = KpsDataset(testing_file, normalization=True)
    X_test, y_test, _ = testing_dataset.load_x_y_from_data()
    model = pickle.load(open(model_dir + model_save_name, 'rb'))
    print("Evaluating on ", len(read_json(testing_file)), " data-points")
    pred_classes = []
    pred_classes = model.predict(X_test)
    count = 0
    for i in range(len(pred_classes)):
        if pred_classes[i] == y_test[i]:
            count += 1

    accuracy = count / len(pred_classes)
    return accuracy


def run_real_world_inference(
    testing_file, model_save_name, predict_fn, model_dir="trained_models_lr/"
):
    testing_dataset = KpsDataset(testing_file, normalization=True)
    X_test, y_test = testing_dataset.load_x_y_from_data()
    model = pickle.load(open(model_dir + model_save_name, 'rb'))
    pred_classes = model.predict(X_test)
    count = 0
    for i in range(len(pred_classes)):
        if pred_classes[i] == y_test[i]:
            count += 1


def train_model_lr(training_file, model_save_name, model_dir="trained_models_lr/"):
    print(
        "Training on: ",
        training_file,
        " which has ",
        len(read_json(training_file)),
        " data-points",
    )
    model_loc = model_dir + model_save_name
    if os.path.exists(model_loc):
        print("Trained model exists. Skipping training again.")
        return
    training_dataset = KpsDataset(training_file, normalization=True)
    X_train, y_train, _ = training_dataset.load_x_y_from_data()
    model = LogisticRegression()
    model.fit(X_train, y_train)
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    pickle.dump(model, open(model_loc, 'wb'))
    print("Model saved at: ", model_dir + model_save_name)