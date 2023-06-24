"""
Implement checks to test similarity between two pieces of text. 
"""

from __future__ import annotations
import typing as t

import numpy as np
from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *


@register_op
class CosineSimilarity(ColumnOp):
    col_in_vector_1: str
    col_in_vector_2: str

    def setup(self, _: t.Optional[Settings] = None):
        return self

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        vector_1 = data.get_column(self.col_in_vector_1)
        vector_2 = data.get_column(self.col_in_vector_2)

        results = []
        for i in range(len(vector_1)):
            v1 = np.array(vector_1[i])
            v2 = np.array(vector_2[i])
            similarity_score = np.dot(v1, v2) / np.linalg.norm(v1) * np.linalg.norm(v2)
            results.append(similarity_score)

        return {"output": pl.Series(results).alias(get_output_col_name_at(0))}
