"""
Implement checks for content coherence across long-form articles.

This module provides the `ContentCoherence` operator, which evaluates whether a
long-form machine-generated article keeps a consistent terminology throughout,
flagging cases where the same concept is referred to by different terms (for
example an article about American soccer that drifts between "soccer" and
"football").
"""

from __future__ import annotations
import typing as t
import json

from loguru import logger
import polars as pl
from uptrain.operators.language.prompts.classic import (
    CONTENT_COHERENCE_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.few_shots import (
    CONTENT_COHERENCE_FEW_SHOT__CLASSIFY,
    CONTENT_COHERENCE_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import CHAIN_OF_THOUGHT, CLASSIFY
from uptrain.operators.language.prompts.output_format import (
    CONTENT_COHERENCE_OUTPUT_FORMAT__CLASSIFY,
    CONTENT_COHERENCE_OUTPUT_FORMAT__COT,
)

from uptrain.utilities.prompt_utils import parse_scenario_description

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import register_op, ColumnOp, TYPE_TABLE_OUTPUT
from uptrain.utilities import polars_to_json_serializable_dict
from uptrain.operators.language.llm import LLMMulticlient


@register_op
class ContentCoherence(ColumnOp):
    """
    Operator to evaluate the content coherence of long-form articles.

    It checks whether a long-form article keeps consistent terminology across
    every section, i.e. that the same concept is not referred to by different
    terms as the article progresses.

    Attributes:
        col_response: (str) The name of the input column containing the article text
        col_out (str): The name of the output column containing the scores
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_response: str = "response"
    col_out: str = "score_content_coherence"
    scenario_description: t.Optional[str] = None
    score_mapping: dict = {"A": 1.0, "B": 0.5, "C": 0.0}

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self.settings = settings
        if self.settings.evaluate_locally and (
            self.settings.uptrain_access_token is None
            or not len(self.settings.uptrain_access_token)
        ):
            self._api_client = LLMMulticlient(settings)
        else:
            self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = polars_to_json_serializable_dict(data)
        for row in data_send:
            row["response"] = row.pop(self.col_response)

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "content_coherence",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ContentCoherence`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_content_coherence": self.col_out}
                )
            )
        }

    def content_coherence_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B", "C"]
        return is_correct

    def content_coherence_cot_validate_func(self, llm_output):
        is_correct = self.content_coherence_classify_validate_func(llm_output)
        is_correct = is_correct and ("Reasoning" in llm_output)
        return is_correct

    def evaluate_local(self, data):
        """
        Our methodology is based on the model grade evaluation introduced by openai evals.
        """

        self.scenario_description, scenario_vars = parse_scenario_description(
            self.scenario_description
        )
        input_payloads = []
        if self.settings.eval_type == "basic":
            few_shot_examples = CONTENT_COHERENCE_FEW_SHOT__CLASSIFY
            output_format = CONTENT_COHERENCE_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.content_coherence_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = CONTENT_COHERENCE_FEW_SHOT__COT
            output_format = CONTENT_COHERENCE_OUTPUT_FORMAT__COT
            validation_func = self.content_coherence_cot_validate_func
            prompting_instructions = CHAIN_OF_THOUGHT
        else:
            raise ValueError(
                f"Invalid eval_type: {self.settings.eval_type}. Must be either 'basic' or 'cot'"
            )

        for idx, row in enumerate(data):
            kwargs = row
            kwargs.update(
                {
                    "output_format": output_format,
                    "prompting_instructions": prompting_instructions,
                    "few_shot_examples": few_shot_examples,
                }
            )
            try:
                grading_prompt_template = CONTENT_COHERENCE_PROMPT_TEMPLATE.replace(
                    "{scenario_description}", self.scenario_description
                ).format(**kwargs)
            except KeyError as e:
                raise KeyError(
                    f"Missing required attribute(s) for scenario description: {e}"
                )
            input_payloads.append(
                self._api_client.make_payload(idx, grading_prompt_template)
            )
        output_payloads = self._api_client.fetch_responses(
            input_payloads, validation_func
        )

        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            output = {
                "score_content_coherence": None,
                "explanation_content_coherence": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_content_coherence"] = float(score)
                output["explanation_content_coherence"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))
        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results