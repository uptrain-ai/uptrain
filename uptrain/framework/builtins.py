"""This module hosts built-in checks for some common LLM evaluation tasks."""

from __future__ import annotations
import typing as t

from .checks import Check
from uptrain.operators import Histogram
from uptrain.operators import ResponseFactualScore, ModelGradeScore

# -----------------------------------------------------------
# Context related
# -----------------------------------------------------------

_TEMPLATE_CONTEXT_REL_GRADE = """
You are a detail-oriented LLM which pays close attention to the details, checks for consistency, and is adept at identifying logical fallacies, incorrect assumptions, or other errors in reasoning.
You are comparing an extracted context which is used to answer a given technical question.

Here is the data:
[BEGIN DATA]
************
[Question]: {question}
************
[Extracted Context]: {context}
************
[END DATA]

Compare the semantic similarity of the extracted context with the question. Ignore any differences in style, grammar, or punctuation.
The generated answer may either contain sufficient information to answer the given question completely, or contains relevant but incomplete information to answer the given question or doesn't have any information to answer the given question at all. 
Determine which case applies by selecting one of the following options:
(A) The extracted context can answer the given question completely.
(B) The extracted context can given some relevant answer for the given question but can't answer it completely.
(C) The extracted context doesn't contain any information to answer the given question.
"""

CheckContextRelevance = lambda: Check(
    name="context_relevance_score",
    operators=[
        ModelGradeScore(
            grading_prompt_template=_TEMPLATE_CONTEXT_REL_GRADE,
            eval_type="cot_classify",
            choice_strings=["A", "B", "C"],
            choice_scores={"A": 1.0, "B": 0.5, "C": 0.0},
            context_vars={
                "question": "question",
                "context": "context",
            },
            col_out="context_relevance_score",
        )
    ],
    plots=[Histogram(x="context_relevance_score")],
)

CheckResponseFacts = lambda: Check(
    name="response_factual_score",
    operators=[ResponseFactualScore()],
    plots=[Histogram(x="response_factual_score")],
)
