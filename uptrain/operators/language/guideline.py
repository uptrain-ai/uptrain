"""
Implement operators to evaluate question-response-guideline and question-response datapoints for a 
LLM-powered agent pipeline. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


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

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"
    guideline: str
    guideline_name: str = "guideline"
    response_schema: t.Union[str, None] = None
    col_out: str  = "score_guideline_adherence"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = [
            {
                "question": row[self.col_question],
                "response": row[self.col_response],
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate(
                "GuidelineAdherence", data_send, {
                    "guideline": self.guideline,
                    "guideline_name": self.guideline_name,
                    "response_schema": self.response_schema
                })
                
        except Exception as e:
            logger.error(f"Failed to run evaluation for `GuidelineAdherenceScore`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results).rename({f"score_{self.guideline_name}_adherence": self.col_out}))}

@register_op
class PromptInjectionScore(ColumnOp):
    """
    Grade if the LLM agent outputs the system prompt or not.

     Attributes:
        col_question (str): Column name for the stored questions
        col_response (str): Column name for the stored responses
        col_out (str): Column name to output scores
    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"
    col_out: str  = "score_prompt_injection"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = [
            {
                "question": row[self.col_question],
                "response": row[self.col_response],
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate(
                "prompt_injection", data_send)
                
        except Exception as e:
            logger.error(f"Failed to run evaluation for `PromptInjectionScore`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results).rename({f"score_prompt_injection": self.col_out}))}
