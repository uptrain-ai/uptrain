"""
Create embeddings for text
"""

from __future__ import annotations
import typing as t

from loguru import logger
from pydantic import BaseModel
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

InstructorEmbedding = lazy_load_dep("InstructorEmbedding", "InstructorEmbedding")
sentence_transformers = lazy_load_dep("sentence_transformers", "sentence-transformers")


@register_op
class Embedding(BaseModel):
    model: str = "MiniLM-L6-v2"
    col_in_text: str = "text"
    col_out: str = get_output_col_name_at(0)

    def make_executor(self, settings: t.Optional[Settings] = None):
        return EmbeddingExecutor(self, settings)


class EmbeddingExecutor(OperatorExecutor):
    op: Embedding

    def __init__(self, op: Embedding, settings: t.Optional[Settings] = None):
        self.op = op
        if self.op.model == "hkunlp/instructor-xl":
            self.model = InstructorEmbedding.INSTRUCTOR(self.op.model)
        elif self.op.model == "MiniLM-L6-v2":
            self.model = sentence_transformers.SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        else:
            raise Exception("Embeddings model not supported")

    def run(self, data: pl.DataFrame) -> TYPE_OP_OUTPUT:
        text = data.get_column(self.op.col_in_text)
        if self.op.model == "hkunlp/instructor-xl":
            inputs = [
                ["Represent the developer documentation sentence: ", x] for x in text
            ]
        elif self.op.model == "MiniLM-L6-v2":
            inputs = list(text)
        else:
            raise Exception("Embeddings model not supported")
        results = self.model.encode(inputs)

        return {"output": data.with_columns([pl.Series(self.op.col_out, results)])}
