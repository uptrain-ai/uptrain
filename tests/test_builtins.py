"""
Test that the builtin checks work without raising an error. NOT that they are appropriate for the task.

What we are checking
1. Check returns a DataFrame with the expected columns
2. The score and explanation columns have the expected types
3. The score and explanation columns have at least one non-null value (i.e. the check ran successfully)
"""

import polars as pl

from uptrain.framework import Settings
from uptrain.framework.builtins import (
    CheckResponseCompleteness,
    CheckResponseConciseness,
    CheckResponseRelevance,
    CheckValidResponse,
    CheckResponseConsistency,
    CheckContextRelevance,
    CheckResponseCompletenessWrtContext,
    CheckResponseFacts,
    CheckLanguageQuality,
    CheckToneQuality,
    CheckCodeHallucination,
    CheckConversationSatisfaction,
    CheckGuidelineAdherence,
    CheckResponseMatching,
    CheckPromptInjection,
    CheckJailbreakDetection,
)

settings = Settings(openai_api_key="sk-************************")
dataset = pl.DataFrame(
    {
        "response": [
            "The actress who played Lolita, Sue Lyon, was 14 at the time of filming.",
            "Shakespeare wrote 154 sonnets.",
            "Sachin Tendulkar retired from cricket in 2013.",
            "Python language was created by Guido van Rossum.",
            "The first manned Apollo mission was Apollo 1.",
        ],
        "question": [
            "What was the age of Sue Lyon when she played Lolita?",
            "How many sonnets did Shakespeare write?",
            "When did Sachin Tendulkar retire from cricket?",
            "Who created the Python language?",
            "Which was the first manned Apollo mission?",
        ],
        "context": [
            "Lolita is a 1962 psychological comedy-drama film directed by Stanley Kubrick. The film follows Humbert Humbert, a middle-aged literature lecturer who becomes infatuated with Dolores Haze, a young adolescent girl. It stars Sue Lyon as the titular character.",
            "William Shakespeare was an English playwright and poet, widely regarded as the world's greatest dramatist. He is often called the Bard of Avon. His works consist of some 39 plays, 154 sonnets and a few other verses.",
            "Sachin Tendulkar is a former international cricketer from India. He is widely regarded as one of the greatest batsmen in the history of cricket. He is the highest run scorer of all time in International cricket and played until 16 May 2013.",
            "Python is a high-level general-purpose programming language. Its design philosophy emphasizes code readability. Its language constructs aim to help programmers write clear, logical code for both small and large-scale projects.",
            "The Apollo program was a human spaceflight program carried out by NASA. It accomplished landing the first humans on the Moon from 1969 to 1972. The program was named after Apollo, the Greek god of light, music, and the sun. The first mission flown was dubbed as Apollo 1.",
        ],
    }
)


# -----------------------------------------------------------
# Response Quality
# -----------------------------------------------------------


def test_check_response_completeness():
    check = CheckResponseCompleteness()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_response_completeness" in output.columns and "explanation_response_completeness" in output.columns
    assert output["score_response_completeness"].dtype == pl.Float64 and len(output["score_response_completeness"]) - output["score_response_completeness"].null_count() > 0
    assert output["explanation_response_completeness"].dtype == pl.Utf8 and len(output["explanation_response_completeness"]) - output["explanation_response_completeness"].null_count() > 0


def test_check_response_conciseness():
    check = CheckResponseConciseness()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_response_conciseness" in output.columns and "explanation_response_conciseness" in output.columns
    assert output["score_response_conciseness"].dtype == pl.Float64 and len(output["score_response_conciseness"]) - output["score_response_conciseness"].null_count() > 0
    assert output["explanation_response_conciseness"].dtype == pl.Utf8 and len(output["explanation_response_conciseness"]) - output["explanation_response_conciseness"].null_count() > 0


