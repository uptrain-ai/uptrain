"""
Implement operators to evaluate question-response-guideline datapoints for a 
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
        col_response (str): Coloumn name for the stored responses
        guideline (str): Guideline to be followed
        guideline_name (str): Name the given guideline to be used in the score column name
        response_schema (str | None): Schema of the response if it is in form of a json string

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"
    guideline: str
    guideline_name: str = "guideline"
    response_schema: t.Union[str, None] = None

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
        return {"output": data.with_columns(pl.from_dicts(results))}
