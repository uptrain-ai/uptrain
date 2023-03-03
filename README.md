<h4 align="center">
  <a href="https://uptrain.ai">
    <img width="300" src="https://user-images.githubusercontent.com/108270398/214240695-4f958b76-c993-4ddd-8de6-8668f4d0da84.png" alt="uptrain">
  </a>
</h4>
<h2>
  <p align="center">
    <p align="center">UpTrain is an open-source framework to monitor machine learning models, built for engineers</p>
  </p>
</h2>

<p align="center">
<br>
<a href="https://docs.uptrain.ai/docs/" rel="nofollow"><strong>Read documentation »</strong></a>
<br>
<a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/" rel="nofollow"><strong>Try it out »</strong></a>
</p>

<h4 align="center">
  <a href="https://github.com/uptrainai/uptrain/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="UpTrain is released under the Apache 2.0 license." />
  </a>
  <a href="https://pypi.org/project/uptrain/">
    <img src="https://badge.fury.io/py/uptrain.svg" alt="PyPI version" />
  </a>
  <a href="https://docs.uptrain.ai/docs/">
    <img src="https://img.shields.io/badge/Read-Docs-blue" alt="Docs" />
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

<h4 align="center">
<img src="https://user-images.githubusercontent.com/108270398/218686821-a54e112f-8b14-485f-acef-de1f611adb2f.png" width="70%" alt="Performance" />
</h4>

<h4>
</h4>

**[UpTrain](https://uptrain.ai)** is an open-source, data-secure tool for ML practitioners to observe and refine their ML models by monitoring their performance, checking for (data) distribution shifts, and collecting edge cases to retrain them upon. It integrates seamlessly with your existing production pipelines and takes minutes to get started ⚡.

<h4>
</h4>
<h4> </h4>

# **[Key Features](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)** 💡

- **[Data Drift Checks](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/run.ipynb)** - Identify distribution shifts in your model inputs.
- **[Performance Monitoring](https://github.com/uptrain-ai/uptrain/blob/main/examples/fraud_detection/run.ipynb)** - Track the performance of your models in realtime and get alerted as soon as a dip is observed.
- **[Embeddings Support](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)** - Specialized dashboards to understand model-inferred embeddings.
- **[Edge Case Signals](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_edge_cases_torch.ipynb)** - User-defined signals and statistical techniques to detect out-of-distribution data-points.
- **[Data Integrity Checks](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_data_integrity.ipynb)** - Checks for missing or inconsistent data, duplicate records, data quality, etc. 
- **[Customizable metrics](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_data_drift_custom_measures.ipynb)** - Define custom metrics that make sense for your use case.
- **[Automated Retraining](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)** - Automate model retraining by attaching your training and inference pipelines.
- **[Model Bias](https://github.com/uptrain-ai/uptrain/blob/main/examples/shopping_cart_recommendation/run.ipynb)** - Track popularity bias in your recommendation models.
- **Data Security** - Your data never goes out of your machine.


## 🚨Coming soon🚨

- **Realtime Dashboards** - To visualize your model's health.
- **Slack Integration** - Get alerts on Slack.
- **Label Shift** - Identify drifts in your predictions. Specially useful in cases when ground truth is unavailable.
- **Prediction Stability** - Filter cases where model prediction is not stable.
- **AI Explainability** - Understand relative importance of multiple features on predictions.
- **Adversarial Checks** - Combat adversarial attacks

And more.

<h4> </h4>

# Get started 🙌

You can quickly get started with [Google collab here](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F).

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

For more info, visit our [get started guide](https://docs.uptrain.ai/docs/get-started).

<h4> </h4>

# UpTrain in [action](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb) 🎬

One of the most common use cases of ML today is language models, be it text summarization, NER, chatbots, language translation, etc. UpTrain provides ways to visualize differences in the training and real-world data via UMAP clustering of text embeddings (inferred from bert).
<h1 align="left">
<img alt="Meme" width="60%" src="https://user-images.githubusercontent.com/108270398/220204024-437c48f9-51d9-4ed8-9e23-5ec7033b8f7b.png">
</h1>

Additionally, UpTrain also provides statistical measures to quantify these differences and enables automated alerts whenever this drift crosses a certain threshold.
<h1 align="left">
<img alt="Meme" width="43%" src="https://user-images.githubusercontent.com/108270398/220204120-84433f34-33e9-4106-9da3-5db1b8fc68f3.png">
<img alt="Meme" width="51%" src="https://user-images.githubusercontent.com/108270398/220204284-3ced3db3-7f1d-4147-8fc1-21cdd28bbb40.png">
</h1>

# Why UpTrain 🤔?

Machine learning (ML) models are widely used to make critical business decisions. Still, no ML model is 100% accurate, and, further, their accuracy deteriorates over time 😣. For example, Sales prediction becomes inaccurate over time due to a shift in consumer buying habits. Additionally, due to the black box nature of ML models, it's challenging to identify and fix their problems.

UpTrain solves this. We make it easy for data scientists and ML engineers to understand where their models are going wrong and help them fix them before others complain 🗣️.

UpTrain can be used for a wide variety of Machine learning models such as LLMs, recommendation models, prediction models, Computer vision models, etc.

We are constantly working to make UpTrain better. Want a new feature or need any integrations? Feel free to [create an issue](https://github.com/uptrain-ai/uptrain/issues) or [contribute](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) directly to the repository.

<h1 align="left">
<img alt="Meme" width="60%" src="https://user-images.githubusercontent.com/108270398/215209245-4d6b1f47-7af9-4db8-8d8c-63dcc610571c.jpg">
</h1>

# License 💻

This repo is published under Apache 2.0 license. We're currently focused on developing non-enterprise offerings that should cover most use cases. In the future, we will add a hosted version which we might charge for.

# Stay Updated ☎️
We are continuously adding tons of features and use cases. Please support us by giving the project a star ⭐!

# Provide feedback (Harsher the better 😉) 

We are building UpTrain in public. Help us improve by giving your feedback **[here](https://forms.gle/PXd89D5LiFubro9o9)**.

# Contributors 🖥️

We welcome contributions to uptrain. Please see our [contribution guide](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) for details.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
