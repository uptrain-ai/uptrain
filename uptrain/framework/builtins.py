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
    ResponseCompletenessWrtContext,
    GuidelineAdherenceScore
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


CheckResponseCompletenessWrtContext = lambda: Check(
    name="response_completeness_wrt_context_score",
    operators=[ResponseCompletenessWrtContext()],
    plots=[Histogram(x="score_response_completeness_wrt_context")],
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

# -----------------------------------------------------------
# Guideline related
# -----------------------------------------------------------

CheckGuidelineAdherence = lambda guideline, guideline_name="guideline", response_schema=None: Check(
    name = f"{guideline_name}_adherence_score",
    operators=[GuidelineAdherenceScore(guideline=guideline, guideline_name=guideline_name, response_schema=response_schema)],
    plots=[Histogram(x=f"score_{guideline_name}_adherence")]
)