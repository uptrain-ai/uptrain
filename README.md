<h4 align="center">
  <a href="https://www.uptrain.ai">
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

<h4 align="center">
  <img src="https://github.com/uptrain-ai/uptrain/assets/108270398/10d0faeb-c4f8-422f-a01e-49a891fa7ada" alt="Demo of UpTrain's LLM evaluations with scores for hallucinations, retrieved-context quality, response tonality for a customer support chatbot"/>
</h4>

**[UpTrain](https://www.uptrain.ai)** is an open-source unified platform to evaluate and improve Generative AI applications. We provide grades for 20+ preconfigured checks (covering language, code, embedding use-cases), perform root cause analysis on failure cases and give insights on how to resolve them.    

<br />

# Key Features 🔑

<img width="1088" alt="Data Security" src="https://github.com/uptrain-ai/uptrain/assets/43818888/7b737bfc-b061-4f87-b51e-5bad67879332">

All the evaluations and analysis run locally on your system, ensuring that the data never leaves your secure environment (except for LLM calls while using model grading checks)

<img width="1088" alt="Experimentation" src="https://github.com/uptrain-ai/uptrain/assets/43818888/fd9c5c7f-3951-4d69-9b77-4fece6ff0830">

**Experiment with different embedding models** like text-embedding-3-large/small, text-embedding-3-ada, baai/bge-large, etc. UpTrain supports HuggingFace models, Replicate endpoints, or custom models hosted on your endpoint.

<img width="1088" alt="Cost Effective" src="https://github.com/uptrain-ai/uptrain/assets/43818888/8b9bc91b-389a-4664-88f6-11b9c91e1e0f">

By leveraging model grading and introducing an 'Unclear' grade, we are able to leverage GPT-3.5-turbo-1106 as the default evaluator and get high quality yet cost effective scores.

<img width="1088" alt="Root Cause Analysis" src="https://github.com/uptrain-ai/uptrain/assets/43818888/32df049c-c0a4-4377-a807-f74e2efa57b5">

You can **perform root cause analysis** on cases with either negative user feedback or low evaluation scores to understand which part of your LLM pipeline is giving suboptimal results. Check out the supported RCA templates.

<img width="1088" alt="Configure your own evaluation LLM" src="https://github.com/uptrain-ai/uptrain/assets/43818888/b87c75b1-b86d-4770-8d37-e8428d5f17c2">

We allow you to use any of OpenAI, Anthropic, Mistral, Azure's Openai endpoints or open-source LLMs hosted on Anyscale to be used as evaluator.

<img width="1088" alt="Customize Evaluations" src="https://github.com/uptrain-ai/uptrain/assets/43818888/167488ec-9feb-48a7-9659-7bb9478584f9">

UpTrain provides tons of ways to **customize evaluations**. You can customize evaluation method (chain of thought vs classify), few shot examples, add scenario description, as well as create custom evaluators.

<img width="1088" alt="40+ Operators Supported" src="https://github.com/uptrain-ai/uptrain/assets/43818888/55d99fb9-ce0a-409f-b898-acb550fa0804">

Support for **40+ operators** such as BLEU, ROUGE, Embeddings Similarity, Exact match, etc.


### Coming Soon:

1. Experiment Dashboards
2. Collaborate with your team
3. Embedding visualization via UMAP and Clustering
4. Pattern recognition among failure cases
5. Prompt improvement suggestions

<br />

# Pre-built Evaluations We Offer 📝
<img width="1088" alt="quality of your responses" src="https://github.com/uptrain-ai/uptrain/assets/43818888/654b2289-2799-4310-84be-fcdd071f3e2e">

| Eval | Description |
| ---- | ----------- |
|[Reponse Completeness](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-completeness) | Grades whether the response has answered all the aspects of the question specified. |
|[Reponse Conciseness](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-conciseness) | Grades how concise the generated response is or if it has any additional irrelevant information for the question asked. |
|[Reponse Relevance](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-relevance)| Grades how relevant the generated context was to the question specified.|
|[Reponse Validity](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-validity)| Grades if the response generated is valid or not. A response is considered to be valid if it contains any information.|
|[Reponse Consistency](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-consistency)| Grades how consistent the response is with the question asked as well as with the context provided.|

<img width="1088" alt="quality of retrieved context and response groundedness" src="https://github.com/uptrain-ai/uptrain/assets/43818888/a7e384a3-c857-4a71-a938-7a2a70f8db1e">

| Eval | Description |
| ---- | ----------- |
|[Context Relevance](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-relevance) | Grades how relevant the context was to the question specified. |
|[Context Utilization](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-utilization) | Grades how complete the generated response was for the question specified given the information provided in the context. |
|[Factual Accuracy](https://docs.uptrain.ai/predefined-evaluations/context-awareness/factual-accuracy)| Grades whether the response generated is factually correct and grounded by the provided context.|
|[Context Conciseness](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-conciseness)| Evaluates the concise context cited from an original context for irrelevant information.
|[Context Reranking](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-reranking)| Evaluates how efficient the reranked context is compared to the original context.|

<img width="1088" alt="language quality of the response" src="https://github.com/uptrain-ai/uptrain/assets/43818888/776cbc6d-bb4c-4ed1-a892-7a1df38d12d5">

| Eval | Description |
| ---- | ----------- |
|[Language Features](https://docs.uptrain.ai/predefined-evaluations/language-quality/fluency-and-coherence) | Grades whether the response has answered all the aspects of the question specified. |
|[Tonality](https://docs.uptrain.ai/predefined-evaluations/code-evals/code-hallucination) | Grades whether the generated response matches the required persona's tone  |

<img width="1088" alt="language quality of the response" src="https://github.com/uptrain-ai/uptrain/assets/36454110/2fba9f0b-71b3-4d90-90f8-16ef38cef3ab">

| Eval | Description |
| ---- | ----------- |
|[Code Hallucination](https://docs.uptrain.ai/predefined-evaluations/code-evals/code-hallucination) | Grades whether the code present in the generated response is grounded by the context. |

<img width="1088" alt="conversation as a whole" src="https://github.com/uptrain-ai/uptrain/assets/43818888/194f8dd7-26ca-48eb-bdff-028212db9e25">

| Eval | Description |
| ---- | ----------- |
|[User Satisfaction](https://docs.uptrain.ai/predefined-evaluations/conversation-evals/user-satisfaction) | Grade the conversations between the user and the LLM/AI assistant. |

<img width="1088" alt="custom evaluations and others" src="https://github.com/uptrain-ai/uptrain/assets/43818888/0bbc2d82-0f96-49ab-969c-4eec29fef988">

 Eval | Description |
| ---- | ----------- |
|[Custom Guideline](https://docs.uptrain.ai/predefined-evaluations/custom-evals/custom-guideline) | Grades how well the LLM adheres to a provided guideline when giving a response. |
|[Custom Prompts](https://docs.uptrain.ai/predefined-evaluations/custom-evals/custom-prompt-eval) | Allows you to create your own set of evaluations. |

<img width="1088" alt="compare responses with ground truth" src="https://github.com/uptrain-ai/uptrain/assets/36454110/e3ee22f4-9984-47a5-a7d2-9d8688a090fb">

| Eval | Description |
| ---- | ----------- |
|[Response Matching](https://docs.uptrain.ai/predefined-evaluations/ground-truth-comparison/response-matching) | Grades whether the generated response is leaking any system prompt. |

<img width="1088" alt="safeguard system prompts and avoid LLM mis-use" src="https://github.com/uptrain-ai/uptrain/assets/43818888/4fcdb1e8-f356-443b-88f0-94146e08829e">

| Eval | Description |
| ---- | ----------- |
|[Prompt Injection](https://docs.uptrain.ai/predefined-evaluations/safeguarding/prompt-injection) | Grades whether the generated response is leaking any system prompt. |
|[Jailbreak Detection](https://docs.uptrain.ai/predefined-evaluations/safeguarding/jailbreak) | Grades whether the user's prompt is an attempt to jailbreak (i.e. generate illegal or harmful responses). |

<br />

# Get started 🙌

### Install the package through pip:
```bash
pip install uptrain
```

### How to use UpTrain:

You can evaluate your responses via the open-source version by providing your OpenAI API key to run evaluations.

```python
from uptrain import EvalLLM, Evals
import json

OPENAI_API_KEY = "sk-***************"

data = [{
    'question': 'Which is the most popular global sport?',
    'context': "The popularity of sports can be measured in various ways, including TV viewership, social media presence, number of participants, and economic impact. Football is undoubtedly the world's most popular sport with major events like the FIFA World Cup and sports personalities like Ronaldo and Messi, drawing a followership of more than 4 billion people. Cricket is particularly popular in countries like India, Pakistan, Australia, and England. The ICC Cricket World Cup and Indian Premier League (IPL) have substantial viewership. The NBA has made basketball popular worldwide, especially in countries like the USA, Canada, China, and the Philippines. Major tennis tournaments like Wimbledon, the US Open, French Open, and Australian Open have large global audiences. Players like Roger Federer, Serena Williams, and Rafael Nadal have boosted the sport's popularity. Field Hockey is very popular in countries like India, Netherlands, and Australia. It has a considerable following in many parts of the world.",
    'response': 'Football is the most popular sport with around 4 billion followers worldwide'
}]

eval_llm = EvalLLM(openai_api_key=OPENAI_API_KEY)

results = eval_llm.evaluate(
    data=data,
    checks=[Evals.CONTEXT_RELEVANCE, Evals.FACTUAL_ACCURACY, Evals.RESPONSE_COMPLETENESS]
)

print(json.dumps(results, indent=3))
```
If you have any questions, please join our [Slack community](https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg)

Speak directly with the maintainers of UpTrain by [booking a call here](https://calendly.com/uptrain-sourabh/30min).

<br />

# Integrations 🤝

| Eval Frameworks  | LLM Providers | LLM Packages | Serving frameworks | LLM Observability | Vector DBs |
| ------------- | ------------- | ------------- | ------------- | ------------- |  ------------- |
| OpenAI Evals ✅ | GPT-3.5-turbo ✅ | Langchain 🔜 | HuggingFace ✅ | Langfuse 🔜 | Qdrant ✅ |
| EleutherAI LM Eval 🔜 | GPT-4 ✅  | Llama Index ✅ |  Replicate ✅ | Helicone 🔜 | Pinecone 🔜 |
| BIG-Bench 🔜 | Claude ✅ | AutoGPT 🔜 |  AnyScale ✅ | | Chroma ✅ |
| | Cohere ✅ | | Together ai 🔜 |
| | Llama2 ✅ | | Ollama 🔜 |
| | Mistral ✅ |

<br />

# Resources 💡

1. [How to evaluate your LLM application](https://blog.uptrain.ai/how-to-evaluate-your-llm-applications)
1. [How to detect jailbreaks](https://blog.uptrain.ai/llm-jailbreak/)
1. [Dealing with hallucinations](https://blog.uptrain.ai/dealing-with-hallucinations-in-llms-a-deep-dive/)

<br />

# Why we are building UpTrain 🤔

Having worked with ML and NLP models for the last 8 years, we were continuosly frustated with numerous hidden failures in our models which led to us building UpTrain. UpTrain was initially started as an ML observability tool with checks to identify regression in accuracy. 

However we soon released that LLM developers face an even bigger problem -- there is no good way to measure accuracy of their LLM applications, let alone identify regression.

We also saw release of [OpenAI evals](https://github.com/openai/evals), where they proposed the use of LLMs to grade the model responses. Furthermore, we gained confidence to approach this after reading [how Anthropic leverages RLAIF](https://arxiv.org/pdf/2212.08073.pdf) and dived right into the LLM evaluations research (We are soon releasing a repository of awesome evaluations research). 

So, come today, UpTrain is our attempt to bring order to LLM chaos and contribute back to the community. While a majority of developers still rely on intuition and productionise prompt changes by reviewing a couple of cases, we have heard enough regression stories to believe "evaluations and improvement" will be a key part of LLM ecosystem as the space matures.

1. Robust evaluations allows you to systematically experiment with different configurations and prevent any regressions by helping objectively select the best choice.

1. It helps you understand where your systems are going wrong, find the root cause(s) and fix them - long before your end users complain and potentially churn out.

1. Evaluations like prompt injection and jailbreak detection are essential to maintain safety and security of your LLM applications.

1. Evaluations help you provide transparency and build trust with your end-users - especially relevant if you are selling to enterprises.

<br />

# Why open-source? 

1. We understand that there is **no one-size-fits-all solution** when it come to evaluations. We are increasingly seeing the desire from developers to modify the evaluation prompt or set of choices or the few shot examples, etc. We believe the best developer experience lies in open-source, instead of exposing 20 different parameters.

1. **Foster innovation**: The field of LLM evaluations and using LLM-as-a-judge is still pretty nascent. We see a lot of exciting research happening, almost on a daily basis and being open-source provides the right platform to us and our community to implement those techniques and innovate faster.

<br />

## How You Can Help 🙏

We are continuously striving to enhance UpTrain, and there are several ways you can contribute:

1. **Notice any issues or areas for improvement:** If you spot anything wrong or have ideas for enhancements, please [create an issue](https://github.com/uptrain-ai/uptrain/issues) on our GitHub repository.

1. **Contribute directly:** If you see an issue you can fix or have code improvements to suggest, feel free to contribute directly to the [repository](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md).

1. **Request custom evaluations:** If your application requires a tailored evaluation, [let us know]((https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg)), and we'll add it to the repository.

1. **Integrate with your tools:** Need integration with your existing tools? [Reach out]((https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg)), and we'll work on it.

1. **Assistance with evaluations:** If you need assistance with evaluations, post your query on our [Slack channel](https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg), and we'll resolve it promptly.

1. **Show your support:** Show your support by starring us ⭐ on GitHub to track our progress.

1. **Spread the word:** If you like what we've built, give us a shoutout on Twitter!

Your contributions and support are greatly appreciated! Thank you for being a part of UpTrain's journey.

<br />

# License 💻

This repo is published under Apache 2.0 license and we are committed to adding more functionalities to the UpTrain open-source repo. We also have a managed version if you just want a more hands-off experience. Please book a [demo call here](https://calendly.com/uptrain-sourabh/30min).

<br />

# Provide feedback (Harsher the better 😉) 

We are building UpTrain in public. Help us improve by giving your feedback **[here](https://docs.google.com/forms/d/e/1FAIpQLSezGUkkC0JoEvx-0gCrRSmGutA-jqyb7kl2lomXv302_C3MnQ/viewform?usp=sf_link)**.

<br />

# Contributors 🖥️

We welcome contributions to UpTrain. Please see our [contribution guide](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) for details.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
