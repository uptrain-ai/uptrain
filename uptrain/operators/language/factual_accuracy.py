"""
Implement operators to evaluate factual correctness of the response.
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl
import numpy as np

from uptrain.utilities.prompt_utils import parse_scenario_description

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import (
    register_op,
    ColumnOp,
    TYPE_TABLE_OUTPUT,
)
from uptrain.utilities import polars_to_json_serializable_dict
from uptrain.operators.language.llm import LLMMulticlient, parse_json

from uptrain.operators.language.prompts.classic import (
    FACT_EVAL_PROMPT_TEMPLATE,
    FACT_GENERATE_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.few_shots import (
    FACT_EVAL_FEW_SHOT__CLASSIFY,
    FACT_EVAL_FEW_SHOT__COT,
    FACT_GENERATE_FEW_SHOT,
)
from uptrain.operators.language.prompts.instructions import (
    CLASSIFY,
    CHAIN_OF_THOUGHT,
)
from uptrain.operators.language.prompts.output_format import (
    FACT_EVALUATE_OUTPUT_FORMAT__CLASSIFY,
    FACT_EVALUATE_OUTPUT_FORMAT__COT,
    FACT_GENERATE_OUTPUT_FORMAT,
)


@register_op
class ResponseFactualScore(ColumnOp):
    """
    Grade how factual the generated response was.

     Attributes:
        col_question (str): Column name for the stored questions
        col_context (str): Coloumn name for stored context
        col_response (str): Coloumn name for the stored responses
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts
    """

    col_question: str = "question"
    col_context: str = "context"
    col_response: str = "response"
    col_out: str = "score_factual_accuracy"
    scenario_description: t.Optional[str] = None
    score_mapping: dict = {"yes": 1.0, "unclear": 0.5, "no": 0.0}

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
                results = self._api_client.evaluate(
                    "factual_accuracy",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseFactualScore`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_factual_accuracy": self.col_out})
            )
        }

    def fact_generate_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and "Facts" in llm_output
        return is_correct

    def fact_eval_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and isinstance(llm_output["Result"], list)
        for row in llm_output["Result"]:
            is_correct = (
                is_correct and min([x in row for x in ["Judgement", "Fact"]]) > 0
            )
            is_correct = is_correct and row["Judgement"].lower() in [
                "yes",
                "no",
                "unclear",
            ]
        return is_correct

    def fact_eval_cot_validate_func(self, llm_output):
        is_correct = self.fact_eval_classify_validate_func(llm_output)
        for row in llm_output["Result"]:
            is_correct = is_correct and min([x in row for x in ["Reasoning"]]) > 0
        return is_correct

    def evaluate_local(self, data):
        """
        Our methodology is based on https://arxiv.org/abs/2305.14251
        FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation
        """

        # Step 0: Parse the scenario description
        self.scenario_description, scenario_vars = parse_scenario_description(
            self.scenario_description
        )

        # Step 1: Extract facts from the response
        input_payloads = []
        for idx, row in enumerate(data):
            kwargs = row
            kwargs.update(
                {
                    "output_format": FACT_GENERATE_OUTPUT_FORMAT,
                    "few_shot_examples": FACT_GENERATE_FEW_SHOT,
                }
            )
            try:
                grading_prompt_template = FACT_GENERATE_PROMPT_TEMPLATE.replace(
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
            input_payloads, self.fact_generate_validate_func
        )

        fact_results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            try:
                facts = parse_json(res.response.choices[0].message.content)
                fact_results.append((idx, facts))
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                fact_results.append((idx, []))
        fact_results = [val for _, val in sorted(fact_results, key=lambda x: x[0])]

        # Step 2: Verify the facts wrt context
        input_payloads = []
        if self.settings.eval_type == "basic":
            few_shot_examples = FACT_EVAL_FEW_SHOT__CLASSIFY
            output_format = FACT_EVALUATE_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.fact_eval_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = FACT_EVAL_FEW_SHOT__COT
            output_format = FACT_EVALUATE_OUTPUT_FORMAT__COT
            validation_func = self.fact_eval_cot_validate_func
            prompting_instructions = CHAIN_OF_THOUGHT
        else:
            raise Exception("Unknown Eval Type: Choose from 'basic' or 'cot'")

        for idx, row in enumerate(data):
            kwargs = row
            kwargs.update(
                {
                    "facts": fact_results[idx],
                    "output_format": output_format,
                    "prompting_instructions": prompting_instructions,
                    "few_shot_examples": few_shot_examples,
                }
            )
            try:
                grading_prompt_template = FACT_EVAL_PROMPT_TEMPLATE.replace(
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
                "score_factual_accuracy": None,
                "explanation_factual_accuracy": None,
            }
            try:
                judgements = [x["Judgement"] for x in parse_json(res.response.choices[0].message.content)["Result"]]
                score = np.mean([self.score_mapping[x.lower()] for x in judgements])
                output["score_factual_accuracy"] = float(score)
                output["explanation_factual_accuracy"] = res.response.choices[0].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))
        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results
