from __future__ import annotations

import typing as t

from pydantic import BaseModel


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
    data: list[dict]
    checks: list[t.Any]
    metadata: dict
    schema_dict: dict
    project: str


class EvaluateV3(BaseModel):
    model: str
    project_name: str
    dataset_name: str
    checks: list[t.Any]
    metadata: dict = None


class ProjectsList(BaseModel):
    user_name: str
    data: list[t.Any]


class ProjectData(BaseModel):
    data: list[t.Any]
    project_name: str
