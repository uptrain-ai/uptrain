<h4 align="center">
  <a href="https://uptrain.ai">
    <img width="300" src="https://user-images.githubusercontent.com/108270398/214240695-4f958b76-c993-4ddd-8de6-8668f4d0da84.png" alt="uptrain">
  </a>
</h4>
<h2>
  <p align="center">
    <p align="center">An open-source framework to observe ML applications, built for engineers</p>
  </p>
</h2>

<p align="center">
<a href="https://docs.uptrain.ai/docs/" rel="nofollow"><strong>Docs</strong></a>
-
<a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/" rel="nofollow"><strong>Try it out</strong></a>
-
<a href="https://discord.com/invite/gVvZhhrQaQ/" rel="nofollow"><strong>Discord Community</strong></a>
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
  <a href="https://discord.com/invite/gVvZhhrQaQ">
    <img src="https://img.shields.io/badge/Discord-Community-orange" alt="Community" />
  </a>
  <a href="https://uptrain.ai/">
    <img src="https://img.shields.io/badge/UpTrain-Website-yellow" alt="Website" />
  </a>
  <a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
  </a>
</h4>

https://user-images.githubusercontent.com/43818888/229681912-a1d9733d-0c41-4be1-83cf-408d5271518e.mp4

**Read this in other languages**: 
<kbd>[<img title="English" alt="English language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/us.svg" width="22">](/README.md)</kbd>
<kbd>[<img title="German" alt="German language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="22">](/i18n/README.de.md)</kbd>
<kbd>[<img title="Chinese" alt="Chinese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/cn.svg" width="22">](/i18n/README.zh-CN.md)</kbd>
<kbd>[<img title="Hindi" alt="Hindi language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="22">](/i18n/README.hi.md)</kbd>
<kbd>[<img title="Spanish" alt="Spanish language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="22">](/i18n/README.es.md)</kbd>
<kbd>[<img title="French" alt="French language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="22">](/i18n/README.fr.md)</kbd>
<kbd>[<img title="Japanese" alt="Japanese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](/i18n/README.ja.md)</kbd>
<kbd>[<img title="Russian" alt="Russian language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/ru.svg" width="22">](/i18n/README.ru.md)</kbd>


**[UpTrain](https://uptrain.ai)** is a Python framework that helps users to check the performance of their LLM applications on aspects such as correctness, structural integrity, bias, hallucination, etc. UpTrain can be used to:

1) Validate model's response and safeguard your users against hallucinations, bias, incorrect output formats, etc.
2) Experiment across multiple model providers, prompt templates, and quantify model's performance for  
3) Monitor your model's performance in production and protect yourself against unwanted drifts


# Integrations:

| Eval Frameworks  | LLM Providers | LLM Packages | Serving frameworks | 
| ------------- | ------------- | ------------- | ------------- | 
| OpenAI Evals  | GPT-3.5-turbo (ChatGPT) | Langchain | HuggingFace |
| Content Cell  | GPT-4  | Llama Index |  Replicate |


# **[Key Features](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)** 💡


- **[Output Validation]()** - Safeguard against 
- **[Embeddings Similarity Check](https://docs.uptrain.ai/docs/uptrain-monitors/data-drift)** - Compute cosine similarity between prompt and response embeddings
- **[UMAP Visualization and Clustering](https://docs.uptrain.ai/docs/uptrain-monitors/concept-drift)** - Track the performance of your models in realtime and get degradation alerts.
- **[ChatGPT Grading](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)** - Specialized dashboards to understand model-inferred embeddings.
- **[Custom Grading Checks](https://docs.uptrain.ai/docs/uptrain-monitors/edge-case-detection)** - User-defined signals and statistical techniques to detect out-of-distribution data-points.
- **[](https://docs.uptrain.ai/docs/uptrain-monitors/data-integrity)** - Checks for missing or inconsistent data, duplicate records, data quality, etc. 
- **[Read from Delta Table and JSONL files](https://docs.uptrain.ai/docs/monitoring-custom-metrics)** - Define custom metrics that make sense for your use case.
- **[Hallucination Checks](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)** - Automate model retraining by attaching your training and inference pipelines.
- **[Toxic Keywords Checks](https://docs.uptrain.ai/docs/uptrain-monitors/model-bias)** - Track bias in your ML model's predictions.
- **[Feature Slicing](https://docs.uptrain.ai/docs/uptrain-visuals/shap-explainability)** - Understand relative importance of multiple features on predictions.
- **Realtime Dashboards** - To visualize your model's health live.


# Get started 🙌

You can quickly get started with [Google Colab here](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F).

To run it in your machine, follow the steps below:

### Install the package through pip:
```console
pip install uptrain
```

### Define your checks:
Say we want to check if the responses generated by our model contain any grammatical mistakes or not?

```console
# Define your checkset - list of checks, dataset file, and api_keys

checkset = CheckSet(
    checks = SimpleCheck(
        name = "grammar_score",
        compute = [
            GrammarScore(
                col_in_text = "model_response",
                col_out = "grammar_score"
            ),
        ],
        plot = PlotlyChart(kind = "table")
    ),
    source = '...',
    settings = Settings(openai_api_key = '...')
)

checkset.setup()
checkset.run()

```

For a quick walkthrough of how UpTrain works, check out our [quickstart tutorial](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial).

<h4> </h4>

# UpTrain in Action

## Experimentation

You can use the UpTrain experimentation api to run and compare LLM responses for different prompts, models, LLM chains, etc.



## Validation

## Monitoring




# Why UpTrain 🤔?

Large language models are trained over billions of data-points and perform really well over a wide variety of tasks. But one thing these models are not good at, is being deterministic. Even with the most well-crafted prompts, the model can misbehave for certain inputs, be it hallucinations, wrong output structure, toxic or biased response, irrelevant response, error modes can be immense. 

To ensure your LLM applications work reliably and correctly, UpTrain makes it easy for developers to evaluate the responses of their applications on multiple criterion. UpTrain's evaluation framework can be used to:

1) Validate (and correct) the response of the model before showing it to the user
2) Get quantitative measures to experiment across multiple prompts, model providers, etc.
3) Do unit testing to ensure no buggy prompt or code gets pushed into your production
4) Monitor your LLM applications in real-time and understand when they are going wrong in order to fix them before users complain.

We are constantly working to make UpTrain better. Want a new feature or need any integrations? Feel free to [create an issue](https://github.com/uptrain-ai/uptrain/issues) or [contribute](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) directly to the repository.

# License 💻

This repo is published under Apache 2.0 license. We are also working towards adding a hosted offering with limited seats - please fill this form to get a waitlist slot.

# Stay Updated ☎️
We are continuously adding tons of features and use cases. Please support us by giving the project a star ⭐!

# Provide feedback (Harsher the better 😉) 

We are building UpTrain in public. Help us improve by giving your feedback **[here](https://forms.gle/PXd89D5LiFubro9o9)**.

# Contributors 🖥️

We welcome contributions to UpTrain. Please see our [contribution guide](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) for details.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
