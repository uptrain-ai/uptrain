"""
Create embeddings for text
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

from InstructorEmbedding import INSTRUCTOR
from sentence_transformers import SentenceTransformer

class SchemaEmbedding(BaseModel):
    col_text: str = "text"

class Embedding(BaseModel):
    schema_data: SchemaEmbedding = Field(default_factory=SchemaEmbedding)
    # model: str = 'hkunlp/instructor-xl'
    model: str = 'MiniLM-L6-v2'

    def make_executor(self, settings: t.Optional[Settings] = None):
        return EmbeddingExecutor(self, settings)
    
@register_op
class EmbeddingExecutor(OperatorExecutor):
    op: Embedding

    def __init__(self, op: Embedding, settings: t.Optional[Settings] = None):
        self.op = op
        if self.op.model == 'hkunlp/instructor-xl':
            self.model = INSTRUCTOR(self.op.model)
        elif self.op.model == 'MiniLM-L6-v2':
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        else:
            raise Exception("Embeddings model not supported")

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text = data.get_column(self.op.schema_data.col_text)
        if self.op.model == 'hkunlp/instructor-xl':
            inputs = [['Represent the developer documentation sentence: ', x] for x in text]
        elif self.op.model == 'MiniLM-L6-v2':
            inputs = list(text)
        results = self.model.encode(inputs)
        return {"output": add_output_cols_to_data(data, [pl.Series(results)])}