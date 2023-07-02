"""
Implement operators to generate text. 
"""

from __future__ import annotations
import itertools
import typing as t

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.llm import LLMMulticlient, Payload


@register_op
class PromptExperiment(TableOp):
    """Operator to generate text given different prompts/LLM-input-parameters.

    Attributes:
        prompt_template (str) : A string template for the prompt.
        prompt_params (dict[str, list[str]]): A dictionary mapping parameter names to lists of values.
            The cartesian product of all the parameter values will be used to
            construct the prompts.
        models (list[str]): A list of models to run the experiment on.
        context_vars (Union[list[str], dict[str, str]]): A dictionary mapping context variable names to corresponding
            columns in the input dataset.

    """

    prompt_template: str
    prompt_params: dict[str, list[str]]
    models: list[str]
    context_vars: t.Union[list[str], dict[str, str]]
    _settings: Settings

    def setup(self, settings: "Settings"):
        self._settings = settings
        if isinstance(self.context_vars, list):
            self.context_vars=dict(zip(self.context_vars, self.context_vars))
        return self

    """Construct all the prompt variations and generate completions for each."""
    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        list_params = []
        for combo in itertools.product(*self.prompt_params.values(), self.models):
            prompt_params, model = combo[:-1], combo[-1]
            variables = dict(zip(self.prompt_params.keys(), prompt_params))
            list_params.append(
                {
                    "template": self.prompt_template,
                    "exp_model": model,
                    **variables,
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
            fill.update({k: row[k] for k in self.prompt_params.keys()})
            prompt = row["template"].format(**fill)
            prompts.append(prompt)
        input_w_prompts = input_dataset.with_columns([pl.Series("exp_prompt", prompts)])

        # get text completions for each row
        op_completion = TextCompletion(
            col_in_prompt="exp_prompt", col_in_model="exp_model"
        )
        completions = op_completion.setup(self._settings).run(input_w_prompts)["output"]
        assert completions is not None
        return {
            "output": input_w_prompts.with_columns([completions.alias("exp_generated")])
        }


@register_op
class TextCompletion(ColumnOp):
    """
    Take a prompt template, parameters to vary and generate output text
    by calling an LLM.
    
    Attributes:
        col_in_prompt (str): The name of the column containing the prompt template.
        col_in_model (str): The name of the column containing the model name.
    
    Returns:
        TYPE_COLUMN_OUTPUT: A dictionary containing the output text.

    """

    col_in_prompt: str = "prompt"
    col_in_model: str = "model"
    _api_client: LLMMulticlient

    def setup(self, settings: t.Optional[Settings] = None):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def _make_payload(self, id: t.Any, text: str, model: str) -> Payload:
        return Payload(
            endpoint="chat.completions",
            data={
                "model": model,
                "messages": [{"role": "user", "content": text}],
            },
            metadata={"index": id},
        )

    def run(self, data: pl.DataFrame) -> TYPE_COLUMN_OUTPUT:
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
        return {"output": output_text}
