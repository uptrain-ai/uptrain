"""
Implement checks to test similarity between two pieces of text. 
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

from sklearn.metrics.pairwise import cosine_similarity

# pip install InstructorEmbedding torch sentence_transformers

class SchemaSimilarity(BaseModel):
    col_vector_1: str
    col_vector_2: str


class CosineSimilarity(BaseModel):
    schema_data: SchemaSimilarity = Field(default_factory=SchemaSimilarity)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return CosineSimilarityExecutor(self, settings) 
   
@register_op
class CosineSimilarityExecutor(OperatorExecutor):
    op: CosineSimilarity
    
    def __init__(self, op: CosineSimilarity, settings: t.Optional[Settings] = None):
        self.op = op
    
    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        vector_1 = data.get_column(self.op.schema_data.col_vector_1)
        vector_2 = data.get_column(self.op.schema_data.col_vector_2)

        results = []
        for i in range(len(vector_1)):            
            similarity_score = int(cosine_similarity(vector_1[i], vector_2[i]) * 100)
            results.append(similarity_score)

        return {"output": add_output_cols_to_data(data, [pl.Series(values=results)])}
