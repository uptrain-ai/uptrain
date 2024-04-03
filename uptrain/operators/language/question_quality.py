"""
Implement operators to check the quality of the question given by the user. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl
import json

from uptrain.utilities.prompt_utils import parse_scenario_description

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import register_op, ColumnOp, TYPE_TABLE_OUTPUT
from uptrain.framework import APIClient
from uptrain.utilities import polars_to_json_serializable_dict
from uptrain.operators.language.llm import LLMMulticlient

from uptrain.operators.language.prompts.classic import (
    QUERY_REWRITE_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.instructions import CLASSIFY
from uptrain.operators.language.prompts.output_format import (
    QUERY_REWRITE_OUTPUT_FORMAT__CLASSIFY,
)


@register_op
class ValidQuestionScore(ColumnOp):
    """
    Simply check the number of words in the question and grades as incomplete if below a threshold
    Attributes:
        col_question: (str) Column Name for the stored questions
        col_out: (str) Column
    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    words_threshold: int = 1
    col_out: str = "score_valid_question"

    def setup(self, settings: t.Optional[Settings] = None):
        assert settings is not None
        self.settings = settings
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = data.to_dicts()
        results = []
        try:
            for row in data_send:
                question = row.pop(self.col_question)
                results.append(
                    {
                        "score_valid_question": int(
                            len(question.split(" ")) > self.words_threshold
                        )
                    }
                )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ValidQuestionScore`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_valid_question": self.col_out})
            )
        }

@register_op
class QueryRewrite(ColumnOp):
    """
    Given the past dialogues between 2 entities, this operator rewrites the question for the 'user' entity.
    Attributes:
        col_question: (str) Column Name for the stored questions
        col_conversation: (str) Column Name for the past conversations
        col_out: (str) Column Name for the output column
    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_conversation: str = "conversation"
    scenario_description: t.Optional[str] = None
    col_out: str = "revised_question"

    def setup(self, settings: t.Optional[Settings] = None):
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
            row["conversation"] = row[self.col_conversation]
            row["question"] = row[self.col_question]
        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "query_rewriting",
                    data_send
                )
        except Exception as e:
            logger.error(
                f"Failed to run evaluation for `QueryRewrite`: {e}"
            )
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"revised_question": self.col_out}
                )
            )
        }
    
    def query_rewrite_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Question" in llm_output)
        return is_correct
    
    def evaluate_local(self, data):
        """
        Our methodology is based on the model grade evaluation introduced by openai evals.
        """

        self.scenario_description, scenario_vars = parse_scenario_description(
            self.scenario_description
        )
        input_payloads = []

        output_format = QUERY_REWRITE_OUTPUT_FORMAT__CLASSIFY
        validation_func = self.query_rewrite_validate_func
        prompting_instructions = CLASSIFY
        
        for idx, row in enumerate(data):
            kwargs = row
            kwargs.update(
                {
                    "output_format": output_format,
                    "prompting_instructions": prompting_instructions
                }
            )
            try:
                grading_prompt_template = (
                    QUERY_REWRITE_PROMPT_TEMPLATE.replace(
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
                "revised_question": None,
            }
            try:
                revised_question = json.loads(res.response.choices[0].message.content)["Question"]
                output["revised_question"] = revised_question
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))
        results = [val for _, val in sorted(results, key=lambda x: x[0])]
        return results