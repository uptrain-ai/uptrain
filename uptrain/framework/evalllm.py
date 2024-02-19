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
import copy

from uptrain.framework.remote import APIClientWithoutAuth, DataSchema
from uptrain.framework.base import Settings
from uptrain.framework.evals import (
    Evals,
    JailbreakDetection,
    ParametricEval,
    CritiqueTone,
    GuidelineAdherence,
    ResponseMatching,
    ConversationSatisfaction,
)
from uptrain.operators import (
    ResponseFactualScore,
    ContextRelevance,
    ResponseCompleteness,
    ResponseCompletenessWrtContext,
    ResponseConciseness,
    ResponseConsistency,
    ValidResponseScore,
    JailbreakDetectionScore,
    PromptInjectionScore,
    GuidelineAdherenceScore,
    ConversationSatisfactionScore,
    LanguageCritique,
    ToneCritique,
    ResponseRelevance,
)

EVAL_TO_OPERATOR_MAPPING = {
    Evals.FACTUAL_ACCURACY: ResponseFactualScore(),
    Evals.CONTEXT_RELEVANCE: ContextRelevance(),
    Evals.RESPONSE_COMPLETENESS: ResponseCompleteness(),
    Evals.RESPONSE_CONCISENESS: ResponseConciseness(),
    Evals.RESPONSE_COMPLETENESS_WRT_CONTEXT: ResponseCompletenessWrtContext(),
    Evals.RESPONSE_CONSISTENCY: ResponseConsistency(),
    Evals.RESPONSE_RELEVANCE: ResponseRelevance(),
    Evals.VALID_RESPONSE: ValidResponseScore(),
    Evals.PROMPT_INJECTION: PromptInjectionScore(),
    Evals.CRITIQUE_LANGUAGE: LanguageCritique(),
}

PARAMETRIC_EVAL_TO_OPERATOR_MAPPING = {
    "JailbreakDetection": JailbreakDetectionScore,
    "GuidelineAdherence": GuidelineAdherenceScore,
    "ConversationSatisfaction": ConversationSatisfactionScore,
    "CritiqueTone": ToneCritique,
}


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
        scenario_description: t.Union[str, list[str], None] = None,
        schema: t.Union[DataSchema, dict[str, str], None] = None,
        metadata: t.Optional[dict[str, str]] = None,
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
        for idx, m in enumerate(checks):
            if m in [Evals.SUB_QUERY_COMPLETENESS]:
                req_attrs.update([schema.sub_questions, schema.question])
            elif m in [Evals.CONTEXT_CONCISENESS]:
                req_attrs.update(
                    [schema.question, schema.context, schema.concise_context]
                )
            elif m in [Evals.CONTEXT_RERANKING]:
                req_attrs.update(
                    [schema.question, schema.context, schema.reranked_context]
                )
            elif m in [
                Evals.FACTUAL_ACCURACY,
                Evals.RESPONSE_COMPLETENESS_WRT_CONTEXT,
                Evals.RESPONSE_CONSISTENCY,
                Evals.CODE_HALLUCINATION,
            ]:
                req_attrs.update([schema.question, schema.context, schema.response])
            elif m in [
                Evals.RESPONSE_RELEVANCE,
                Evals.VALID_RESPONSE,
                Evals.RESPONSE_COMPLETENESS,
                Evals.RESPONSE_CONCISENESS,
            ]:
                req_attrs.update([schema.question, schema.response])
            elif m in [Evals.CONTEXT_RELEVANCE]:
                req_attrs.update([schema.question, schema.context])
            elif (
                m in [Evals.CRITIQUE_LANGUAGE]
                or isinstance(m, CritiqueTone)
                or isinstance(m, GuidelineAdherence)
            ):
                req_attrs.update([schema.response])
            elif isinstance(m, ResponseMatching):
                req_attrs.update(
                    [schema.question, schema.response, schema.ground_truth]
                )
            elif isinstance(m, ConversationSatisfaction):
                req_attrs.update([schema.conversation])
            elif m in [Evals.PROMPT_INJECTION] or isinstance(m, JailbreakDetection):
                req_attrs.update([schema.question])

            this_scenario_description = (
                scenario_description
                if not isinstance(scenario_description, list)
                else scenario_description[idx]
            )

            if isinstance(m, ParametricEval):
                dictm = m.dict()
                dictm.update({"scenario_description": this_scenario_description})
                ser_checks.append({"check_name": m.__class__.__name__, **dictm})
            elif isinstance(m, Evals):
                dictm = {"scenario_description": this_scenario_description}
                ser_checks.append({"check_name": m.value, **dictm})
            else:
                raise ValueError(f"Invalid metric: {m}")

        for idx, row in enumerate(data):
            if not req_attrs.issubset(row.keys()):
                raise ValueError(
                    f"Row {idx} is missing required all required attributes for evaluation: {req_attrs}"
                )

        if self.settings.evaluate_locally:
            results = copy.deepcopy(data)
            for idx, check in enumerate(checks):
                if isinstance(check, ParametricEval):
                    # Use the check_name field to get the operator and remove it from ser_checks
                    op = PARAMETRIC_EVAL_TO_OPERATOR_MAPPING[
                        ser_checks[idx].pop("check_name")
                    ](**ser_checks[idx])
                    res = (
                        op.setup(self.settings)
                        .run(pl.DataFrame(data))["output"]
                        .to_dicts()
                    )
                elif check in EVAL_TO_OPERATOR_MAPPING:
                    op = EVAL_TO_OPERATOR_MAPPING[check]
                    op.scenario_description = (
                        scenario_description
                        if not isinstance(scenario_description, list)
                        else scenario_description[idx]
                    )
                    res = (
                        op.setup(self.settings)
                        .run(pl.DataFrame(data))["output"]
                        .to_dicts()
                    )
                else:
                    res = self.evaluate_on_server(data, [ser_checks[idx]], schema)
                for idx, row in enumerate(res):
                    results[idx].update(row)
        else:
            results = self.evaluate_on_server(data, ser_checks, schema)
        return results

    def evaluate_on_server(self, data, ser_checks, schema):
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
                            "uptrain_settings": self.settings.dict(),
                        },
                    )
                    break
                except Exception as e:
                    logger.info("Retrying evaluation request")
                    if try_num == NUM_TRIES - 1:
                        logger.error(f"Evaluation failed with error: {e}")
                        raise e

            results.extend(batch_results)
        return results
