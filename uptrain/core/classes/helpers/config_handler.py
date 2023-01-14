from pydantic import BaseModel
import typing
from datetime import datetime
from uptrain.constants import AnnotationMethod
import numpy as np


class AnnotationArgs(BaseModel):
    method: AnnotationMethod
    args: typing.Dict = {}


class TrainingArgs(BaseModel):
    orig_training_file: str = ""
    fold_name: str = "uptrain_smart_data_" + str(datetime.utcnow())
    cluster_plot_func: typing.Callable = None
    annotation_method: AnnotationArgs = {}
    training_func: typing.Callable = None
    data_transformation_func: typing.Callable = None


class EvaluationArgs(BaseModel):
    inference_func: typing.Callable = None
    golden_testing_dataset: str = None
    metrics_to_check: typing.List[str] = []


class Config(BaseModel):
    training_args: TrainingArgs = TrainingArgs()
    evaluation_args: EvaluationArgs = EvaluationArgs()
    data_identifier: str = "id"
    checks: typing.List[typing.Dict] = []
    retrain: bool = True
    retrain_after: int = 250
    data_id: typing.Literal["id", "utc_timestamp"] = "id"
    log_folder: str = "uptrain_logs"
    tb_logging: bool = True
    st_logging: bool = False
    feat_name_list: list = None


class InputArgs(BaseModel):
    data: dict
    id: typing.Optional[typing.Union[list, np.ndarray]]

    class Config:
        arbitrary_types_allowed = True


class GroundTruthArgs(BaseModel):
    gt: typing.Union[np.ndarray, list]
    id: typing.Union[np.ndarray, list]

    class Config:
        arbitrary_types_allowed = True
