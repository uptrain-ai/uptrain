"""
Implement operators to evaluate question-response-guideline and question-response datapoints for a 
LLM-powered agent pipeline. 
"""

from __future__ import annotations
from loguru import logger

import json
import polars as pl
import typing as t

from uptrain.operators.language.llm import LLMMulticlient
from uptrain.operators.language.prompts.classic import (
    GUIDELINE_ADHERENCE_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.few_shots import (
    GUIDELINE_ADHERENCE_FEW_SHOT__CLASSIFY,
    GUIDELINE_ADHERENCE_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import CHAIN_OF_THOUGHT, CLASSIFY
from uptrain.operators.language.prompts.output_format import (
    GUIDELINE_ADHERENCE_OUTPUT_FORMAT__CLASSIFY,
    GUIDELINE_ADHERENCE_OUTPUT_FORMAT__COT,
)
from uptrain.utilities.prompt_utils import parse_scenario_description

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import (
    register_op,
    ColumnOp,
    TYPE_TABLE_OUTPUT,
)
from uptrain.utilities import polars_to_json_serializable_dict


@register_op
class GuidelineAdherenceScore(ColumnOp):
    """
    Grade if the LLM agent follows the given guideline or not.

     Attributes:
        col_question (str): Column name for the stored questions
        col_response (str): Column name for the stored responses
        guideline (str): Guideline to be followed
        guideline_name (str): Name the given guideline to be used in the score column name
        response_schema (str | None): Schema of the response if it is in form of a json string
        col_out (str): Column name to output scores
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"
    guideline: str
    guideline_name: str = "guideline"
    response_schema: t.Union[str, None] = None
    col_out: str = "score_guideline_adherence"
    scenario_description: t.Optional[str] = None
    score_mapping: dict = {"A": 1.0, "B": 0.0}

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
            row["question"] = row.pop(self.col_question)
            row["response"] = row.pop(self.col_response)

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "GuidelineAdherence",
                    data_send,
                    {
                        "guideline": self.guideline,
                        "guideline_name": self.guideline_name,
                        "response_schema": self.response_schema,
                        "scenario_description": self.scenario_description,
                    },
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `GuidelineAdherenceScore`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {f"score_{self.guideline_name}_adherence": self.col_out}
                )
            )
        }

    def guideline_adherence_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B"]
        return is_correct

    def guideline_adherence_cot_validate_func(self, llm_output):
        is_correct = self.guideline_adherence_classify_validate_func(llm_output)
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
            few_shot_examples = GUIDELINE_ADHERENCE_FEW_SHOT__CLASSIFY
            output_format = GUIDELINE_ADHERENCE_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.guideline_adherence_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = GUIDELINE_ADHERENCE_FEW_SHOT__COT
            output_format = GUIDELINE_ADHERENCE_OUTPUT_FORMAT__COT
            validation_func = self.guideline_adherence_cot_validate_func
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
                    "guideline": self.guideline,
                }
            )
            try:
                grading_prompt_template = GUIDELINE_ADHERENCE_PROMPT_TEMPLATE.replace(
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
                "score_guideline_adherence": None,
                "explanation_guideline_adherence": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_guideline_adherence"] = float(score)
                output["explanation_guideline_adherence"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))

        results = [val for _, val in sorted(results, key=lambda x: x[0])]
        return results
