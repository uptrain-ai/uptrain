
from __future__ import annotations
import os
import typing as t

from loguru import logger
import polars as pl
from uptrain.framework.evals import Evals, ParametricEval
from uptrain.framework.evalllm import EvalLLM
from uptrain.framework.remote import DataSchema


from llama_index.indices.query.base import BaseQueryEngine


__all__ = [
    "LlamaLLM"
]

class LlamaLLM:
    query_engine: BaseQueryEngine

    def __init__(self, query_engine: BaseQueryEngine) -> None: 
        if not isinstance(query_engine, BaseQueryEngine):
            raise Exception("Please provide Query Engine for the evaluation")
        self.query_engine = query_engine

    def evaluate(
        self, 
        client : EvalLLM,
        data: t.Union[list[dict], pl.DataFrame],  
        checks: list[t.Union[str, Evals, ParametricEval]],
        schema: t.Union[DataSchema, dict[str, str], None] = None
    ):
        try:
            from llama_index.async_utils import run_async_tasks
        except ImportError:
            raise ImportError(
                "llama_index must be installed to use this function. "
                "Install it with `pip install llama_index`."
            )
        """
        Run evaluation of llama_index QueryEngine with different Evals

        NOTE: This api doesn't log any data.
        Args:
            client: EvalLLM object used for the evaluation using user's openai keys.
            data: Data to evaluate on. Either a Polars DataFrame or a list of dicts.
            checks: List of checks to evaluate on.
            schema: Schema of the data. Only required if the data attributes aren't typical (question, response, context).

        Returns:
            results: List of dictionaries with each data point and corresponding evaluation results.
        """
        
        if isinstance(data, pl.DataFrame):
            data = data.to_dicts()

        responses = run_async_tasks([self.query_engine.aquery(data[i]['question']) for i in range(len(data))])

        for index, r in enumerate(responses):
            data[index]['response'] = r.response
            data[index]['context'] = "\n".join([c.node.get_content() for c in r.source_nodes])
        
        results = client.evaluate(
            data=data,
            checks=checks,
            schema =schema
        )
        return results