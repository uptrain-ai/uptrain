<h4 align="center">
  <a href="https://uptrain.ai">
    <img width="300" src="https://user-images.githubusercontent.com/108270398/214240695-4f958b76-c993-4ddd-8de6-8668f4d0da84.png" alt="uptrain">
  </a>
</h4>
<h2>
  <p align="center">
    <p align="center">An open-source framework to evaluate and monitor LLM applications</p>
  </p>
</h2>

<p align="center">
<!-- -
<a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/" rel="nofollow"><strong>Try it out</strong></a> -->
<a href="https://demo.uptrain.ai/evals_demo/" rel="nofollow"><strong>Try out Evaluations</strong></a>
-
<!-- <a href="https://docs.uptrain.ai/docs/" rel="nofollow"><strong>Docs</strong></a>
- -->
<a href="https://demo.uptrain.ai/dashboard" rel="nofollow"><strong>Self-serve Console</strong></a>
-
<a href="https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg" rel="nofollow"><strong>Slack Community</strong></a>
-
<!-- <a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=bug&template=bug_report.md&title=" rel="nofollow"><strong>Bug Report</strong></a>
- -->
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=" rel="nofollow"><strong>Feature Request</strong></a>
-
<a href="https://uptrain.ai/#demo" rel="nofollow"><strong>UpTrain in Action</strong></a>
</p>

<h4 align="center">
  <a href="https://demo.uptrain.ai/evals_demo/">
    <img src="https://img.shields.io/badge/Prebuilt-Evaluations-violet.svg?style=shields">
  </a>
  <a href="https://demo.uptrain.ai/dashboard">
    <img src="https://img.shields.io/badge/Self-Serve-indigo.svg?style=shields">
  </a>
  <a href='https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md'>
    <img alt='PRs Welcome' src='https://img.shields.io/badge/PRs-welcome-blue.svg?style=shields'/>
  </a>
  <a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/uptrain-ai/uptrain">
  </a>
  <a href="https://docs.uptrain.ai/docs/">
    <img src="https://img.shields.io/badge/Read-Docs-yellow" alt="Docs" />
  </a>
  <a href="https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg">
    <img src="https://img.shields.io/badge/Slack-Community-orange" alt="Community" />
  </a>
  <a href="https://uptrain.ai/">
    <img src="https://img.shields.io/badge/UpTrain-Website-red" alt="Website" />
  </a>
  <!-- <a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
  </a> -->
</h4>

<!-- https://user-images.githubusercontent.com/43818888/229681912-a1d9733d-0c41-4be1-83cf-408d5271518e.mp4 -->

