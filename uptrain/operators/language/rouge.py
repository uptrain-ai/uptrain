"""
Implement checks to test if a piece of text has been taken from a source.  
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel
import polars as pl


if t.TYPE_CHECKING:
    from uptrain.framework.config import *
from uptrain.operators.base import *

from rouge_score import rouge_scorer

# pip install rouge_score


@register_op
class RougeScore(BaseModel):
    score_type: str = "precision"
    col_in_generated: str = "text_generated"
    col_in_source: str = "text_source"
    col_out: str = get_output_col_name_at(0)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return RougeScoreExecutor(self, settings)


class RougeScoreExecutor(OperatorExecutor):
    op: RougeScore

    def __init__(self, op: RougeScore, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text_generated = data.get_column(self.op.col_in_generated)
        text_source = data.get_column(self.op.col_in_source)

        results = []
        scores = []
        for i in range(len(text_generated)):
            scorer = rouge_scorer.RougeScorer(["rougeL"])
            scores.append(scorer.score(text_source[i], text_generated[i]))

        if self.op.score_type == "precision":
            results = [int(x["rougeL"][0] * 100) for x in scores]
        elif self.op.score_type == "recall":
            results = [int(x["rougeL"][1] * 100) for x in scores]
        elif self.op.score_type == "f1":
            results = [int(x["rougeL"][2] * 100) for x in scores]
        else:
            raise Exception(f"{self.op.score_type} not implemented")
        return {"output": data.with_columns([pl.Series(self.op.col_out, results)])}
