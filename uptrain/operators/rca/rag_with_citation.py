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

from uptrain import RcaTemplate


@register_op
class RagWithCitation(ColumnOp):
    """
    Performs Root Cause Analysis in a rag pipeline

     Attributes:
        col_question (str): Column name for the stored questions
        col_context: (str) Column name for stored context
        col_response (str): Column name for the stored responses
        col_context_cited (str): Column name for the stored cited context 

    Raises:
        Exception: Raises exception for any failed evaluation attempts
    """

    col_question: str = "question"
    col_context: str = "context"
    col_response: str = "response"
    col_context_cited: str = "context_cited"
    scenario_description: t.Union[str, list[str], None] = None

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
                "context_cited": row[self.col_context_cited],
            }
            for row in data.to_dicts()
        ]
        try:
            results = self._api_client.perform_root_cause_analysis(
                   project_name = "internal_evaluation", 
                   data = data_send,
                   rca_template = RcaTemplate.RAG_WITH_CITATION,
                   scenario_description = self.scenario_description,
                   metadata = { "internal_call": True }
                   )
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseFactualScore`: {e}")
            raise e
        
        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}

