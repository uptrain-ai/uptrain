import numpy as np
import uptrain


# Define your signal
def demo_signal(inputs, outputs, gts=None, extra_args={}):
    feats = np.array(inputs['feats'])
    feats_shape = list(feats.shape)
    return np.max(feats, axis=tuple(range(1,len(feats_shape)))) > extra_args["val_threshold"]


def test_edge_case_detection():
    # Define your signal formulae
    signal = (
            uptrain.Signal("Demo", demo_signal, extra_args={"val_threshold": 1})
            & (uptrain.Signal(
                uptrain.ModelSignal.CROSS_ENTROPY_CONFIDENCE,
                is_model_signal=True) > 0.4)
            | (uptrain.Signal(
                uptrain.ModelSignal.CROSS_ENTROPY_CONFIDENCE,
                is_model_signal=True) > 0.8))
    cfg = {
    "checks": [{
        'type': uptrain.Anomaly.EDGE_CASE, 
        "signal_formulae": signal
    }],
    "retrain": False}
    framework = uptrain.Framework(cfg)

    proxy_input_data = [[np.random.normal(0, 0.5, 5)] for x in range(10000)]

    def proxy_model(inputs):
        return [np.random.uniform(0, 2, 3)]

    for datapoint in proxy_input_data:
        inputs = {'data': {"feats": datapoint}}
        outputs = proxy_model(inputs)
        framework.log(inputs=inputs, outputs=outputs)
    print(
        "Selected %d from a total of %d data-points"
        % (framework.selected_count, framework.predicted_count)
    )

if __name__ == "__main__":
    test_edge_case_detection()