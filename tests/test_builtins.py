"""
Test that the builtin checks work without raising an error. NOT that they are appropriate for the task.

What we are checking
1. Check returns a DataFrame with the expected columns
2. The score and explanation columns have the expected types
3. The score and explanation columns have at least one non-null value (i.e. the check ran successfully)
"""

import polars as pl
import os

from uptrain.framework import Settings
from uptrain.framework.builtins import (
    CheckResponseCompleteness,
    CheckResponseConciseness,
    CheckResponseRelevance,
    CheckValidResponse,
    CheckResponseConsistency,
    CheckContextRelevance,
    CheckContextReranking,
    CheckContextConciseness,
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
    CheckSubQueryCompleteness,
)

# Enter your OpenAI API key here if it is not already set as an environment variable
openai_api_key = os.environ.get("OPENAI_API_KEY")

settings = Settings(openai_api_key=openai_api_key)

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
    assert (
        "score_response_completeness" in output.columns
        and "explanation_response_completeness" in output.columns
    )
    assert (
        output["score_response_completeness"].dtype == pl.Float64
        and len(output["score_response_completeness"])
        - output["score_response_completeness"].null_count()
        > 0
    )
    assert (
        output["explanation_response_completeness"].dtype == pl.Utf8
        and len(output["explanation_response_completeness"])
        - output["explanation_response_completeness"].null_count()
        > 0
    )


def test_check_response_conciseness():
    check = CheckResponseConciseness()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_response_conciseness" in output.columns
        and "explanation_response_conciseness" in output.columns
    )
    assert (
        output["score_response_conciseness"].dtype == pl.Float64
        and len(output["score_response_conciseness"])
        - output["score_response_conciseness"].null_count()
        > 0
    )
    assert (
        output["explanation_response_conciseness"].dtype == pl.Utf8
        and len(output["explanation_response_conciseness"])
        - output["explanation_response_conciseness"].null_count()
        > 0
    )


def test_check_response_relevance():
    check = CheckResponseRelevance()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_response_relevance" in output.columns
        and "explanation_response_relevance" in output.columns
    )
    assert (
        output["score_response_relevance"].dtype == pl.Float64
        and len(output["score_response_relevance"])
        - output["score_response_relevance"].null_count()
        > 0
    )
    assert (
        output["explanation_response_relevance"].dtype == pl.Utf8
        and len(output["explanation_response_relevance"])
        - output["explanation_response_relevance"].null_count()
        > 0
    )


def test_check_valid_response():
    check = CheckValidResponse()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_valid_response" in output.columns
        and "explanation_valid_response" in output.columns
    )
    assert (
        output["score_valid_response"].dtype == pl.Float64
        and len(output["score_valid_response"])
        - output["score_valid_response"].null_count()
        > 0
    )
    assert (
        output["explanation_valid_response"].dtype == pl.Utf8
        and len(output["explanation_valid_response"])
        - output["explanation_valid_response"].null_count()
        > 0
    )


def test_check_response_consistency():
    check = CheckResponseConsistency()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_response_consistency" in output.columns
        and "explanation_response_consistency" in output.columns
    )     
    assert (
        output["score_response_consistency"].dtype == pl.Float64 
        and len(output["score_response_consistency"]) 
        - output["score_response_consistency"].null_count() > 0
    )
    assert (
        output["explanation_response_consistency"].dtype == pl.Utf8 
        and len(output["explanation_response_consistency"]) 
        - output["explanation_response_consistency"].null_count() > 0
    )


response_matching_dataset = pl.DataFrame(
    {
        "question": [
            "Do both Ronaldo and Messi play in the Spanish League?",
        ],
        "response": [
            "Yes, Messi plays in the Spanish League. However, Ronaldo plays in the English league.",
        ],
        "ground_truth": [
            "no",
        ],
    }
)


def test_check_response_matching():
    check = CheckResponseMatching()
    output = check.setup(settings).run(response_matching_dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_response_matching" in output.columns
        and "explanation_response_matching" in output.columns
    )
    assert (
        output["score_response_matching"].dtype == pl.Float64
        and len(output["score_response_matching"])
        - output["score_response_matching"].null_count()
        > 0
    )
    assert (
        output["explanation_response_matching"].dtype == pl.Utf8
        and len(output["explanation_response_matching"])
        - output["explanation_response_matching"].null_count()
        > 0
    )


