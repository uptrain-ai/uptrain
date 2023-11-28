"""
Implement checks to test if a piece of text has been taken from a source.
"""

from __future__ import annotations
import typing as t
import os
import copy 

from loguru import logger
import polars as pl
from uptrain.framework import Settings

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.openai_evals import OpenaiEval
from uptrain.operators.language.llm import LLMMulticlient, Payload
# from evals.elsuite.modelgraded.classify_utils import (
#     # append_answer_prompt,
#     # get_choice,
#     # get_choice_score,
# )

import logging
import string
from typing import Any, Callable, Iterable, Optional, Union

MATCH_FNS = {
    "include": lambda x, y: float(x in y),
    "exact": lambda x, y: float(x == y),
    "endswith": lambda x, y: x.endswith(y),
    "starts_or_endswith": lambda x, y: x.startswith(y) or x.endswith(y),
}
INVALID_STR = "__invalid__"

ANSWER_PROMPTS = {
    # e.g. "Yes"
    "classify": "Answer the question by printing only a single choice from {choices} (without quotes or punctuation) corresponding to the correct answer with no other text.".strip(),
    # e.g. "Yes\n The reasons are: ..."
    "classify_cot": "First, answer by printing a single choice from {choices} (without quotes or punctuation) corresponding to the correct answer. Then, from the next line, explain your reasonings step by step.".strip(),
    # e.g. "Let's think step by step. ...\nYes"
    "cot_classify": """
You are also given scores for each choice as {choice_scores}. {choice_scores_text}

First, write out in a step by step manner your reasoning to be sure that your conclusion is correct. Avoid simply stating the correct answer at the outset.
Then print only the score from {scores_text} associated to the correct answer in a separate line. Finally repeat the same score on a new line.
Reasoning:"""
}

def get_choice_score(
    choice: str,
    choice_strings: Iterable[str],
    choice_scores: Optional[Union[dict[str, float], str]] = None,
) -> Optional[float]:
    if choice_scores is None:
        return None
    if choice_scores == "from_strings":
        choice_scores = {c: float(c) for c in choice_strings}
    # assumption: each INVALID_STR contributes the lowest score
    if choice == INVALID_STR:
        return min(choice_scores.values())
    return choice_scores[choice]

def choice_to_str(choice_strings: Iterable[str]) -> str:
    """Return a string of choices, e.g. '"Yes" or "No" or "Maybe"'."""
    return " or ".join(f'"{choice}"' for choice in choice_strings)

def append_answer_prompt(
    prompt: list,
    eval_type: str,
    append_type: str = "as_content",
    answer_prompt: Optional[list] = None,
    choice_strings: Optional[Iterable[str]] = None,
) -> list:
    """Append answer prompt to prompt."""
    answer_prompt = answer_prompt or ANSWER_PROMPTS[eval_type] #.format(**{"choice_strings": ','.join(choice_strings)})
    answer_prompt = format_prompt(answer_prompt, choices=choice_to_str(choice_strings))
    if append_type == "as_content":
        assert isinstance(answer_prompt, str), f"prompt must be str, not {type(answer_prompt)}"
        prompt[-1]["content"] += "\n\n" + answer_prompt
    elif append_type == "as_message":
        assert is_chat_prompt(answer_prompt), f"prompt must be chat prompt, not {answer_prompt}"
        prompt += answer_prompt
    else:
        raise ValueError(f"append_type must be 'as_content' or 'as_message', not {append_type}")
    return prompt


def is_chat_prompt(prompt) -> bool:
    return isinstance(prompt, list) and all(isinstance(msg, dict) for msg in prompt)

def chat_prompt_to_text_prompt(prompt: list, for_completion: bool = True) -> str:
    """
    Render a chat prompt as a text prompt. User and assistant messages are separated by newlines
    and prefixed with "User: " and "Assistant: ", respectively, unless there is only one message.
    System messages have no prefix.
    """
    assert is_chat_prompt(prompt), f"Expected a chat prompt, got {prompt}"
    chat_to_prefixes = {
        # roles
        "system": "",
        # names
        "example_user": "User: ",
        "example_assistant": "Assistant: ",
    }

    # For a single message, be it system, user, or assistant, just return the message
    if len(prompt) == 1:
        return prompt[0]["content"]

    text = ""
    for msg in prompt:
        role = msg["name"] if "name" in msg else msg["role"]
        prefix = chat_to_prefixes.get(role, role.capitalize() + ": ")
        content = msg["content"]
        text += f"{prefix}{content}\n"
    if for_completion:
        text += "Assistant: "
    return text.lstrip()

