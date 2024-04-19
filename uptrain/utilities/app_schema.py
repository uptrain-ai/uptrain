from __future__ import annotations

import typing as t

from pydantic import BaseModel

import datetime as dt

class Dataset(BaseModel):
    name: str
    version: t.Optional[int]


class TopicGenerate(BaseModel):
    items: list[t.Any]
    scores: list[t.Any]


class UserCreate(BaseModel):
    name: str


class Evaluate(BaseModel):
    eval_name: str
    dataset: list[dict]
    params: dict


class EvaluateV2(BaseModel):
    data: list[dict] #done
    sink_data: list[dict] #done
    checks: list[dict] #done
    metadata: dict #
    schema_dict: dict
    project: str #done
    evaluation: str #done
    exp_column: t.Optional[str] = None

class DefaultRun(BaseModel):
    model: t.Any
    dataset_id: t.Any
    evaluation_name: t.Any
    checks: t.Any
    project_id: t.Any
    metadata: t.Any

class ProjectDataset(BaseModel):
    name: str
    version: t.Optional[int]
    id: str

class DefaultPrompt(BaseModel):
    project_id: str
    model: str
    dataset_id: str
    prompt: str
    prompt_name: str
    checks: t.Any
    metadata: t.Any


class EvalCreate(BaseModel):
    evaluation_id: str
    evaluation_name: str
    dataset_id: str
    project_id: str
    address: str
    user_id: str
    run_type: str
    checks: dict
    prompt_id: t.Optional[str] = None
    exp_column: t.Optional[str] = None


class EvaluateV3(BaseModel):
    model: str
    project_name: str
    dataset_name: str
    checks: list[t.Any]
    metadata: dict = None

class ProjectRun(BaseModel):
    project_id: str
    created_at: dt.datetime
    evaluation_name: str
    evaluation_id: str
    dataset_id: str
    run_type: str
    exp_column: t.Optional[str] = None

class PromptRun(BaseModel):
    evaluation_id: str
    prompt_id: str
    prompt_name: str
    prompt_version: t.Union[str, int]
    prompt: str
    created_at: dt.datetime
    dataset_id: str
    scores: dict


class ProjectsList(BaseModel):
    user_name: str
    data: list[t.Any]


class ProjectData(BaseModel):
    data: list[t.Any]
    id: str


class Project(BaseModel):
    project_id: str
    project_type: str
    created_at: dt.datetime
    project_name: str
    dataset_id: t.Union[str, None]
    checks: t.Union[list[dict], dict, None]