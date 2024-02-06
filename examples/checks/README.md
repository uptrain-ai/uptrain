<h4 align="center">
  <a href="https://uptrain.ai">
   <img alt="Github banner 006 (1)" src="https://github.com/uptrain-ai/uptrain/assets/108270398/96ac1505-7811-4e12-958e-fce9519542a1"/>
  </a>
</h4>

<p align="center">
<a href="https://demo.uptrain.ai/evals_demo/" rel="nofollow"><strong>Try out Evaluations</strong></a>
-
<a href="https://docs.uptrain.ai/getting-started/introduction" rel="nofollow"><strong>Read Docs</strong></a>
-
<a href="https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg" rel="nofollow"><strong>Slack Community</strong></a>
-
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=" rel="nofollow"><strong>Feature Request</strong></a>
</p>

<h4 align="center">
<a href='https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md'>
    <img alt='PRs Welcome' src='https://img.shields.io/badge/PRs-welcome-blue.svg?style=shields'/>
  </a>
  <a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/uptrain-ai/uptrain" />
  </a>
  <a href="https://docs.uptrain.ai/getting-started/quickstart">
    <img src="https://img.shields.io/badge/Quickstart-tutorial-orange" alt="Quickstart" />
  </a>
  <a href="https://uptrain.ai/">
    <img src="https://img.shields.io/badge/UpTrain-Website-red" alt="Website" />
  </a>
</h4>


# Pre-built Evaluations We Offer 📝

#### Evaluate the quality of your responses: 

| Metrics  | Usage | 
|------------|----------|
| [Response Completeness](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/completeness.ipynb)        | Evaluate if the response completely resolves the given user query.      | 
| [Response Relevance](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/relevance.ipynb)      | Evaluate whether the generated response for the given question, is relevant or not.    | 
| [Response Conciseness](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/conciseness.ipynb) | Evaluate how concise the generated response is i.e. the extent of additional irrelevant information in the response.    | 
| [Response Matching ](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/matching.ipynb)  | Compare the LLM-generated text with the gold (ideal) response using the defined score metric.  |
| [Response Consistency](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/consistency.ipynb)   | Evaluate how consistent the response is with the question asked as well as with the context provided.  |


#### Evaluate the quality of retrieved context and response groundedness:

| Metrics  | Usage | 
|------------|----------|
| [Factual Accuracy](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/factual_accuracy.ipynb)       | Evaluate if the facts present in the response can be verified by the retrieved context.    | 
| [Response Completeness wrt Context](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/response_completeness_wrt_context.ipynb)      | Grades how complete the response was for the question specified concerning the information present in the context.| 
| [Context Relevance](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/relevance.ipynb) | Evaluate if the retrieved context contains sufficient information to answer the given question.    | 


#### Evaluations to safeguard system prompts and avoid LLM mis-use:

| Metrics  | Usage | 
|------------|----------|
| [Prompt Injection](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/safeguarding/system_prompt_injection.ipynb)       | Identify prompt leakage attacks| 


#### Evaluate the language quality of the response:

| Metrics  | Usage | 
|------------|----------|
| [Tone Critique](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/language_features/tone_critique.ipynb)       | Assess if the tone of machine-generated responses matches with the desired persona.| 
| [Language Critique](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/language_features/language_critique.ipynb)       | Evaluate LLM generated responses on multiple aspects - fluence, politeness, grammar, and coherence.| 

#### Evaluate the conversation as a whole:

| Metrics  | Usage | 
|------------|----------|
| [Conversation Satisfaction](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/conversation/conversation_satisfaction.ipynb)       | Measures the user’s satisfaction with the conversation with the AI assistant based on completeness and user acceptance.| 

#### Defining custom evaluations and others:

| Metrics  | Usage | 
|------------|----------|
| [Guideline Adherence](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/custom/guideline_adherence.ipynb)       | Grade how well the LLM adheres to a given custom guideline.| 
| [Custom Prompt Evaluation](https://github.com/uptrain-ai/uptrain/blob/main)       | Evaluate by defining your custom grading prompt.| 
| [Cosine Similarity](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/custom/cosine_similarity.ipynb)       | Calculate cosine similarity between embeddings of two texts.| 

If you face any difficulties, need some help with using UpTrain or want to brainstorm on custom evaluations for your use-case, [speak to the maintainers of UpTrain here](https://calendly.com/uptrain-sourabh/30min).

You can also raise a request for a new metrics [here](https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=)