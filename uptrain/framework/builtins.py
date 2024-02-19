"""This module hosts built-in checks for some common LLM evaluation tasks."""

from __future__ import annotations
from .checks import Check
from uptrain.operators import Histogram
from uptrain.operators import (
    ResponseFactualScore,
    ValidResponseScore,
    ResponseCompleteness,
    ResponseRelevance,
    ResponseConsistency,
    ResponseConciseness,
    ContextRelevance,
    PromptInjectionScore,
    LanguageCritique,
    ToneCritique,
    ResponseCompletenessWrtContext,
    GuidelineAdherenceScore,
    ResponseMatchingScore,
    ConversationSatisfactionScore,
    CodeHallucinationScore,
    JailbreakDetectionScore,
)


# -----------------------------------------------------------
# Response Quality
# -----------------------------------------------------------

def CheckResponseCompleteness():
    return Check(
        name="response_completeness_score",
        operators=[ResponseCompleteness()],
        plots=[Histogram(x="score_response_completeness")],
    )


def CheckResponseConciseness():
    return Check(
        name="response_conciseness_score",
        operators=[ResponseConciseness()],
        plots=[Histogram(x="score_response_conciseness")],
    )


def CheckResponseRelevance():
    return Check(
        name="response_relevance_score",
        operators=[ResponseRelevance()],
        plots=[Histogram(x="score_response_relevance")],
    )


def CheckValidResponse():
    return Check(
        name="valid_response_score",
        operators=[ValidResponseScore()],
        plots=[Histogram(x="score_valid_response")],
    )


def CheckResponseConsistency():
    return Check(
        name="response_consistency_score",
        operators=[ResponseConsistency()],
        plots=[Histogram(x="score_response_consistency")],
    )


# -----------------------------------------------------------
# Context Quality
# -----------------------------------------------------------

def CheckContextRelevance():
    return Check(
        name="score_context_relevance",
        operators=[ContextRelevance()],
        plots=[Histogram(x="score_context_relevance")],
    )


def CheckResponseCompletenessWrtContext():
    return Check(
        name="response_completeness_wrt_context_score",
        operators=[ResponseCompletenessWrtContext()],
        plots=[Histogram(x="score_response_completeness_wrt_context")],
    )


def CheckResponseFacts():
    return Check(
        name="score_factual_accuracy",
        operators=[ResponseFactualScore()],
        plots=[Histogram(x="score_factual_accuracy")],
    )



# -----------------------------------------------------------
# Language Proficiency
# -----------------------------------------------------------

def CheckLanguageQuality():
    return Check(
        name="language_critique_score",
        operators=[LanguageCritique()],
        plots=[
            Histogram(x="score_language_critique"),
        ],
    )


def CheckToneQuality(llm_persona):
    return Check(
        name="tone_critique_score",
        operators=[ToneCritique(llm_persona=llm_persona)],
        plots=[Histogram(x="score_critique_tone")],
    )


# -----------------------------------------------------------
# Code generation
# -----------------------------------------------------------

def CheckCodeHallucination():
    return Check(
        name="code_hallucination_score",
        operators=[CodeHallucinationScore()],
        plots=[Histogram(x="score_code_hallucination")],
    )


# -----------------------------------------------------------
# Conversation Quality
# -----------------------------------------------------------

def CheckConversationSatisfaction(user_persona="user", llm_persona=None):
    return Check(
        name="conversation_satisfaction_score",
        operators=[ConversationSatisfactionScore(user_persona, llm_persona)],
        plots=[Histogram(x="score_conversation_satisfaction")],
    )


# -----------------------------------------------------------
# Custom Evaluations
# -----------------------------------------------------------

def CheckGuidelineAdherence(
    guideline, guideline_name="guideline", response_schema=None
):
    return Check(
        name=f"{guideline_name}_adherence_score",
        operators=[
            GuidelineAdherenceScore(
                guideline=guideline,
                guideline_name=guideline_name,
                response_schema=response_schema,
            )
        ],
        plots=[Histogram(x=f"score_{guideline_name}_adherence")],
    )


# -----------------------------------------------------------
# Compare response with ground truth
# -----------------------------------------------------------

def CheckResponseMatching(method="llm"):
    return Check(
        name=f"{method}_score",
        operators=[ResponseMatchingScore(method=method)],
        plots=[Histogram(x=f"{method}_score")],
    )


# -----------------------------------------------------------
# Security
# -----------------------------------------------------------

def CheckPromptInjection():
    return Check(
        name="prompt_injection_score",
        operators=[PromptInjectionScore()],
        plots=[Histogram(x="score_prompt_injection")],
    )


def CheckJailbreakDetection():
    return Check(
        name="j`ailbreak_detection_score",
        operators=[JailbreakDetectionScore()],
        plots=[Histogram(x="score_jailbreak_attempted")],
    )
