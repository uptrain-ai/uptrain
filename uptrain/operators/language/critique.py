"""
Implement checks to test language quality on different aspects. 

This module provides the `Critique` class, which evaluates a text generation on multiple 
aspects. It provides a score for each of the aspects on a scale of 1 to 5.
"""

from __future__ import annotations
import re
import typing as t

from loguru import logger
import polars as pl

if t.TYPE_CHECKING:
    from uptrain.framework import Settings
from uptrain.operators.base import *
import httpx


ALLOWED_LANGUAGE_QUALITY_ASPECTS = ["fluency", "coherence", "grammar", "politeness"]


@register_op
class LanguageQuality(ColumnOp):
    """
    Operator to score machine generated responses in a conversation on different language quality aspects like fluency, coherence, grammar correctness and politeness.

    Attributes:
        col_question (str): The name of the input column containing the input question.
        col_response (str): The name of the input column containing the LLM response.
        col_out_suffix (str): Suffix for the name of the output columns containing the scores.
    """

    col_question: str = "question"
    col_response: str = "response"
    col_out_suffix: str = "_score"
    aspects: list = ALLOWED_LANGUAGE_QUALITY_ASPECTS

    def setup(self, settings: t.Optional[Settings] = None):
        if set(self.aspects) - set(ALLOWED_LANGUAGE_QUALITY_ASPECTS):
            raise Exception(f"Language quality aspects are not supported: {set(self.aspects) - set(ALLOWED_LANGUAGE_QUALITY_ASPECTS)}")
        self.client = httpx.Client()
        self.settings = settings
        self.url = "http://localhost:9000/evaluate"
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        response = self.client.post(
            self.url,
            json={
                "input_data": {
                    'question': data.to_dict()[self.col_question].to_list(),
                    'response': data.to_dict()[self.col_response].to_list(),
                },
                "checks": self.aspects,
                "settings": self.settings.dict()
            },
        ).json()

        results = []
        for aspect in self.aspects:
            results.extend([
                pl.Series(response['results'][aspect + "_score"]).alias(aspect + self.col_out_suffix),
                pl.Series(response['results'][aspect + "_explanation"]).alias(aspect + self.col_out_suffix + "_explanation")
            ])

        return {"output": data.with_columns(results)}


@register_op
class Tonality(ColumnOp):
    """
    Operator to assess the tone of machine generated responses in terms of how well it aligns with the desired persona.

    Attributes:
        persona (str): Persona we want the LLM to replicate.
        col_question (str): The name of the input column containing the input question.
        col_response (str): The name of the input column containing the LLM response.
        col_out_prefix (str): Prefix for the name of the output columns containing the scores.
    """

    persona: str
    col_question: str = "question"
    col_response: str = "response"
    col_out: str = "tone_match_score"

    def setup(self, settings: t.Optional[Settings] = None):
        self.client = httpx.Client()
        self.settings = settings
        self.url = "http://localhost:9000/evaluate"
        return self

    def run(self, data: pl.DataFrame) -> TYPE_TABLE_OUTPUT:
        response = self.client.post(
            self.url,
            json={
                "input_data": {
                    'question': data.to_dict()[self.col_question].to_list(),
                    'response': data.to_dict()[self.col_response].to_list(),
                },
                'extra_args': {
                    'persona': self.persona,
                },
                "checks": ['tone'],
                "settings": self.settings.dict()
            },
        ).json()
        results = []
        results.extend([
            pl.Series(response['results']["tone_match_score"]).alias(self.col_out),
        ])

        return {"output": data.with_columns(results)}