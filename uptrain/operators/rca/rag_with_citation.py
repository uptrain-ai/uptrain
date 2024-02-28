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
from uptrain.utilities import polars_to_json_serializable_dict


@register_op
class RagWithCitation(ColumnOp):
    """
    Performs Root Cause Analysis in a rag pipeline which provides citations

     Attributes:
        col_question (str): Column name for the stored questions
        col_context: (str) Column name for stored context
        col_response (str): Column name for the stored responses
        col_cited_context (str): Column name for the stored cited context

    Raises:
        Exception: Raises exception for any failed analysis attempts
    """

    col_question: str = "question"
    col_context: str = "context"
    col_response: str = "response"
    col_cited_context: str = "cited_context"
    col_out: str = "score_context_relevance"
    scenario_description: t.Optional[str] = None

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
            row["cited_context"] = row.pop(self.col_cited_context)

        try:
            results = self._api_client.perform_root_cause_analysis(
                project_name="_internal",
                data=data_send,
                rca_template=RcaTemplate.RAG_WITH_CITATION,
                scenario_description=self.scenario_description,
                metadata={"internal_call": True},
            )
        except Exception as e:
            logger.error(
                f"Failed to run Root cause analysis for `RagWithCitation`: {e}"
            )
            raise e

        assert results is not None
        return {"output": data.with_columns(pl.from_dicts(results))}
