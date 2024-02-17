# Factual Accuracy
FACT_EVAL_FEW_SHOT__CLASSIFY = """
[Facts]: ["1. The Eiffel Tower is located in Paris.", "2. The Eiffel Tower is the tallest structure in Paris.", "3. The Eiffel Tower is very old."]
[Context]: The Eiffel Tower, located in Paris, is one of the most visited monuments in the world. It was named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals.
[Output]: 
[
    {
        "Fact": "1. The Eiffel Tower is located in Paris.",
        "Judgement": "yes",
    },
    {
        "Fact": "2. The Eiffel Tower is the tallest structure in Paris.",
        "Judgement": "no",
    },
    {
        "Fact": "3. The Eiffel Tower is very old.",
        "Judgement": "unclear",
    },
]
"""

FACT_EVAL_FEW_SHOT__COT = """
[Facts]: ["1. The Eiffel Tower is located in Paris.", "2. The Eiffel Tower is the tallest structure in Paris.", "3. The Eiffel Tower is very old."]
[Context]: The Eiffel Tower, located in Paris, is one of the most visited monuments in the world. It was named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals.
[Output]: 
[
    {
        "Fact": "1. The Eiffel Tower is located in Paris.",
        "Reasoning": "The context explicity states that Paris, one of the most visited monuments in the world is located in Paris. Hence, the fact can be verified by the context.",
        "Judgement": "yes",
    },
    {
        "Fact": "2. The Eiffel Tower is the tallest structure in Paris.",
        "Reasoning": "While the context speaks about the popularity of Effiel Tower, it has no mention about its height or whether it is tallest or not. Hence, the the fact can not be verified by the context.",
        "Judgement": "no",
    },
    {
        "Fact": "3. The Eiffel Tower is very old.",
        "Reasoning": "While the context mentions that the Eiffel Tower was built in 1880s, it doesn't clarify what very old means.",
        "Judgement": "unclear",
    },
]
"""

FACT_GENERATE_FEW_SHOT = """
[Question]: Which is the tallest monument in Paris?
[Response]: The Eiffel Tower, located in Paris, is one of the most visited monuments in the world. It was named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals.
[Output]: 
[
    "1. The Eiffel Tower is located in Paris.",
    "2. The Eiffel Tower is one of the most visited monuments in the world.",
    "3. The Eiffel Tower was named after the engineer Gustave Eiffel.",
    "4. The Eiffel Tower was constructed from 1887 to 1889."
]


[Question]: Is Leaning Tower of Pisa, which is located in Italy, the oldest monument in Europe?
[Response]: No
[Output]: 
[
    "1. The Leaning Tower of Pisa is not the oldest monument in Europe.",
]
"""


# Context Relevance
CONTEXT_RELEVANCE_FEW_SHOT__COT = """
[Query]: Who is Lionel Messi?
[Context]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Output]:
{{
    "Reasoning": "The given context can answer the given question because it provides relevant information about Lionel Messi. The context includes his birth date, nationality and his recogniton in the world of football. This information can answer the given question completely. Hence, selected choice is A. The extracted context can answer the given question completely.",
    "Choice": "A"
}}
"""

CONTEXT_RELEVANCE_FEW_SHOT__CLASSIFY = """
[Query]: Who is Lionel Messi?
[Context]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Output]:
{{
    "Choice": "A"
}}
"""


# Response Completeness
RESPONSE_COMPLETENESS_FEW_SHOT__CLASSIFY = """
[Question]: Who is Lionel Messi?
[Response]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Output]:
{{
    "Choice": "A"
}}
"""

RESPONSE_COMPLETENESS_FEW_SHOT__COT = """
[Question]: Who is Lionel Messi?
[Response]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Output]:
{{
    "Reasoning": "The given response is complete for the given question because it provides relevant information about Lionel Messi. The response includes his birth date, nationality and his recogniton in the world of football. This information directly addresses the question about Lionel Messi.",
    "Choice": "A"
}}
"""


# Response Conciseness
RESPONSE_CONCISENESS_FEW_SHOT__CLASSIFY = """
[Question]: Who is Lionel Messi?
[Response]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Output]:
{{
    "Choice": "C"
}}
"""

