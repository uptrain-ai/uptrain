"""
Implement checks to test if a piece of text has been taken from a source.  
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel, Field
import polars as pl

from uptrain.operators.base import *
if t.TYPE_CHECKING:
    from uptrain.framework.config import *

from rouge_score import rouge_scorer

# pip install rouge_score

class SchemaRougeScore(BaseModel):
    col_generated: str = "text_generated"
    col_source: str = "text_source"

class RougeScore(BaseModel):
    schema_data: SchemaRougeScore = Field(default_factory=SchemaRougeScore)
    score_type : str = "precision"

    def make_executor(self, settings: t.Optional[Settings] = None):
        return RougeScoreExecutor(self, settings)

@register_op
class RougeScoreExecutor(OperatorExecutor):
    op: RougeScore

    def __init__(self, op: RougeScore, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text_generated = data.get_column(self.op.schema_data.col_generated)
        text_source = data.get_column(self.op.schema_data.col_source)

        results = []
        scores = []
        for i in range(len(text_generated)):
            scorer = rouge_scorer.RougeScorer(['rougeL'])
            scores.append(scorer.score(text_source[i], text_generated[i]))

        if self.op.score_type == "precision":
            results = [int(x['rougeL'][0]* 100) for x in scores]
        elif self.op.score_type == "recall":
            results = [int(x['rougeL'][1]* 100) for x in scores]
        elif self.op.score_type == "f1":
            results = [int(x['rougeL'][2]* 100) for x in scores]
        else:
            raise Exception(f"{self.op.score_type} not implemented")

        return {"output": add_output_cols_to_data(data, [pl.Series(values=results)])}