"""
Implement operators to evaluate conversation datapoints for a 
LLM-powered agent pipeline. 
"""

from __future__ import annotations
import json
import typing as t

from loguru import logger
import polars as pl

from uptrain.operators.language.llm import LLMMulticlient
from uptrain.operators.language.prompts.classic import (
    CONVERSATION_SATISFACTION_PROMPT_TEMPLATE,
)
from uptrain.operators.language.prompts.few_shots import (
    CONVERSATION_SATISFACTION_FEW_SHOT__CLASSIFY,
    CONVERSATION_SATISFACTION_FEW_SHOT__COT,
)
from uptrain.operators.language.prompts.instructions import CHAIN_OF_THOUGHT, CLASSIFY
from uptrain.operators.language.prompts.output_format import (
    CONVERSATION_SATISFACTION_OUTPUT_FORMAT__CLASSIFY,
    CONVERSATION_SATISFACTION_OUTPUT_FORMAT__COT,
)
from uptrain.utilities.prompt_utils import parse_scenario_description

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import (
    register_op,
    ColumnOp,
    TYPE_TABLE_OUTPUT,
)

from uptrain.utilities import polars_to_json_serializable_dict


@register_op
class ConversationSatisfactionScore(ColumnOp):
    """
    Grade if the user is satifised with the conversation with the ChatBot.

     Attributes:
        col_conversation (str): Column name for the stored conversations.
        col_out (str): Column name to output scores
        assistant_persona (str): The personality description of the assistant.
        user_role (str): Designation of the user in the conversation.
        assistant_role (str): Designation of the assistant in the conversation.
        scenario_description (str | None): Optional scenario description to incorporate in the evaluation prompt.

    Raises:
        Exception: Raises exception for any failed evaluation attempts

    """

    col_conversation: str = "conversation"
    col_out: str = "score_conversation_satisfaction"
    assistant_persona: t.Union[str, None] = None
    user_role: str = "User"
    assistant_role: str = "Assistant"
    scenario_description: t.Optional[str] = None
    score_mapping: dict = {"A": 0.0, "B": 0.5, "C": 1.0}

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
        for row in data_send:
            row["conversation"] = row[self.col_conversation]

        try:
            if self.settings.evaluate_locally and (
                self.settings.uptrain_access_token is None
                or not len(self.settings.uptrain_access_token)
            ):
                results = self.evaluate_local(data_send)
            else:
                results = self._api_client.evaluate(
                    "ConversationSatisfaction",
                    data_send,
                    {
                        "user_persona": self.user_role,
                        "llm_persona": self.assistant_role,
                    },
                )

        except Exception as e:
            logger.error(
                f"Failed to run evaluation for `ConversationSatisfactionScore`: {e}"
            )
            raise e

        assert results is not None
        return {
            "output": data.with_columns(
                pl.from_dicts(results).rename(
                    {"score_conversation_satisfaction": self.col_out}
                )
            )
        }

    def conversation_satisfaction_classify_validate_func(self, llm_output):
        is_correct = True
        is_correct = is_correct and ("Choice" in llm_output)
        is_correct = is_correct and llm_output["Choice"] in ["A", "B", "C"]
        return is_correct

    def conversation_satisfaction_cot_validate_func(self, llm_output):
        is_correct = self.conversation_satisfaction_classify_validate_func(llm_output)
        is_correct = is_correct and ("Reasoning" in llm_output)
        return is_correct

    def evaluate_local(self, data):
        """
        Our methodology is based on the model grade evaluation introduced by openai evals.
        """

        self.scenario_description, scenario_vars = parse_scenario_description(
            self.scenario_description
        )
        input_payloads = []
        if self.settings.eval_type == "basic":
            few_shot_examples = CONVERSATION_SATISFACTION_FEW_SHOT__CLASSIFY
            output_format = CONVERSATION_SATISFACTION_OUTPUT_FORMAT__CLASSIFY
            validation_func = self.conversation_satisfaction_classify_validate_func
            prompting_instructions = CLASSIFY
        elif self.settings.eval_type == "cot":
            few_shot_examples = CONVERSATION_SATISFACTION_FEW_SHOT__COT
            output_format = CONVERSATION_SATISFACTION_OUTPUT_FORMAT__COT
            validation_func = self.conversation_satisfaction_cot_validate_func
            prompting_instructions = CHAIN_OF_THOUGHT
        else:
            raise ValueError(
                f"Invalid eval_type: {self.settings.eval_type}. Must be either 'basic' or 'cot'"
            )

        for idx, row in enumerate(data):
            kwargs = row
            kwargs.update(
                {
                    "output_format": output_format,
                    "prompting_instructions": prompting_instructions,
                    "few_shot_examples": few_shot_examples,
                    "user_role": self.user_role,
                    "assistant_role": self.assistant_role,
                    "assistant_persona": self.assistant_persona,
                }
            )
            try:
                grading_prompt_template = (
                    CONVERSATION_SATISFACTION_PROMPT_TEMPLATE.replace(
                        "{scenario_description}", self.scenario_description
                    ).format(**kwargs)
                )
            except KeyError as e:
                raise KeyError(
                    f"Missing required attribute(s) for scenario description: {e}"
                )
            input_payloads.append(
                self._api_client.make_payload(idx, grading_prompt_template)
            )
        output_payloads = self._api_client.fetch_responses(
            input_payloads, validation_func
        )

        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            output = {
                "score_conversation_satisfaction": None,
                "explanation_conversation_satisfaction": None,
            }
            try:
                score = self.score_mapping[
                    json.loads(res.response.choices[0].message.content)["Choice"]
                ]
                output["score_conversation_satisfaction"] = float(score)
                output["explanation_conversation_satisfaction"] = res.response.choices[
                    0
                ].message.content
            except Exception:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
            results.append((idx, output))
        results = [val for _, val in sorted(results, key=lambda x: x[0])]

        return results
