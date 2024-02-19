"""
Implement operator to detect code in a response.
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework.base import *
from uptrain.operators.base import *
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
    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_response: str = "response"
    col_question: str = "question"
    col_context: str = "context"
    col_out: str = "score_code_hallucination"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = polars_to_json_serializable_dict(data)
        for row in data_send:
            row["question"] = row.pop(self.col_question)
            row["response"] = row.pop(self.col_response)
            row["context"] = row.pop(self.col_context)
        try:
            results = self._api_client.evaluate("code_hallucination", data_send)

        except Exception as e:
            logger.error(f"Failed to evaluate `CodeHallucination`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {f"score_code_hallucination": self.col_out}
                )
            )
        }
