"""
Implement operators to generate text. Used when evaluating different 
prompts/LLM-input-parameters for gnerating text. 
"""

from __future__ import annotations
import itertools
import typing as t
import json
import numpy as np 

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.llm import LLMMulticlient, Payload


@register_op
class PromptGenerator(TransformOp):
    """Operator to generate text given different prompts/LLM-input-parameters.

    Attributes:
        prompt_template (str) : A string template for the prompt.
        prompt_params (dict[str, list[str]]): A dictionary mapping parameter names to lists of values.
            The cartesian product of all the parameter values will be used to
            construct the prompts.
        models (list[str]): A list of models to run the experiment on.
        context_vars (Union[list[str], dict[str, str]]): A dictionary mapping context variable names to corresponding
            columns in the input dataset.
        col_out_prefix (str): Prefix for the output columns.

    """

    prompt_template: str
    prompt_params: dict[str, list[str]]
    models: list[str]
    context_vars: t.Union[list[str], dict[str, str]]
    col_out_prefix: str = "exp_"

    def setup(self, settings: "Settings"):
        self._settings = settings
        if isinstance(self.context_vars, list):
            self.context_vars = dict(zip(self.context_vars, self.context_vars))
        return self

    """Construct all the prompt variations and generate completions for each."""

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        list_params = []
        for experiment_id, combo in enumerate(
            itertools.product(*self.prompt_params.values(), self.models)
        ):
            prompt_params, model = combo[:-1], combo[-1]
            variables = dict(zip(self.prompt_params.keys(), prompt_params))
            list_params.append(
                {
                    "template": self.prompt_template,
                    self.col_out_prefix + "model": model,
                    **{self.col_out_prefix + k: v for k, v in variables.items()},
                    self.col_out_prefix + "experiment_id": experiment_id,
                }
            )
        params_dataset = pl.DataFrame(list_params)

        # Do a cross join of the input with the params dataset to get all the
        # inputs for the completion step
        input_dataset = data.join(params_dataset, on=None, how="cross")

        # construct the prompts by iterating over the rows of the input dataset and
        # formatting the prompt template with the row values
        prompts = []
        for row in input_dataset.iter_rows(named=True):
            fill = {k: row[v] for k, v in self.context_vars.items()}
            fill.update(
                {k: row[self.col_out_prefix + k] for k in self.prompt_params.keys()}
            )

            # TODO: Temp Fix for handling json in prompts. Permanent fix is to integrate langchain?
            try:
                prompt = row["template"].format(**fill)
            except:
                prompt = row["template"]
                for k, v in fill.items():
                    prompt = prompt.replace("{{" + k + "}}", v)
            prompts.append(prompt)

        input_w_prompts = input_dataset.with_columns(
            [pl.Series(self.col_out_prefix + "prompt", prompts)]
        )
        return {"output": input_w_prompts}

        # # get text completions for each row
        # op_completion = TextCompletion(
        #     col_in_prompt="exp_prompt", col_in_model="exp_model"
        # )
        # completions = op_completion.setup(self._settings).run(input_w_prompts)["output"]
        # assert completions is not None
        # return {
        #     "output": input_w_prompts.with_columns([completions.alias("exp_generated")])
        # }


@register_op
class TextCompletion(TransformOp):
    """
    Takes a table of prompts and LLM model to use, generates output text.

    Attributes:
        col_in_prompt (str): The name of the column containing the prompt template.
        col_in_model (str): The name of the column containing the model name.
        col_out_completion (str): The name of the column containing the generated text.
        temperature (float): Temperature for the LLM to generate responses.

    Returns:
        TYPE_TABLE_OUTPUT: A dictionary containing the dataset with the output text.
    """

    col_in_prompt: str = "prompt"
    col_in_model: str = "model"
    col_out_completion: str = "generated"
    temperature: float = 1.0
    _api_client: LLMMulticlient

    def setup(self, settings: Settings):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def _make_payload(self, id: t.Any, text: str, model: str) -> Payload:
        return Payload(
            data={
                "model": model,
                "messages": [{"role": "user", "content": text}],
                "temperature": self.temperature,
            },
            metadata={"index": id},
        )

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        prompt_ser = data.get_column(self.col_in_prompt)
        model_ser = data.get_column(self.col_in_model)
        input_payloads = [
            self._make_payload(idx, text, model)
            for idx, (text, model) in enumerate(zip(prompt_ser, model_ser))
        ]
        output_payloads = self._api_client.fetch_responses(input_payloads)

        results = []
        for res in output_payloads:
            assert (
                res is not None
            ), "Response should not be None, we should've handled exceptions beforehand."
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                resp_text = res.response["choices"][0]["message"]["content"]
                results.append((idx, resp_text))

        output_text = pl.Series(
            values=[val for _, val in sorted(results, key=lambda x: x[0])]
        )
        return {
            "output": data.with_columns([output_text.alias(self.col_out_completion)])
        }


