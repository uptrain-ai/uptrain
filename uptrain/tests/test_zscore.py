import uptrain
from test_helpers import KpsDataset, get_data_from_remote, body_length_signal, train_model_torch, BinaryClassification
import torch


def test_zscore():
    get_data_from_remote()

    inference_batch_size = 16
    training_file = 'data/training_data.json'
    golden_testing_file = 'data/real_world_testing_data.json'
    real_world_test_cases = 'data/real_world_testing_data.json'
    annotation_args = {'master_file': 'data/master_annotation_data.json'}

    train_model_torch(training_file, 'version_0')

    cfg = {
        "checks": [
            {
                'type': uptrain.Monitor.DATA_INTEGRITY,
                'measurable_args': {
                    'type': uptrain.MeasurableType.INPUT_FEATURE,
                    'feature_name': 'kps'
                },
                'integrity_type': 'z_score',
                'threshold': 3.0,
            }
        ],
        "retraining_folder": "uptrain_smart_data_data_integrity",
    }

    framework_torch = uptrain.Framework(cfg)

    model_dir = 'trained_models_torch/'
    model_save_name = 'version_0'
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
