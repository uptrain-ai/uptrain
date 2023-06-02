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

class SchemaEmbedding(BaseModel):
    col_text: str = "text"

class Embedding(BaseModel):
    schema_data: SchemaEmbedding = Field(default_factory=SchemaEmbedding)
    model: str = 'hkunlp/instructor-xl'

    def make_executor(self, settings: t.Optional[Settings] = None):
        return EmbeddingExecutor(self, settings)
    
@register_op
class EmbeddingExecutor(OperatorExecutor):
    op: Embedding

    def __init__(self, op: Embedding, settings: t.Optional[Settings] = None):
        self.op = op
        if self.op.model == 'hkunlp/instructor-xl':
            self.model = INSTRUCTOR(self.op.model)
        else:
            raise Exception("Embeddings model not supported")

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text = data.get_column(self.op.schema_data.col_text)
        inputs = [['Represent the developer documentation sentence:', x] for x in text]
        results = self.model.encode(inputs)
        return {"output": add_output_cols_to_data(data, [pl.Series(results)])}