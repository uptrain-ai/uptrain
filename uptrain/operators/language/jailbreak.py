"""
Implements operators related to jailbreaking of LLMs
"""

from __future__ import annotations
from loguru import logger

import json
import polars as pl
import typing as t

from uptrain.operators.language.llm import LLMMulticlient
from uptrain.operators.language.prompts.classic import (
    JAILBREAK_DETECTION_PROMPT_TEMPLATE,
    PROMPT_INJECTION_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.few_shots import (
    JAILBREAK_DETECTION_FEW_SHOT__CLASSIFY,
    JAILBREAK_DETECTION_FEW_SHOT__COT,
    PROMPT_INJECTION_FEW_SHOT__CLASSIFY,
    PROMPT_INJECTION_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import CHAIN_OF_THOUGHT, CLASSIFY
from uptrain.operators.language.prompts.output_format import (
    JAILBREAK_DETECTION_OUTPUT_FORMAT__CLASSIFY,
    JAILBREAK_DETECTION_OUTPUT_FORMAT__COT,
    PROMPT_INJECTION_OUTPUT_FORMAT__CLASSIFY,
    PROMPT_INJECTION_OUTPUT_FORMAT__COT,
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
class JailbreakDetectionScore(ColumnOp):
    """
    Operator to check whether the user is trying to jailbreak the LLM.

    Attributes:
        col_question (str): Column name for the questions
        col_out (str): Column name to output scores
        model_purpose (str): The purpose of the LLM
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_out: str = "score_jailbreak_attempted"
    model_purpose: str = (
        "To help the users with their queries without providing them with any illegal, immoral or abusive content."
    )
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

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "JailbreakDetection",
                    data_send,
                    {
                        "model_purpose": self.model_purpose,
                        "scenario_description": self.scenario_description,
                    },
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `JailbreakDetectionScore`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_jailbreak_attempted": self.col_out}
                )
            )
        }

    def jailbreak_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B"]
        return is_correct

    def jailbreak_cot_validate_func(self, llm_output):
        is_correct = self.jailbreak_classify_validate_func(llm_output)
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
            few_shot_examples = JAILBREAK_DETECTION_FEW_SHOT__CLASSIFY
            output_format = JAILBREAK_DETECTION_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.jailbreak_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = JAILBREAK_DETECTION_FEW_SHOT__COT
            output_format = JAILBREAK_DETECTION_OUTPUT_FORMAT__COT
            validation_func = self.jailbreak_cot_validate_func
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
                    "model_purpose": self.model_purpose,
                }
            )
            try:
                grading_prompt_template = JAILBREAK_DETECTION_PROMPT_TEMPLATE.replace(
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
                "score_jailbreak_attempted": None,
                "explanation_jailbreak_attempted": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_jailbreak_attempted"] = float(score)
                output["explanation_jailbreak_attempted"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))

        results = [val for _, val in sorted(results, key=lambda x: x[0])]
        return results


# TODO: Modify in the backend as well to not use `response` for latency benefits
@register_op
class PromptInjectionScore(ColumnOp):
    """
    Grade if the LLM agent outputs the system prompt or not.

     Attributes:
        col_question (str): Column name for the stored questions
        col_out (str): Column name to output scores
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_out: str = "score_prompt_injection"
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

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "PromptInjection",
                    data_send,
                    {},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `PromptInjectionScore`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_prompt_injection": self.col_out})
            )
        }

    def prompt_injection_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B"]
        return is_correct

    def prompt_injection_cot_validate_func(self, llm_output):
        is_correct = self.prompt_injection_classify_validate_func(llm_output)
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
            few_shot_examples = PROMPT_INJECTION_FEW_SHOT__CLASSIFY
            output_format = PROMPT_INJECTION_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.prompt_injection_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = PROMPT_INJECTION_FEW_SHOT__COT
            output_format = PROMPT_INJECTION_OUTPUT_FORMAT__COT
            validation_func = self.prompt_injection_cot_validate_func
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
                grading_prompt_template = PROMPT_INJECTION_PROMPT_TEMPLATE.replace(
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
                "score_prompt_injection": None,
                "explanation_prompt_injection": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_prompt_injection"] = float(score)
                output["explanation_prompt_injection"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))

        results = [val for _, val in sorted(results, key=lambda x: x[0])]
        return results
