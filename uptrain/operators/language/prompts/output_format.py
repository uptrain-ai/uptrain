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


