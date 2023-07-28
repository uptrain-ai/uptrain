"""
Implement operators to evaluate question-response-context datapoints from a 
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

PROMPT_TEMPLATE = """
You are an evidence-driven LLM that places high importance on supporting facts and references. You diligently verify claims and check for evidence within the document to ensure answers rely on reliable information.

[Task]: Extract relevant context. 
You are presented with a question along with some context retrieved to answer it using a search engine. 
From the provided context, please identify and return the sentences that are directly relevant to answering the question. If no sentences are relevant, return 'No sentences are relevant'.

Example 1.
[Question]: What is the capital of France?
[Context]: France, in Western Europe, encompasses medieval cities, alpine villages and Mediterranean beaches. Paris, its capital, is famed for its fashion houses, classical art museums including the Louvre and monuments like the Eiffel Tower.
[Relevant]: "Paris, its capital, is famed for its fashion houses, classical art museums including the Louvre and monuments like the Eiffel Tower."

Example 2.
[Question]: Who wrote "Pride and Prejudice"?
[Context]: "Pride and Prejudice" is a romantic novel of manners written by Jane Austen in 1813. The novel follows the character development of Elizabeth Bennet, the dynamic protagonist of the book who learns about the repercussions of hasty judgments and comes to appreciate the difference between superficial goodness and actual goodness.
[Relevant]: "Pride and Prejudice" is a romantic novel of manners written by Jane Austen in 1813.

Task data.
[Question]: {question}
[Context]: {context}
[Relevant]: 
"""


@register_op
class ContextRelevanceScore(ColumnOp):
    col_question: str = "question"
    col_context: str = "context"
    col_out: str = "context_relevance_score"

    def setup(self, settings: Settings):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def _make_payload(self, id: t.Any, messages: list[dict], context: str) -> Payload:
        return Payload(
            endpoint="chat.completions",
            data={"model": "gpt-3.5-turbo", "messages": messages, "temperature": 0.2},
            metadata={"index": id, "context": context},
        )

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        input_payloads = []
        for _id, row in enumerate(data.rows(named=True)):
            context = row[self.col_context]
            if isinstance(context, list):
                context = ". ".join(context)

            subs = {
                "question": row[self.col_question],
                "context": context,
            }
            prompt_msgs = [{"role": "user", "content": PROMPT_TEMPLATE.format(**subs)}]
            input_payloads.append(self._make_payload(_id, prompt_msgs, context))

        output_payloads = self._api_client.fetch_responses(input_payloads)
        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                try:
                    context = res.metadata["context"]
                    resp_text = res.response["choices"][0]["message"]["content"]
                    if resp_text == "No sentences are relevant":
                        results.append((idx, 0.0))
                    else:
                        # find overlap between context and response
                        resp_sents = [
                            s.strip() for s in resp_text.split(".") if len(s) > 0
                        ]
                        context_sents = [
                            s.strip() for s in context.split(".") if len(s) > 0
                        ]
                        overlap = sum(1 for sent in resp_sents if sent in context_sents)
                        results.append((idx, overlap / len(context_sents)))
                except Exception as e:
                    logger.error(
                        f"Error when processing payload at index {idx}, not API error: {e}"
                    )
                    results.append((idx, None))
