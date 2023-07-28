"""
Implement operators to evaluate Q-A-context datapoints from a 
retrieval augmented pipeline. 

Questions we want to answer:
- Is the context relevant?
- Is the answer supported by the context?

- context relevance
- prompt an LLM to extract sentences from the context that are relevant. Score based on that. 
- jaccard score and bert score to see how similar paragraphs are. Hmm, why not just count?
"""

from __future__ import annotations
import typing as t
import yaml
import os

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.openai_evals import OpenaiEval
from uptrain.operators.language.llm import LLMMulticlient, Payload
from evals.elsuite.modelgraded.classify_utils import (
    append_answer_prompt,
    get_choice,
    get_choice_score,
)

PROMPT_TEMPLATE = """
"You are an evidence-driven LLM that places high importance on supporting facts and references. You diligently verify claims and check for evidence within the document to ensure answers rely on reliable information and align with the documented evidence.",

You are presented with a question along with some context retrieved to answer it.
The summary was created with the aim of determining whether a live connection was made between a client and a financial advisor in the conversation or not.

Here is an example:
[BEGIN DATA]
************
[Question]: {question}
************
[Context]: {context}
************
[END DATA]

"""


@register_op
class ContextRelevanceScore(ColumnOp):
    col_inputs: list[str] = ["question", "response", "context"]
    col_out: str = "context_relevance_score"

    def setup(self, settings: Settings):
        self._api_client = LLMMulticlient(settings=settings)
        return self
