"""
Implement checks to test language quality on different aspects. 

This module provides the `Critique` class, which evaluates a text generation on multiple 
aspects using the OpenAI GPT-3.5-turbo language model. It provides a score for each of 
the aspects on a scale of 1 to 5.
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
from uptrain.operators.language.llm import LLMMulticlient, Payload


def _make_payload(id: t.Any, msg: str) -> Payload:
    return Payload(
        endpoint="chat.completions",
        data={
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a language assessment coach who critiques and grades machine generated responses in a conversation.",
                },
                {"role": "user", "content": msg},
            ],
            "temperature": 0.2,
        },
        metadata={"index": id},
    )


_CRITIQUE_TEMPLATE = """ 
Please evaluate the quality of the responses in the provided question-response pairs, on the listed aspects. 

Fluency: On a scale of 1-5, how fluent and natural sounding is the response, with 5 being completely fluent and 1 being not fluent at all.
Coherence: On a scale of 1-5, how well does the response follow logically from the question and context, with 5 being completely coherent and on topic and 1 being completely incoherent or unrelated.
Grammar: On a scale of 1-5, assess the grammar and word usage in the response, with 5 having perfect grammar and word choice and 1 having many grammatical errors or awkward phrasing.
Politeness: On a scale of 1-5, how polite or impolite is the tone of the response, with 5 being extremely polite and 1 being very rude or inappropriate.

Provide a score and brief justification for each aspect.

Example.
[Question]: How do I get to the airport from the Eiffel tower?
[Response]: I'm afraid I don't have enough information to provide directions. Could you please share what city you are currently located in?
[Answer]:
Fluency: 4. The response is mostly clear and natural but a little awkward.
Coherence: 3. It relates to the question but does not fully answer it.
Grammar: 5. No grammar or spelling errors.
Helpfulness: 3. Politely asks for missing information but does not provide the requested directions. 

Task data.
[Question]: {question}
[Response]: {response}
[Answer]: 
"""


@register_op
class LanguageCritique(ColumnOp):
    """
    Operator to score machine generated responses in a conversation using the OpenAI GPT-3.5-turbo language model.

    Attributes:
        col_in_text (str): The name of the input column containing the text to evaluate.
        col_out_prefix (str): Prefix for the name of the output columns containing the scores.
    """

    col_question: str = "question"
    col_response: str = "response"
    col_out_prefix: str = "score_"

    def setup(self, settings: t.Optional[Settings] = None):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        input_payloads = []
        for _id, row in enumerate(data.rows(named=True)):
            msg = _CRITIQUE_TEMPLATE.format(
                question=row[self.col_question], response=row[self.col_response]
            )
            input_payloads.append(_make_payload(_id, msg))
        output_payloads = self._api_client.fetch_responses(input_payloads)

        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                resp_text = res.response["choices"][0]["message"]["content"]
                scores = re.findall(r"([A-Za-z]+): (\d+)\.", resp_text)
                try:
                    score_dict = {
                        aspect.lower(): int(score) / 5 for aspect, score in scores
                    }
                    results.append((idx, score_dict))
                except Exception as e:
                    logger.error(f"Error when processing payload at index {idx}: {e}")
                    results.append((idx, None))

        result_scores = [val for _, val in sorted(results, key=lambda x: x[0])]
        result_cols = []
        for aspect in ["fluency", "coherence", "grammar", "politeness"]:
            result_cols.append(
                pl.Series(
                    [
                        x.get(aspect, None) if x is not None else None
                        for x in result_scores
                    ]
                ).alias(self.col_out_prefix + aspect)
            )
        return {"output": data.with_columns(result_cols)}


_TONE_ASSESS_TEMPLATE = """
Please assess the tone of the machine-generated response in the provided question-response pairs, based on the persona specified for the machine to follow. 

Please rate how well the tone aligns with expectations for the specified persona, on a scale of 1-5, with 1 meaning a very inappropriate tone for that role and 5 meaning the tone perfectly matches expectations.

Example.
Persona: Math Tutor
Question: I'm having trouble understanding this algebra question. Can you explain it step-by-step?
Response: I'm sorry, but I can't just give you the answers. However if you show me your work so far, we can figure out together where you are getting stuck.
Tone: 4. Encouraging tone providing guidance without giving away answers. 

Example.
Persona: Insurance Agent
Question: I was in a car accident that wasn't my fault. Will my insurance rates go up?
Response: I'm sorry to hear about your accident. While filing a claim should not directly impact your rates, premium amount depends on multiple factors. I would be happy to discuss your specific policy details to provide more information about what you can expect.
Tone: 5. Sympathetic and transparent tone building trust.

Task data.
Persona: {persona}
Question: {question}
Response: {response}
Tone:
"""


@register_op
class ToneCritique(ColumnOp):
    """
    Operator to assess the tone of machine generated responses using the OpenAI GPT-3.5-turbo language model.

    Attributes:
        col_in_text (str): The name of the input column containing the text to evaluate.
        col_out_prefix (str): Prefix for the name of the output columns containing the scores.
    """

    persona: str = "helpful-chatbot"
    col_question: str = "question"
    col_response: str = "response"
    col_out: str = "score_tone"

    def setup(self, settings: t.Optional[Settings] = None):
        self._api_client = LLMMulticlient(settings=settings)
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        input_payloads = []
        for _id, row in enumerate(data.rows(named=True)):
            msg = _TONE_ASSESS_TEMPLATE.format(
                persona=self.persona,
                question=row[self.col_question],
                response=row[self.col_response],
            )
            input_payloads.append(_make_payload(_id, msg))
        output_payloads = self._api_client.fetch_responses(input_payloads)

        results = []
        for res in output_payloads:
            idx = res.metadata["index"]
            if res.error is not None:
                logger.error(
                    f"Error when processing payload at index {idx}: {res.error}"
                )
                results.append((idx, None))
            else:
                resp_text = res.response["choices"][0]["message"]["content"]
                scores = re.findall(r"Tone: (\d+)\.", resp_text)
                try:
                    results.append((idx, int(scores[0]) / 5))
                except Exception as e:
                    logger.error(f"Error when processing payload at index {idx}: {e}")
                    results.append((idx, None))

        result_scores = pl.Series(
            [val for _, val in sorted(results, key=lambda x: x[0])]
        ).alias(self.col_out)
        return {"output": data.with_columns([result_scores])}