def test_check_response_relevance():
    check = CheckResponseRelevance()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_response_relevance" in output.columns and "explanation_response_relevance" in output.columns
    assert output["score_response_relevance"].dtype == pl.Float64 and len(output["score_response_relevance"]) - output["score_response_relevance"].null_count() > 0
    assert output["explanation_response_relevance"].dtype == pl.Utf8 and len(output["explanation_response_relevance"]) - output["explanation_response_relevance"].null_count() > 0


def test_check_valid_response():
    check = CheckValidResponse()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_valid_response" in output.columns and "explanation_valid_response" in output.columns
    assert output["score_valid_response"].dtype == pl.Float64 and len(output["score_valid_response"]) - output["score_valid_response"].null_count() > 0
    assert output["explanation_valid_response"].dtype == pl.Utf8 and len(output["explanation_valid_response"]) - output["explanation_valid_response"].null_count() > 0


def test_check_response_consistency():
    check = CheckResponseConsistency()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_response_consistency" in output.columns and "explanation_response_consistency" in output.columns
    assert output["score_response_consistency"].dtype == pl.Float64 and len(output["score_response_consistency"]) - output["score_response_consistency"].null_count() > 0
    assert output["explanation_response_consistency"].dtype == pl.Utf8 and len(output["explanation_response_consistency"]) - output["explanation_response_consistency"].null_count() > 0

# -----------------------------------------------------------
# Context Quality
# -----------------------------------------------------------


def test_check_context_relevance():
    check = CheckContextRelevance()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_context_relevance" in output.columns and "explanation_context_relevance" in output.columns
    assert output["score_context_relevance"].dtype == pl.Float64 and len(output["score_context_relevance"]) - output["score_context_relevance"].null_count() > 0
    assert output["explanation_context_relevance"].dtype == pl.Utf8 and len(output["explanation_context_relevance"]) - output["explanation_context_relevance"].null_count() > 0


def test_check_response_completeness_wrt_context():
    check = CheckResponseCompletenessWrtContext()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_response_completeness_wrt_context" in output.columns and "explanation_response_completeness_wrt_context" in output.columns
    assert output["score_response_completeness_wrt_context"].dtype == pl.Float64 and len(output["score_response_completeness_wrt_context"]) - output["score_response_completeness_wrt_context"].null_count() > 0
    assert output["explanation_response_completeness_wrt_context"].dtype == pl.Utf8 and len(output["explanation_response_completeness_wrt_context"]) - output["explanation_response_completeness_wrt_context"].null_count() > 0


def test_check_response_facts():
    check = CheckResponseFacts()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_factual_accuracy" in output.columns and "explanation_factual_accuracy" in output.columns
    assert output["score_factual_accuracy"].dtype == pl.Float64 and len(output["score_factual_accuracy"]) - output["score_factual_accuracy"].null_count() > 0
    assert output["explanation_factual_accuracy"].dtype == pl.Utf8 and len(output["explanation_factual_accuracy"]) - output["explanation_factual_accuracy"].null_count() > 0


# -----------------------------------------------------------
# Language Proficiency
# -----------------------------------------------------------

def test_check_language_quality():
    check = CheckLanguageQuality()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_critique_language" in output.columns and "explanation_critique_language" in output.columns
    assert output["score_critique_language"].dtype == pl.Float64 and len(output["score_critique_language"]) - output["score_critique_language"].null_count() > 0
    assert output["explanation_critique_language"].dtype == pl.Utf8 and len(output["explanation_critique_language"]) - output["explanation_critique_language"].null_count() > 0


def test_check_tone_quality():
    check = CheckToneQuality(llm_persona="wikipedia-bot")
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_critique_tone" in output.columns and "explanation_critique_tone" in output.columns
    assert output["score_critique_tone"].dtype == pl.Float64 and len(output["score_critique_tone"]) - output["score_critique_tone"].null_count() > 0
    assert output["explanation_critique_tone"].dtype == pl.Utf8 and len(output["explanation_critique_tone"]) - output["explanation_critique_tone"].null_count() > 0


# # -----------------------------------------------------------
# # Code Hallucinations
# # -----------------------------------------------------------
    