def format_necessary(template: str, allow_missing: bool = False, **kwargs: dict[str, str]) -> str:
    """Format a template string with only necessary kwargs."""
    keys = [k[1] for k in string.Formatter().parse(template) if k[1]]
    if allow_missing:
        assert (
            len([k for k in keys if k in kwargs]) > 0
        ), f"Required: {keys}, got: {sorted(kwargs)}, no inputs are used.\nTemplate:\n{template}"
        cur_keys = {k: kwargs.get(k, "{" + k + "}") for k in keys}
    else:
        assert all(
            k in kwargs for k in keys
        ), f"Required: {keys}, got: {sorted(kwargs)}.\nTemplate:\n{template}"
        cur_keys = {k: kwargs[k] for k in keys}
    return template.format(**cur_keys)


def format_prompt(
    prompt: list, allow_missing: bool = False, **kwargs: dict[str, str]
) -> list:
    """Format a prompt with only necessary kwargs."""
    # if any input kwargs is chat prompt, convert to text prompt
    kwargs = {
        k: chat_prompt_to_text_prompt(v, for_completion=False) if is_chat_prompt(v) else v
        for k, v in kwargs.items()
    }
    if is_chat_prompt(prompt):
        new_prompt = []
        for msg in prompt:
            formatted_msg = copy.copy(msg)
            if "content" in formatted_msg:
                formatted_msg["content"] = format_necessary(
                    formatted_msg["content"], allow_missing=allow_missing, **kwargs
                )
            new_prompt.append(formatted_msg)
        prompt = new_prompt
    else:
        # Prompt is a string
        prompt = format_necessary(prompt, allow_missing=allow_missing, **kwargs)
    return prompt


@register_op
class OpenAIGradeScore(ColumnOp):
    """
    Operator to calculate the grade score of text completions using OpenAI models.

    Attributes:
        col_in_input (str): The name of the input column containing the prompts.
        col_in_completion (str): The name of the input column containing the completions.
        eval_name (str): The name of the OpenAI evaluation to use.
        col_out (str): The name of the output column containing the grade scores.

    Returns:
        dict: A dictionary containing the calculated grade scores.

    """

    col_in_input: str = "prompt"
    col_in_completion: str = "response"
    col_out: str = "openai_grade_score"
    eval_name: str

    def setup(self, settings: Settings):
        self._settings = settings
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        samples = data.select(
            [
                pl.col(self.col_in_input).alias("input"),
                pl.col(self.col_in_completion).alias("completion"),
            ]
        )
        grading_op = OpenaiEval(
            bundle_path="",
            completion_name="gpt-3.5-turbo",
            eval_name=self.eval_name,
        )

        grading_op.setup(settings=self._settings)
        oaieval_res = grading_op.run(samples)
        assert (
            "extra" in oaieval_res
            and "metrics" in oaieval_res["extra"]
            and "score" in oaieval_res["extra"]["metrics"]
        )

        results = pl.Series(oaieval_res["extra"]["metrics"]["score"])
        return {"output": data.with_columns([results.alias(self.col_out)])}


