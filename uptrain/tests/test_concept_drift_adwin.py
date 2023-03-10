import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import uptrain

# Generate data for 4 distributions
random_state = np.random.RandomState(seed=1337)
params = [
    (0.2, 0.03, 1000),
    (0.5, 0.08, 1000),
    (0.8, 0.02, 1000),
    (0.6, 0.1, 1000)
]
distributions = np.array([random_state.normal(*param) for param in params])
stream = distributions.flatten()

def plot_data(drifts=None):
    _ = plt.figure(figsize=(7,3), tight_layout=True)
    gridspecs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    
    ax1, ax2 = plt.subplot(gridspecs[0]), plt.subplot(gridspecs[1])
    ax1.grid()
    ax1.plot(stream, label='stream')
    ax2.grid(axis='y')
    
    for index, dist in enumerate(distributions):
        ax2.hist(dist, label=f'dist_{index}')
    
    drift_color = 'red'
    if drifts is not None:
        for drift_detected in drifts:
            ax1.axvline(drift_detected, color=drift_color)
    plt.tight_layout()
    plt.show()

# plot_data()

cfg = {
    "checks": [
        {
            'type': uptrain.Monitor.CONCEPT_DRIFT,
            'algorithm': uptrain.DataDriftAlgo.ADWIN,
            'measurable_args': {
                'type': uptrain.MeasurableType.INPUT_FEATURE,
                'feature_name': 'data'
            },
            'delta': 0.002,
            'clock': 32,
            'max_buckets': 5,
            'min_window_length': 5,
            'grace_period': 5,
        }
    ],

    "retraining_folder": "uptraining_smart_data_concept_drift_adwin",

    "logging_args": {"st_logging": True}
}

framework = uptrain.Framework(cfg)
batch_size = 64
size = len(stream)

for i in range(size // batch_size):
    inputs = {'data': stream[i * batch_size : (i + 1) * batch_size]}
    ids = framework.log(inputs=inputs)
    gts = [0] * batch_size
    framework.log(identifiers=ids, gts=gts)
