import uptrain.v0 as v0
from test_helpers import KpsDataset, get_data_from_remote
import torch
from test_helpers import body_length_signal, train_model_torch, BinaryClassification


def test_data_integrity():
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

    cfg = {
        "checks": [
            {
                "type": v0.Monitor.DATA_INTEGRITY,
                "measurable_args": {
                    "type": v0.MeasurableType.INPUT_FEATURE,
                    "feature_name": "kps",
                },
                "integrity_type": "non_null",
            },
            {
                "type": v0.Monitor.DATA_INTEGRITY,
                "measurable_args": {
                    "type": v0.MeasurableType.CUSTOM,
                    "signal_formulae": v0.Signal("body_length", body_length_signal),
                },
                "integrity_type": "greater_than",
                "threshold": 50,
            },
        ],
        "retraining_folder": "uptrain_smart_data_data_integrity",
    }

    framework_torch = v0.Framework(cfg)

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

        # Log model inputs and outputs to the uptrain Framework to monitor data integrity
        idens = framework_torch.log(inputs=inputs, outputs=preds)
