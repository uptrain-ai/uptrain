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

<h4 align="center">
  <img src="https://github.com/uptrain-ai/uptrain/assets/108270398/10d0faeb-c4f8-422f-a01e-49a891fa7ada" alt="Demo of UpTrain's LLM evaluations with scores for hallucinations, retrieved-context quality, response tonality for a customer support chatbot"/>
</h4>

**[UpTrain](https://uptrain.ai)** is an open-source platform to evaluate and improve your LLM applications. We provide grades for 20+ preconfigured checks, perform root cause analysis on failure cases and give insights on how to resolve them.

# Key Features 🔑:

1. **Data-secure**: All the evaluations and analysis run locally on your system, ensuring that the data never leaves your secure environment (except for LLM calls while using model grading checks)

2. **Experiment with different embedding models** like text-embedding-3-large/small, text-embedding-3-ada, baai/bge-large, etc. UpTrain supports HuggingFace models, Replicate endpoints, or custom models hosted on your endpoint.

3. **Cost-effective**: By leveraging model grading and introducing an 'Unclear' grade, we are able to leverage GPT-3.5-turbo-1106 as the default evaluator and get high quality yet cost effective scores.

4. You can **perform root cause analysis** on cases with either negative user feedback or low evaluation scores to understand which part of your LLM pipeline is giving suboptimal results. Check out the supported RCA templates.

5. **Configure your own evaluation LLM**: We allow you to use any of OpenAI, Anthropic, Mistral, Azure's Openai endpoints or open-source LLMs hosted on Anyscale to be used as evaluator.

6. UpTrain provides tons of ways to **customize evaluations**. You can customize evaluation method (chain of thought vs classify), few shot examples, add scenario description, as well as create custom evaluators.

7. Support for **50+ operators** such as BLEU, ROUGE, Embeddings Similarity, Exact match, etc.


### Coming Soon:

1. Experiment Dashboards
2. Collaborate with your team
3. Embedding visualization via UMAP and Clustering
4. Pattern recognition among failure cases
5. Prompt improvement suggestions

# Pre-built Evaluations We Offer 📝
<img width="1088" alt="quality of your responses" src="https://github.com/uptrain-ai/uptrain/assets/108270398/2cbff61d-a571-404e-bc7c-a8cd712dc854">

1. [Response Completeness](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/completeness.ipynb): Grades how if the response completely resolves the given user query.
2. [Response Relevance](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/relevance.ipynb): Grades how relevant the generated response is for the given question.
3. [Response Conciseness](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/conciseness.ipynb): Grades how concise the generated response is i.e. the extent of additional irrelevant information in the response.
4. [Response Matching](): Operator to compare the llm-generated text with the gold (ideal) response using the defined score metric.
5. [Response Consistency](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/response_quality/consistency.ipynb): Grades how consistent the response is with the question asked as well as with the context provided.

<img width="1088" alt="quality of retrieved context and response groundedness" src="https://github.com/uptrain-ai/uptrain/assets/108270398/0866a939-5bde-4723-b7bf-e72b9b154041">

1. [Factual Accuracy](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/factual_accuracy.ipynb): Checks if the facts present in the response can be verified by the retrieved context
2. [Response Completeness wrt Context](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/response_completeness_wrt_context.ipynb): Grades how complete the response was for the question specified with respect to the information present in the context
3. [Context Relevance](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/context_awareness/relevance.ipynb): Evaluates if the retrieved context contain sufficient information to answer the given question

<img width="1088" alt="safeguard system prompts and avoid LLM mis-use" src="https://github.com/uptrain-ai/uptrain/assets/108270398/a66868ca-e6d5-40ba-b433-3001324862fd">

1. [Prompt Injection](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/safeguarding/system_prompt_injection.ipynb): Identifys prompt leakage attacks
2. [Jailbreak Detection](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/safeguarding/jailbreak_detection.ipynb): Measures if the user prompts to generate a response over potentially harmful or illegal behaviour.

<img width="1088" alt="language quality of the response" src="https://github.com/uptrain-ai/uptrain/assets/108270398/2a2748e7-c137-4d70-8845-731878d5d39a">

1. [Tone Critique](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/language_features/tone_critique.ipynb): Assesses if the tone of machine-generated responses matches with the desired persona.
2. [Language Critique](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/language_features/language_critique.ipynb): Scores machine generated responses on multiple aspects - fluence, politeness, grammar, and coherence.

<img width="1088" alt="custom evaluations and others" src="https://github.com/uptrain-ai/uptrain/assets/108270398/3d843449-6624-4433-8f6e-acfebda92eb3">

1. [Guideline Adherence](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/custom/guideline_adherence.ipynb): Grades how well the LLM adheres to a given custom guideline.
2. [Custom Prompt Evaluation](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/custom/writing_custom_evals.ipynb): Evaluate by defining your custom grading prompt.
3. [Cosine Similarity](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/custom/cosine_similarity.ipynb): Calculate cosine similarity between embeddings of two texts.

<img width="1088" alt="conversation as a whole" src="https://github.com/uptrain-ai/uptrain/assets/108270398/a4c5d746-2867-4299-91e0-4efdfa76aedf">

1. [Conversation Satisfaction](https://github.com/uptrain-ai/uptrain/blob/main/examples/checks/conversation/conversation_satisfaction.ipynb): Measures the user’s satisfaction with the conversation with the LLM/AI assistant based on completeness and user’s acceptance.


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

<h4> </h4>

# Integrations 🤝

| Eval Frameworks  | LLM Providers | LLM Packages | Serving frameworks | LLM Observability | Vector DBs |
| ------------- | ------------- | ------------- | ------------- | ------------- |  ------------- |
| OpenAI Evals ✅ | GPT-3.5-turbo ✅ | Langchain 🔜 | HuggingFace ✅ | Langfuse 🔜 | Qdrant ✅ |
| EleutherAI LM Eval 🔜 | GPT-4 ✅  | Llama Index ✅ |  Replicate ✅ | Helicone 🔜 | Pinecone 🔜 |
| BIG-Bench 🔜 | Claude ✅ | AutoGPT 🔜 |  AnyScale ✅ | | Chroma ✅ |
| | Cohere ✅ | | Together ai 🔜 |
| | Llama2 ✅ | | Ollama 🔜 |
| | Mistral ✅ |

# Resources 💡

1. [How to evaluate your LLM application](https://uptrain.ai/blog/how-to-evaluate-your-llm-applications)
2. [How to detect jailbreaks](https://blog.uptrain.ai/llm-jailbreak/)
3. [Dealing with hallucinations](https://blog.uptrain.ai/dealing-with-hallucinations-in-llms-a-deep-dive/)


# Why we are building UpTrain 🤔

Having worked with ML and NLP models for the last 8 years, we were continuosly frustated with numerous hidden failures in our models which led to us building UpTrain. UpTrain was initially started as an ML observability tool with checks to identify regression in accuracy. 

However we soon released that LLM developers face an even bigger problem -- there is no good way to measure accuracy of their LLM applications, let alone identify regression.

We also saw release of [OpenAI evals](https://github.com/openai/evals), where they proposed the use of LLMs to grade the model responses. Further more we gained more confidence to approach this after reading [how Anthropic leverages RLAIF](https://arxiv.org/pdf/2212.08073.pdf) and dived right into the LLM evaluations research (We are soon releasing a repository of awesome Eval research). 

So, come today, UpTrain is our attempt to bring order to LLM chaos and contribute back to the community. While a majority of developers still go with the vibes and productionise prompt changes by reviewing a couple of cases, we have heard enough regression stories to believe "evaluations and improvement" will be a key part of LLM ecosystem as the space matures.

1. Robust evaluations allows you to systematically experiment with different configurations and prevent any regressions by helping objectively select the best choice.

2. It helps you understand where your systems are going wrong, find root cause and fix them - long before your end users complain and potentially churn out.

3. Evaluations like prompt injection, jailbreak are essential to maintain safety and security of your LLM applications.

4. Evaluations help you to provide transparency and build trust with your end-users - especially relevant if you are selling to enterprises.

# Why open-source? 

1. We understand there is **no one-size-fits-all solution** when it come to evaluations. We are increasingly seeing the desire from developers to modify the evaluation prompt or set of choices or the few shot examples, etc. We believe the best developer experience lies in open-source, instead of exposing 20 different variables.

2. **Foster innovation**: The field of LLM evaluations and using LLM-as-a-judge is still pretty nascent. We see a lot of exciting research happening, almost on a daily basis and being open-source provides the right platform to us and our community to implement those techniques and innovate faster.


# How you can help 🙏

We are constantly working to make UpTrain better. Few ways you can help:

1. Your application needs a custom eval - let us know and we will add it to the repo
2. Want us to integrate with your existing tools - let us know and we will do it
3. Notice an issue with UpTrain - post in on our Slack channel and we will resolve it asap
4. Star us ⭐ to track our progress
5. Like something which we have built - give us a shoutout on Twitter

Feel free to [create an issue](https://github.com/uptrain-ai/uptrain/issues) or [contribute](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) directly to the repository.

# License 💻

This repo is published under Apache 2.0 license and we are committed to adding more functionalities to the UpTrain open-source repo. We also have a managed version if you just want a more hands-off experience. Please book a [demo call here](https://calendly.com/uptrain-sourabh/30min).

# Provide feedback (Harsher the better 😉) 

We are building UpTrain in public. Help us improve by giving your feedback **[here](https://docs.google.com/forms/d/e/1FAIpQLSezGUkkC0JoEvx-0gCrRSmGutA-jqyb7kl2lomXv302_C3MnQ/viewform?usp=sf_link)**.

# Contributors 🖥️

We welcome contributions to UpTrain. Please see our [contribution guide](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) for details.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