<!-- **Read this in other languages**: 
<kbd>[<img title="English" alt="English language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/us.svg" width="22">](/README.md)</kbd>
<kbd>[<img title="German" alt="German language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="22">](/i18n/README.de.md)</kbd>
<kbd>[<img title="Chinese" alt="Chinese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/cn.svg" width="22">](/i18n/README.zh-CN.md)</kbd>
<kbd>[<img title="Hindi" alt="Hindi language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="22">](/i18n/README.hi.md)</kbd>
<kbd>[<img title="Spanish" alt="Spanish language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="22">](/i18n/README.es.md)</kbd>
<kbd>[<img title="French" alt="French language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="22">](/i18n/README.fr.md)</kbd>
<kbd>[<img title="Japanese" alt="Japanese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](/i18n/README.ja.md)</kbd>
<kbd>[<img title="Russian" alt="Russian language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/ru.svg" width="22">](/i18n/README.ru.md)</kbd> -->


**[UpTrain](https://uptrain.ai)** is a Python framework that ensures your LLM applications are performing reliably by allowing users to check aspects such as correctness, structural integrity, bias, hallucination, etc. UpTrain can be used to:

## Experimentation

UpTrain framework can be used to experiment across multiple prompts, model providers, chain configurations, etc. and get quantitative scores to compare them. Check out the [experimentation tutorial](https://github.com/uptrain-ai/uptrain/blob/main/examples/prompt_experiments_tutorial.ipynb) to learn more.

<img width="500" src="https://github.com/uptrain-ai/uptrain/assets/108270398/12c93f96-fe2a-45d0-8394-4faf1b64af0c" alt="uptrain experimentation">

## Validation

You can use the UpTrain Validation Manager to define checks, retry logic and validate your LLM responses before showing it to your users. Check out the [tutorial here](https://github.com/uptrain-ai/uptrain/blob/main/examples/validation_tutorial.ipynb).

<img width="500" src="https://github.com/uptrain-ai/uptrain/assets/108270398/09bcdd2b-28cc-4b39-9cf8-78df47a3b297" alt="uptrain validation">

## Monitoring

You can use the UpTrain framework to continuously monitor your model's performance and get real-time insights on how well it is doing on a variety of evaluation metrics. Check out the monitoring tutorial to learn more.

<img width="500" src="https://github.com/uptrain-ai/uptrain/assets/108270398/0ede5648-d1c3-44ff-af65-a1b688792888" alt="uptrain monitoring">

# Get started 🙌

<!-- You can quickly get started with [Google Colab here](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F). -->

To run it on your machine, checkout the [Quickstart tutorial](https://docs.uptrain.ai/getting-started/quickstart):

### Install the package through pip:
```bash
pip install uptrain
```

Note: Uptrain uses commonly used python libraries like openai-evals and sentence-transformers. To make sure, all the functionalities work, use the `uptrain-add` command to install the full version of the package.
```bash
uptrain-add --feature full
```

### How to use UpTrain:

#### Using UpTrain's builtin evaluation sets:
UpTrain provides a variety of checks like response relevance, response completeness, factual accuracy, retrieved-context quality, etc. which can be accessed using UpTrain's API key. To seem them in action, you can see the [Live Evaluation Demo](https://demo.uptrain.ai/evals_demo/)

To learn how more about these builtin checks, check out the [Built-in Checks Documentation](https://docs.uptrain.ai/key-components/check#built-in-checks).

Get your free UpTrain API Key [here](https://uptrain.ai/dashboard).

```python

data = pl.DataFrame({
  "question": ["What is the meaning of life?"],
  "response": ["Who knows 🤔"]
})

check = CheckResponseCompleteness()
output = check.setup(Settings(uptrain_access_token="up-9g....")).run(data)
```


#### Configuring your own evaluation sets:

Say we want to plot a line chart showing whether our model's responses contain any grammatical mistakes or not.

```python

# Step 1: Choose and create the appropriate operator from UpTrain
grammar_score = GrammarScore(
  col_in_text = "model_response",       # input column name (from dataset)
  col_out = "grammar_score"             # desired output column name
)

# Step 2: Create a check with the operators and the required plots as arguments 
grammar_check = Check(
  operators = [grammar_score],
  plots = LineChart(y = "grammar_score")
)
# We can also use prebuilt checks like CheckResponseCompleteness, CheckResponseRelevance, etc.
response_completeness_check = CheckResponseRelevance()


# Step 3: Create a CheckSet with the checks and data source as arguments
checkset = CheckSet(
    checks = [grammar_check, response_relevance_check]
    source = JsonReader(fpath = '...')
)

# Step 4: Set up and run the CheckSet
checkset.setup(Settings(openai_api_key = '...'))
checkset.run(dataset)
```

### Running evaluations on UpTrain's hosted platform:

To learn how to run evaluations on [UpTrain's hosted platform](https://demo.uptrain.ai/dashboard), check out the [UpTrain API Client Tutorial](https://docs.uptrain.ai/tutorials/uptrain-api-client).

<!-- For a quick walkthrough of how UpTrain works, check out our [quickstart tutorial](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial). -->

<h4> </h4>

# Key Features 💡


- **[ChatGPT Grading](https://uptrain-ai.github.io/uptrain/operators/language/OpenAIGradeScore/)** - Utilize LLMs to grade your model outputs.
- **[Custom Grading Checks](https://uptrain-ai.github.io/uptrain/operators/language/ModelGradeScore/)** - Write your custom grading prompts.
- **[Embeddings Similarity Check](https://uptrain-ai.github.io/uptrain/operators/CosineSimilarity/)** - Compute cosine similarity between prompt and response embeddings
- **[Output Validation](https://github.com/uptrain-ai/uptrain/blob/main/examples/validation_tutorial.ipynb)** - Safeguard your users against inappropriate responses
- **[Prompt A/B Testing](https://github.com/uptrain-ai/uptrain/blob/main/examples/prompt_experiments_tutorial.ipynb)** - Experiment across multiple prompts and compare them quantatively.
- **[UMAP Visualization and Clustering](https://uptrain-ai.github.io/uptrain/operators/UMAP/)** - Visualize your embedding space using tools like UMAP and t-SNE.
- **[Hallucination Checks]()** - Use metrics like custom grading, text similarity, and embedding similarity to check for hallucinations.
- **[Toxic Keywords Checks]()** - Make sure your model outputs are not biased or contain toxic keywords.
- **[Feature Slicing]()** - Built-in pivoting functionalities for data dice and slice to pinpoint low-performing cohorts.
- **[Realtime Dashboards]()** - Monitor your model's performance in realtime.


# Integrations

| Eval Frameworks  | LLM Providers | LLM Packages | Serving frameworks | 
| ------------- | ------------- | ------------- | ------------- | 
| OpenAI Evals ✅ | GPT-3.5-turbo ✅ | Langchain 🔜 | HuggingFace 🔜 |
| EleutherAI LM Eval 🔜 | GPT-4 ✅  | Llama Index 🔜 |  Replicate 🔜 |
| BIG-Bench 🔜 | Claude 🔜 | AutoGPT 🔜 |
| | Cohere 🔜 | 


# Why UpTrain 🤔?

Large language models are trained over billions of data points and perform really well over a wide variety of tasks. But one thing these models are not good at is being deterministic. Even with the most well-crafted prompts, the model can misbehave for certain inputs, be it hallucinations, wrong output structure, toxic or biased response, irrelevant response, and error modes can be immense. 

To ensure your LLM applications work reliably and correctly, UpTrain makes it easy for developers to evaluate the responses of their applications on multiple criteria. UpTrain's evaluation framework can be used to:

1) Validate (and correct) the response of the model before showing it to the user
2) Get quantitative measures to experiment across multiple prompts, model providers, etc.
3) Do unit testing to ensure no buggy prompt or code gets pushed into your production
4) Monitor your LLM applications in real-time and understand when they are going wrong in order to fix them before users complain.

We are constantly working to make UpTrain better. Want a new feature or need any integrations? Feel free to [create an issue](https://github.com/uptrain-ai/uptrain/issues) or [contribute](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) directly to the repository.

# License 💻

This repo is published under Apache 2.0 license and we are committed to adding more functionalities to the UpTrain open-source repo. Upon popular demand, we have also rolled out a [no-code self-serve console](https://demo.uptrain.ai/dashboard). For customized onboarding, please book a [demo call here](https://calendly.com/uptrain-sourabh/uptrain-demo).

# Stay Updated ☎️
We are continuously adding tons of features and use cases. Please support us by giving the project a star ⭐!

# Provide feedback (Harsher the better 😉) 

We are building UpTrain in public. Help us improve by giving your feedback **[here](https://docs.google.com/forms/d/e/1FAIpQLSezGUkkC0JoEvx-0gCrRSmGutA-jqyb7kl2lomXv302_C3MnQ/viewform?usp=sf_link)**.

# Contributors 🖥️

We welcome contributions to UpTrain. Please see our [contribution guide](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) for details.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
