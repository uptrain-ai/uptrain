"""
Implement checks to test language quality. 
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel, Field
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework.config import *
from uptrain.operators.base import *
from uptrain.operators.language.llm import LLMMulticlient, Payload

__all__ = ["GrammarScore"]


class SchemaGrammarScore(BaseModel):
    in_col_text: str = "text"
    out_col: str = get_output_col_name_at(0)


@register_op
class GrammarScore(BaseModel):
    schema: SchemaGrammarScore = Field(default_factory=SchemaGrammarScore)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return GrammarScoreExecutor(self, settings)


class GrammarScoreExecutor(OperatorExecutor):
    op: GrammarScore
    api_client: LLMMulticlient

    def __init__(self, op: GrammarScore, settings: t.Optional[Settings] = None):
        self.op = op
        self.api_client = LLMMulticlient(settings=settings)

    def _make_payload(self, id: t.Any, text: str) -> Payload:
        return Payload(
            endpoint="chat.completions",
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

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text_ser = data.get_column(self.op.schema.in_col_text)
        input_payloads = [
            self._make_payload(idx, text) for idx, text in enumerate(text_ser)
        ]
        output_payloads = self.api_client.fetch_responses(input_payloads)

        results = []
        for res in output_payloads:
            assert (
                res is not None
            ), "Response should not be None, we must handle all exceptions before."
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
        return {
            "output": data.with_columns(
                [pl.Series(self.op.schema.out_col, result_scores)]
            )
        }
