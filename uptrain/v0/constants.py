from enum import Enum
from uptrain.v0.core.lib.model_signal_funcs import *


class AnnotationMethod(Enum):
    MASTER_FILE = 1


class DataDriftAlgo(str, Enum):
    DDM = "DDM"
    ADWIN = "ADWIN"


class BiasAlgo(str, Enum):
    POPULARITY_BIAS = "popularity_bias"


class MeasurableType(str, Enum):
    INPUT_FEATURE = "input_feature"
    FEATURE_CONCAT = "feature_concat"
    PREDICTION = "prediction"
    CUSTOM = "custom"
    ACCURACY = "accuracy"
    MAE = "MAE"
    MAPE = "MAPE"
    CONDITION_ON_INPUT = "condition_on_input"
    CONDITION_ON_PREDICTION = "condition_on_prediction"
    SCALAR_FROM_EMBEDDING = "scalar_from_embedding"
    DISTANCE = "distance"
    REC_HIT_RATE = "hit_rate"
    GRAMMAR_SCORE = "grammar_score"


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


class Monitor(str, Enum):
    ACCURACY = "accuracy"
    EDGE_CASE = "edge_case"
    DATA_DRIFT = "data_drift"
    FEATURE_DRIFT = "feature_drift"
    CUSTOM_MONITOR = "custom_monitor"
    CONCEPT_DRIFT = "concept_drift"
    POPULARITY_BIAS = "popularity_bias"
    DATA_INTEGRITY = "data_integrity"
    OUTPUT_COMPARISON = "output_comparison"


class PlotType(str, Enum):
    BAR_CHART = "bar_chart"
    HISTOGRAM = "histogram"
    LINE_CHART = "line_chart"
    SCATTER_PLOT = "scatter_plot"


class Statistic(str, Enum):
    DISTANCE = "distance"
    DISTRIBUTION_STATS = "distribution_stats"
    CONVERGENCE_STATS = "convergence_stats"
    FINETUNE = "finetune"
    NORM_EMBEDDING = "norm_embedding"


class Visual(str, Enum):
    UMAP = "UMAP"
    TSNE = "t-SNE"
    SHAP = "SHAP"
    PLOT = "PLOT"


class ClusteringAlgorithm(str, Enum):
    DBSCAN = "DBSCAN"
    HDBSCAN = "HDBSCAN"


class ComparisonModel(str, Enum):
    FASTER_WHISPER = "faster_whisper"


class ComparisonMetric(str, Enum):
    ROGUE_L_F1 = "rogue-l-f"
