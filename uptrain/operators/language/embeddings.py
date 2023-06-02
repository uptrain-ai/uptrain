"""
Create embeddings for text
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel
import polars as pl

from uptrain.operators.base import *

from InstructorEmbedding import INSTRUCTOR

class SchemaEmbedding(BaseModel):
    col_text: str = "text"

class Embedding(BaseModel):
    schema_data: SchemaEmbedding = SchemaEmbedding()

    def make_executor(self):
        return EmbeddingExecutor(self)
    
class EmbeddingExecutor:
    op: Embedding
    model: INSTRUCTOR

    def __init__(self, op: Embedding):
        self.op = op
        self.model = INSTRUCTOR('hkunlp/instructor-xl')

    def run(self, data: TYPE_OP_INPUT) -> TYPE_OP_OUTPUT:
        if isinstance(data, pl.DataFrame):
            data = data.get_column(self.op.schema_data.col_text)
            
        results = []
        for i in range(len(data)):
            embedding = self.model.encode([[data[i]]])
            results.append(embedding[0])

        return {"output": pl.Series(values=results)}

# model = INSTRUCTOR('hkunlp/instructor-xl')

# def embed(sentence, feature):
#     return model.encode([[f"Represent the {feature} sentence: ", sentence]])