# def test_check_code_hallucination():
#     check = CheckCodeHallucination()
#     output = check.setup(settings).run(dataset)
#     assert isinstance(output, pl.DataFrame)
#     assert "score_code_hallucination" in output.columns and "explanation_code_hallucination" in output.columns
#     assert output["score_code_hallucination"].dtype == pl.Float64 and len(output["score_code_hallucination"]) - output["score_code_hallucination"].null_count() > 0
#     assert output["explanation_code_hallucination"].dtype == pl.Utf8 and len(output["explanation_code_hallucination"]) - output["explanation_code_hallucination"].null_count() > 0


# # -----------------------------------------------------------
# # Conversation Quality
# # -----------------------------------------------------------
    
# def test_check_conversation_satisfaction():
#     check = CheckConversationSatisfaction(user_persona="user", llm_persona="wikipedia-bot")
#     output = check.setup(settings).run(dataset)
#     assert isinstance(output, pl.DataFrame)
#     assert "score_conversation_satisfaction" in output.columns and "explanation_conversation_satisfaction" in output.columns
#     assert output["score_conversation_satisfaction"].dtype == pl.Float64 and len(output["score_conversation_satisfaction"]) - output["score_conversation_satisfaction"].null_count() > 0
#     assert output["explanation_conversation_satisfaction"].dtype == pl.Utf8 and len(output["explanation_conversation_satisfaction"]) - output["explanation_conversation_satisfaction"].null_count() > 0


# -----------------------------------------------------------
# Custom Evaluations
# -----------------------------------------------------------
    
def test_check_guideline_adherence():
    check = CheckGuidelineAdherence(guideline="The response should not contain any numbers or statistic", guideline_name="guideline", response_schema=None)
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_guideline_adherence" in output.columns and "explanation_guideline_adherence" in output.columns
    assert output["score_guideline_adherence"].dtype == pl.Float64 and len(output["score_guideline_adherence"]) - output["score_guideline_adherence"].null_count() > 0
    assert output["explanation_guideline_adherence"].dtype == pl.Utf8 and len(output["explanation_guideline_adherence"]) - output["explanation_guideline_adherence"].null_count() > 0


# # -----------------------------------------------------------
# # Compare response with ground truth
# # -----------------------------------------------------------
    
# def test_check_response_matching():
#     check = CheckResponseMatching()
#     output = check.setup(settings).run(dataset)
#     assert isinstance(output, pl.DataFrame)
#     assert "score_response_matching" in output.columns and "explanation_response_matching" in output.columns
#     assert output["score_response_matching"].dtype == pl.Float64 and len(output["score_response_matching"]) - output["score_response_matching"].null_count() > 0
#     assert output["explanation_response_matching"].dtype == pl.Utf8 and len(output["explanation_response_matching"]) - output["explanation_response_matching"].null_count() > 0


# -----------------------------------------------------------
# Security
# -----------------------------------------------------------
    
def test_check_prompt_injection():
    check = CheckPromptInjection()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_prompt_injection" in output.columns and "explanation_prompt_injection" in output.columns
    assert output["score_prompt_injection"].dtype == pl.Float64 and len(output["score_prompt_injection"]) - output["score_prompt_injection"].null_count() > 0
    assert output["explanation_prompt_injection"].dtype == pl.Utf8 and len(output["explanation_prompt_injection"]) - output["explanation_prompt_injection"].null_count() > 0


def test_check_jailbreak_detection():
    check = CheckJailbreakDetection()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert "score_jailbreak_attempted" in output.columns and "explanation_jailbreak_attempted" in output.columns
    assert output["score_jailbreak_attempted"].dtype == pl.Float64 and len(output["score_jailbreak_attempted"]) - output["score_jailbreak_attempted"].null_count() > 0
    assert output["explanation_jailbreak_attempted"].dtype == pl.Utf8 and len(output["explanation_jailbreak_attempted"]) - output["explanation_jailbreak_attempted"].null_count() > 0

