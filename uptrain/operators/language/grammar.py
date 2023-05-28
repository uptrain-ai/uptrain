"""
Implement checks to test language quality. 
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel
import polars as pl

from uptrain.operators.base import *
from uptrain.operators.language.llm import LLMMulticlient, Payload


class SchemaGrammarScore(BaseModel):
    col_text: str = "text"


class GrammarScore(BaseModel):
    schema_data: SchemaGrammarScore = SchemaGrammarScore()

    def make_executor(self):
        return GrammarScoreExecutor(self)


class GrammarScoreExecutor:
    op: GrammarScore
    api_client: LLMMulticlient

    def __init__(self, op: GrammarScore):
        self.op = op
        self.api_client = LLMMulticlient(concurrency=4)

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

    def run(self, data: TYPE_OP_INPUT) -> TYPE_OP_OUTPUT:
        if isinstance(data, pl.DataFrame):
            data = data.get_column(self.op.schema_data.col_text)
        input_payloads = [
            self._make_payload(idx, text) for idx, text in enumerate(data)
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
        results = [val for idx, val in sorted(results, key=lambda x: x[0])]

        return {"output": pl.Series(values=results)}
