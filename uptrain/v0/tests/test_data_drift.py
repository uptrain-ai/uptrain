import uptrain.v0 as v0
from test_helpers import KpsDataset, get_data_from_remote
import torch
from test_helpers import (
    body_length_signal,
    train_model_torch,
    get_accuracy_torch,
    BinaryClassification,
)


# if __name__ == "__main__":
def test_data_drift():
    get_data_from_remote()

    inference_batch_size = 16

    # Training data
    training_file = "data/training_data.json"

    # A testing dataset to evaluate model performance
    golden_testing_file = "data/golden_testing_data.json"

    # The data-points which the models sees in production
    real_world_test_cases = "data/real_world_testing_data.json"

    # To annotate the collected data points, we extract the ground truth from a master annotation file
    # (we can also import from any other annotation pipelines such as an annotation job on Mechanical turk).
    annotation_args = {"master_file": "data/master_annotation_data.json"}

    train_model_torch(training_file, "version_0")

    check1 = {
        "type": v0.Monitor.DATA_DRIFT,
        "reference_dataset": training_file,
        "is_embedding": True,
        "measurable_args": {
            "type": v0.MeasurableType.INPUT_FEATURE,
            "feature_name": "kps",
        },
    }

    check2 = {
        "type": v0.Monitor.DATA_DRIFT,
        "reference_dataset": training_file,
        "save_edge_cases": False,
        "measurable_args": {
            "type": v0.MeasurableType.SCALAR_FROM_EMBEDDING,
            "idx": 0,
            "extract_from": {
                "type": v0.MeasurableType.INPUT_FEATURE,
                "feature_name": "kps",
            },
        },
    }

    check3 = {
        "type": v0.Monitor.DATA_DRIFT,
        "reference_dataset": training_file,
        "is_embedding": False,
        "save_edge_cases": False,
        "measurable_args": {
            "type": v0.MeasurableType.CUSTOM,
            "signal_formulae": v0.Signal("Body Length", body_length_signal),
        },
    }

    checks = [check1, check2, check3]

    # Define the training pipeline to annotate data and retrain the model automatically
    training_args = {
        "annotation_method": {
            "method": v0.AnnotationMethod.MASTER_FILE,
            "args": annotation_args,
        },
        "training_func": train_model_torch,
        "orig_training_file": training_file,
    }

    # Define evaluation pipeline to test retrained model against original model
    evaluation_args = {
        "inference_func": get_accuracy_torch,
        "golden_testing_dataset": golden_testing_file,
    }

    cfg = {
        "checks": checks,
        "training_args": training_args,
        "evaluation_args": evaluation_args,
        # Retrain when 200 datapoints are collected in the retraining dataset
        "retrain_after": 200,
        # A local folder to store the retraining dataset
        "retraining_folder": "uptrain_smart_data_data_drift",
    }

    framework = v0.Framework(cfg)

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

        # Retrain only once
        if framework.version > 1:
            break
