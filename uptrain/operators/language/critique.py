"""
Implement checks to test language quality on different aspects. 

This module provides the `Critique` class, which evaluates a text generation on multiple 
aspects - fluence, politeness, grammar, and coherence,. It provides a score for each of the 
aspects on a scale of 0 to 1, along with an explanation for the score. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class LanguageCritique(ColumnOp):
    """
    Operator to score machine generated responses in a conversation. The response
    is evaluated on multiple aspects - fluence, politeness, grammar, and coherence.
    It provides a score for each of the aspects on a scale of 0 to 1, along with an
    explanation for the score.

    Attributes:
        col_response (str): The name of the input column containing response text
    
    Raises:
        Exception: Raises exception for any failed evaluation attempts
    
    """

    col_response: str = "response"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = [
            {"text": row[self.col_response]}
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate("critique_language", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `LanguageCritique`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}


@register_op
class ToneCritique(ColumnOp):
    """
    Operator to assess the tone of machine generated responses.

    Attributes:
        persona (str): The persona the chatbot being assesses was expected to follow
        col_response (str): The name of the input column containing response text
    
    Raises:
        Exception: Raises exception for any failed evaluation attempts
    
    """

    persona: str = "helpful-chatbot"
    col_response: str = "response"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = [
            {"response": row[self.col_response]}
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate(
                "critique_tone", data_send, {"persona": self.persona}
            )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ToneCritique`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}
