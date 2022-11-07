import numpy as np
from oodles.core.lib.decorators import signal_fn


@signal_fn
def cross_entropy_confidence(inputs, outputs, extra_args={}):
    logits = np.array(outputs[0])
    logits = logits - np.max(logits)
    logits = np.exp(logits)
    logits = logits / np.sum(logits)
    conf = np.max(logits)
    if conf > extra_args["conf_threshold"]:
        return False
    else:
        return True


@signal_fn
def binary_entropy_confidence(inputs, outputs, extra_args={}):
    conf = np.array(outputs[0])
    if conf < 0.5:
        conf = 1 - conf
    if conf > extra_args["conf_threshold"]:
        return False
    else:
        return True


@signal_fn
def pass_all(inputs, outputs, extra_args={}):
    return True


@signal_fn
def pass_none(inputs, outputs, extra_args={}):
    return False
