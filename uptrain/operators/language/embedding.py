"""
Create embeddings for text
"""

from __future__ import annotations
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.utilities import lazy_load_dep

InstructorEmbedding = lazy_load_dep("InstructorEmbedding", "InstructorEmbedding")
sentence_transformers = lazy_load_dep("sentence_transformers", "sentence-transformers")


@register_op
class Embedding(ColumnOp):
    model: str = "MiniLM-L6-v2"
    col_in_text: str = "text"
    _model_obj: t.Any

    def setup(self, _: t.Optional[Settings] = None):
        if self.model == "hkunlp/instructor-xl":
            self._model_obj = InstructorEmbedding.INSTRUCTOR(self.op.model)  # type: ignore
        elif self.model == "MiniLM-L6-v2":
            self._model_obj = sentence_transformers.SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )  # type: ignore
        else:
            raise Exception(f"Embeddings model: {self.model} is not supported yet.")

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
        text = data.get_column(self.col_in_text)
        if self.model == "hkunlp/instructor-xl":
            inputs = [
                ["Represent the developer documentation sentence: ", x] for x in text
            ]
        elif self.model == "MiniLM-L6-v2":
            inputs = list(text)
        else:
            raise Exception("Embeddings model not supported")
        results = self._model_obj.encode(inputs)

        return {"output": pl.Series(results).alias(get_output_col_name_at(0))}
