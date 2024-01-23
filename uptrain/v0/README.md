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


**[UpTrain](https://uptrain.ai)** is an open-source, data-secure tool for ML practitioners to observe and refine their ML models by monitoring their performance, checking for (data) distribution shifts, and collecting edge cases to retrain them upon. It integrates seamlessly with your existing production pipelines and takes minutes to get started ⚡.


# **[Key Features](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)** 💡

- **[Data Drift Checks](https://docs.uptrain.ai/docs/uptrain-monitors/data-drift)** - Identify distribution shifts in your model inputs.
- **[Performance Monitoring](https://docs.uptrain.ai/docs/uptrain-monitors/concept-drift)** - Track the performance of your models in realtime and get degradation alerts.
- **[Embeddings Support](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)** - Specialized dashboards to understand model-inferred embeddings.
- **[Edge Case Signals](https://docs.uptrain.ai/docs/uptrain-monitors/edge-case-detection)** - User-defined signals and statistical techniques to detect out-of-distribution data-points.
- **[Data Integrity Checks](https://docs.uptrain.ai/docs/uptrain-monitors/data-integrity)** - Checks for missing or inconsistent data, duplicate records, data quality, etc. 
- **[Customizable metrics](https://docs.uptrain.ai/docs/monitoring-custom-metrics)** - Define custom metrics that make sense for your use case.
- **[Automated Retraining](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)** - Automate model retraining by attaching your training and inference pipelines.
- **[Model Bias](https://docs.uptrain.ai/docs/uptrain-monitors/model-bias)** - Track bias in your ML model's predictions.
- **[AI Explainability](https://docs.uptrain.ai/docs/uptrain-visuals/shap-explainability)** - Understand relative importance of multiple features on predictions.
- **Data Security** - Your data never goes out of your machine.
- **Slack Integration** - Get alerts on Slack.
- **Realtime Dashboards** - To visualize your model's health live.

## 🚨Coming soon🚨

- **Label Shift** - Identify drifts in your predictions. Specially useful in cases when ground truth is unavailable.
- **Model confidence interval** - Confidence intervals for model predictions 
- **Advanced drift detection techniques** - Outlier-based drift detection methods
- **Advanced feature slicing** - Ability to slice statistical properties
- **Kolmogorov-Smirnov Test** - For detecting distribution shifts
- **Prediction Stability** - Filter cases where model prediction is not stable.
- **Adversarial Checks** - Combat adversarial attacks

And more.


# Get started 🙌

You can quickly get started with [Google Colab here](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F).

To run it in your machine, follow the steps below:

### Install the package through pip:
```console
pip install uptrain
```

### Run your first example:
```console
git clone git@github.com:uptrain-ai/uptrain.git
cd uptrain/examples
pip install jupyterlab
jupyter lab
```

For a quick walkthrough of how UpTrain works, check out our [quickstart tutorial](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial).

<h4> </h4>

# UpTrain in [action](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb) 🎬

One of the most common use cases of ML today is language models, be it text summarization, NER, chatbots, language translation, etc. UpTrain provides ways to visualize differences in the training and real-world data via UMAP clustering of text embeddings (inferred from BERT). Following are some replays from the UpTrain dashboard.

### AI Explainability out-of-the-box

<h1 align="center">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/4_Explanability_recording.gif">
</h1>

### Live Model Performance Monitoring and Data Integrity Checks

<h1 align="center">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/fraud_detection/concept_drift_avg_acc.gif"> <img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/data_integrity.gif">
</h1>

### UMAP Dimensionality Reduction and Visualization

<h1 align="center">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/text_summarization/umap.gif">
</h1>


### Edge-case Collection for Finetuning the Model later

<h1 align="center">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/edge_cases.gif">
</h1>

# Why UpTrain 🤔?

Machine learning (ML) models are widely used to make critical business decisions. Still, no ML model is 100% accurate, and, further, their accuracy deteriorates over time 😣. For example, Sales prediction becomes inaccurate over time due to a shift in consumer buying habits. Additionally, due to the black box nature of ML models, it's challenging to identify and fix their problems.

UpTrain solves this. We make it easy for data scientists and ML engineers to understand where their models are going wrong and help them fix them before others complain 🗣️.

UpTrain can be used for a wide variety of Machine learning models such as LLMs, recommendation models, prediction models, Computer vision models, etc.

We are constantly working to make UpTrain better. Want a new feature or need any integrations? Feel free to [create an issue](https://github.com/uptrain-ai/uptrain/issues) or [contribute](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) directly to the repository.

<h1 align="center">
<img alt="Meme" width="40%" src="https://user-images.githubusercontent.com/108270398/215209245-4d6b1f47-7af9-4db8-8d8c-63dcc610571c.jpg">
</h1>

# License 💻

This repo is published under Apache 2.0 license, with the exception of the ee directory which will contain premium features requiring an enterprise license in the future. We're currently focused on developing non-enterprise offerings that should cover most use cases by adding more features and extending to more models. We also working towards adding a hosted offering - [contact us](mailto:tech@uptrain.ai) if you are interested.

# Stay Updated ☎️
We are continuously adding tons of features and use cases. Please support us by giving the project a star ⭐!

# Provide feedback (Harsher the better 😉) 

We are building UpTrain in public. Help us improve by giving your feedback **[here](https://forms.gle/PXd89D5LiFubro9o9)**.

# Contributors 🖥️

We welcome contributions to UpTrain. Please see our [contribution guide](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) for details.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
