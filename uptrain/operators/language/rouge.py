"""
Implement checks to test if a piece of text has been taken from a source.  
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel
import polars as pl

from uptrain.operators.base import *
from uptrain.operators.language.embeddings import embed
from uptrain.operators.language.llm import LLMMulticlient

from rouge_score import rouge_scorer

# pip install rouge_score

class SchemaRougeScore(BaseModel):
    col_text_generated: str = "text_generated"
    col_text_source: str = "text_source"
    col_score_type : str = "score_type"

class RougeScore(BaseModel):
    schema_data: SchemaRougeScore = SchemaRougeScore()

    def make_executor(self):
        return RougeScoreExecutor(self)
    
class RougeScoreExecutor:
    op: RougeScore
    api_client: LLMMulticlient

    def __init__(self, op: RougeScore):
        self.op = op
        self.api_client = LLMMulticlient(concurrency=4)

    def run(self, data: TYPE_OP_INPUT) -> TYPE_OP_OUTPUT:
        if isinstance(data, pl.DataFrame):
            text_generated = data.get_column(self.op.schema_data.col_text_generated)
            text_source = data.get_column(self.op.schema_data.col_text_source)
            score_type = data.get_column(self.op.schema_data.col_score_type)

        results = []
        for i in range(len(text_generated)):
            scorer = rouge_scorer.RougeScorer(['rougeL'])
            scores = scorer.score(text_source[i], text_generated[i])

            if score_type[i] == "recall":
                results.append(int(scores['rougeL'][1]* 100))
            elif score_type[i] == "fmeasure":
                results.append(int(scores['rougeL'][2]* 100))
            else:
                # precision by default
                results.append(int(scores['rougeL'][0]* 100))

        return {"output": pl.Series(values=results)}
    

