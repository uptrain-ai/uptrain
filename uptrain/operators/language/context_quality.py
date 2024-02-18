"""
Implement operators to evaluate retrieval quality i.e. quality of the extracted context.
"""

from __future__ import annotations
import typing as t
import json

from loguru import logger
import polars as pl

from uptrain.utilities.prompt_utils import parse_scenario_description

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import register_op, ColumnOp, TYPE_TABLE_OUTPUT
from uptrain.utilities import polars_to_json_serializable_dict
from uptrain.operators.language.llm import LLMMulticlient

from uptrain.operators.language.prompts.classic import CONTEXT_RELEVANCE_PROMPT_TEMPLATE
from uptrain.operators.language.prompts.few_shots import (
    CONTEXT_RELEVANCE_FEW_SHOT__CLASSIFY,
    CONTEXT_RELEVANCE_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import (
    CLASSIFY,
    CHAIN_OF_THOUGHT,
)
from uptrain.operators.language.prompts.output_format import (
    CONTEXT_RELEVANCE_OUTPUT_FORMAT__CLASSIFY,
    CONTEXT_RELEVANCE_OUTPUT_FORMAT__COT,
)


@register_op
class ContextRelevance(ColumnOp):
    """
    Grade how relevant the context was to the question asked.

    Attributes:
        col_question: (str) Column Name for the stored questions
        col_context: (str) Coloumn name for stored context
        col_out (str): Column name to output scores
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_context: str = "context"
    col_out: str = "score_context_relevance"
    scenario_description: t.Optional[str] = None
    score_mapping: dict = {"A": 1.0, "B": 0.5, "C": 0.0}

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self.settings = settings
        if self.settings.evaluate_locally:
            self._api_client = LLMMulticlient(settings)
        else:
            self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = polars_to_json_serializable_dict(data)
        for row in data_send:
            row["question"] = row.pop(self.col_question)
            row["context"] = row.pop(self.col_context)

        try:
            if self.settings.evaluate_locally:
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "context_relevance",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ContextRelevance`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_context_relevance": self.col_out})
            )
        }

    def context_relevance_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in json.loads(llm_output))
        is_correct = is_correct and json.loads(llm_output)["Choice"] in ["A", "B", "C"]
        return is_correct

    def context_relevance_cot_validate_func(self, llm_output):
        is_correct = self.context_relevance_classify_validate_func(llm_output)
        is_correct = is_correct and ("Reasoning" in json.loads(llm_output))
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
            few_shot_examples = CONTEXT_RELEVANCE_FEW_SHOT__CLASSIFY
            output_format = CONTEXT_RELEVANCE_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.context_relevance_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = CONTEXT_RELEVANCE_FEW_SHOT__COT
            output_format = CONTEXT_RELEVANCE_OUTPUT_FORMAT__COT
            validation_func = self.context_relevance_cot_validate_func
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
                grading_prompt_template = CONTEXT_RELEVANCE_PROMPT_TEMPLATE.replace(
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
                "score_context_relevance": None,
                "explanation_context_relevance": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_context_relevance"] = float(score)
                output["explanation_context_relevance"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))
        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results