@register_op
class ModelGradeScore(ColumnOp):
    """
    Operator to calculate the grade score of text completions using a custom prompt
    for grading. It is a wrapper using the same utilities from the OpenAI evals library,
    replacing just the completion call.

    Attributes:
        grading_prompt_template (str): Template for the grading prompt.
        eval_type (Literal["cot_classify", "classify", "classify_cot"]): The type of evaluation for grading ("cot_classify" by default).
        choice_strings (list[str]): The list of choice strings for grading.
        choice_scores (dict[str, float]): The dictionary mapping choice strings to scores.
        context_vars (dict[str, str]): A dictionary mapping context variable names to corresponding
            columns in the input dataset.
    """

    grading_prompt_template: str
    eval_type: t.Literal["cot_classify", "classify", "classify_cot"] = "cot_classify"
    choice_strings: list[str]
    choice_scores: dict[str, float]  #t.Union[dict[str, float], dict[str, list[float]]]
    context_vars: dict[str, str]
    col_out: t.Union[str, list[str]] = "model_grade_score"

    def setup(self, settings: Settings):
        self._api_client = LLMMulticlient(settings=settings)
        self.model = settings.model
        if self.eval_type != "cot_classify":
            raise Exception("Only eval_type: cot_classify is supported for model grading check")
        for choice, score in self.choice_scores.items():
            score = format(score, ".3f")
            if score[-1] == "0":
                score = score[0:-1]
                if score[-1] == "0":
                    score = score[0:-1]
            self.choice_scores[choice] = score
        choice_scores = "(" + str(self.choice_scores)[1:-1] + ")"
        choice_scores_text = ""
        for choice, score in self.choice_scores.items():
            choice_scores_text += f"If selected choice is {choice}, score should be {score}. "
        scores_text = "(" + ", ".join(list(self.choice_scores.values())) + ")"
        answer_prompt = ANSWER_PROMPTS[self.eval_type].format(choice_scores=choice_scores, choice_scores_text=choice_scores_text, scores_text=scores_text)
        self.grading_prompt_template += answer_prompt
        return self

    def _make_payload(self, id: t.Any, messages: list[dict]) -> Payload:
        return Payload(
            data={"model": self.model, "messages": messages, "temperature": 0.2},
            metadata={"index": id},
        )

    def get_choice_via_llm(self, text: str, grading_prompt_template: str) -> str:
        """Queries LLM to get score from the text"""

        prompt = f"""
        Extract the score from the given text. The available choices and associated scores is present in the context.

        Context: {grading_prompt_template}
        Text: {text}

        Score:
        """

        payload = self._make_payload(0, [{"role": "user", "content": prompt}])
        output_payload = self._api_client.fetch_responses([payload])[0]

        try:
            score = output_payload.response["choices"][0]["message"]["content"]
            float(score)
            return score
        except:
            return str(0.0)


    def get_choice(
        self, text: str, eval_type: str, match_fn: Union[str, Callable], choice_strings: Iterable[str]
    ) -> str:
        """Clean the answer string to a choice string to one of choice_strings. Return '__invalid__.' if no match."""
        is_fn_extract_score = False
        if match_fn == 'extract_score':
            is_fn_extract_score = True
        else:
            if isinstance(match_fn, str):
                match_fn = MATCH_FNS[match_fn]
        lines = text.strip().split("\n")
        if eval_type.startswith("cot_classify"):
            lines = lines[::-1]  # reverse lines
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if is_fn_extract_score:
                if "." in line:
                    part_before_decimal = line.split(".")[0][::-1]
                    prev_char = ""
                    for char in part_before_decimal:
                        new_char = char + prev_char
                        try:
                            float(new_char)
                        except:
                            break
                        prev_char = new_char
                    part_before_decimal = prev_char

                    part_after_decimal = line.split(".")[1]
                    prev_char = ""
                    for char in part_after_decimal:
                        new_char = prev_char + char
                        try:
                            float(new_char)
                        except:
                            break
                        prev_char = new_char
                    part_after_decimal = prev_char
                    choice = part_before_decimal + "." + part_after_decimal
                    try:
                        float(choice)
                        if float(choice) > 1.0 or float(choice) < 0.0:
                            return self.get_choice_via_llm(text, self.grading_prompt_template)
                        return str(choice)
                    except:
                        return self.get_choice_via_llm(text, self.grading_prompt_template)
                else:
                    return self.get_choice_via_llm(text, self.grading_prompt_template)
            else:
                line = "".join(c for c in line if c not in string.punctuation)
                if not line:
                    continue
                for choice in choice_strings:
                    if match_fn(line, choice):
                        return choice
        logging.warn(f"Choices {choice_strings} not parsable for {eval_type}: {text}")
        return INVALID_STR

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        prompts = []
        for row in data.rows(named=True):
            subs = {k: row[v] for k, v in self.context_vars.items()}
            # fill in context variables in the prompt template
            _prompt = self.grading_prompt_template.format(**subs)
            # following the `evals` code to create the grading instruction
            #  https://github.com/openai/evals/blob/main/evals/elsuite/modelgraded/classify_utils.py
            _prompt_chat = [{"role": "user", "content": _prompt}]
            # _prompt_chat = append_answer_prompt(
            #     prompt=[{"role": "user", "content": _prompt}],
            #     eval_type=self.eval_type,
            #     choice_strings=self.choice_strings,
            # )
            prompts.append(_prompt_chat)

        input_payloads = [
            self._make_payload(idx, prompt_msgs)
            for idx, prompt_msgs in enumerate(prompts)
        ]
        output_payloads = self._api_client.fetch_responses(input_payloads)

        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None, None))
            else:
                try:
                    resp_text = res.response["choices"][0]["message"]["content"]
                    choice = self.get_choice(
                        text=resp_text,
                        eval_type=self.eval_type,
                        match_fn="extract_score",
                        choice_strings=self.choice_strings,
                    )
                    score = float(choice)
                    results.append((idx, score, resp_text))
                except Exception as e:
                    logger.error(
                        f"Error when processing payload at index {idx}, not API error: {e}"
                    )
                    results.append((idx, None, None))

        results = sorted(results, key=lambda x: x[0])
        if isinstance(self.col_out, list):
            result_scores = [
                pl.Series(
                    [val[idx] if val is not None else None for _, val, _ in results]
                ).alias(self.col_out[idx])
                for idx in range(len(self.col_out))
            ]
            result_scores.extend(
                [
                    pl.Series([explanation for _, _, explanation in results]).alias(
                        self.col_out[idx] + "_explanation"
                    )
                    for idx in range(len(self.col_out))
                ]
            )
        else:
            result_scores = [
                pl.Series([val for _, val, _ in results]).alias(self.col_out),
                pl.Series([explanation for _, _, explanation in results]).alias(
                    self.col_out + "_explanation"
                ),
            ]
        return {"output": data.with_columns(result_scores)}