# -----------------------------------------------------------
# Context Quality
# -----------------------------------------------------------


def test_check_context_relevance():
    check = CheckContextRelevance()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_context_relevance" in output.columns
        and "explanation_context_relevance" in output.columns
    )
    assert (
        output["score_context_relevance"].dtype == pl.Float64
        and len(output["score_context_relevance"])
        - output["score_context_relevance"].null_count()
        > 0
    )
    assert (
        output["explanation_context_relevance"].dtype == pl.Utf8
        and len(output["explanation_context_relevance"])
        - output["explanation_context_relevance"].null_count()
        > 0
    )


context_reranking_dataset = pl.DataFrame(
    {
        "question": ["What are the main causes of climate change?"],
        "context": [
            """
            1. The main causes of climate change include greenhouse gas emissions from human activities such as burning fossil fuels, deforestation, and industrial processes.
            2. Climate change is primarily driven by human-induced factors, including the release of carbon dioxide and other greenhouse gases into the atmosphere.
            3. Human activities such as the burning of fossil fuels, agricultural practices, and land-use changes contribute significantly to climate change by increasing the concentration of greenhouse gases in the atmosphere.
            4. Other factors that contribute to climate change include methane emissions from livestock and rice paddies, as well as nitrous oxide emissions from agricultural fertilizers.
            5. Changes in land use, such as urbanization and deforestation, also play a role in altering local climates and contributing to global climate change.
            """,
        ],
        "reranked_context": [
            """
            1. Climate change is primarily driven by human-induced factors, including the release of carbon dioxide and other greenhouse gases into the atmosphere.
            2. The main causes of climate change include greenhouse gas emissions from human activities such as burning fossil fuels, deforestation, and industrial processes.
            3. Human activities such as the burning of fossil fuels, agricultural practices, and land-use changes contribute significantly to climate change by increasing the concentration of greenhouse gases in the atmosphere.
            4. Other factors that contribute to climate change include methane emissions from livestock and rice paddies, as well as nitrous oxide emissions from agricultural fertilizers.
            5. Changes in land use, such as urbanization and deforestation, also play a role in altering local climates and contributing to global climate change.
            """,
        ],
    }
)


def test_check_context_reranking():
    check = CheckContextReranking()
    output = check.setup(settings).run(context_reranking_dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_context_reranking" in output.columns
        and "explanation_context_reranking" in output.columns
    )
    assert (
        output["score_context_reranking"].dtype == pl.Float64
        and len(output["score_context_reranking"])
        - output["score_context_reranking"].null_count()
        > 0
    )
    assert (
        output["explanation_context_reranking"].dtype == pl.Utf8
        and len(output["explanation_context_reranking"])
        - output["explanation_context_reranking"].null_count()
        > 0
    )


context_conciseness_dataset = pl.DataFrame(
    {
        "question": ["What are the main causes of climate change?"],
        "context": [
            """
            1. The main causes of climate change include greenhouse gas emissions from human activities such as burning fossil fuels, deforestation, and industrial processes.
            2. Climate change is primarily driven by human-induced factors, including the release of carbon dioxide and other greenhouse gases into the atmosphere.
            3. Human activities such as the burning of fossil fuels, agricultural practices, and land-use changes contribute significantly to climate change by increasing the concentration of greenhouse gases in the atmosphere.
            4. Other factors that contribute to climate change include methane emissions from livestock and rice paddies, as well as nitrous oxide emissions from agricultural fertilizers.
            5. Changes in land use, such as urbanization and deforestation, also play a role in altering local climates and contributing to global climate change.
            """,
        ],
        "concise_context": [
            """
            1. Climate change is primarily driven by human-induced factors, including the release of carbon dioxide and other greenhouse gases into the atmosphere.
            2. The main causes of climate change include greenhouse gas emissions from human activities such as burning fossil fuels, deforestation, and industrial processes.
            """,
        ],
    }
)


