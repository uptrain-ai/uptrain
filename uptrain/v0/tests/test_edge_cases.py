import uptrain.v0 as v0
from test_helpers import KpsDataset, get_data_from_remote, read_json
import torch
from test_helpers import (
    pushup_signal,
    train_model_torch,
    get_accuracy_torch,
    BinaryClassification,
)


# if __name__ == "__main__":
def test_edge_cases():
    get_data_from_remote()

    training_file = "data/training_data.json"
    golden_testing_file = "data/golden_testing_data.json"

    # Real world test cases contains the data-points which the models sees in production
    real_world_test_cases = "data/real_world_testing_data.json"

    # To annotate the collected data points, we extract the ground truth from the master annotation file
    # (this can also do something like schedule an annotation job on Mechanical turk or
    # integrate with your other annotation pipelines).
    annotation_args = {"master_file": "data/master_annotation_data.json"}

    # Log the collected data-points to a local folder (this can also be a SQL table, a data warehouse etc.).
    data_save_folder = "uptrain_smart_data__edge_cases"

    # Defining the pushup egde-case signal
    pushup_edge_case = v0.Signal("Pushup", pushup_signal)

    # Defining the model confidence edge-case signal
    # That is, identify model confidence <0.9 as an edge-case
    low_conf_edge_case = (
        v0.Signal(v0.ModelSignal.BINARY_ENTROPY_CONFIDENCE, is_model_signal=True) < 0.9
    )

    cfg = {
        # Define your signal to identify edge cases
        "checks": [
            {
                "type": v0.Monitor.EDGE_CASE,
                "signal_formulae": (pushup_edge_case | low_conf_edge_case),
            }
        ],
        # Connect training pipeline to annotate data and retrain the model
        "training_args": {
            "annotation_method": {
                "method": v0.AnnotationMethod.MASTER_FILE,
                "args": annotation_args,
            },
            "training_func": train_model_torch,
            "orig_training_file": training_file,
        },
        # Retrain once 250 edge cases are collected
        "retrain_after": 250,
        # A local folder to store the retraining dataset
        "retraining_folder": "uptrain_smart_data_edge_cases_torch",
        # Connect evaluation pipeline to test retrained model against original model
        "evaluation_args": {
            "inference_func": get_accuracy_torch,
            "golden_testing_dataset": golden_testing_file,
        },
    }

    framework = v0.Framework(cfg)

    inference_batch_size = 16
    model_dir = "trained_models_torch/"
    model_save_name = "version_0"
    real_world_dataset = KpsDataset(
        real_world_test_cases,
        batch_size=inference_batch_size,
        shuffle=False,
        augmentations=False,
        is_test=True,
    )
    model = BinaryClassification()
    model.load_state_dict(torch.load(model_dir + model_save_name))
    model.eval()
    gt_data = read_json(annotation_args["master_file"])
    all_gt_ids = [x["id"] for x in gt_data]

    for i, elem in enumerate(real_world_dataset):
        # Do model prediction
        inputs = {"kps": elem[0]["kps"], "id": elem[0]["id"]}
        x_test = torch.tensor(inputs["kps"]).type(torch.float)
        test_logits = model(x_test).squeeze()
        preds = torch.round(torch.sigmoid(test_logits)).detach().numpy()
        idens = framework.log(inputs=inputs, outputs=preds)

        # Attach ground truth
        this_elem_gt = [gt_data[all_gt_ids.index(x)]["gt"] for x in elem[0]["id"]]
        framework.log(identifiers=idens, gts=this_elem_gt)

        # Retrain only once
        if framework.version > 1:
            break
