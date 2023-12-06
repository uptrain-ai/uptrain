"""
Implement operators to evaluate conversation datapoints for a 
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
class ConversationSatisfactionScore(ColumnOp):
    """
    Grade if the user is satifised with the conversation with the ChatBot. 

     Attributes:
        col_conversation (str): Column name for the stored conversations
        role (str): Entity name asking the queries.
    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """
    col_conversation: str = "conversation"
    role: str = "user"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = [
            {
                "conversation": row[self.col_conversation]
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate(
                "ConversationSatisfaction", data_send, {
                    "role": self.role
                })
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ConversationSatisfactionScore`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}
