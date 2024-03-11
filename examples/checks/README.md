<h4 align="center">
  <a href="https://uptrain.ai">
   <img alt="Logo of UpTrain - an open-source platform to evaluate and improve LLM applications" src="https://github.com/uptrain-ai/uptrain/assets/108270398/b6a4905f-63fd-47ab-a894-1026a6669c86"/>
  </a>
</h4>


<p align="center">
<a href="https://demo.uptrain.ai/evals_demo/" rel="nofollow"><strong>Try out Evaluations</strong></a>
-
<a href="https://docs.uptrain.ai/getting-started/introduction" rel="nofollow"><strong>Read Docs</strong></a>
-
<a href="https://docs.uptrain.ai/getting-started/quickstart" rel="nofollow"><strong>Quickstart Tutorials</strong></a>
-
<a href="https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg" rel="nofollow"><strong>Slack Community</strong></a>
-
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=" rel="nofollow"><strong>Feature Request</strong></a>
</p>


**[UpTrain](https://uptrain.ai)** is an open-source unified platform to evaluate and improve Generative AI applications. We provide grades for 20+ preconfigured checks (covering language, code, embedding use-cases), perform root cause analysis on failure cases and give insights on how to resolve them.    

<br />

# Pre-built Evaluations We Offer 📝
<img width="1088" alt="quality of your responses" src="https://github.com/uptrain-ai/uptrain/assets/43818888/654b2289-2799-4310-84be-fcdd071f3e2e">

| Eval | Description |
| ---- | ----------- |
|[Response Completeness](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-completeness) | Grades whether the response has answered all the aspects of the question specified. |
|[Response Conciseness](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-conciseness) | Grades how concise the generated response is or if it has any additional irrelevant information for the question asked. |
|[Response Relevance](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-relevance)| Grades how relevant the generated context was to the question specified.|
|[Response Validity](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-validity)| Grades if the response generated is valid or not. A response is considered to be valid if it contains any information.|
|[Response Consistency](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-consistency)| Grades how consistent the response is with the question asked as well as with the context provided.|

<img width="1088" alt="quality of retrieved context and response groundedness" src="https://github.com/uptrain-ai/uptrain/assets/43818888/a7e384a3-c857-4a71-a938-7a2a70f8db1e">

| Eval | Description |
| ---- | ----------- |
|[Context Relevance](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-relevance) | Grades how relevant the context was to the question specified. |
|[Context Utilization](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-utilization) | Grades how complete the generated response was for the question specified, given the information provided in the context. |
|[Factual Accuracy](https://docs.uptrain.ai/predefined-evaluations/context-awareness/factual-accuracy)| Grades whether the response generated is factually correct and grounded by the provided context.|
|[Context Conciseness](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-conciseness)| Evaluates the concise context cited from an original context for irrelevant information.
|[Context Reranking](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-reranking)| Evaluates how efficient the reranked context is compared to the original context.|

<img width="1088" alt="language quality of the response" src="https://github.com/uptrain-ai/uptrain/assets/43818888/776cbc6d-bb4c-4ed1-a892-7a1df38d12d5">

| Eval | Description |
| ---- | ----------- |
|[Language Features](https://docs.uptrain.ai/predefined-evaluations/language-quality/fluency-and-coherence) | Grades the quality and effectiveness of language in a response, focusing on factors such as clarity, coherence, conciseness, and overall communication. |
|[Tonality](https://docs.uptrain.ai/predefined-evaluations/code-evals/code-hallucination) | Grades whether the generated response matches the required persona's tone  |

<img width="1088" alt="language quality of the response" src="https://github.com/uptrain-ai/uptrain/assets/36454110/2fba9f0b-71b3-4d90-90f8-16ef38cef3ab">

| Eval | Description |
| ---- | ----------- |
|[Code Hallucination](https://docs.uptrain.ai/predefined-evaluations/code-evals/code-hallucination) | Grades whether the code present in the generated response is grounded by the context. |

<img width="1088" alt="conversation as a whole" src="https://github.com/uptrain-ai/uptrain/assets/43818888/194f8dd7-26ca-48eb-bdff-028212db9e25">

| Eval | Description |
| ---- | ----------- |
|[User Satisfaction](https://docs.uptrain.ai/predefined-evaluations/conversation-evals/user-satisfaction) | Grades how well the user's concerns are addressed and assesses their satisfaction based on provided conversation. |

<img width="1088" alt="custom evaluations and others" src="https://github.com/uptrain-ai/uptrain/assets/43818888/0bbc2d82-0f96-49ab-969c-4eec29fef988">

 Eval | Description |
| ---- | ----------- |
|[Custom Guideline](https://docs.uptrain.ai/predefined-evaluations/custom-evals/custom-guideline) | Allows you to specify a guideline and grades how well the LLM adheres to the provided guideline when giving a response. |
|[Custom Prompts](https://docs.uptrain.ai/predefined-evaluations/custom-evals/custom-prompt-eval) | Allows you to create your own set of evaluations. |

<img width="1088" alt="compare responses with ground truth" src="https://github.com/uptrain-ai/uptrain/assets/36454110/e3ee22f4-9984-47a5-a7d2-9d8688a090fb">

| Eval | Description |
| ---- | ----------- |
|[Response Matching](https://docs.uptrain.ai/predefined-evaluations/ground-truth-comparison/response-matching) | Compares and grades how well the response generated by the LLM aligns with the provided ground truth. |

<img width="1088" alt="safeguard system prompts and avoid LLM mis-use" src="https://github.com/uptrain-ai/uptrain/assets/43818888/4fcdb1e8-f356-443b-88f0-94146e08829e">

| Eval | Description |
| ---- | ----------- |
|[Prompt Injection](https://docs.uptrain.ai/predefined-evaluations/safeguarding/prompt-injection) | Grades whether the user's prompt is an attempt to make the LLM reveal its system prompts. |
|[Jailbreak Detection](https://docs.uptrain.ai/predefined-evaluations/safeguarding/jailbreak) | Grades whether the user's prompt is an attempt to jailbreak (i.e. generate illegal or harmful responses). |

<img width="1088" alt="evaluate the clarity of user queries" src="https://github.com/uptrain-ai/uptrain/assets/36454110/50ed622f-0b92-468c-af48-2391ff6ab8e0">

| Eval | Description |
| ---- | ----------- |
|[Sub-Query Completeness](https://docs.uptrain.ai/predefined-evaluations/query-quality/sub-query-completeness) | Evaluate whether all of the sub-questions generated from a user's query, taken together, cover all aspects of the user's query or not |
