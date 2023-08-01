"""
Implement checks to test language quality on different aspects. 

This module provides the `Critique` class, which evaluates a text generation on multiple 
aspects using the OpenAI GPT-3.5-turbo language model. It provides a score for each of 
the aspects on a scale of 1 to 5.
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.llm import LLMMulticlient, Payload


_CRITIQUE_TEMPLATE = """ 
Please evaluate the quality of the responses in the provided question-response pairs, on the listed aspects. 

Fluency: On a scale of 1-5, how fluent and natural sounding is the response, with 5 being completely fluent and 1 being not fluent at all.
Coherence: On a scale of 1-5, how well does the response follow logically from the question and context, with 5 being completely coherent and on topic and 1 being completely incoherent or unrelated.
Grammar: On a scale of 1-5, assess the grammar and word usage in the response, with 5 having perfect grammar and word choice and 1 having many grammatical errors or awkward phrasing.
Politeness: On a scale of 1-5, how polite or impolite is the tone of the response, with 5 being extremely polite and 1 being very rude or inappropriate.

Provide a score and brief justification for each aspect.

Example.
[Question]: How do I get to the airport from the Eiffel tower?
[Response]: I'm afraid I don't have enough information to provide directions. Could you please share what city you are currently located in?
[Answer]:
Fluency: 4. The response is mostly clear and natural but a little awkward.
Coherence: 3. It relates to the question but does not fully answer it.
Grammar: 5. No grammar or spelling errors.
Helpfulness: 3. Politely asks for missing information but does not provide the requested directions. 

Task data.
[Question]: {question}
[Response]: {response}
[Answer]: 
"""


@register_op
class Critique(ColumnOp):
    """
    Operator to test the grammatical correctness of sentences using the OpenAI GPT-3.5-turbo language model.

    Attributes:
        col_in_text (str): The name of the input column containing the text to evaluate.
        col_out_prefix (str): Prefix for the name of the output columns containing the scores.
    """

    col_question: str = "question"
    col_response: str = "response"
    col_out_prefix: str = "language_score_"

    def setup(self, settings: t.Optional[Settings] = None):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def _make_payload(self, id: t.Any, question: str, response: str) -> Payload:
        return Payload(
            endpoint="chat.completions",
            data={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a language assessment coach who critiques and grades machine generated responses in a conversation.",
                    },
                    {
                        "role": "user",
                        "content": _CRITIQUE_TEMPLATE.format(
                            question=question, response=response
                        ),
                    },
                ],
                "temperature": 0.2,
            },
            metadata={"index": id},
        )

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        input_payloads = []
        for _id, row in enumerate(data.rows(named=True)):
            input_payloads.append(
                self._make_payload(_id, row[self.col_question], row[self.col_response])
            )
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
                resp_text = res.response["choices"][0]["message"]["content"]
                scores = re.findall(r"([A-Za-z]+): (\d+)\.", resp_text)
                score_dict = {aspect.lower(): int(score) for aspect, score in scores}
                results.append((idx, score_dict))

        result_scores = [val for _, val in sorted(results, key=lambda x: x[0])]
        result_cols = []
        for aspect in ["fluency", "coherence", "grammar", "politeness"]:
            result_cols.append(
                pl.Series(
                    [
                        x.get(aspect, None) if x is not None else None
                        for x in result_scores
                    ]
                ).alias(self.col_out_prefix + aspect)
            )
        return {"output": data.with_columns(result_cols)}
