[<img src="https://user-images.githubusercontent.com/108270398/214240695-4f958b76-c993-4ddd-8de6-8668f4d0da84.png" width= "20%" />](https://uptrain.ai)

## An open-source tool to observe and improve ML models in production
[![GitHub license](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/uptrainai/uptrain/blob/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/uptrain.svg)](https://pypi.org/project/uptrain/)
[![UpTrain Docs](https://img.shields.io/badge/UpTrain-Docs-blue)](https://uptrain-ai.gitbook.io/uptrain-documentation/)
[![Join Discord](https://img.shields.io/badge/Join-Discord-orange)](https://discord.com/invite/gVvZhhrQaQ)

## Problem

Machine learning (ML) models are widely used to make critical business decisions, but no ML models is perfect and, further, their accuracy deteriorates over time. For example, A retail store's ML model for sales prediction becomes inaccurate due to a shift in consumer buying habits caused by the COVID-19 pandemic. This can lead to unexpected errors or biases in the predictions, implying serious business consequences. 

Furthermore, due to lack of transparency in its predictions, ML models are often considered as "black boxes" which makes it difficult to identify and fix their problems. Our tool, UpTrain, addresses these problems by providing ways to observe and improve ML models in production. It automates the process of monitoring the model's performance, detecting issues, and retraining the model with the right data at the right time, thus keeping it up to date and accurate while saving monitoring and retraining costs.

## What is UpTrain?
UpTrain is an open-source toolkit for ML practitioners to understand how their models are performing in production and continuously improve them over time by monitoring their performance, checking for (data) distribution shifts and collecting edge cases to retrain them upon. 

Our toolkit helps you keep an eye on your machine learning models to ensure they're performing at their best. It provides two main features:

**ML Observability:** It keeps track of how your model is performing over time, detect any issues such as concept drift, edge cases, data drift, data integrity etc.

**ML Refinement:** It improve your models by selecting the best data points for retraining, proactively catching model issues, and implementing a fully automated model refinement loop. This helps you save costs and prevent issues for your customers.

With ML models now being used almost everywhere, we strive to equip data scientists and ML engineers with the right tools to ensure they can adopt the best practices of observability and constant iteration which led to great advancement in the software domains. With UpTrain, they can define domain-specific signals and customized reports to continuously monitor, debug and improve their ML models. 

## Get Started
Install the package through pip:
```console
pip install uptrain
```
Run your first example:
```console
git clone git@github.com:uptrain-ai/uptrain.git
cd uptrain/examples/1_orientation_classification
pip install jupyterlab
jupyter lab
```

## How the UpTrain framework works?
UpTrain monitors the difference between the dataset the model was trained upon, and the real-world data points the model encounters during production (the wild!). This "difference" can be custom statistical measures designed by ML practitioners based on their use case. Additionally, it monitors for edge cases defined as rule-based smart signals on the model inputs. Whenever the framework sees a distribution shift or an increased frequency of edge cases, it raises an alert while identifying the subset of data that experienced these issues. Finally, it retrains the model by taking a balanced mixture of original training samples and the collected edge cases, improving its performance on the production samples.

![Section 02](https://user-images.githubusercontent.com/108270398/213943659-7ad062b0-9ee3-4007-8860-9333c4124ffe.jpg)


## Integrate UpTrain to your ML pipelines in <5 minutes
After installing the UpTrain package, the user can define a config that tells the tool about the metrics to monitor and the signals to capture. The signals can be edge cases to check, and the metric can be data distribution shifts. Based on the monitoring results, the tool automatically refines the model by using the optimal subset of the real-world dataset. An illustration is provided below. 

<img width="729" alt="Screenshot 2023-01-22 at 2 16 56 PM" src="https://user-images.githubusercontent.com/108270398/213943297-0fbb2afb-908f-4a02-83ca-3e5926716001.png">

UpTrain supports a wide variety of Machine learning models such as LLMs, recommendation models, prediction models, Computer vision models etc.

### How UpTrain can be used to observe and improve LLMs:
1. Monitoring model performance: Track the performance of your language model over time, such as the perplexity, BLEU, or METEOR scores, to identify any changes or degradation in the model's performance.
2. Detecting input distribution shift: Compare the distribution of the input data used to train the model to the distribution of the input data used in production. This can help identify input distribution shift and how it may be affecting the model's performance.
3. Analyzing data integrity: Monitor the quality and consistency of the input data being fed to the model, such as checking for missing values or outliers, to ensure the model is receiving the right input data.
4. Identifying edge cases: Understand how your model is performing on inputs it has not seen before, such as out-of-vocabulary words or unusual sentence structures, which can help identify areas where the model may not be performing well.
5. Tracking user engagement: Track how users interact with the model's outputs, such as click-through rates or sentiment analysis, to understand which outputs are most effective. 

### Similarly, this is how UpTrain can be used in recommendation systems:
1. Monitoring model performance: Track the performance of your recommendation model over time, such as the accuracy, precision, and recall of the model's recommendations.
2. Detecting concept drift: Check for changes in the user's behavior or the distribution of the items being recommended, which could indicate concept drift in the model's performance.
3. Identifying edge cases: Understand how your model is performing on items or users it has not seen before, which can help identify areas where the model may not be performing well.
4. Analyzing data drift: Analyze the distribution of the data used to train the model and compare it to the distribution of the data being used in production. This can help identify data drift and how it may be affecting the model's performance.
5. Evaluating diversity and fairness: Monitor the diversity of the recommendations and ensure that the model is not biased towards certain items or user groups.
6. Tracking user engagement: Track how users interact with the recommendations, such as click-through rates or purchase rates, to understand which recommendations are most effective.

## Stay Updated
We are continuously improving the package by simplifying the interface as well as adding tons of features. Support us by giving the project a star!

Please fill this form to provide your feedback:
https://forms.gle/PXd89D5LiFubro9o9
