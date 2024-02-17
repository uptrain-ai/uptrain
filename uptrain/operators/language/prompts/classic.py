FACT_EVAL_PROMPT_TEMPLATE = """
You are a detail-oriented LLM whose task is to determine if the given facts are supported by the given context. 
Each fact is separated by the following symbol: ", ". Go over each fact sentence one by one, and write down your judgement.
{prompting_instructions}


{scenario_description}


Example Data.
{few_shot_examples}


Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
{output_format}


Task Data.
[Facts]: {facts}
[Context]: {context}
[Output]:
"""


FACT_GENERATE_PROMPT_TEMPLATE = """
You are given a response along with its question. Please breakdown the following response into independent facts. A fact is a sentence that is true and can only be stated from the response. Facts should not depend on each another and must not convey the same information. Limit to 5 facts in the output. 

{scenario_description}


Example Data.
{few_shot_examples}


Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
{output_format}


Task Data.
[Question]: {question}
[Response]: {response}
[Output]: 
"""


CONTEXT_RELEVANCE_PROMPT_TEMPLATE = """
You are a detail-oriented LLM which pays close attention to the details, checks for consistency, and is adept at identifying logical fallacies, incorrect assumptions, or other errors in reasoning.
Your task is to determine if the given context has enough information to answer the given query.
{prompting_instructions}


{scenario_description}


Example Data.
{few_shot_examples}


Compare the semantic similarity of the extracted context with the query. Ignore any differences in style, grammar, or punctuation.
The context may either contain sufficient information to answer the given query completely, or contains relevant but incomplete information to form the answer or doesn't have any relevant information at all. 
Determine which case applies by selecting one of the following options:
(A) The extracted context can answer the given query completely.
(B) The extracted context can give some relevant answer for the given query but can't answer it completely.
(C) The extracted context doesn't contain any information to answer the given query.


Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
{output_format}


Task Data.
[Query]: {question}
[Extracted Context]: {context}
[Output]:
"""


RESPONSE_COMPLETENESS_PROMPT_TEMPLATE = """
You are a detail-oriented LLM which pays close attention to the details, checks for consistency, and is adept at identifying logical fallacies, incorrect assumptions, or other errors in reasoning.
Your task is to determine if the given response is able to answer the given query completely.

{prompting_instructions}

{scenario_description}

Example Data.
{few_shot_examples}


For the provided question-answer pair, please assess if the machine-generated response is relevant and answers the user query adequately. Don't focus on aspects like style, grammar, or punctuation. 
Please form your response by selecting one of the following options. 
(A) The generated answer doesn't answer the given question at all.
(B) The generated answer only partially answers the given question.
(C) The generated answer adequately answers the given question. 


Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
{output_format}


Task Data.
[Question]: {question}
[Response]: {response}
[Output]:
"""