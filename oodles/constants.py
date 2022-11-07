from enum import Enum
from oodles.core.lib.model_signal_funcs import *


class ModelSignal(Enum):
    DEFAULT = 1
    CROSS_ENTROPY_CONFIDENCE = 2
    BINARY_ENTROPY_CONFIDENCE = 3


MODEL_SIGNAL_TO_FN_MAPPING = {
    ModelSignal.DEFAULT: pass_none,
    ModelSignal.CROSS_ENTROPY_CONFIDENCE: cross_entropy_confidence,
    ModelSignal.BINARY_ENTROPY_CONFIDENCE: binary_entropy_confidence,
}


class AnnotationMethod:
    MASTER_FILE = 1
