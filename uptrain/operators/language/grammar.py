"""
Implement checks to test language quality.

This module provides the `GrammarScore` class, which allows evaluating the grammatical correctness of sentences using
the OpenAI GPT-3.5-turbo language model. It generates a grammar score for each input sentence on a scale of 0 to 100.

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

__all__ = ["GrammarScore"]


@register_op
class GrammarScore(ColumnOp):
    """
    Operator to test the grammatical correctness of sentences using the OpenAI GPT-3.5-turbo language model.

    Attributes:
        col_in_text (str): The name of the input column containing the sentences to evaluate.
        col_out (str): The name of the output column containing the grammar scores.

    Returns:
        dict: A dictionary containing the grammar scores for each input sentence.

    """

    col_in_text: str = "text"
    col_out: str = "grammar_score"

    def setup(self, settings: t.Optional[Settings] = None):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def _make_payload(self, id: t.Any, text: str) -> Payload:
        return Payload(
            data={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a grammatical correctness evaluator who produces only a number and no explanation.",
                    },
                    {
                        "role": "user",
                        "content": "Score following sentence on grammatical correctness on a scale of 0 to 100: \n\n {statement}".format(
                            statement=text
                        ),
                    },
                ],
            },
            metadata={"index": id},
        )

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        text_ser = data.get_column(self.col_in_text)
        input_payloads = [
            self._make_payload(idx, text) for idx, text in enumerate(text_ser)
        ]
        output_payloads = self._api_client.fetch_responses(input_payloads)

        results = []
        for res in output_payloads:
            assert (
                res is not None
            ), "Response should not be None, we should've handled exceptions beforehand."
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                resp_text = res.response["choices"][0]["message"]["content"]
                number = int(re.findall(r"\d+", resp_text)[0])
                results.append((idx, number))

        result_scores = pl.Series(
            [val for _, val in sorted(results, key=lambda x: x[0])]
        )
        return {"output": data.with_columns([result_scores.alias(self.col_out)])}
