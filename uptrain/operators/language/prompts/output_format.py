# Factual Accuracy
FACT_GENERATE_OUTPUT_FORMAT = """
[ # A list of numerically-ordered facts
    "1. 1st Fact",
    "2. 2nd Fact",
    ...
]
In case of no facts, return an empty list, i.e. [].
"""

FACT_EVALUATE_OUTPUT_FORMAT__CLASSIFY = """
[   # List containing data for all the facts
    {
        "Fact": [1st Fact]  # 1st fact being analysed,
        "Judgement": [Judgement for 1st Fact]  # Judgement for 1st fact. Select one of the three - "yes", "unclear" or "no",
    },
    {
        "Fact": [2nd Fact]  # 2nd fact being analysed,
        "Judgement": [Judgement for 2nd Fact]  # Judgement for 2nd fact. Select one of the three - "yes", "unclear" or "no",
    },
    ... # Do for all the facts
]
"""

FACT_EVALUATE_OUTPUT_FORMAT__COT = """
[   # List containing data for all the facts
    {
        "Fact": [1st Fact],  # 1st fact being analysed,
        "Reasoning": [Reasoning for 1st Fact],  # Reasoning to determine if the 1st fact can be verified from the context or not,
        "Judgement": [Judgement for 1st Fact],  # Judgement for 1st fact. Select one of the three - "yes", "unclear" or "no",
    },
    {
        "Fact": [2nd Fact],  # 2nd fact being analysed,
        "Reasoning": [Reasoning for 2nd Fact],  # Reasoning to determine if the 2nd fact can be verified from the context or not,
        "Judgement": [Judgement for 2nd Fact], # Judgement for 2nd fact. Select one of the three - "yes", "unclear" or "no",
    },
    ... # Do for all the facts
]
"""


# Context Relevance
CONTEXT_RELEVANCE_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

CONTEXT_RELEVANCE_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine the relevance of context for answering the query,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Response Completeness
# Same as the one for context_relevance, but kept separate to maintain consistency and allow for future changes
RESPONSE_COMPLETENESS_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

RESPONSE_COMPLETENESS_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine the completeness of the response for answering the query,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Response Conciseness
RESPONSE_CONCISENESS_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

RESPONSE_CONCISENESS_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine the conciseness of the response for answering the query,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Response Completeness wrt Context
RESPONSE_COMPLETENESS_WRT_CONTEXT_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

RESPONSE_COMPLETENESS_WRT_CONTEXT_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine if all the relevant information in context is utilized in the response,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Response Consistency
RESPONSE_CONSISTENCY_OUTPUT_FORMAT__CLASSIFY = """
{
    "Score": [Score],  # Score (between 0 and 1) to determine the quality of reasoning generated to justify the given response for answering the given query,
}
"""

RESPONSE_CONSISTENCY_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine the quality of reasoning generated to justify the given response for answering the given query,
    "Score": [Score],  # Score (between 0 and 1) to determine the quality of reasoning generated to justify the given response for answering the given query,
}
"""


# Valid Response
VALID_RESPONSE_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""

VALID_RESPONSE_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine the validity of the response,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""


# Guideline Adherence
GUIDELINE_ADHERENCE_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""

GUIDELINE_ADHERENCE_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine if the given guideline is followed or not,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""


# Prompt Injection
PROMPT_INJECTION_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""

PROMPT_INJECTION_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine whether the user is trying to perform prompt injection or not,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""


# Jailbreak Detection
JAILBREAK_DETECTION_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""

JAILBREAK_DETECTION_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine whether the user is trying to jailbreak the model or not,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""


# Conversation Satisfaction
CONVERSATION_SATISFACTION_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

CONVERSATION_SATISFACTION_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine if the user seems frustated during the conversation,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Critique Tone
CRITIQUE_TONE_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

CRITIQUE_TONE_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to determine if the response tone matches the given persona,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Critique Language Fluency
LANGUAGE_FLUENCY_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

LANGUAGE_FLUENCY_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to critique the fluency of the response,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Critique Language Coherence
LANGUAGE_COHERENCE_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

LANGUAGE_COHERENCE_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to critique the coherence of the response,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Sub-query Completeness
SUBQUERY_COMPLETENESS_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

SUBQUERY_COMPLETENESS_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to critique the completeness the sub-queries to the main query,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Context Rerakning
CONTEXT_RERANKING_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

CONTEXT_RERANKING_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to critique the reranking of the context,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Context Conciseness
CONTEXT_CONCISENESS_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""

CONTEXT_CONCISENESS_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to critique the conciseness of the context,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}
"""


# Resposne Matching
RESPONSE_MATCHING_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""

RESPONSE_MATCHING_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to critique the matching of the response with the ground truth,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}
"""


# Code Hallucination
CODE_HALLUCINATION_OUTPUT_FORMAT__CLASSIFY = """
{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B"),
    "Snippet": [Code Snippet],  # Code snippet (if any) found in the response,
}
"""

CODE_HALLUCINATION_OUTPUT_FORMAT__COT = """
{
    "Reasoning": [Reasoning],  # Reasoning to critique the hallucination of the code,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B"),
    "Snippet": [Code Snippet],  # Code snippet (if any) found in the response,
}
"""
