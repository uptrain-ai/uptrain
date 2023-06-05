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
    in_col_text: str = "text"
    out_col: str = get_output_col_name_at(0)


@register_op
class Embedding(BaseModel):
    schema: SchemaEmbedding = Field(default_factory=SchemaEmbedding)
    # model: str = 'hkunlp/instructor-xl'
    model: str = "MiniLM-L6-v2"

    def make_executor(self, settings: t.Optional[Settings] = None):
        return EmbeddingExecutor(self, settings)


class EmbeddingExecutor(OperatorExecutor):
    op: Embedding

    def __init__(self, op: Embedding, settings: t.Optional[Settings] = None):
        self.op = op
        if self.op.model == "hkunlp/instructor-xl":
            self.model = INSTRUCTOR(self.op.model)
        elif self.op.model == "MiniLM-L6-v2":
            self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        else:
            raise Exception("Embeddings model not supported")

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text = data.get_column(self.op.schema.in_col_text)
        if self.op.model == "hkunlp/instructor-xl":
            inputs = [
                ["Represent the developer documentation sentence: ", x] for x in text
            ]
        elif self.op.model == "MiniLM-L6-v2":
            inputs = list(text)
        results = self.model.encode(inputs)

        return {
            "output": data.with_columns(
                [pl.Series(self.op.schema.out_col, results)]
            )
        }
