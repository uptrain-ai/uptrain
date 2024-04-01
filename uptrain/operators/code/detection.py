"""
Implement operator to detect code in a response.
"""

from __future__ import annotations
import json
import typing as t

from loguru import logger
import polars as pl
from uptrain.operators.language.llm import LLMMulticlient
from uptrain.operators.language.prompts.classic import (
    CODE_HALLUCINATION_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.few_shots import (
    CODE_HALLUCINATION_FEW_SHOT__CLASSIFY,
    CODE_HALLUCINATION_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import CHAIN_OF_THOUGHT, CLASSIFY
from uptrain.operators.language.prompts.output_format import (
    CODE_HALLUCINATION_OUTPUT_FORMAT__CLASSIFY,
    CODE_HALLUCINATION_OUTPUT_FORMAT__COT,
)
from uptrain.utilities.prompt_utils import parse_scenario_description

from uptrain.operators.base import (
    ColumnOp,
    register_op,
    TYPE_TABLE_OUTPUT,
)
from uptrain.framework.base import Settings

from uptrain.utilities import polars_to_json_serializable_dict


@register_op
class CodeHallucinationScore(ColumnOp):
    """
    Go through the response and identify if the code part in it is hallucinating or not.
    If found, it returns the code snippet.

    Attributes:
        col_response (str): Column name for the stored responses
        col_question (str): Column name for the stored questions
        col_context (str): Column name for the stored contexts
        col_out (str): Column name to output scores
        scenario_description (str | None): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_response: str = "response"
    col_question: str = "question"
    col_context: str = "context"
    col_out: str = "score_code_hallucination"
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
            row["context"] = row.pop(self.col_context)

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate("code_hallucination", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `CodeHallucination`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_code_hallucination": self.col_out}
                )
            )
        }

    def code_hallucination_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B"]
        return is_correct

    def code_hallucination_cot_validate_func(self, llm_output):
        is_correct = self.code_hallucination_classify_validate_func(llm_output)
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
            few_shot_examples = CODE_HALLUCINATION_FEW_SHOT__CLASSIFY
            output_format = CODE_HALLUCINATION_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.code_hallucination_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = CODE_HALLUCINATION_FEW_SHOT__COT
            output_format = CODE_HALLUCINATION_OUTPUT_FORMAT__COT
            validation_func = self.code_hallucination_cot_validate_func
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
                grading_prompt_template = CODE_HALLUCINATION_PROMPT_TEMPLATE.replace(
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
                "score_code_hallucination": None,
                "explanation_code_hallucination": None,
                "code_snippet": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                snippet = json.loads(res.response.choices[0].message.content).get(
                    "Snippet", None
                )
                output["score_code_hallucination"] = float(score)
                output["explanation_code_hallucination"] = res.response.choices[
                    0
                ].message.content
                if snippet:
                    output["code_snippet"] = snippet
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))

        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results
