"""
Implement operaores to evaluate response quality i.e. quality of the generated response.
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
    RESPONSE_COMPLETENESS_PROMPT_TEMPLATE,
    RESPONSE_CONCISENESS_PROMPT_TEMPLATE,
    RESPONSE_CONSISTENCY_PROMPT_TEMPLATE,
    VALID_RESPONSE_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.few_shots import (
    RESPONSE_COMPLETENESS_FEW_SHOT__CLASSIFY,
    RESPONSE_COMPLETENESS_FEW_SHOT__COT,
    RESPONSE_CONCISENESS_FEW_SHOT__CLASSIFY,
    RESPONSE_CONCISENESS_FEW_SHOT__COT,
    RESPONSE_CONSISTENCY_FEW_SHOT__CLASSIFY,
    RESPONSE_CONSISTENCY_FEW_SHOT__COT,
    VALID_RESPONSE_FEW_SHOT__CLASSIFY,
    VALID_RESPONSE_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import CHAIN_OF_THOUGHT, CLASSIFY
from uptrain.operators.language.prompts.output_format import (
    RESPONSE_COMPLETENESS_OUTPUT_FORMAT__CLASSIFY,
    RESPONSE_COMPLETENESS_OUTPUT_FORMAT__COT,
    RESPONSE_CONCISENESS_OUTPUT_FORMAT__CLASSIFY,
    RESPONSE_CONCISENESS_OUTPUT_FORMAT__COT,
    RESPONSE_CONSISTENCY_OUTPUT_FORMAT__CLASSIFY,
    RESPONSE_CONSISTENCY_OUTPUT_FORMAT__COT,
    VALID_RESPONSE_OUTPUT_FORMAT__CLASSIFY,
    VALID_RESPONSE_OUTPUT_FORMAT__COT,
)


@register_op
class ResponseCompleteness(ColumnOp):
    """
    Grades if the response is able to answer the question asked completely or not.

    Attributes:
        col_question: (str) Column Name for the stored questions
        col_response: (str) Coloumn name for stored response
        col_out: (str) Column name for the output score
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"
    col_out: str = "score_response_completeness"
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
            row["response"] = row.pop(self.col_response)

        try:
            if self.settings.evaluate_locally:
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "response_completeness",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseCompleteness`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_response_completeness": self.col_out}
                )
            )
        }

    def response_completeness_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in json.loads(llm_output))
        is_correct = is_correct and json.loads(llm_output)["Choice"] in ["A", "B", "C"]
        return is_correct

    def response_completeness_cot_validate_func(self, llm_output):
        is_correct = self.response_completeness_classify_validate_func(llm_output)
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
            few_shot_examples = RESPONSE_COMPLETENESS_FEW_SHOT__CLASSIFY
            output_format = RESPONSE_COMPLETENESS_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.response_completeness_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = RESPONSE_COMPLETENESS_FEW_SHOT__COT
            output_format = RESPONSE_COMPLETENESS_OUTPUT_FORMAT__COT
            validation_func = self.response_completeness_cot_validate_func
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
                grading_prompt_template = RESPONSE_COMPLETENESS_PROMPT_TEMPLATE.replace(
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
                "score_response_completeness": None,
                "explanation_response_completeness": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_response_completeness"] = float(score)
                output["explanation_response_completeness"] = res.response.choices[
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
class ResponseConciseness(ColumnOp):
    """
    Grades if the response is concise or not.

    Attributes:
        col_question: (str) Column Name for the stored questions
        col_response: (str) Coloumn name for stored response
        col_out: (str) Column name for the output score
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"
    col_out: str = "score_response_conciseness"
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
            row["response"] = row.pop(self.col_response)

        try:
            if self.settings.evaluate_locally:
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "response_conciseness",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseConciseness`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_response_conciseness": self.col_out}
                )
            )
        }

    def response_conciseness_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in json.loads(llm_output))
        is_correct = is_correct and json.loads(llm_output)["Choice"] in ["A", "B", "C"]
        return is_correct

    def response_conciseness_cot_validate_func(self, llm_output):
        is_correct = self.response_conciseness_classify_validate_func(llm_output)
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
            few_shot_examples = RESPONSE_CONCISENESS_FEW_SHOT__CLASSIFY
            output_format = RESPONSE_CONCISENESS_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.response_conciseness_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = RESPONSE_CONCISENESS_FEW_SHOT__COT
            output_format = RESPONSE_CONCISENESS_OUTPUT_FORMAT__COT
            validation_func = self.response_conciseness_cot_validate_func
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
                grading_prompt_template = RESPONSE_CONCISENESS_PROMPT_TEMPLATE.replace(
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
                "score_response_conciseness": None,
                "explanation_response_conciseness": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_response_conciseness"] = float(score)
                output["explanation_response_conciseness"] = res.response.choices[
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
class ResponseConsistency(ColumnOp):
    """
    Grades if the response is consistent or not.

    Attributes:
        col_response: (str) Coloumn name for stored response
        col_out: (str) Column name for the output score
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_response: str = "response"
    col_out: str = "score_response_consistency"
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
            row["response"] = row.pop(self.col_response)

        try:
            if self.settings.evaluate_locally:
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "response_consistency",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseConsistency`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_response_consistency": self.col_out}
                )
            )
        }

    def response_consistency_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in json.loads(llm_output))
        is_correct = is_correct and json.loads(llm_output)["Choice"] in ["A", "B", "C"]
        return is_correct

    def response_consistency_cot_validate_func(self, llm_output):
        is_correct = self.response_consistency_classify_validate_func(llm_output)
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
            few_shot_examples = RESPONSE_CONSISTENCY_FEW_SHOT__CLASSIFY
            output_format = RESPONSE_CONSISTENCY_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.response_consistency_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = RESPONSE_CONSISTENCY_FEW_SHOT__COT
            output_format = RESPONSE_CONSISTENCY_OUTPUT_FORMAT__COT
            validation_func = self.response_consistency_cot_validate_func
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
                grading_prompt_template = RESPONSE_CONSISTENCY_PROMPT_TEMPLATE.replace(
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
                "score_response_consistency": None,
                "explanation_response_consistency": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_response_consistency"] = float(score)
                output["explanation_response_consistency"] = res.response.choices[
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
class ValidResponseScore(ColumnOp):
    """
    Grades if the response is valid or not.

    Attributes:
        col_response: (str) Coloumn name for stored response
        col_out: (str) Column name for the output score
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt
        score_mapping (dict): Mapping of different grades to float scores

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_response: str = "response"
    col_out: str = "score_valid_response"
    scenario_description: t.Optional[str] = None
    score_mapping: dict = {"A": 1.0, "B": 0.0}

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
            row["response"] = row.pop(self.col_response)

        try:
            if self.settings.evaluate_locally:
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "valid_response",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ValidResponseScore`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_valid_response": self.col_out})
            )
        }

    def valid_response_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in json.loads(llm_output))
        is_correct = is_correct and json.loads(llm_output)["Choice"] in ["A", "B", "C"]
        return is_correct

    def valid_response_cot_validate_func(self, llm_output):
        is_correct = self.valid_response_classify_validate_func(llm_output)
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
            few_shot_examples = VALID_RESPONSE_FEW_SHOT__CLASSIFY
            output_format = VALID_RESPONSE_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.valid_response_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = VALID_RESPONSE_FEW_SHOT__COT
            output_format = VALID_RESPONSE_OUTPUT_FORMAT__COT
            validation_func = self.valid_response_cot_validate_func
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
                grading_prompt_template = VALID_RESPONSE_PROMPT_TEMPLATE.replace(
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
            output = {"score_valid_response": None, "explanation_valid_response": None}
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_valid_response"] = float(score)
                output["explanation_valid_response"] = res.response.choices[
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
class ResponseRelevance(ColumnOp):
    """
    Grades if the response is relevant or not.

    Attributes:
        col_question: (str) Column Name for the stored questions
        col_response: (str) Coloumn name for stored response
        col_out: (str) Column name for the output score
        scenario_description (str): Optional scenario description to incorporate in the evaluation prompt

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"
    col_out: str = "score_response_relevance"
    scenario_description: t.Optional[str] = None

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
            row["response"] = row.pop(self.col_response)

        try:
            if self.settings.evaluate_locally:
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "response_relevance",
                    data_send,
                    {"scenario_description": self.scenario_description},
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseRelevance`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_response_relevance": self.col_out}
                )
            )
        }

    def response_relevance_classify_validate_func(self, llm_output):
        pass

    def response_relevance_cot_validate_func(self, llm_output):
        pass

    def evaluate_local(self, data):
        """
        Our methodology is based on the model grade evaluation introduced by openai evals.
        """

        # Works by calling evaluate_local on ResponseCompleteness and ResponseConciseness and taking the f1 score of the two
        response_completeness = ResponseCompleteness(
            col_question=self.col_question,
            col_response=self.col_response,
            scenario_description=self.scenario_description,
        )
        output_completeness = (
            response_completeness.setup(settings=self.settings)
            .run(pl.DataFrame(data))["output"]
            .to_dicts()
        )

        response_conciseness = ResponseConciseness(
            col_response=self.col_response,
            scenario_description=self.scenario_description,
        )

        output_conciseness = (
            response_conciseness.setup(settings=self.settings)
            .run(pl.DataFrame(data))["output"]
            .to_dicts()
        )

        results = []
        for combined_row in zip(output_conciseness, output_completeness):
            precision = combined_row[0]["score_response_conciseness"]
            recall = combined_row[1]["score_response_completeness"]
            output = {
                "score_response_relevance": None,
                "explanation_response_relevance": None,
            }
            if (
                precision is not None
                and recall is not None
            ):
                explanation = (
                    "Response Precision: " + str(precision)
                    + str(combined_row[0]["explanation_response_conciseness"])
                    + "\n"
                    + "Response Recall: " + str(recall)
                    + str(combined_row[1]["explanation_response_completeness"])
                )
                output["explanation_response_relevance"] = explanation

                if (
                    precision != 0
                    and recall != 0
                ):
                    output["score_response_relevance"] = 2 * (
                        (precision * recall) / (precision + recall)
                    )
                else:
                    output['score_response_relevance'] = 0
            results.append(output)
        return results
