"""
Implement checks to test language quality on different aspects. 

This module provides the `Critique` class, which evaluates a text generation on multiple 
aspects - fluence, politeness, grammar, and coherence,. It provides a score for each of the 
aspects on a scale of 0 to 1, along with an explanation for the score. 
"""

from __future__ import annotations
import json
import typing as t

from loguru import logger
import polars as pl

from uptrain.operators.language.llm import LLMMulticlient
from uptrain.operators.language.prompts.classic import (
    LANGUAGE_FLUENCY_PROMPT_TEMPLATE,
    LANGUAGE_COHERENCE_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.few_shots import (
    LANGUAGE_FLUENCY_FEW_SHOT__CLASSIFY,
    LANGUAGE_FLUENCY_FEW_SHOT__COT,
    LANGUAGE_COHERENCE_FEW_SHOT__CLASSIFY,
    LANGUAGE_COHERENCE_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import CHAIN_OF_THOUGHT, CLASSIFY
from uptrain.operators.language.prompts.output_format import (
    LANGUAGE_FLUENCY_OUTPUT_FORMAT__CLASSIFY,
    LANGUAGE_FLUENCY_OUTPUT_FORMAT__COT,
    LANGUAGE_COHERENCE_OUTPUT_FORMAT__CLASSIFY,
    LANGUAGE_COHERENCE_OUTPUT_FORMAT__COT,
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
class LanguageCritique(ColumnOp):
    """
    Operator to score the fluency of machine generated responses.
    It provides a score for each of the aspects on a scale of 0 to 1, along with an
    explanation for the score.

    Attributes:
        col_response (str): The name of the input column containing response text
        col_out (str): The name of the output column containing the scores
        scenario_description (str | None): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_response: str = "response"
    col_out: str = "score_language_critique"
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
                results = self._api_client.evaluate("critique_language", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `LanguageCritique`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_language_critique": self.col_out})
            )
        }

    def critique_language_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B", "C"]
        return is_correct

    def critique_language_cot_validate_func(self, llm_output):
        is_correct = self.critique_language_classify_validate_func(llm_output)
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
            few_shot_examples = LANGUAGE_FLUENCY_FEW_SHOT__CLASSIFY
            output_format = LANGUAGE_FLUENCY_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.critique_language_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = LANGUAGE_FLUENCY_FEW_SHOT__COT
            output_format = LANGUAGE_FLUENCY_OUTPUT_FORMAT__COT
            validation_func = self.critique_language_cot_validate_func
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
                grading_prompt_template = LANGUAGE_FLUENCY_PROMPT_TEMPLATE.replace(
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
                "score_critique_language": None,
                "explanation_critique_language": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_critique_language"] = float(score)
                output["explanation_critique_language"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))

        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results


@register_op
class ResponseCoherence(ColumnOp):
    """
    Operator to score the coherence of machine generated responses.
    It provides a score for each of the aspects on a scale of 0 to 1, along with an
    explanation for the score.

    Attributes:
        col_response (str): The name of the input column containing response text
        col_out (str): The name of the output column containing the scores
        scenario_description (str | None): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_response: str = "response"
    col_out: str = "score_response_coherence"
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
                results = self._api_client.evaluate("critique_language", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `LanguageCritique`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_response_coherence": self.col_out}
                )
            )
        }

    def critique_language_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B", "C"]
        return is_correct

    def critique_language_cot_validate_func(self, llm_output):
        is_correct = self.critique_language_classify_validate_func(llm_output)
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
            few_shot_examples = LANGUAGE_COHERENCE_FEW_SHOT__CLASSIFY
            output_format = LANGUAGE_COHERENCE_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.critique_language_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = LANGUAGE_COHERENCE_FEW_SHOT__COT
            output_format = LANGUAGE_COHERENCE_OUTPUT_FORMAT__COT
            validation_func = self.critique_language_cot_validate_func
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
                grading_prompt_template = LANGUAGE_COHERENCE_PROMPT_TEMPLATE.replace(
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
                "score_response_coherence": None,
                "explanation_response_coherence": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_response_coherence"] = float(score)
                output["explanation_response_coherence"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))

        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results
