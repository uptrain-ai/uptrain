"""
Implement checks to test if a piece of text has been taken from a source.  
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel, Field
import polars as pl

from uptrain.operators.base import *

if t.TYPE_CHECKING:
    from uptrain.framework.config import *

from uptrain.operators.language.openai_evals import OpenaiEval


class SchemaModelGradeScore(BaseModel):
    in_col_input: str = "prompt"
    in_col_completion: str = "response"
    out_col: str = get_output_col_name_at(0)


@register_op
class ModelGradeScore(BaseModel):
    dataschema: SchemaModelGradeScore = Field(default_factory=SchemaModelGradeScore)
    score_type: str = "correct"

    def make_executor(self, settings: t.Optional[Settings] = None):
        return ModelGradeExecutor(self, settings)


class ModelGradeExecutor(OperatorExecutor):
    op: ModelGradeScore

    def __init__(self, op: ModelGradeScore, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text_input = data.get_column(self.op.dataschema.in_col_input)
        text_completion = data.get_column(self.op.dataschema.in_col_completion)

        samples = pl.from_dict({"input": text_input, "completion": text_completion})

        grading_op = OpenaiEval(
            bundle_path="",
            completion_name="gpt-3.5-turbo",
            eval_name="coqa-closedqa-correct",
        )
        res = grading_op.make_executor().run(samples)

        scores = []
        for event in res["extra"]["all_events"]:
            if "data" in event:
                if "score" in event["data"]:
                    scores.append(event["data"]["score"])
        return {
            "output": data.with_columns([pl.Series(self.op.dataschema.out_col, scores)])
        }
