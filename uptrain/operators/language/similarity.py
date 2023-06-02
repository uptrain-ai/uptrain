"""
Implement checks to test similarity between two pieces of text. 
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
from pydantic import BaseModel
import polars as pl

from uptrain.operators.base import *
from uptrain.operators.language.embeddings import embed
from uptrain.operators.language.llm import LLMMulticlient

from sklearn.metrics.pairwise import cosine_similarity

# pip install InstructorEmbedding torch sentence_transformers

class SchemaCosineSimilarity(BaseModel):
    col_feature: str = "feature"
    col_model_input: str = "model_input"
    col_model_output: str = "model_output"


class CosineSimilarity(BaseModel):
    schema_data: SchemaCosineSimilarity = SchemaCosineSimilarity()

    def make_executor(self):
        return CosineSimilarityExecutor(self)
    

class CosineSimilarityExecutor:
    op: CosineSimilarity
    api_client: LLMMulticlient

    def __init__(self, op: CosineSimilarity):
        self.op = op
        self.api_client = LLMMulticlient(concurrency=4)
    
    def run(self, data: TYPE_OP_INPUT) -> TYPE_OP_OUTPUT:
        if isinstance(data, pl.DataFrame):
            feature = data.get_column(self.op.schema_data.col_feature)
            model_input = data.get_column(self.op.schema_data.col_model_input)
            model_output = data.get_column(self.op.schema_data.col_model_output)

        results = []
        for i in range(len(model_input)):
            embedding_1 = embed(model_input[i], feature[i])
            embedding_2 = embed(model_output[i], feature[i])
            
            similarity_score = int(cosine_similarity(embedding_1, embedding_2) * 100)
        
            results.append(similarity_score)

        return {"output": pl.Series(values=results)}