RESPONSE_CONCISENESS_FEW_SHOT__COT = """
[Question]: Who is Lionel Messi?
[Response]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Output]:
{{ 
    "Reasoning": "The given response is appropriate for the given question because it provides relevant information about Lionel Messi. The response includes his birth date, nationality and his recogniton in the world of football. This information directly addresses the question about Lionel Messi.",
    "Choice": "C",
}}
"""


# Response Completeness wrt Context
RESPONSE_COMPLETENESS_WRT_CONTEXT_FEW_SHOT__CLASSIFY = """
[Question]: Who is Lionel Messi?
[Context]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Response]: Lionel Messi is an Argentine professional soccer (football) player widely regarded as one of the greatest footballers of all time. He was born on June 24, 1987, in Rosario, Argentina. Messi spent the majority of his career with FC Barcelona, where he became an iconic figure and achieved numerous records and accolades.
[Output]:
{{
    "Choice": "A"
}}
"""

RESPONSE_COMPLETENESS_WRT_CONTEXT_FEW_SHOT__COT = """
[Question]: Who is Lionel Messi?
[Context]: Lionel Andrés Messi (born 24 June 1987), also known as Leo Messi, is an Argentine professional footballer who plays as a forward for and captains both Major League Soccer club Inter Miami and the Argentina national team. Widely regarded as one of the greatest players of all time, Messi has won a record seven Ballon d'Or awards] and a record six European Golden Shoes, and in 2020 he was named to the Ballon d'Or Dream Team. Until leaving the club in 2021, he had spent his entire professional career with Barcelona, where he won a club-record 34 trophies, including ten La Liga titles, seven Copa del Rey titles and the UEFA Champions League four times.
[Response]: Lionel Messi is an Argentine professional soccer (football) player widely regarded as one of the greatest footballers of all time. He was born on June 24, 1987, in Rosario, Argentina. Messi spent the majority of his career with FC Barcelona, where he became an iconic figure and achieved numerous records and accolades.
[Output]:
{{
    "Reasoning": "The given response is complete for the given question because it provides relevant information about Lionel Messi. The response includes his birth date and his recogniton in the world of football. This information directly addresses the question about Lionel Messi.",
    "Choice": "A"
}}
"""


# Response Consistency
RESPONSE_CONSISTENCY_FEW_SHOT__CLASSIFY = """
[Question]: What is postgres?
[Context]: PostgreSQL is a powerful, open source object-relational database system that uses and extends the SQL language combined with many features that safely store and scale the most complicated data workloads. The origins of PostgreSQL date back to 1986 as part of the POSTGRES project at the University of California at Berkeley and has more than 35 years of active development on the core platform.
[Response]: Instead of inserting each row directly into the PostgreSQL database, each record is at first inserted into Redis. New records are inserted using bulk operations for better performance. Note that many duplicate records may be received from mobile clients.
[Output]:
{{
    "Choice": "B"
}}
"""

RESPONSE_CONSISTENCY_FEW_SHOT__COT = """
[Question]: What is postgres?
[Context]: PostgreSQL is a powerful, open source object-relational database system that uses and extends the SQL language combined with many features that safely store and scale the most complicated data workloads. The origins of PostgreSQL date back to 1986 as part of the POSTGRES project at the University of California at Berkeley and has more than 35 years of active development on the core platform.
[Response]: Instead of inserting each row directly into the PostgreSQL database, each record is at first inserted into Redis. New records are inserted using bulk operations for better performance. Note that many duplicate records may be received from mobile clients.
[Output]:
{{
    "Reasoning": "The given response is not appropriate for the given question because it does not contain any key information about PostgreSQL as given in the context. Moreover, there is no information about Redis in the given context."
    "Choice": "B"
}}
"""


# Valid Response
VALID_RESPONSE_FEW_SHOT__CLASSIFY = """
[Question]: Who is the director of the 2003 film which has scenes in it filmed at the Quality Cafe in Los Angeles? 
[Response]: Todd Phillips
[Output]:
{{
    "Choice": "A"
}}
"""

VALID_RESPONSE_FEW_SHOT__COT = """
[Question]: Who is the director of the 2003 film which has scenes in it filmed at the Quality Cafe in Los Angeles?
[Response]: Todd Phillips
[Output]:
{{
    "Reasoning": "The response 'Todd Phillips' provides the name of a person. Therefore, the response does contain information relevant to the question."
    "Choice": "A"
}}
"""