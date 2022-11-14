import tensorflow as tf
import numpy as np

from dataset import KpsDataset, read_json, ClassicalKpsDataset

import joblib
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


def get_accuracy(testing_file, model_save_name,logistic_reg=True):
    if logistic_reg==False:
        testing_dataset = KpsDataset(
            testing_file,
            batch_size=len(read_json(testing_file)),
            shuffle=False,
            augmentations=False,
            is_test=True,
        )
        model = tf.keras.models.load_model("trained_models/" + model_save_name)
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
    else:
        testing_dataset = ClassicalKpsDataset(testing_file,normalization=True)
        X_test, y_test = testing_dataset.load_x_y_from_data()
        model = joblib.load("trained_models/" + model_save_name)
        print("Evaluating on ", len(read_json(testing_file)), " data-points")
        pred_classes = []
        gt_classes = []
        pred_classes = model.predict(X_test)
        gt_classes = y_test
        count = 0
        for i in range(len(pred_classes)):
            if pred_classes[i]==y_test[i]:
                count+=1
     
                   
        accuracy = count/len(pred_classes)
        return accuracy
        
        
        


def run_real_world_inference(testing_file, model_save_name, predict_fn,logistic_reg==False):
    if logistic_reg==False:
        testing_dataset = KpsDataset(
            testing_file, batch_size=1, shuffle=False, augmentations=False, is_test=True
        )
        model = tf.keras.models.load_model("trained_models/" + model_save_name)

        pred_classes = []
        for i,elem in enumerate(testing_dataset):
            preds = predict_fn({"model": model, "kps": elem[0]["kps"], "id": elem[0]["id"]})
            pred_class = int(round(float(preds)))
            pred_classes.append(pred_class)
            if i > 1500:
                break
    else:
        testing_dataset = ClassicalKpsDataset(testing_file,normalization=True)
        X_test, y_test = testing_dataset.load_x_y_from_data()
        model = joblib.load("trained_models/" + model_save_name)
        pred_classes = model.predict(X_test)
        count=0
        for i in range(len(pred_classes)):
            if pred_classes[i]==y_test[i]:
                count+=1
         
