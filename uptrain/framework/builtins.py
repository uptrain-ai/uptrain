"""This module hosts built-in checks for some common LLM evaluation tasks."""

from __future__ import annotations
import typing as t

from .checks import Check
from uptrain.operators import Histogram
from uptrain.operators import (
    ResponseFactualScore,
    ResponseCompleteness,
    ResponseRelevance,
    ContextRelevance,
    LanguageCritique,
    ToneCritique,
)

# -----------------------------------------------------------
# Context related
# -----------------------------------------------------------

CheckContextRelevance = lambda: Check(
    name="score_context_relevance",
    operators=[ContextRelevance()],
    plots=[Histogram(x="score_context_relevance")],
)

CheckResponseFacts = lambda: Check(
    name="score_factual_accuracy",
    operators=[ResponseFactualScore()],
    plots=[Histogram(x="score_factual_accuracy")],
)

# -----------------------------------------------------------
# Response related
# -----------------------------------------------------------

CheckResponseCompleteness = lambda: Check(
    name="response_completeness_score",
    operators=[ResponseCompleteness()],
    plots=[Histogram(x="score_response_completeness")],
)

CheckResponseRelevance = lambda: Check(
    name="response_relevance_score",
    operators=[ResponseRelevance()],
    plots=[Histogram(x="score_response_relevance")],
)

# -----------------------------------------------------------
# Language quality related
# -----------------------------------------------------------

CheckLanguageQuality = lambda: Check(
    name="language_critique_score",
    operators=[LanguageCritique()],
    plots=[
        Histogram(x="score_fluency"),
        Histogram(x="score_coherence"),
        Histogram(x="score_politeness"),
        Histogram(x="score_grammar"),
    ],
)

CheckToneQuality = lambda persona: Check(
    name="tone_critique_score",
    operators=[ToneCritique(persona=persona)],
    plots=[Histogram(x="score_tone")],
)