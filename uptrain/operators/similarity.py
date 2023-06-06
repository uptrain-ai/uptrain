"""
Implement checks to test similarity between two pieces of text. 
"""

from __future__ import annotations
import re
import typing as t
import numpy as np
from loguru import logger
from pydantic import BaseModel, Field
import polars as pl

from uptrain.operators.base import *

if t.TYPE_CHECKING:
    from uptrain.framework.config import *

# pip install InstructorEmbedding torch sentence_transformers


class SchemaSimilarity(BaseModel):
    in_col_vector_1: str
    in_col_vector_2: str
    out_col: str = get_output_col_name_at(0)


@register_op
class CosineSimilarity(BaseModel):
    dataschema: SchemaSimilarity = Field(default_factory=SchemaSimilarity)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return CosineSimilarityExecutor(self, settings)


class CosineSimilarityExecutor(OperatorExecutor):
    op: CosineSimilarity

    def __init__(self, op: CosineSimilarity, settings: t.Optional[Settings] = None):
        self.op = op

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        vector_1 = data.get_column(self.op.dataschema.in_col_vector_1)
        vector_2 = data.get_column(self.op.dataschema.in_col_vector_2)

        results = []
        for i in range(len(vector_1)):
            v1 = np.array(vector_1[i])
            v2 = np.array(vector_2[i])
            similarity_score = np.dot(v1, v2) / np.linalg.norm(v1) * np.linalg.norm(v2)
            results.append(similarity_score)

        return {
            "output": data.with_columns(
                [pl.Series(self.op.dataschema.out_col, results)]
            )
        }
