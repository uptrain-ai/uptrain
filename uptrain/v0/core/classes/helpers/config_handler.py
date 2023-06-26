from __future__ import annotations
import typing
from datetime import datetime

from pydantic import BaseModel
import numpy as np

from uptrain.v0.constants import AnnotationMethod


class AnnotationArgs(BaseModel):
    method: AnnotationMethod
    args: typing.Dict = {}


class TrainingArgs(BaseModel):
    orig_training_file: str = ""
    annotation_method: AnnotationArgs = {}
    training_func: typing.Callable = None
    data_transformation_func: typing.Callable = None


class EvaluationArgs(BaseModel):
    inference_func: typing.Callable = None
    golden_testing_dataset: str = None
    metrics_to_check: typing.List[str] = []


class LoggingArgs(BaseModel):
    slack_webhook_url: str = None
    dashboard_port: int = None
    log_folder: str = "uptrain_logs"
    log_data: bool = True
    st_logging: bool = False
    postgres_logging: bool = False
    database: str = None
    run_background_streamlit: bool = True
    use_new_handler: bool = False


class LicenseArgs(BaseModel):
    openai_key: str = None


class ReaderArgs(BaseModel):
    mode: str = 'default'
    frequency_in_seconds: typing.Optional[typing.Union[float, int]] = None
    num_backlog: typing.Optional[int] = 1
    type: str = None
    sql_query: str = None
    sql_variables_dictn: typing.Optional[dict] = None
    database: str = None

class Config(BaseModel):
    training_args: TrainingArgs = TrainingArgs()
    evaluation_args: EvaluationArgs = EvaluationArgs()
    logging_args: LoggingArgs = LoggingArgs()
    license_args: LicenseArgs = LicenseArgs()
    data_identifier: str = "id"
    checks: typing.List[typing.Dict] = []
    retrain: bool = True
    retrain_after: int = 100000000000
    retraining_folder: str = "uptrain_smart_data"
    data_id: str = "id"
    feat_name_list: list = None
    cluster_visualize_func: typing.Callable = None
    use_cache: bool = False
    run_background_log_consumer: bool = False
    running_ee: bool = False
    reader_args: ReaderArgs = ReaderArgs()


# class InputArgs(BaseModel):
#     data: dict
#     id: typing.Optional[typing.Union[list, np.ndarray]]

#     class Config:
#         arbitrary_types_allowed = True


class GroundTruthArgs(BaseModel):
    gt: typing.Union[np.ndarray, list]
    id: typing.Union[np.ndarray, list]

    class Config:
        arbitrary_types_allowed = True
