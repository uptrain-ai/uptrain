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


class ModelGradingScore(BaseModel):
    col_prompt: str = "prompt"
    col_answer: str = "answer"
    col_ideal: str = "ideal"
    col_out: str = get_output_col_name_at(0)

    def make_executor(self):
        return ModelGradingScoreExecutor(self)


class ModelGradingScoreExecutor:
    op: ModelGradingScore
    api_client: LLMMulticlient

    def __init__(self, op: ModelGradingScore):
        self.op = op
        self.api_client = LLMMulticlient()

    def _make_payload(
        self, id: t.Any, question: str, ideal: str, answer: str
    ) -> Payload:
        return Payload(
            endpoint="chat.completions",
            data={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "Assume role of an evaluator who produces only a number between 1 to 100 and no explanation.",
                    },
                    {
                        "role": "user",
                        "content": "For the given question: {question}, assume that {ideal} is the desired answer. Now, rate the given response: {answer} on how accurately it answers the given question. Give 1 if response is extremely inaccurate and 100 if the response is extremely accurate.".format(
                            question=question, ideal=ideal, answer=answer
                        ),
                    },
                ],
            },
            metadata={"index": id},
        )

    def run(self, data: t.Optional[pl.DataFrame]) -> TYPE_OP_OUTPUT:
        if isinstance(data, pl.DataFrame):
            question = data.get_column(self.op.col_prompt)
            ideal = data.get_column(self.op.col_ideal)
            answer = data.get_column(self.op.col_answer)
        else:
            raise TypeError(f"Expected DataFrame, got {type(data)}")

        input_payloads = [
            self._make_payload(idx, question[idx], ideal[idx], answer[idx])
            for idx in range(len(data))
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
        return {"output": data.with_columns([pl.Series(self.op.col_out, results)])}
