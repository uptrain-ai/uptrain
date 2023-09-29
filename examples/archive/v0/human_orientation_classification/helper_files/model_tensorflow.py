import os
import tensorflow as tf
import numpy as np

from helper_files import KpsDataset, read_json

import random

random.seed(0)
tf.random.set_seed(0)


def make_model(input_shape=34):
    kernel_initializer = tf.keras.initializers.GlorotUniform(seed=10)
    bias_initializer = tf.keras.initializers.zeros()

    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.Dense(
        18,
        activation="relu",
        kernel_initializer=kernel_initializer,
        bias_initializer=bias_initializer,
    )(inputs)
    outputs = tf.keras.layers.Dense(
        1,
        activation="sigmoid",
        kernel_initializer=kernel_initializer,
        bias_initializer=bias_initializer,
    )(x)
    return tf.keras.Model(inputs, outputs)


def get_accuracy_tf(testing_file, model_save_name, model_dir="trained_models_tf/"):
    testing_dataset = KpsDataset(
        testing_file,
        batch_size=len(read_json(testing_file)),
        shuffle=False,
        augmentations=False,
        is_test=True,
    )
    model = tf.keras.models.load_model(model_dir + model_save_name)
    print("Evaluating on ", len(read_json(testing_file)), " data-points")

    pred_classes = []
    gt_classes = []
    for elem in testing_dataset:
        preds = model.predict(elem[0]["kps"])
        pred_class = [int(round(float(x))) for x in preds]
        pred_classes.extend(pred_class)
        gt_classes.extend(list(elem[1]))

    accuracy = np.sum(np.array(gt_classes) == np.array(pred_classes)) / len(
        pred_classes
    )
    return accuracy


def train_model_tf(training_file, model_save_name, model_dir="trained_models_tf/"):
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

    model = make_model(input_shape=34)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=5e-4),
        loss="binary_crossentropy",
        metrics=tf.keras.metrics.BinaryAccuracy(),
    )

    training_dataset = KpsDataset(training_file, shuffle=True, augmentations=True)
    x = [x[0] for x in training_dataset]
    y = [y[1] for y in training_dataset]
    dataset = tf.data.Dataset.from_tensor_slices((x, y))
    model.fit(dataset, epochs=10)
    model.save(model_loc)
    print("Model saved at: ", model_loc)
