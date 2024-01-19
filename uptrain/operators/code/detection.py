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


@register_op
class CodeIdentificationScore(ColumnOp):
    """
    
    Go through the response and identify if there is any code in it.
    If found, it returns the code snippet.

    Attributes:
        col_response (str): Column name for the stored responses
        col_out (str): Column name to output scores
    Raises:
        Exception: Raises exception for any failed evaluation attempts
    
    """

    col_response: str = "response"
    col_out: str = "score_code_identification"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = [
            {
                "response": row[self.col_response],
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.evaluate(
                "code_identification", data_send
            )

        except Exception as e:
            logger.error(f"Failed to evaluate `CodeIdentification`: {e}")
            raise e
        
        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results).rename({f"score_code_identification": self.col_out}))}
