"""
This module implements a simple LLM wrapper that can be used to evaluate performance
of LLM applications. 
"""

import typing as t
from datetime import datetime
from loguru import logger
import httpx
import polars as pl
import pandas as pd
import pydantic
import copy
import os
import httpx
from uptrain.utilities.utils import get_current_datetime, parse_prompt
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
    ResponseMatchingScore,
    ValidResponseScore,
    JailbreakDetectionScore,
    PromptInjectionScore,
    GuidelineAdherenceScore,
    ConversationSatisfactionScore,
    LanguageCritique,
    ToneCritique,
    ResponseRelevance,
    ContextConciseness,
    ContextReranking,
    SubQueryCompleteness,
)

EVAL_TO_OPERATOR_MAPPING = {
    Evals.FACTUAL_ACCURACY: ResponseFactualScore(),
    Evals.CONTEXT_RELEVANCE: ContextRelevance(),
    Evals.CONTEXT_RERANKING: ContextReranking(),
    Evals.CONTEXT_CONCISENESS: ContextConciseness(),
    Evals.RESPONSE_COMPLETENESS: ResponseCompleteness(),
    Evals.RESPONSE_CONCISENESS: ResponseConciseness(),
    Evals.RESPONSE_COMPLETENESS_WRT_CONTEXT: ResponseCompletenessWrtContext(),
    Evals.RESPONSE_CONSISTENCY: ResponseConsistency(),
    Evals.RESPONSE_RELEVANCE: ResponseRelevance(),
    Evals.VALID_RESPONSE: ValidResponseScore(),
    Evals.PROMPT_INJECTION: PromptInjectionScore(),
    Evals.CRITIQUE_LANGUAGE: LanguageCritique(),
    Evals.SUB_QUERY_COMPLETENESS: SubQueryCompleteness(),
}

PARAMETRIC_EVAL_TO_OPERATOR_MAPPING = {
    "JailbreakDetection": JailbreakDetectionScore,
    "GuidelineAdherence": GuidelineAdherenceScore,
    "ConversationSatisfaction": ConversationSatisfactionScore,
    "CritiqueTone": ToneCritique,
    "ResponseMatching": ResponseMatchingScore,
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
        project_name: str = "Project - " + str(datetime.utcnow()),
        scenario_description: t.Optional[str] = None,
        schema: t.Union[DataSchema, dict[str, str], None] = None,
        metadata: t.Optional[dict[str, str]] = None,
    ):
        """Run an evaluation on the UpTrain server using user's openai keys.
        NOTE: This api doesn't log any data.

        Args:
            project_name: Name of the project.
            data: Data to evaluate on. Either a Pandas DataFrame or a list of dicts.
            checks: List of checks to evaluate on.
            schema: Schema of the data. Only required if the data attributes aren't typical (question, response, context).
            metadata: Attributes to attach to this dataset. Useful for filtering and grouping in the UI.
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
        ## local server calls
        try:
            url = "http://localhost:4300/api/public/user"
            client = httpx.Client(
                headers={"uptrain-access-token": "default_key"},
                timeout=httpx.Timeout(7200, connect=5),
            )
            response = client.post(
                url,
                json={"name": "default_key"}
            )

            user_id = response.json()['id']
            checks = []
            for res in results:
                row_check = {}
                for key in res:
                    if key.startswith('score')  or key.startswith('explanation'):
                        row_check.update({key: res[key]})
                checks.append(row_check)
            
            url = "http://localhost:4300/api/public/add_project_data"
            response = client.post(
                        url,
                        json={
                            "data": results,
                            "checks": checks,
                            "metadata": metadata,
                            "schema_dict": schema.dict(),
                            "project": project_name,
                        },
                    )
        except:
            user_id = "default_key"
            logger.info('Server is not running!')
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

    def evaluate_experiments(
        self,
        project_name: str,
        data: t.Union[list[dict], pl.DataFrame],
        checks: list[t.Union[str, Evals, ParametricEval]],
        exp_columns: list[str],
        schema: t.Union[DataSchema, dict[str, str], None] = None,
        metadata: t.Optional[dict[str, t.Any]] = None,
    ):
        """Evaluate experiments on the given data.

        Args:
            project_name: Name of the project.
            data: Data to evaluate on. Either a Pandas DataFrame or a list of dicts.
            checks: List of checks to evaluate on.
            exp_columns: List of columns/keys which denote different experiment configurations.
            schema: Schema of the data. Only required if the data attributes aren't typical (question, response, context).
            metadata: Attributes to attach to this dataset. Useful for filtering and grouping in the UI.

        Returns:
            results: List of dictionaries with each data point and corresponding evaluation results for all the experiments.
        """
        if metadata is None:
            metadata = {}

        metadata.update({"uptrain_experiment_columns": exp_columns})

        if schema is None:
            schema = DataSchema()
        elif isinstance(schema, dict):
            schema = DataSchema(**schema)

        results = self.evaluate(
            project_name=project_name,
            data=data,
            checks=checks,
            schema=schema,
            metadata=metadata,
        )

        results = pl.DataFrame(results)
        all_cols = set(results.columns)
        value_cols = list(all_cols - set([schema.question] + exp_columns))
        index_cols = metadata.get("uptrain_index_columns", [schema.question])
        exp_results = results.pivot(
            values=value_cols, index=index_cols, columns=exp_columns
        )
        exp_results = exp_results.to_dicts()
        return exp_results


    def evaluate_prompts(
        self,
        project_name: str,
        data: t.Union[list[dict], pl.DataFrame],
        checks: list[t.Union[str, Evals, ParametricEval]],
        prompt: str, 
        schema: t.Union[DataSchema, dict[str, str], None] = None,
        metadata: t.Optional[dict[str, t.Any]] = None,
    ):
        """Evaluate experiments on the server and log the results.

        Args:
            project_name: Name of the project.
            data: Data to evaluate on. Either a Pandas DataFrame or a list of dicts.
            checks: List of checks to evaluate on.
            prompt: prompt for generating responses.
            exp_columns: List of columns/keys which denote different experiment configurations.
            schema: Schema of the data. Only required if the data attributes aren't typical (question, response, context).
            metadata: Attributes to attach to this dataset. Useful for filtering and grouping in the UI.

        Returns:
            results: List of dictionaries with each data point and corresponding evaluation results for all the experiments.
        """
        if metadata is None:
            metadata = {}
        
        base_prompt, prompt_vars = parse_prompt(prompt)

        prompts =[]
        context_vars = {}
        context_vars.update(zip(prompt_vars, prompt_vars))
        for idx, item in enumerate(data):
            subs = {k: item[v] for k, v in context_vars.items()}
            msg = base_prompt.format(**subs)
            prompts.append(msg)

        model = metadata["model"]
        dataset = pl.DataFrame(data)
        dataset = dataset.with_columns(pl.Series(name="model", values=[model] * len(dataset)))
        dataset = dataset.with_columns(pl.Series(name="prompt", values= prompts))
        
        from uptrain.operators import TextCompletion
        
        dataset = TextCompletion(
            col_in_prompt = "prompt", 
            col_in_model = "model", 
            col_out_completion = "response", 
            temperature = 0.0
            ).setup(self.settings).run(dataset)['output']
        
        dataset = dataset.to_dicts()

        if schema is None:
            schema = DataSchema()
        elif isinstance(schema, dict):
            schema = DataSchema(**schema)

        results = self.evaluate(
            project_name=project_name,
            data=dataset,
            checks=checks,
            schema=schema,
            metadata=metadata,
        )
        return results
