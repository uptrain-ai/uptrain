"""
Implement checks to test if a piece of text has been taken from a source.  
"""

from __future__ import annotations
import typing as t
import yaml
import os

from loguru import logger
from pydantic import BaseModel, Field
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.openai_evals import OpenaiEval

UPTRAIN_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@register_op
class OpenAIGradeScore(BaseModel):
    score_type: str = "correct"
    col_in_input: str = "prompt"
    col_in_completion: str = "response"
    col_out: str = get_output_col_name_at(0)
    eval_name: str

    def make_executor(self, settings: t.Optional[Settings] = None):
        return OpenAIGradeExecutor(self, settings)


class OpenAIGradeExecutor(OperatorExecutor):
    op: OpenAIGradeScore
    settings: Settings

    def __init__(self, op: OpenAIGradeScore, settings: t.Optional[Settings] = None):
        self.op = op
        self.settings = settings

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text_input = data.get_column(self.op.col_in_input)
        text_completion = data.get_column(self.op.col_in_completion)

        samples = pl.from_dict({"input": text_input, "completion": text_completion})
        grading_op = OpenaiEval(
            bundle_path="",
            completion_name="gpt-3.5-turbo",
            eval_name=self.op.eval_name,
        )

        res = grading_op.make_executor(settings=self.settings).run(samples)["extra"][
            "metrics"
        ]
        return {"output": data.with_columns([pl.Series(self.op.col_out, res["score"])])}


@register_op
class ModelGradeScore(BaseModel):
    col_in_input: str
    col_in_completion: str
    col_out: str = get_output_col_name_at(0)
    grading_prompt_template: str
    eval_type: str = "cot_classify"
    choice_strings: list
    choice_scores: dict
    grading_prompt_mapping: dict

    def make_executor(self, settings: t.Optional[Settings] = None):
        return ModelGradeExecutor(self, settings)


class ModelGradeExecutor(OperatorExecutor):
    op: ModelGradeScore
    settings: Settings

    def __init__(self, op: ModelGradeScore, settings: t.Optional[Settings] = None):
        self.op = op
        self.settings = settings

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text_input = data.get_column(self.op.col_in_input)
        text_completion = data.get_column(self.op.col_in_completion)

        grade_spec_dictn = {
            "uptrain_custom": {
                "prompt": self.op.grading_prompt_template,
                "eval_type": self.op.eval_type,
                "choice_strings": self.op.choice_strings,
                "choice_scores": self.op.choice_scores,
                "input_outputs": {
                    self.op.grading_prompt_mapping[
                        self.op.col_in_input
                    ]: self.op.grading_prompt_mapping[self.op.col_in_completion]
                },
            }
        }

        eval_dictn = {
            "uptrain_custom_grading_eval": {"id": "uptrain_custom_grading_eval.v0"},
            "uptrain_custom_grading_eval.v0": {
                "class": "evals.elsuite.modelgraded.classify:ModelBasedClassify",
                "args": {"modelgraded_spec": "uptrain_custom"},
            },
        }

        BASE_DIR = os.path.join(UPTRAIN_BASE_DIR, "openai_eval_custom")
        os.makedirs(
            os.path.join(BASE_DIR, "custom_registry", "modelgraded"), exist_ok=True
        )
        with open(
            os.path.join(BASE_DIR, "custom_registry", "modelgraded", "tmp_custom.yaml"),
            "w",
        ) as f:
            yaml.dump(grade_spec_dictn, f)

        os.makedirs(os.path.join(BASE_DIR, "custom_registry", "evals"), exist_ok=True)
        with open(
            os.path.join(BASE_DIR, "custom_registry", "evals", "tmp_custom.yaml"), "w"
        ) as f:
            yaml.dump(eval_dictn, f)

        samples = pl.from_dict(
            {
                self.op.grading_prompt_mapping[self.op.col_in_input]: text_input,
                self.op.grading_prompt_mapping[
                    self.op.col_in_completion
                ]: text_completion,
            }
        )
        grading_op = OpenaiEval(
            bundle_path=BASE_DIR,
            completion_name="gpt-3.5-turbo",
            eval_name="uptrain_custom_grading_eval",
        )
        res = grading_op.make_executor(settings=self.settings).run(samples)["extra"][
            "metrics"
        ]
        return {"output": data.with_columns([pl.Series(self.op.col_out, res["score"])])}
