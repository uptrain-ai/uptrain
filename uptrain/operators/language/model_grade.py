"""
Implement checks to test if a piece of text has been taken from a source.

"""

from __future__ import annotations
import typing as t
import os

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.openai_evals import OpenaiEval
from uptrain.operators.language.llm import LLMMulticlient, Payload
from evals.elsuite.modelgraded.classify_utils import (
    append_answer_prompt,
    get_choice,
    get_choice_score,
)


@register_op
class OpenAIGradeScore(ColumnOp):
    """
    Operator to calculate the grade score of text completions using OpenAI models.

    Attributes:
        col_in_input (str): The name of the input column containing the prompts.
        col_in_completion (str): The name of the input column containing the completions.
        eval_name (str): The name of the OpenAI evaluation to use.
        col_out (str): The name of the output column containing the grade scores.

    Returns:
        dict: A dictionary containing the calculated grade scores.

    """

    col_in_input: str = "prompt"
    col_in_completion: str = "response"
    col_out: str = "openai_grade_score"
    eval_name: str

    def setup(self, settings: Settings):
        self._settings = settings
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
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

        results = pl.Series(oaieval_res["extra"]["metrics"]["score"])
        return {"output": data.with_columns([results.alias(self.col_out)])}


@register_op
class ModelGradeScore(ColumnOp):
    """
    Operator to calculate the grade score of text completions using a custom prompt
    for grading. It is a wrapper using the same utilities from the OpenAI evals library,
    replacing just the completion call.

    Attributes:
        grading_prompt_template (str): Template for the grading prompt.
        eval_type (Literal["cot_classify", "classify", "classify_cot"]): The type of evaluation for grading ("cot_classify" by default).
        choice_strings (list[str]): The list of choice strings for grading.
        choice_scores (dict[str, float]): The dictionary mapping choice strings to scores.
        context_vars (dict[str, str]): A dictionary mapping context variable names to corresponding
            columns in the input dataset.

    """

    grading_prompt_template: str
    eval_type: t.Literal["cot_classify", "classify", "classify_cot"] = "cot_classify"
    choice_strings: list[str]
    choice_scores: t.Union[dict[str, float], dict[str, list[float]]]
    context_vars: dict[str, str]
    col_out: t.Union[str, list[str]] = "model_grade_score"

    def setup(self, settings: Settings):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def _make_payload(self, id: t.Any, messages: list[dict]) -> Payload:
        return Payload(
            endpoint="chat.completions",
            data={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.2},
            metadata={"index": id},
        )

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        prompts = []
        for row in data.rows(named=True):
            subs = {k: row[v] for k, v in self.context_vars.items()}
            # fill in context variables in the prompt template
            _prompt = self.grading_prompt_template.format(**subs)
            # following the `evals` code to create the grading instruction
            #  https://github.com/openai/evals/blob/main/evals/elsuite/modelgraded/classify_utils.py
            _prompt_chat = append_answer_prompt(
                prompt=[{"role": "user", "content": _prompt}],
                eval_type=self.eval_type,
                choice_strings=self.choice_strings,
            )
            prompts.append(_prompt_chat)

        input_payloads = [
            self._make_payload(idx, prompt_msgs)
            for idx, prompt_msgs in enumerate(prompts)
        ]
        output_payloads = self._api_client.fetch_responses(input_payloads)

        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                try:
                    resp_text = res.response["choices"][0]["message"]["content"]
                    choice = get_choice(
                        text=resp_text,
                        eval_type=self.eval_type,
                        match_fn="starts_or_endswith",
                        choice_strings=self.choice_strings,
                    )
                    score = get_choice_score(
                        choice, self.choice_strings, self.choice_scores
                    )
                    results.append((idx, score))
                except Exception as e:
                    logger.error(
                        f"Error when processing payload at index {idx}, not an API error: {e}"
                    )
                    results.append((idx, None))

        if isinstance(self.col_out, list):
            sorted(results, key=lambda x: x[0])
            result_scores = [
                pl.Series(
                    [val[idx] if val is not None else None for _, val in results]
                ).alias(self.col_out[idx])
                for idx in range(len(self.col_out))
            ]
        else:
            result_scores = pl.Series(
                [val for _, val in sorted(results, key=lambda x: x[0])]
            ).alias(self.col_out)
        return {"output": data.with_columns(result_scores)}