def test_check_context_conciseness():
    check = CheckContextConciseness()
    output = check.setup(settings).run(context_conciseness_dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_context_conciseness" in output.columns
        and "explanation_context_conciseness" in output.columns
    )
    assert (
        output["score_context_conciseness"].dtype == pl.Float64
        and len(output["score_context_conciseness"])
        - output["score_context_conciseness"].null_count()
        > 0
    )
    assert (
        output["explanation_context_conciseness"].dtype == pl.Utf8
        and len(output["explanation_context_conciseness"])
        - output["explanation_context_conciseness"].null_count()
        > 0
    )


def test_check_response_completeness_wrt_context():
    check = CheckResponseCompletenessWrtContext()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_response_completeness_wrt_context" in output.columns
        and "explanation_response_completeness_wrt_context" in output.columns
    )
    assert (
        output["score_response_completeness_wrt_context"].dtype == pl.Float64
        and len(output["score_response_completeness_wrt_context"])
        - output["score_response_completeness_wrt_context"].null_count()
        > 0
    )
    assert (
        output["explanation_response_completeness_wrt_context"].dtype == pl.Utf8
        and len(output["explanation_response_completeness_wrt_context"])
        - output["explanation_response_completeness_wrt_context"].null_count()
        > 0
    )


def test_check_response_facts():
    check = CheckResponseFacts()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_factual_accuracy" in output.columns
        and "explanation_factual_accuracy" in output.columns
    )
    assert (
        output["score_factual_accuracy"].dtype == pl.Float64
        and len(output["score_factual_accuracy"])
        - output["score_factual_accuracy"].null_count()
        > 0
    )
    assert (
        output["explanation_factual_accuracy"].dtype == pl.Utf8
        and len(output["explanation_factual_accuracy"])
        - output["explanation_factual_accuracy"].null_count()
        > 0
    )


# -----------------------------------------------------------
# Language Proficiency
# -----------------------------------------------------------


def test_check_language_quality():
    check = CheckLanguageQuality()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_critique_language" in output.columns
        and "explanation_critique_language" in output.columns
    )
    assert (
        output["score_critique_language"].dtype == pl.Float64
        and len(output["score_critique_language"])
        - output["score_critique_language"].null_count()
        > 0
    )
    assert (
        output["explanation_critique_language"].dtype == pl.Utf8
        and len(output["explanation_critique_language"])
        - output["explanation_critique_language"].null_count()
        > 0
    )


def test_check_tone_quality():
    check = CheckToneQuality(llm_persona="wikipedia-bot")
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_critique_tone" in output.columns
        and "explanation_critique_tone" in output.columns
    )
    assert (
        output["score_critique_tone"].dtype == pl.Float64
        and len(output["score_critique_tone"])
        - output["score_critique_tone"].null_count()
        > 0
    )
    assert (
        output["explanation_critique_tone"].dtype == pl.Utf8
        and len(output["explanation_critique_tone"])
        - output["explanation_critique_tone"].null_count()
        > 0
    )


# # -----------------------------------------------------------
# # Code Hallucinations
# # -----------------------------------------------------------

