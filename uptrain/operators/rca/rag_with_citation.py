"""
Implement operators to evaluate question-response-context datapoints from a 
retrieval augmented pipeline. 
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl
import copy

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import (
    ColumnOp,
    register_op,
    TYPE_TABLE_OUTPUT,
)

from uptrain import RcaTemplate
from uptrain.utilities import polars_to_json_serializable_dict
from uptrain.operators.language.llm import LLMMulticlient
from uptrain.operators import (
    ValidQuestionScore,
    ResponseFactualScore,
    ContextRelevance,
    ValidResponseScore,
)


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
            row["question"] = row.pop(self.col_question)
            row["response"] = row.pop(self.col_response)
            row["context"] = row.pop(self.col_context)
            row["cited_context"] = row.pop(self.col_cited_context)

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
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

    def evaluate_local(self, data):
        question_valid_scores = (
            ValidQuestionScore(col_question="question")
            .setup(settings=self.settings)
            .run(pl.DataFrame(data))["output"]
            .to_dicts()
        )

        response_valid_scores = (
            ValidResponseScore(col_response="response")
            .setup(settings=self.settings)
            .run(pl.DataFrame(data))["output"]
            .to_dicts()
        )

        context_relevance_scores = (
            ContextRelevance(col_question="question", col_context="context")
            .setup(settings=self.settings)
            .run(pl.DataFrame(data))["output"]
            .to_dicts()
        )

        factual_accuracy_scores = (
            ResponseFactualScore(
                col_question="question", col_context="context", col_response="response"
            )
            .setup(settings=self.settings)
            .run(pl.DataFrame(data))["output"]
            .to_dicts()
        )

        data_cited = (
            copy.deepcopy(pl.DataFrame(data))
            .drop("context")
            .rename({"cited_context": "context"})
        )

        cited_context_relevance_scores = (
            ContextRelevance(col_question="question", col_context="context")
            .setup(settings=self.settings)
            .run(data_cited)["output"]
            .to_dicts()
        )

        cited_factual_accuracy_scores = (
            ResponseFactualScore(
                col_question="question", col_context="context", col_response="response"
            )
            .setup(settings=self.settings)
            .run(data_cited)["output"]
            .to_dicts()
        )

        results = []

        for idx, row in enumerate(data):
            this_row_scores = [None, None, None, None, None, None]
            this_row_error = None
            this_row_suggestion = None

            question_completeness = question_valid_scores[idx]["score_valid_question"]
            valid_response = response_valid_scores[idx]["score_valid_response"]
            context_relevance = context_relevance_scores[idx]["score_context_relevance"]
            factual_accuracy = factual_accuracy_scores[idx]["score_factual_accuracy"]
            cited_relevance = cited_context_relevance_scores[idx][
                "score_context_relevance"
            ]
            cited_factual = cited_factual_accuracy_scores[idx]["score_factual_accuracy"]

            this_row_explanations = [
                None,
                response_valid_scores[idx]["explanation_valid_response"],
                context_relevance_scores[idx]["explanation_context_relevance"],
                factual_accuracy_scores[idx]["explanation_factual_accuracy"],
                cited_context_relevance_scores[idx]["explanation_context_relevance"],
                cited_factual_accuracy_scores[idx]["explanation_factual_accuracy"],
            ]

            this_row_scores = [
                question_completeness,
                valid_response,
                context_relevance,
                factual_accuracy,
                cited_relevance,
                cited_factual,
            ]

            if question_completeness == 0:
                this_row_scores = [0, 0, 0, 0, 0, 0]
                this_row_explanations = [
                    None,
                    "Default explanation as the question is incomplete",
                    "Default explanation as the question is incomplete",
                    "Default explanation as the question is incomplete",
                    "Default explanation as the question is incomplete",
                    "Default explanation as the question is incomplete",
                ]
                this_row_error = "Incomplete Question"
                this_row_suggestion = "Ask the user to provide a valid question. In case of an ongoing conversation, rewrite the question by taking previous messages into account."
            elif valid_response == 0:
                this_row_scores = [1, 0, context_relevance, 0, 0, 0]
                this_row_explanations = [
                    None,
                    response_valid_scores[idx]["explanation_valid_response"],
                    context_relevance_scores[idx]["explanation_context_relevance"],
                    "Default explanation as the response doesn't contain any relevant information",
                    "Default explanation as the response doesn't contain any relevant information",
                    "Default explanation as the response doesn't contain any relevant information",
                ]
                if context_relevance == 0:
                    this_row_error = "Response With No Information - Poor Retrieval"
                    this_row_suggestion = "Context Retrieval Pipeline needs improvement"
                else:
                    this_row_error = (
                        "Response With No Information - Poor Context Utilization"
                    )
                    this_row_suggestion = "Add intermediary steps so as the LLM can better understand context and generate a valid response"
            elif context_relevance == 0:
                this_row_error = "Poor Retrieval"
                this_row_suggestion = "Context Retrieval Pipeline needs improvement"
            elif factual_accuracy == 0:
                this_row_error = "Hallucinations"
                this_row_suggestion = "Add instructions to your LLM to adher to the context provide - Try tipping"
            elif cited_factual == 0:
                this_row_error = "Poor citation"
                this_row_suggestion = "LLM is extracting facts from the context which are not cited correctly. Improve the citation quality of LLM by adding more instructions"
            elif cited_relevance == 0:
                this_row_error = "Poor Context Utilization"
                this_row_suggestion = "Add intermediary steps so as the LLM can better understand context and generate a complete response"
            else:
                this_row_error = "Others"
                this_row_suggestion = (
                    "Please reach out to the UpTrain team for further brainstorming"
                )

            results.append(
                {
                    "error_mode": this_row_error,
                    "error_resolution_suggestion": this_row_suggestion,
                    "score_question_completeness": this_row_scores[0],
                    "score_valid_response": this_row_scores[1],
                    "explanation_valid_response": this_row_explanations[1],
                    "score_context_relevance": this_row_scores[2],
                    "explanation_context_relevance": this_row_explanations[2],
                    "score_factual_accuracy": this_row_scores[3],
                    "explanation_factual_accuracy": this_row_explanations[3],
                    "score_cited_context_relevance": this_row_scores[4],
                    "explanation_cited_context_relevance": this_row_explanations[4],
                    "score_factual_accuracy_wrt_cited": this_row_scores[5],
                    "explanation_factual_accuracy_wrt_cited": this_row_explanations[5],
                }
            )

        return results
