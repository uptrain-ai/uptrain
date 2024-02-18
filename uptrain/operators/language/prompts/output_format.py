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
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""

CONTEXT_RELEVANCE_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine the relevance of context for answering the query,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""


# Response Completeness
# Same as the one for context_relevance, but kept separate to maintain consistency and allow for future changes
RESPONSE_COMPLETENESS_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""

RESPONSE_COMPLETENESS_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine the completeness of the response for answering the query,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""


# Response Conciseness
RESPONSE_CONCISENESS_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""

RESPONSE_CONCISENESS_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine the conciseness of the response for answering the query,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""


# Response Completeness wrt Context
RESPONSE_COMPLETENESS_WRT_CONTEXT_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""

RESPONSE_COMPLETENESS_WRT_CONTEXT_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine the completeness of the response for answering the query with respect to the context,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""


# Response Consistency
RESPONSE_CONSISTENCY_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""

RESPONSE_CONSISTENCY_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine the consistency of the response for answering the query with respect to the context,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""


# Valid Response
VALID_RESPONSE_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""

VALID_RESPONSE_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine the validity of the response for answering the query,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""


# Guideline Adherence
GUIDELINE_ADHERENCE_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""

GUIDELINE_ADHERENCE_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine the adherence of the response to the given guideline,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""


# Prompt Injection
PROMPT_INJECTION_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""

PROMPT_INJECTION_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine whether the user is trying to perform prompt injection or not,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""


# Jailbreak Detection
JAILBREAK_DETECTION_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""

JAILBREAK_DETECTION_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine whether the user is trying to jailbreak the model or not,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B")
}}
"""


# Conversation Satisfaction
CONVERSATION_SATISFACTION_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""

CONVERSATION_SATISFACTION_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to determine the satisfaction level of the user with the conversation,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""


# Critique Tone
CRITIQUE_TONE_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""

CRITIQUE_TONE_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to critique the tone of the AI model's responses,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""


# Critique Language
CRITIQUE_LANGUAGE_OUTPUT_FORMAT__CLASSIFY = """
{{
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""

CRITIQUE_LANGUAGE_OUTPUT_FORMAT__COT = """
{{
    "Reasoning": [Reasoning],  # Reasoning to critique the fluency, politeness, coherence and grammar of the AI model's responses,
    "Choice": [Selected Choice],  # Choice selected for the given task data, one of ("A", "B", "C")
}}
"""
