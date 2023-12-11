"""
Implement operators to evaluate question-response-context datapoints from a 
retrieval augmented pipeline. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class ResponseFactualScore(ColumnOp):
    """
    Grade how factual the generated response was.

     Attributes:
        col_question (str): Column name for the stored questions
        col_context: (str) Coloumn name for stored context
        col_response (str): Coloumn name for the stored responses

    Raises:
        Exception: Raises exception for any failed evaluation attempts



    """

    col_question: str = "question"
    col_context: str = "context"
    col_response: str = "response"

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
                "context": row[self.col_context],
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate("factual_accuracy", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseFactualScore`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}


@register_op
class ResponseCompleteness(ColumnOp):
    """
    Grade how complete the generated response was for the question specified.

    Attributes:
        col_question (str): Column name for the stored questions
        col_response (str): Coloumn name for the stored responses

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_response: str = "response"

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
            results = self._api_client.evaluate("response_completeness", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseCompleteness`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}


@register_op
class ResponseCompletenessWrtContext(ColumnOp):
    """
    Grade how complete the generated response was for the question specified given the information provided in the context.
    """

    col_question: str = "question"
    col_response: str = "response"
    col_context: str = "context"

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
                "context": row[self.col_context],
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate(
                "response_completeness_wrt_context", data_send
            )
        except Exception as e:
            logger.error(
                f"Failed to run evaluation for `ResponseCompletenessWrtContext`: {e}"
            )
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}


@register_op
class ContextRelevance(ColumnOp):
    """
    Grade how relevant the context was to the question asked.

    Attributes:
        col_question: (str) Column Name for the stored questions
        col_context: (str) Coloumn name for stored context

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_question: str = "question"
    col_context: str = "context"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = [
            {
                "question": row[self.col_question],
                "context": row[self.col_context],
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate("context_relevance", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ContextRelevance`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}


@register_op
class ResponseRelevance(ColumnOp):
    """
    Grades how relevant the generated response is or if it has any additional irrelevant information for the question asked.

    Attributes:
        col_question (str): Column name for the stored questions
        col_response (str): Coloumn name for the stored responses

    Raises:
        Exception: Raises exception for any failed evaluation attempts


    """

    col_question: str = "question"
    col_response: str = "response"

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
            results = self._api_client.evaluate("response_relevance", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseRelevance`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}




@register_op
class ResponseConciseness(ColumnOp):
    """
    Grades how concise the generated response is or if it has any additional irrelevant information for the question asked.

    Attributes:
        col_question (str): Column name for the stored questions
        col_response (str): Coloumn name for the stored responses

    Raises:
        Exception: Raises exception for any failed evaluation attempts


    """

    col_question: str = "question"
    col_response: str = "response"

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
            results = self._api_client.evaluate("response_conciseness", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseConciseness`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}




@register_op
class ResponseConsistency(ColumnOp):
    """
    Gives scores how relevant the generated response is for the question asked along with the context.

    Attributes:
        col_question (str): Column name for the stored questions
        col_response (str): Coloumn name for the stored responses
        col_context (str): Column name for the stored contexts

    Raises:
        Exception: Raises exception for any failed evaluation attempts


    """

    col_question: str = "question"
    col_response: str = "response"
    col_context: str = "context"

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
                "context": row[self.col_context]
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate("response_consistency", data_send)
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseConsistency`: {e}")
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}
