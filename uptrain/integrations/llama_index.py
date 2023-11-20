
from __future__ import annotations
import os
import typing as t

from loguru import logger
import polars as pl
from uptrain.framework.evals import Evals, ParametricEval
from uptrain.framework.evalllm import EvalLLM
from uptrain.framework.remote import APIClient
from uptrain.framework.remote import DataSchema


from llama_index.indices.query.base import BaseQueryEngine


__all__ = [
    "EvalLlamaIndex"
]

class EvalLlamaIndex:
    query_engine: BaseQueryEngine

    def __init__(self, query_engine: BaseQueryEngine) -> None: 
        if not isinstance(query_engine, BaseQueryEngine):
            raise Exception("Please provide Query Engine for the evaluation")
        self.query_engine = query_engine

    def evaluate(
        self,
        client : t.Union[EvalLLM, APIClient],
        data: t.Union[list[dict], pl.DataFrame],
        checks: list[t.Union[str, Evals, ParametricEval]],
        project_name: str = None,
        schema: t.Union[DataSchema, dict[str, str], None] = None,
        metadata: t.Optional[dict[str, str]] = None,
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
            project_name: Name of the project to evaluate on.
            client: EvalLLM or APIClient object used for the evaluation using user's openai keys or Uptrain API key.
            data: Data to evaluate on. Either a Polars DataFrame or a list of dicts.
            checks: List of checks to evaluate on.
            schema: Schema of the data. Only required if the data attributes aren't typical (question, response, context).
            metadata: Attributes to attach to this dataset. Useful for filtering and grouping in the UI.
        Returns:
            results: List of dictionaries with each data point and corresponding evaluation results.
        """
        
        if isinstance(data, pl.DataFrame):
            data = data.to_dicts()
        import nest_asyncio
        nest_asyncio.apply()
        
        if schema is None:
            schema = DataSchema()
        elif isinstance(schema, dict):
            schema = DataSchema(**schema)
        
        responses = run_async_tasks([self.query_engine.aquery(data[i][schema.question]) for i in range(len(data))])

        for index, r in enumerate(responses):
            data[index][schema.response] = r.response
            data[index][schema.context] = "\n".join([c.node.get_content() for c in r.source_nodes])

        if isinstance(client, EvalLLM):
            results = client.evaluate(
                data = data,
                checks = checks,
                schema = schema,
                metadata = metadata
            )
        elif isinstance(client, APIClient):
            results = client.log_and_evaluate(
                project_name = project_name,
                data = data,
                checks = checks,
                schema = schema,
                metadata = metadata
            )
        return results