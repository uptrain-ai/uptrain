"""
Implement operators to generate text. 
"""

from __future__ import annotations
import itertools
import typing as t
import json

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
        for experiment_id, combo in enumerate(itertools.product(*self.prompt_params.values(), self.models)):
            prompt_params, model = combo[:-1], combo[-1]
            variables = dict(zip(self.prompt_params.keys(), prompt_params))
            list_params.append(
                {
                    "template": self.prompt_template,
                    self.col_out_prefix + "model": model,
                    **{self.col_out_prefix + k: v for k, v in variables.items()},
                    self.col_out_prefix + "experiment_id": experiment_id
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

            #TODO: Temp Fix for handling json in prompts. Permanent fix is to integrate langchain?
            try:
                prompt = row["template"].format(**fill)
            except:
                prompt = row['template']
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
            endpoint="chat.completions",
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
        return {"output": data.with_columns([parsed_responses[k].alias(v) for k,v in self.col_out_mapping.items()])}