@register_op
class TopicGenerator(ColumnOp):
    """
    Takes a table of clustered texts and identifies the topic for each cluster 

    Attributes:
        col_in_cluster_index (str): The name of the column containing the cluster index.
        col_in_dist (str): The name of the column containing the euclidean distance from its cluster centroid.
        col_in_text (str): The name of the column containing the text where the grouping needs to be performed.
        top_n (int): Number of examples to be considered for each category. 
        col_out_text (str): The name of the column containing the topic for each entry.
        temperature (float): Temperature for the LLM to generate responses.

    Returns:
        TYPE_TABLE_OUTPUT: A dictionary containing the dataset with the output text.
    """
    col_in_cluster_index: str = 'cluster_index'
    col_in_dist: str = 'cluster_index_distance'
    col_in_text: str = 'question'
    top_n: int = 5 
    col_out_text: str = 'topic'
    temperature: float = 1.0
    _api_client: LLMMulticlient

    def setup(self, settings: Settings):
        self._api_client = LLMMulticlient(settings=settings)
        self.model = settings.model
        return self

    def _make_payload(self, id: t.Any, text: str, model: str) -> Payload:
        return Payload(
            data={
                "model": model,
                "messages": [{"role": "user", "content": text}],
                "temperature": self.temperature,
            },
            metadata={"index": id},
        )

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:

        res_data_arr = []

        unique_agg_keys = ['default']
        if '_unique_agg_key_for_clustering' in list(data.columns):
            # First aggregate by col_aggs
            agg_data = data.groupby('_unique_agg_key_for_clustering').agg([pl.col(self.col_in_text).count().alias("num_rows_" + self.col_in_text)])
            agg_data = agg_data.drop("num_rows_" + self.col_in_text)
            unique_agg_keys = [eval(x) for x in list(agg_data['_unique_agg_key_for_clustering'])]

        self.topics = {}

        for unique_agg_key in unique_agg_keys:
            cond = True
            if isinstance(unique_agg_key, dict):
                unique_agg_key = dict([(key, unique_agg_key[key]) for key in sorted(unique_agg_key)])
                for key,val in unique_agg_key.items():
                    cond = cond & (data[key] == val)
            data_subset = data.filter(cond)

            questions = np.asarray(data_subset[self.col_in_text])
            distances = np.asarray(data_subset[self.col_in_dist])

            n_clusters = max(data_subset[self.col_in_cluster_index])
            input_payloads = []
            outputs = [None] * len(questions)
            indexes_cluster = []

            for index in range(n_clusters+1):
                points = data_subset[self.col_in_cluster_index]==index
                indexes_cluster.append(list(np.where(points)[0]))
                distances_cluster = distances[points]
                questions_cluster = questions[points]
                

                indexes_sorted = np.argsort(distances_cluster)
                indexes_top_n = indexes_sorted[:min(self.top_n, len(questions_cluster))]
                questions_top_n = questions_cluster[indexes_top_n]

                text = ''
                for j in range(len(questions_top_n)):
                    text = text + str(j+1) + '. ' + str(questions_top_n[j]) + '\n'
                
                input = f"""{text}"""
                prompt = f""" Identify the common topic in the given sentences below. 
                {input}
                
                You should identify only a single concise topic which should be at max 15 words long. Just print the topic and nothing else. 
                Topic: """
                input_payloads.append(self._make_payload(index, prompt, self.model))
        

            output_payloads = self._api_client.fetch_responses(input_payloads)

            results = []
            for res in output_payloads:
                assert (
                    res is not None
                ), "Response should not be None, we should've handled exceptions beforehand."
                idx = res.metadata["index"]
                if res.error is not None:
                    logger.error(
                        f"Error when processing payload at index {idx}: {res.error}"
                    )
                    results.append((idx, None))
                else:
                    resp_text = res.response["choices"][0]["message"]["content"]
                    results.append((idx, resp_text))
            
            for index, resp_text in results:
                indexes = indexes_cluster[index]
                for idx in indexes:
                    outputs[idx]=resp_text

            output_text = pl.Series(
                values=outputs
            )
            data_subset = data_subset.with_columns([output_text.alias(self.col_out_text)])
            res_data_arr.append(data_subset)

            results.sort(key=lambda x: x[0])
            self.topics[str(unique_agg_key)] = [x[1] for x in results]

        return {
            "output": pl.concat(res_data_arr)
        }


@register_op
class OutputParser(ColumnOp):
    """
    Takes a table of LLM respones and parses them into individual columns

    Attributes:
        col_in_response (str): The name of the column containing the raw model response.
        col_out_mapping (str): A dictionary containing the mapping of keys in response to their output column names.

    Returns:
        TYPE_TABLE_OUTPUT: A dictionary containing the dataset with the output text.
    """

    col_in_response: str
    col_out_mapping: dict

    def setup(self, settings: "Settings"):
        return self

    """Parse the LLM responses"""

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        responses = data[self.col_in_response]
        parsed_responses = pl.DataFrame([json.loads(x) for x in responses])
        return {
            "output": data.with_columns(
                [parsed_responses[k].alias(v) for k, v in self.col_out_mapping.items()]
            )
        }
