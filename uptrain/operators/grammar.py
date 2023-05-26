"""
Implement checks to test language quality. 
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel, root_validator
import numpy as np
import pyarrow as pa

try:
    import openai
except ImportError:
    openai = None

from .base import TYPE_OP_OUTPUT
from uptrain.utilities import (
    array_np_to_arrow,
    table_arrow_to_np_arrays,
    dependency_required,
)


class SchemaGrammarScore(BaseModel):
    col_text: str = "text"


class GrammarScore(BaseModel):
    schema_data: SchemaGrammarScore = SchemaGrammarScore()

    def make_executor(self):
        return GrammarScoreExecutor(self)


@dependency_required(openai, "openai")
class GrammarScoreExecutor:
    op: GrammarScore

    def __init__(self, op: GrammarScore):
        self.op = op

    def _get_score(self, text: str) -> float:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a grammatical correctnes evaluator who only gives only a number and no explanation.",
                    },
                    {
                        "role": "user",
                        "content": "Score following sentence on grammatical correctness on a scale of 0 to 100: \n\n {statement}".format(
                            statement=text
                        ),
                    },
                ],
                temperature=0,
            )
            resp_text = response.choices[0]["message"]["content"]
            number = int(re.findall(r"\d+", resp_text)[0])
            return number
        except Exception:
            logger.exception("Failed to get score for text: {text}", text=text)
            return -1

    def run(self, data: pa.Table) -> TYPE_OP_OUTPUT:
        [text_strings] = table_arrow_to_np_arrays(data, [self.op.schema_data.col_text])
        scores = np.asarray([self._get_score(t) for t in text_strings])
        return {"output": array_np_to_arrow(scores)}
