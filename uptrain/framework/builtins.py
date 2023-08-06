"""This module hosts built-in checks for some common LLM evaluation tasks."""

from __future__ import annotations
import typing as t

from .checks import Check
from uptrain.operators import Histogram
from uptrain.operators import (
    ResponseFactualScore,
    ResponseCompleteness,
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
    plots=[Histogram(x="response_factual_score")],
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

_TEMPLATE_RESPONSE_COMPLETENESS = """
You are a language assessment coach who critiques and grades machine generated responses in a conversation. You can check for consistency, identify logical fallacies or incorrect assumptions, and other errors in reasoning.

For the provided question-answer pair, please assess if the machine-generated response is relevant and answers the user query adequately. Don't focus on aspects like style, grammar, or punctuation. 

Task data.
[Question]: {question}
[Response]: {response}

Please form your response by selecting one of the following options. 

A. The generated answer doesn't answer the given question at all.
B. The generated answer answers the given question partially.
C. The generated answer answers the given question adequately. 
"""

CheckResponseCompleteness = lambda: Check(
    name="response_completeness_score",
    operators=[ResponseCompleteness()],
    plots=[Histogram(x="score_response_completeness")],
)
