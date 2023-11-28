"""
This module implements a simple LLM wrapper that can be used to evaluate performance
of LLM applications. 
"""

import typing as t

from loguru import logger
import httpx
import polars as pl
import pandas as pd
import pydantic

from uptrain.framework.remote import APIClientWithoutAuth, DataSchema
from uptrain.framework.base import Settings

from uptrain.framework.evals import Evals, ParametricEval, CritiqueTone, GuidelineAdherence, ResponseMatching, ConversationSatisfaction


class EvalLLM:

    def __init__(self, settings: Settings = None, openai_api_key: str = None) -> None:
        if (openai_api_key is None) and (settings is None):
            raise Exception("Please provide OpenAI API Key")

        if settings is None:
            self.settings = Settings(openai_api_key=openai_api_key)
        else:
            self.settings = settings
        self.executor = APIClientWithoutAuth(self.settings)

    def evaluate(
        self,
        data: t.Union[list[dict], pl.DataFrame, pd.DataFrame],
        checks: list[t.Union[str, Evals, ParametricEval]],
        schema: t.Union[DataSchema, dict[str, str], None] = None,
        metadata: t.Optional[dict[str, str]] = None
    ):
        """Run an evaluation on the UpTrain server using user's openai keys.
        NOTE: This api doesn't log any data.

        Args:
            data: Data to evaluate on. Either a Pandas DataFrame or a list of dicts.
            checks: List of checks to evaluate on.
            schema: Schema of the data. Only required if the data attributes aren't typical (question, response, context).

        Returns:
            results: List of dictionaries with each data point and corresponding evaluation results.
        """

        if isinstance(data, pl.DataFrame):
            data = data.to_dicts()

        if schema is None:
            schema = DataSchema()
        elif isinstance(schema, dict):
            schema = DataSchema(**schema)

        if metadata is None:
            metadata = {}

        checks = [Evals(m) if isinstance(m, str) else m for m in checks]
        for m in checks:
            assert isinstance(m, (Evals, ParametricEval))

        req_attrs, ser_checks = set(), []
        for m in checks:
            if m in [Evals.FACTUAL_ACCURACY, Evals.RESPONSE_COMPLETENESS_WRT_CONTEXT]:
                req_attrs.update([schema.question, schema.context, schema.response])
            elif m in [Evals.RESPONSE_RELEVANCE, Evals.RESPONSE_COMPLETENESS]:
                req_attrs.update([schema.question, schema.response])
            elif m in [Evals.CONTEXT_RELEVANCE]:
                req_attrs.update([schema.question, schema.context])
            elif m == Evals.CRITIQUE_LANGUAGE or isinstance(m, CritiqueTone) or isinstance(m, GuidelineAdherence):
                req_attrs.update([schema.response])
            elif isinstance(m, ResponseMatching):
                req_attrs.update([schema.response, schema.ground_truth])
            elif isinstance(m, ConversationSatisfaction):
                req_attrs.update([schema.conversation])

            if isinstance(m, ParametricEval):
                ser_checks.append({"check_name": m.__class__.__name__, **m.dict()})
            elif isinstance(m, Evals):
                ser_checks.append(m.value)
            else:
                raise ValueError(f"Invalid metric: {m}")
        for idx, row in enumerate(data):
            if not req_attrs.issubset(row.keys()):
                raise ValueError(
                    f"Row {idx} is missing required all required attributes for evaluation: {req_attrs}"
                )

        # send in chunks of 50, so the connection doesn't time out waiting for the server
        results = []
        NUM_TRIES, BATCH_SIZE = 3, 50
        for i in range(0, len(data), BATCH_SIZE):
            batch_results = []
            for try_num in range(NUM_TRIES):
                try:
                    logger.info(
                        f"Sending evaluation request for rows {i} to <{i+BATCH_SIZE} to the Uptrain"
                    )
                    batch_results = self.executor.evaluate(
                        data=data[i : i + BATCH_SIZE],
                        checks=ser_checks,
                        metadata={
                            "schema": schema.dict(),
                            "uptrain_settings": self.settings.dict()
                        }
                    )

                except Exception as e:
                    logger.info("Retrying evaluation request")
                    if try_num == NUM_TRIES - 1:
                        logger.error(f"Evaluation failed with error: {e}")
                        raise e

            results.extend(batch_results)

        return results
