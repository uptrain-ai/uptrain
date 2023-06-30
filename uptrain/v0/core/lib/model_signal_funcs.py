import numpy as np


def cross_entropy_confidence(inputs, outputs, gts=None, extra_args={}):
    logits = np.reshape(np.array(outputs), (len(outputs), -1))
    logits = logits - np.max(logits, axis=1)
    logits = np.exp(logits)
    logits = logits / np.sum(logits, axis=1)
    conf = np.max(logits, axis=1)
    return conf


def binary_entropy_confidence(inputs, outputs, gts=None, extra_args={}):
    conf = np.reshape(np.array(outputs), -1)
    conf = np.greater_equal(conf, 0.5) * conf + np.less(conf, 0.5) * (1 - conf)
    return conf


def pass_all(inputs, outputs, gts=None, extra_args={}):
    return True


def pass_none(inputs, outputs, gts=None, extra_args={}):
    return False
