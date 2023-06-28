"""
Implement checks to test if a piece of text has been taken from a source.

"""

from __future__ import annotations
import typing as t
import yaml
import os

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.openai_evals import OpenaiEval

UPTRAIN_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@register_op
class OpenAIGradeScore(ColumnOp):
    """
    Operator to calculate the grade score of text completions using OpenAI models.

    Args:
        score_type (str): The type of score to calculate ("correct" or "grade").
        col_in_input (str): The name of the input column containing the prompts.
        col_in_completion (str): The name of the input column containing the completions.
        eval_name (str): The name of the OpenAI evaluation to use.

    Returns:
        dict: A dictionary containing the calculated grade scores.

    """

    score_type: str = "correct"
    col_in_input: str = "prompt"
    col_in_completion: str = "response"
    eval_name: str
    _settings: Settings

    def setup(self, settings: Settings) -> None:
        self._settings = settings
        return self

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        samples = data.select(
            [
                pl.col(self.col_in_input).alias("input"),
                pl.col(self.col_in_completion).alias("completion"),
            ]
        )
        grading_op = OpenaiEval(
            bundle_path="",
            completion_name="gpt-3.5-turbo",
            eval_name=self.eval_name,
        )

        grading_op.setup(settings=self._settings)
        oaieval_res = grading_op.run(samples)
        assert (
            "extra" in oaieval_res
            and "metrics" in oaieval_res["extra"]
            and "score" in oaieval_res["extra"]["metrics"]
        )
        return {
            "output": pl.Series(oaieval_res["extra"]["metrics"]["score"]).alias(
                get_output_col_name_at(0)
            )
        }


@register_op
class ModelGradeScore(ColumnOp):
    """
    Operator to calculate the grade score of text completions using a custom grading model.

    Args:
        col_in_input (str): The name of the input column containing the prompts.
        col_in_completion (str): The name of the input column containing the completions.
        grading_prompt_template (str): The template for the grading prompt.
        eval_type (str): The type of evaluation for grading ("cot_classify" by default).
        choice_strings (list[str]): The list of choice strings for grading.
        choice_scores (dict): The dictionary mapping choice strings to scores.
        grading_prompt_mapping (dict): The mapping of column names to grading prompt variables.

    Returns:
        dict: A dictionary containing the calculated grade scores.

    """

    col_in_input: str
    col_in_completion: str
    grading_prompt_template: str
    eval_type: str = "cot_classify"
    choice_strings: list[str]
    choice_scores: dict
    grading_prompt_mapping: dict
    _settings: Settings

    def setup(self, settings: Settings) -> None:
        self._settings = settings
        return self

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        text_input = data.get_column(self.col_in_input)
        text_completion = data.get_column(self.col_in_completion)

        grade_spec_dictn = {
            "uptrain_custom": {
                "prompt": self.grading_prompt_template,
                "eval_type": self.eval_type,
                "choice_strings": self.choice_strings,
                "choice_scores": self.choice_scores,
                "input_outputs": {
                    self.grading_prompt_mapping[
                        self.col_in_input
                    ]: self.grading_prompt_mapping[self.col_in_completion]
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
                self.grading_prompt_mapping[self.col_in_input]: text_input,
                self.grading_prompt_mapping[self.col_in_completion]: text_completion,
            }
        )
        grading_op = OpenaiEval(
            bundle_path=BASE_DIR,
            completion_name="gpt-3.5-turbo",
            eval_name="uptrain_custom_grading_eval",
        )
        grading_op.setup(settings=self._settings)
        oaieval_res = grading_op.run(samples)
        assert (
            "extra" in oaieval_res
            and "metrics" in oaieval_res["extra"]
            and "score" in oaieval_res["extra"]["metrics"]
        )
        return {
            "output": pl.Series(oaieval_res["extra"]["metrics"]["score"]).alias(
                get_output_col_name_at(0)
            )
        }
