# Pre-built Evaluations We Offer 📝

#### Evaluate the quality of your responses:
1. [Response Completeness](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/completeness.ipynb): Grades how if the response completely resolves the given user query.
2. [Response Relevance](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/relevance.ipynb): Grades how relevant the generated response is for the given question.
3. [Response Conciseness](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/conciseness.ipynb): Grades how concise the generated response is i.e. the extent of additional irrelevant information in the response.
4. [Response Matching](): Operator to compare the llm-generated text with the gold (ideal) response using the defined score metric.
5. [Response Consistency](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/consistency.ipynb): Grades how consistent the response is with the question asked as well as with the context provided.

#### Evaluate the quality of retrieved context and response groundedness:
1. [Factual Accuracy](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/factual_accuracy.ipynb): Checks if the facts present in the response can be verified by the retrieved context
2. [Response Completeness wrt Context](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/response_completeness_wrt_context.ipynb): Grades how complete the response was for the question specified with respect to the information present in the context
3. [Context Relevance](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/relevance.ipynb): Evaluates if the retrieved context contain sufficient information to answer the given question

#### Evaluations to safeguard system prompts and avoid LLM mis-use:
1. [Prompt Injection](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/safeguarding/system_prompt_injection.ipynb): Identifys prompt leakage attacks


#### Evaluate the language quality of the response:
1. [Tone Critique](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/language_features/tone_critique.ipynb): Assesses if the tone of machine-generated responses matches with the desired persona.
2. [Language Critique](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/language_features/language_critique.ipynb): Scores machine generated responses on multiple aspects - fluence, politeness, grammar, and coherence.

#### Defining custom evaluations and others:
1. [Guideline Adherence](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/custom/guideline_adherence.ipynb): Grades how well the LLM adheres to a given custom guideline.
2. [Custom Prompt Evaluation](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/custom/writing_custom_evals.ipynb): Evaluate by defining your custom grading prompt.
3. [Cosine Similarity](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/custom/cosine_similarity.ipynb): Calculate cosine similarity between embeddings of two texts.

#### Evaluate the conversation as a whole:
1. [Conversation Satisfaction](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/conversation/conversation_satisfaction.ipynb): Measures the user’s satisfaction with the conversation with the LLM/AI assistant based on completeness and user’s acceptance.