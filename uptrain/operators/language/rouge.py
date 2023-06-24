"""
Implement checks to test if a piece of text has been taken from a source.  
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

rouge_scorer = lazy_load_dep("rouge_score.rouge_scorer", "rouge_score")


@register_op
class RougeScore(ColumnOp):
    score_type: str = "precision"
    col_in_generated: str = "text_generated"
    col_in_source: str = "text_source"

    def setup(self, _: Settings | None = None) -> None:
        return self

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        text_generated = data.get_column(self.col_in_generated)
        text_source = data.get_column(self.col_in_source)

        results = []
        scores = []
        for i in range(len(text_generated)):
            scorer = rouge_scorer.RougeScorer(["rougeL"])  # type: ignore
            scores.append(scorer.score(text_source[i], text_generated[i]))

        type_to_index = {"precision": 0, "recall": 1, "f1": 2}
        if self.score_type not in type_to_index:
            raise Exception(f"{self.score_type} not implemented")

        results = [
            int(x["rougeL"][type_to_index[self.score_type]] * 100) for x in scores
        ]
        return {"output": pl.Series(get_output_col_name_at(0), results)}