code_hallucination_dataset = pl.DataFrame(
    {
        "question": [
            "How to use the sessionstate feature in Streamlit",
            "Can I create histograms with different bucket colors in Streamlit",
        ],
        "context": [
            'This property lets you store Python primitives such as integers, floating-point numbers, complex numbers and booleans, dataframes, and even [lambdas](https://docs.python.org/3/reference/expressions.html#lambda) returned by functions. However, some execution environments may require serializing all data in Session State, so it may be useful to detect incompatibility during development, or when the execution environment will stop supporting it in the future.\n\nTo that end, Streamlit provides a `runner.enforceSerializableSessionState` [configuration option](https://docs.streamlit.io/library/advanced-features/configuration) that, when set to `true`, only allows pickle-serializable objects in Session State. To enable the option, either create a global or project config file with the following or use it as a command-line flag:\n\n\n```\n# .streamlit/config.toml\n[runner]\nenforceSerializableSessionState = true\n\n```\nBy "*pickle-serializable*", we mean calling `pickle.dumps(obj)` should not raise a [`PicklingError`](https://docs.python.org/3/library/pickle.html#pickle.PicklingError) exception. When the config option is enabled, adding unserializable data to session state should result in an exception. E.g.,\n\n\n```\nimport streamlit as st\n\ndef unserializable_data():\n        return lambda x: x\n\n#👇 results in an exception when enforceSerializableSessionState is on\nst.session_state.unserializable = unserializable_data()\n\n```\n![UnserializableSessionStateError](https://docs.streamlit.io/images/unserializable-session-state-error.png)',
            'eader("Define a custom colorscale")\ndf = px.data.iris()\nfig = px.scatter(\n    df,\n    x="sepal_width",\n    y="sepal_length",\n    color="sepal_length",\n    color_continuous_scale="reds",\n)\n\ntab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])\nwith tab1:\n    st.plotly_chart(fig, theme="streamlit", use_container_width=True)\nwith tab2:\n    st.plotly_chart(fig, theme=None, use_container_width=True)\n\n```\nNotice how the custom color scale is still reflected in the chart, even when the Streamlit theme is enabled 👇\n\nFor many more examples of Plotly charts with and without the Streamlit theme, check out the [plotly.streamlit.app](https://plotly.streamlit.app).\n\n',
        ],
        "response": [
            'Serialization refers to the process of converting an object or data structure into a format that can be persisted and shared, and allowing you to recover the data’s original structure.\n\nBy default, Streamlit’s [Session State](https://docs.streamlit.io/library/advanced-features/session-state) allows you to persist any Python object for the duration of the session, irrespective of the object’s pickle-serializability. \n\nStreamlit provides a `runner.enforceSerializableSessionState` [configuration option](https://docs.streamlit.io/library/advanced-features/configuration) that, when set to `true`, only allows pickle-serializable objects in Session State.\n\nBy "*pickle-serializable*", we mean calling `pickle.dumps(obj)` should not raise a [`PicklingError`](https://docs.python.org/3/library/pickle.html#pickle.PicklingError) exception',
            "The `color_continuous_scale` parameter in the `px.scatter` function allows you to define a custom color scale for the plot. You can use any of the built-in color scales provided by Plotly, or you can define your own custom color scale using a list of colors. The `color_continuous_scale` parameter accepts a string that specifies the name of the color scale to use. You can also pass a list of colors to the `color_continuous_scale` parameter to define a custom color scale. The list of colors can be any length, and the colors can be specified using any valid CSS color format, such as hex, RGB, or HSL. The `color_continuous_scale` parameter allows you to create a custom color scale for the plot that is tailored to your specific needs.",
        ],
    }
)


def test_check_code_hallucination():
    check = CheckCodeHallucination()
    output = check.setup(settings).run(code_hallucination_dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_code_hallucination" in output.columns
        and "explanation_code_hallucination" in output.columns
    )
    assert (
        output["score_code_hallucination"].dtype == pl.Float64
        and len(output["score_code_hallucination"])
        - output["score_code_hallucination"].null_count()
        > 0
    )
    assert (
        output["explanation_code_hallucination"].dtype == pl.Utf8
        and len(output["explanation_code_hallucination"])
        - output["explanation_code_hallucination"].null_count()
        > 0
    )


# # -----------------------------------------------------------
# # Conversation Quality
# # -----------------------------------------------------------

conversation_satisfaction_dataset = pl.DataFrame(
    {
        "conversation": [
            """
            Patient: I have been feeling very tired lately.
            Doctor: Have you been sleeping well?
            Patient: No, I have been having trouble sleeping.
            Doctor: What time do you usually go to bed?
            Patient: I go to bed around 11 pm.
            Doctor: Do you have any other symptoms?
            Patient: No, just the tiredness.
            Doctor: I recommend you get a full blood test done.
            """,
            """
            Patient: My left knee has been hurting a lot.
            Doctor: Have you tried taking painkillers?
            Patient: Yes, but the pain comes back after a while.
            Doctor: You should try to rest your knee.
            Patient: I have been resting it for a few days now.
            Doctor: I don't know what else to suggest.
            """,
        ]
    }
)


