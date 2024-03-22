"""
Implement operaores to evaluate response quality i.e. quality of the generated response.
"""

from __future__ import annotations
import typing as t
import json

from loguru import logger
import polars as pl


from uptrain.utilities.prompt_utils import parse_scenario_description

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import register_op, ColumnOp, TYPE_TABLE_OUTPUT
from uptrain.utilities import polars_to_json_serializable_dict
from uptrain.operators.language.llm import LLMMulticlient
from uptrain.operators.language.prompts.output_format import (
    CLASSIFY_JSON_OUTPUT_FORMAT,
    COT_CLASSIFY_JSON_OUTPUT_FORMAT,
)


@register_op
class CustomPromptEvalScore(ColumnOp):
    """
    Evaluate the quality of a response based on a custom prompt.

    Attributes:
    -----------
    prompt: str
        The prompt to evaluate the response quality.
    prompt_var_to_column_mapping: dict[str, str]
        Mapping from variables in the prompt to columns in the data.
    choices: list[str]
        List of choices for the LLM to select from.
    choice_scores: list[float]
        Scores associated for each choice.
    eval_type: str
        Type of evaluation. Options are "classify" and "cot_classify".
    col_out: str
        Column name to store the score.

    """

    prompt: str
    prompt_var_to_column_mapping: dict[str, str]
    choices: list[str]
    choice_scores: list[float]
    eval_type: t.Literal["classify", "cot_classify"] = "cot_classify"
    col_out: str = "score_custom_prompt"

    def setup(self, settings: t.Optional[Settings] = None):
        from uptrain.framework.remote import APIClient

        assert settings is not None
        self.settings = settings
        if self.settings.evaluate_locally and (
            self.settings.uptrain_access_token is None
            or not len(self.settings.uptrain_access_token)
        ):
            self._api_client = LLMMulticlient(settings)
        else:
            self._api_client = APIClient(settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        data_send = polars_to_json_serializable_dict(data)

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                
                results = self._api_client.evaluate("CustomPromptEval", data_send, {
                    "prompt": self.prompt,
                    "choices": self.choices,
                    "choice_scores": self.choice_scores,
                    "eval_type": self.eval_type,
                    "prompt_var_to_column_mapping": self.prompt_var_to_column_mapping,
                })
        except Exception as e:
            logger.error(f"Failed to run evaluation for `ResponseCompleteness`: {e}")
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename({"score_custom_prompt": self.col_out})
            )
        }

    def evaluate_local(self, data):
        """
        Our methodology is based on the model grade evaluation introduced by openai evals.
        """

        input_payloads = []

        for idx, item in enumerate(data):
            subs = item
            subs = {k: item[v] for k, v in self.prompt_var_to_column_mapping.items()}
            grading_prompt_template = self.prompt.format(**subs)
            if self.eval_type == "classify":
                output_vars = {"Choice": "[Your Choice]"}
                grading_prompt_template += CLASSIFY_JSON_OUTPUT_FORMAT.format(
                    num_choices=len(self.choices),
                    choices=self.choices,
                    output_format=json.dumps(output_vars, indent=2),
                )
            elif self.eval_type == "cot_classify":
                output_vars = {
                    "Choice": "[Your Choice]",
                    "Explanation": "[Your Explanation here]",
                }
                grading_prompt_template += COT_CLASSIFY_JSON_OUTPUT_FORMAT.format(
                    num_choices=len(self.choices),
                    choices=self.choices,
                    output_format=json.dumps(output_vars, indent=2),
                )
            input_payloads.append(
                self._api_client.make_payload(idx, grading_prompt_template)
            )
        output_payloads = self._api_client.fetch_responses(
            input_payloads, lambda x: True
        )
        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            output = {"score_custom_prompt": None}
            try:
                # score_mapping is a mapping from choices to choice_scores
                score_mapping = dict(zip(self.choices, self.choice_scores))
                score = score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_custom_prompt"] = float(score)
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))
        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results
