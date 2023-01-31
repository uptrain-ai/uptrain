from enum import Enum
from uptrain.core.lib.model_signal_funcs import *


class ModelSignal(Enum):
    DEFAULT = 1
    CROSS_ENTROPY_CONFIDENCE = 2
    BINARY_ENTROPY_CONFIDENCE = 3
    PASS_ALL = 4


MODEL_SIGNAL_TO_FN_MAPPING = {
    ModelSignal.DEFAULT: pass_none,
    ModelSignal.CROSS_ENTROPY_CONFIDENCE: cross_entropy_confidence,
    ModelSignal.BINARY_ENTROPY_CONFIDENCE: binary_entropy_confidence,
    ModelSignal.PASS_ALL: pass_all,
}


class AnnotationMethod(Enum):
    MASTER_FILE = 1


class Anomaly(Enum):
    EDGE_CASE = "edge_case"
    DATA_DRIFT = "data_drift"
    CUSTOM_MONITOR = "custom_monitor"
    CONCEPT_DRIFT = "concept_drift"
    POPULARITY_BIAS = "popularity_bias"
    DATA_INTEGRITY = "data_integrity"
    AGGREGATE = "aggregate"
    DISTRIBUTION_STATS = "distribution_stats"
    CONVERGENCE_STATS = "convergence_stats"


class DataDriftAlgo(Enum):
    DDM = "DDM"


class BiasAlgo(Enum):
    POPULARITY_BIAS = "popularity_bias"


class MeasurableType(Enum):
    INPUT_FEATURE = "input_feature"
    PREDICTION = "prediction"
    CUSTOM = "custom"
    ACCURACY = "accuracy"
    CONDITION_ON_INPUT = "condition_on_input"
    CONDITION_ON_PREDICTION = "condition_on_prediction"
    SCALAR_FROM_EMBEDDING = "scalar_from_embedding"
    DISTANCE = "distance"