def test_check_conversation_satisfaction():
    check = CheckConversationSatisfaction(user_role="Patient", llm_role="Doctor")
    output = check.setup(settings).run(conversation_satisfaction_dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_conversation_satisfaction" in output.columns
        and "explanation_conversation_satisfaction" in output.columns
    )
    assert (
        output["score_conversation_satisfaction"].dtype == pl.Float64
        and len(output["score_conversation_satisfaction"])
        - output["score_conversation_satisfaction"].null_count()
        > 0
    )
    assert (
        output["explanation_conversation_satisfaction"].dtype == pl.Utf8
        and len(output["explanation_conversation_satisfaction"])
        - output["explanation_conversation_satisfaction"].null_count()
        > 0
    )


# -----------------------------------------------------------
# Custom Evaluations
# -----------------------------------------------------------


def test_check_guideline_adherence():
    check = CheckGuidelineAdherence(
        guideline="The response should not contain any numbers or statistic",
        guideline_name="guideline",
        response_schema=None,
    )
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_guideline_adherence" in output.columns
        and "explanation_guideline_adherence" in output.columns
    )
    assert (
        output["score_guideline_adherence"].dtype == pl.Float64
        and len(output["score_guideline_adherence"])
        - output["score_guideline_adherence"].null_count()
        > 0
    )
    assert (
        output["explanation_guideline_adherence"].dtype == pl.Utf8
        and len(output["explanation_guideline_adherence"])
        - output["explanation_guideline_adherence"].null_count()
        > 0
    )


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
    assert (
        "score_prompt_injection" in output.columns
        and "explanation_prompt_injection" in output.columns
    )
    assert (
        output["score_prompt_injection"].dtype == pl.Float64
        and len(output["score_prompt_injection"])
        - output["score_prompt_injection"].null_count()
        > 0
    )
    assert (
        output["explanation_prompt_injection"].dtype == pl.Utf8
        and len(output["explanation_prompt_injection"])
        - output["explanation_prompt_injection"].null_count()
        > 0
    )


def test_check_jailbreak_detection():
    check = CheckJailbreakDetection()
    output = check.setup(settings).run(dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_jailbreak_attempted" in output.columns
        and "explanation_jailbreak_attempted" in output.columns
    )
    assert (
        output["score_jailbreak_attempted"].dtype == pl.Float64
        and len(output["score_jailbreak_attempted"])
        - output["score_jailbreak_attempted"].null_count()
        > 0
    )
    assert (
        output["explanation_jailbreak_attempted"].dtype == pl.Utf8
        and len(output["explanation_jailbreak_attempted"])
        - output["explanation_jailbreak_attempted"].null_count()
        > 0
    )


# -----------------------------------------------------------
# Sub Query
# -----------------------------------------------------------

sub_query_dataset = pl.DataFrame(
    {
        "question": [
            "What did Sam Altman do before, during, and after Y Combinator?",
            "What are the causes, effects, and solutions to climate change?",
            "What are the benefits, risks, and regulations of AI?",
            "What are the differences, similarities, and applications of Python and Java?",
            "What are the advantages, disadvantages, and use cases of blockchain?",
        ],
        "sub_questions": [
            """
            1. What did Sam Altman do before Y Combinator?
            2. What did Sam Altman do during Y Combinator?
            3. What did Sam Altman do after Y Combinator?
            """,
            """
            1. What are the causes of climate change?
            2. What are the effects of climate change?
            3. What are the solutions to climate change?
            """,
            """
            1. What are the benefits of AI?
            2. What is AI?
            3. What are the regulations of AI?
            """,
            """
            1. What are the differences between Python and Java?
            2. What are the similarities between Python and Java?
            """,
            """
            1. What are the advantages of blockchain?
            2. What are the disadvantages of blockchain?
            3. What are the use cases of cryptography?
            """,
        ],
    }
)


def test_check_sub_query_completeness():
    check = CheckSubQueryCompleteness()
    output = check.setup(settings).run(sub_query_dataset)
    assert isinstance(output, pl.DataFrame)
    assert (
        "score_sub_query_completeness" in output.columns
        and "explanation_sub_query_completeness" in output.columns
    )
    assert (
        output["score_sub_query_completeness"].dtype == pl.Float64
        and len(output["score_sub_query_completeness"])
        - output["score_sub_query_completeness"].null_count()
        > 0
    )
    assert (
        output["explanation_sub_query_completeness"].dtype == pl.Utf8
        and len(output["explanation_sub_query_completeness"])
        - output["explanation_sub_query_completeness"].null_count()
        > 0
    )
