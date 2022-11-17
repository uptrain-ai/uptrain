import numpy as np

from oodles.core.classes.framework import Framework
from oodles.core.classes.anomalies.signal import Signal
from oodles.core.lib.decorators import signal_fn, monitor
from oodles.core.constants import ModelSignal


# Define your signal
@signal_fn
def demo_signal(inputs, outputs, extra_args={}):
    return bool(np.max(np.array(inputs)) > extra_args["val_threshold"])


# Define your signal formulae
framework = Framework()
framework.add_signal_formulae(
    (
        Signal("Demo", demo_signal, extra_args={"val_threshold": 1})
        & Signal(
            ModelSignal.CROSS_ENTROPY_CONFIDENCE,
            is_model_signal=True,
            extra_args={"conf_threshold": 0.8},
        )
    )
    | Signal(
        ModelSignal.CROSS_ENTROPY_CONFIDENCE,
        is_model_signal=True,
        extra_args={"conf_threshold": 0.4},
    )
)


proxy_input_data = [[np.random.normal(0, 0.5, 5)] for x in range(10000)]


@monitor(framework)
def proxy_model(input):
    return [np.random.uniform(0, 2, 3)]


for datapoint in proxy_input_data:
    output = proxy_model(datapoint)

print(
    "Selected %d from a total of %d data-points"
    % (framework.selected_count, framework.predicted_count)
)
