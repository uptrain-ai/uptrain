import os
import numpy as np
from torch import nn
import torch
from . import KpsDataset, read_json

import random

random.seed(42)
torch.manual_seed(42)


class BinaryClassification(nn.Module):
    def __init__(self):
        super(BinaryClassification, self).__init__()
        # Number of input features is 34.
        self.layer_1 = nn.Linear(34, 64)
        self.layer_out = nn.Linear(64, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.1)

    def forward(self, inputs):
        x = self.relu(self.layer_1(inputs))
        x = self.dropout(x)
        x = self.layer_out(x)
        return x


def get_accuracy_torch(
    testing_file, model_save_name, model_dir="trained_models_torch/"
):
    testing_dataset = KpsDataset(
        testing_file,
        batch_size=len(read_json(testing_file)),
        shuffle=False,
        augmentations=False,
        is_test=True,
    )
    model = BinaryClassification()
    model.load_state_dict(torch.load(model_dir + model_save_name))
    model.eval()
    print(
        "Evaluating model:",
        model_save_name,
        " on ",
        len(read_json(testing_file)),
        " data-points",
    )
    with torch.inference_mode():
        pred_classes = []
        gt_classes = []

        for ele in testing_dataset:
            X_test = ele[0]["kps"]
            y_test = ele[1]

            X_test, y_test = torch.tensor(X_test).type(torch.float), torch.tensor(
                y_test
            ).type(torch.float)
            test_logits = model(X_test).squeeze()
            pred_class = torch.round(torch.sigmoid(test_logits))
            pred_classes.extend(pred_class)
            gt_classes.extend(list(ele[1]))
    accuracy = np.sum(np.array(gt_classes) == np.array(pred_classes)) / len(
        pred_classes
    )
    return accuracy


def train_model_torch(
    training_file, model_save_name, model_dir="trained_models_torch/"
):
    model_loc = model_dir + model_save_name
    os.makedirs(model_dir, exist_ok=True)
    if os.path.exists(model_loc):
        return
    print(
        "Training on: ",
        training_file,
        " which has ",
        len(read_json(training_file)),
        " data-points",
    )
    training_dataset = KpsDataset(training_file, shuffle=True, augmentations=True)
    model = BinaryClassification()
    loss_fn = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(params=model.parameters(), lr=5e-4)
    torch.manual_seed(22)
    epochs = 2
    for epoch in range(epochs):
        model.train()
        loss_sum = 0
        for X_train, y_train in training_dataset:
            X_train = torch.tensor(X_train).type(torch.float)
            y_train = torch.tensor(y_train).type(torch.float)
            y_logits = model(X_train).squeeze()
            loss = loss_fn(y_logits, y_train)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            loss_sum += loss.item()
        print(f"Epoch {epoch}: Loss {loss_sum/len(training_dataset)}")

    torch.save(model.state_dict(), model_loc)
    print("Model saved at: ", model_loc)
