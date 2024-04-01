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

from uptrain.operators.language.prompts.classic import (
    CONTEXT_CONCISENESS_PROMPT_TEMPLATE,
    CONTEXT_RELEVANCE_PROMPT_TEMPLATE,
    CONTEXT_RERANKING_PROMPT_TEMPLATE,
    RESPONSE_COMPLETENESS_WRT_CONTEXT_PROMPT_TEMPLATE,
)

from uptrain.operators.language.prompts.few_shots import (
    CONTEXT_CONCISENESS_FEW_SHOT__CLASSIFY,
    CONTEXT_CONCISENESS_FEW_SHOT__COT,
    CONTEXT_RELEVANCE_FEW_SHOT__CLASSIFY,
    CONTEXT_RELEVANCE_FEW_SHOT__COT,
    CONTEXT_RERANKING_FEW_SHOT__CLASSIFY,
    CONTEXT_RERANKING_FEW_SHOT__COT,
    RESPONSE_COMPLETENESS_WRT_CONTEXT_FEW_SHOT__CLASSIFY,
    RESPONSE_COMPLETENESS_WRT_CONTEXT_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import (
    CLASSIFY,
    CHAIN_OF_THOUGHT,
)
from uptrain.operators.language.prompts.output_format import (
    CONTEXT_CONCISENESS_OUTPUT_FORMAT__CLASSIFY,
    CONTEXT_CONCISENESS_OUTPUT_FORMAT__COT,
    CONTEXT_RELEVANCE_OUTPUT_FORMAT__CLASSIFY,
    CONTEXT_RELEVANCE_OUTPUT_FORMAT__COT,
    CONTEXT_RERANKING_OUTPUT_FORMAT__CLASSIFY,
    CONTEXT_RERANKING_OUTPUT_FORMAT__COT,
    RESPONSE_COMPLETENESS_WRT_CONTEXT_OUTPUT_FORMAT__CLASSIFY,
    RESPONSE_COMPLETENESS_WRT_CONTEXT_OUTPUT_FORMAT__COT,
)


@register_op
class ContextRelevance(ColumnOp):
    """
    Grade how relevant the context was to the question asked.

    Attributes:
        col_question: (str) Column name for the stored questions
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
            row["context"] = row.pop(self.col_context)

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
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
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B", "C"]
        return is_correct

    def context_relevance_cot_validate_func(self, llm_output):
        is_correct = self.context_relevance_classify_validate_func(llm_output)
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


@register_op
class ResponseCompletenessWrtContext(ColumnOp):
    """
    Grades if the response is able to answer the question asked completely with respect to the context or not.

    Attributes:
        col_question: (str) Column name for the stored questions
        col_response: (str) Coloumn name for stored response
        col_context: (str) Column name for stored context
        col_out: (str) Column name for the output score
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"
    col_context: str = "context"
    col_out: str = "score_response_completeness_wrt_context"
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
                    "response_completeness_wrt_context",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(
                f"Failed to run evaluation for `ResponseCompletenessWrtContext`: {e}"
            )
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_response_completeness_wrt_context": self.col_out}
                )
            )
        }

    def response_completeness_wrt_context_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B", "C"]
        return is_correct

    def response_completeness_wrt_context_cot_validate_func(self, llm_output):
        is_correct = self.response_completeness_wrt_context_classify_validate_func(
            llm_output
        )
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
            few_shot_examples = RESPONSE_COMPLETENESS_WRT_CONTEXT_FEW_SHOT__CLASSIFY
            output_format = RESPONSE_COMPLETENESS_WRT_CONTEXT_OUTPUT_FORMAT__CLASSIFY
            validation_func = (
                self.response_completeness_wrt_context_classify_validate_func
            )
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = RESPONSE_COMPLETENESS_WRT_CONTEXT_FEW_SHOT__COT
            output_format = RESPONSE_COMPLETENESS_WRT_CONTEXT_OUTPUT_FORMAT__COT
            validation_func = self.response_completeness_wrt_context_cot_validate_func
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
                grading_prompt_template = (
                    RESPONSE_COMPLETENESS_WRT_CONTEXT_PROMPT_TEMPLATE.replace(
                        "{scenario_description}", self.scenario_description
                    ).format(**kwargs)
                )
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
                "score_response_completeness_wrt_context": None,
                "explanation_response_completeness_wrt_context": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_response_completeness_wrt_context"] = float(score)
                output["explanation_response_completeness_wrt_context"] = (
                    res.response.choices[0].message.content
                )
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))

        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results


@register_op
class ContextReranking(ColumnOp):
    """
    Rerank the context based on the relevance to the question asked.

    Attributes:
        col_question: (str) Column name for the stored questions
        col_context: (str) Coloumn name for stored context
        col_reranked_context: (str) Column name for the output reranked context
        col_out (str): Column name to output scores
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_context: str = "context"
    col_reranked_context: str = "reranked_context"
    col_out: str = "score_context_reranking"
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
            row["question"] = row.pop(self.col_question)
            row["context"] = row.pop(self.col_context)
            row["reranked_context"] = row.pop(self.col_reranked_context)

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "context_reranking",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ContextReranking`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_context_reranking": self.col_out})
            )
        }

    def context_reranking_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B", "C"]
        return is_correct

    def context_reranking_cot_validate_func(self, llm_output):
        is_correct = self.context_reranking_classify_validate_func(llm_output)
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
            few_shot_examples = CONTEXT_RERANKING_FEW_SHOT__CLASSIFY
            output_format = CONTEXT_RERANKING_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.context_reranking_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = CONTEXT_RERANKING_FEW_SHOT__COT
            output_format = CONTEXT_RERANKING_OUTPUT_FORMAT__COT
            validation_func = self.context_reranking_cot_validate_func
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
                grading_prompt_template = CONTEXT_RERANKING_PROMPT_TEMPLATE.replace(
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
                "score_context_reranking": None,
                "explanation_context_reranking": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_context_reranking"] = float(score)
                output["explanation_context_reranking"] = res.response.choices[
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
class ContextConciseness(ColumnOp):
    """
    Grade how concise the new context is with respect to the original context.

    Attributes:
        col_question: (str) Column name for the stored questions
        col_context: (str) Coloumn name for stored context
        col_concise_context: (str) Column name for the output concise context
        col_out (str): Column name to output scores
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_context: str = "context"
    col_concise_context: str = "concise_context"
    col_out: str = "score_context_conciseness"
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
            row["question"] = row.pop(self.col_question)
            row["context"] = row.pop(self.col_context)
            row["concise_context"] = row.pop(self.col_concise_context)

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "context_conciseness",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ContextConciseness`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_context_conciseness": self.col_out}
                )
            )
        }

    def context_conciseness_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B", "C"]
        return is_correct

    def context_conciseness_cot_validate_func(self, llm_output):
        is_correct = self.context_conciseness_classify_validate_func(llm_output)
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
            few_shot_examples = CONTEXT_CONCISENESS_FEW_SHOT__CLASSIFY
            output_format = CONTEXT_CONCISENESS_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.context_conciseness_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = CONTEXT_CONCISENESS_FEW_SHOT__COT
            output_format = CONTEXT_CONCISENESS_OUTPUT_FORMAT__COT
            validation_func = self.context_conciseness_cot_validate_func
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
                grading_prompt_template = CONTEXT_CONCISENESS_PROMPT_TEMPLATE.replace(
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
                "score_context_conciseness": None,
                "explanation_context_conciseness": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_context_conciseness"] = float(score)
                output["explanation_context_conciseness"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )

            results.append((idx, output))

        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results
