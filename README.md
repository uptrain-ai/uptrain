<h4 align="center">
  <a href="https://uptrain.ai">
    <img width="300" src="https://user-images.githubusercontent.com/108270398/214240695-4f958b76-c993-4ddd-8de6-8668f4d0da84.png" alt="uptrain">
  </a>
</h4>
<h2>
  <p align="center">
    <p align="center">An open-source framework to evaluate, test and monitor LLM applications</p>
  </p>
</h2>

<p align="center">
<a href="https://docs.uptrain.ai/docs/" rel="nofollow"><strong>Docs</strong></a>
<!-- -
<a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/" rel="nofollow"><strong>Try it out</strong></a> -->
-
<a href="https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg" rel="nofollow"><strong>Slack Community</strong></a>
-
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=bug&template=bug_report.md&title=" rel="nofollow"><strong>Bug Report</strong></a>
-
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=" rel="nofollow"><strong>Feature Request</strong></a>
</p>

<h4 align="center">
  <a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/uptrain-ai/uptrain">
  </a>
  <a href='https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md'>
    <img alt='PRs Welcome' src='https://img.shields.io/badge/PRs-welcome-orange.svg?style=shields'/>
  </a>
  <a href="https://docs.uptrain.ai/docs/">
    <img src="https://img.shields.io/badge/Read-Docs-brightgreen" alt="Docs" />
  </a>
  <a href="https://join.slack.com/t/uptraincommunity/shared_invite/zt-1yih3aojn-CEoR_gAh6PDSknhFmuaJeg">
    <img src="https://img.shields.io/badge/Slack-Community-orange" alt="Community" />
  </a>
  <a href="https://uptrain.ai/">
    <img src="https://img.shields.io/badge/UpTrain-Website-yellow" alt="Website" />
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

1) Validate model's response and safeguard your users against hallucinations, bias, incorrect output formats, etc.
2) Experiment across multiple model providers, prompt templates, and quantify model's performance.
3) Monitor your model's performance in production and protect yourself against unwanted drifts


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

# Get started 🙌

<!-- You can quickly get started with [Google Colab here](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F). -->

To run it on your machine, checkout the [Quickstart tutorial](https://docs.uptrain.ai/getting-started/quickstart):

### Install the package through pip:
```bash
pip install uptrain
```

### How to define checks:
Say we want to check whether our model's responses contain any grammatical mistakes or not.

```python
# Define your checkset - list of simple checks, dataset file, 
# and api_keys

checkset = CheckSet(
    checks = Check(
        name = "grammar_score",
        operators = [
            GrammarScore(
                col_in_text = "model_response",
                col_out = "grammar_score"
            ),
        ],
        plots = PlotlyChart.Table(title="Grammar scores"),
    ),
    source = JsonReader(fpath = '...')
)
settings = Settings(openai_api_key = '...')

checkset.setup(settings)
checkset.run()
```

<!-- For a quick walkthrough of how UpTrain works, check out our [quickstart tutorial](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial). -->

<h4> </h4>

# Integrations

| Eval Frameworks  | LLM Providers | LLM Packages | Serving frameworks | 
| ------------- | ------------- | ------------- | ------------- | 
| OpenAI Evals ✅ | GPT-3.5-turbo ✅ | Langchain 🔜 | HuggingFace 🔜 |
| EleutherAI LM Eval 🔜 | GPT-4 ✅  | Llama Index 🔜 |  Replicate 🔜 |
| BIG-Bench 🔜 | Claude 🔜 | AutoGPT 🔜 |
| | Cohere 🔜 | 


# UpTrain in Action

## Experimentation

You can use the UpTrain framework to run and compare LLM responses for different prompts, models, LLM chains, etc. Check out the [experimentation tutorial](https://github.com/uptrain-ai/uptrain/blob/main/examples/prompt_experiments_tutorial.ipynb) to learn more.

## Validation

You can use the UpTrain Validation Manager to define checks, retry logic and validate your LLM responses before showing it to your users. Check out the [tutorial here](https://github.com/uptrain-ai/uptrain/blob/main/examples/validation_tutorial.ipynb).

## Monitoring

You can use the UpTrain framework to continuously monitor your model's performance and get real-time insights on how well it is doing on a variety of evaluation metrics. Check out the monitoring tutorial to learn more.


# Why UpTrain 🤔?

Large language models are trained over billions of data points and perform really well over a wide variety of tasks. But one thing these models are not good at is being deterministic. Even with the most well-crafted prompts, the model can misbehave for certain inputs, be it hallucinations, wrong output structure, toxic or biased response, irrelevant response, and error modes can be immense. 

To ensure your LLM applications work reliably and correctly, UpTrain makes it easy for developers to evaluate the responses of their applications on multiple criteria. UpTrain's evaluation framework can be used to:

1) Validate (and correct) the response of the model before showing it to the user
2) Get quantitative measures to experiment across multiple prompts, model providers, etc.
3) Do unit testing to ensure no buggy prompt or code gets pushed into your production
4) Monitor your LLM applications in real time and understand when they are going wrong in order to fix them before users complain.

We are constantly working to make UpTrain better. Want a new feature or need any integrations? Feel free to [create an issue](https://github.com/uptrain-ai/uptrain/issues) or [contribute](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) directly to the repository.

# License 💻

This repo is published under Apache 2.0 license. We are also working towards adding a hosted offering to make setting off eval runs easier - please fill **[this form](https://docs.google.com/forms/d/e/1FAIpQLSf9h_SXoU0rJP2MUc4NIKOmOCqJ5J0xgephN1xgeoXscSHUSA/viewform?usp=sf_link)** to get a waitlist slot.

# Stay Updated ☎️
We are continuously adding tons of features and use cases. Please support us by giving the project a star ⭐!

# Provide feedback (Harsher the better 😉) 

We are building UpTrain in public. Help us improve by giving your feedback **[here](https://docs.google.com/forms/d/e/1FAIpQLSezGUkkC0JoEvx-0gCrRSmGutA-jqyb7kl2lomXv302_C3MnQ/viewform?usp=sf_link)**.

# Contributors 🖥️

We welcome contributions to UpTrain. Please see our [contribution guide](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) for details.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
