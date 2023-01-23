[<img src="https://user-images.githubusercontent.com/108270398/213943166-be7bd32f-7b56-4d99-aeb3-fea1f48162b1.png" width= "20%" />](https://uptrain.ai)

## UpTrain -- Your Open-source toolkit to observe and refine ML models
[![GitHub license](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/uptrainai/uptrain/blob/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/uptrain.svg)](https://pypi.org/project/aqueduct-ml/)
[![UpTrain Docs](https://img.shields.io/badge/UpTrain-Docs-blue)](https://uptrain-ai.gitbook.io/uptrain-documentation/)
[![Join Discord](https://img.shields.io/badge/Join-Discord-orange)](https://discord.com/invite/gVvZhhrQaQ)

## What is UpTrain?
UpTrain is an open-source toolkit for ML practitioners to understand how their models are performing in production and continuously improve them over time by monitoring their performance, checking for (data) distribution shifts and collecting edge cases to retrain them upon. The toolkit serves two key functionalities: 

**ML Observability**
1. Is the performance of my model degrading over time?   [Concept Drift]
2. Is my model encoutering cases which it was not trained upon?   [Edge cases]
3. Is my input data distribution different from the one which I trained my model upon?   [Data Drift]
4. Am I feeding the right data to my model or any of the data pre-processing pipelines are broken?   [Data Integrity]

**ML Refinement**
1. Select the best data-points to retrain your models   (Smart retraining to save costs)
2. Proactively catch model issues and give you the ability to fix them or inform your customers (before they face issues due to incorrect model behavior)
3. A fully automated model refinement loop (Observe => Retrain => Compare => Deploy => ... )

With ML models now being used almost everywhere, we strive to equip data scientists and ML engineers with the right tools to ensure they can adopt the best practices of observability and constant iteration which led to great advancement in the software domains. With UpTrain, they can define domain-specific signals and customized reports to continuously monitor, debug and improve their ML models. 

## Get Started
You can install upTrain via the GitHub repository:
```bash
# Install the package through pip
pip install uptrain

# Run your first example
cd examples/1_orientation_classification
jupyter lab
```

## How the UpTrain framework works?
UpTrain monitors the difference between the dataset the model was trained upon, and the real-world data points the model encounters during production (the wild!). This "difference" can be custom statistical measures designed by ML practitioners based on their use case. Additionally, it monitors for edge cases defined as rule-based smart signals on the model inputs. Whenever the framework sees a distribution shift or an increased frequency of edge cases, it raises an alert while identifying the subset of data that experienced these issues. Finally, it retrains the model by taking a balanced mixture of original training samples and the collected edge cases, improving its performance on the production samples.

![Section 02](https://user-images.githubusercontent.com/108270398/213943659-7ad062b0-9ee3-4007-8860-9333c4124ffe.jpg)


## Integrate UpTrain to your ML pipelines in <5 minutes
After installing the UpTrain package, the user can define a config that tells the tool about the metrics to monitor and the signals to capture. The signals can be edge cases to check, and the metric can be data distribution shifts. Based on the monitoring results, the tool automatically refines the model by using the optimal subset of the real-world dataset. An illustration is provided below. 

<img width="729" alt="Screenshot 2023-01-22 at 2 16 56 PM" src="https://user-images.githubusercontent.com/108270398/213943297-0fbb2afb-908f-4a02-83ca-3e5926716001.png">

### Sample Use-cases:
1. Recommendation Systems: Use UpTrain to monitor popularity bias, recommendation quality across user groups etc.
2. Prediction Systems: Use UpTrain to monitor feature drift and the effectiveness of your predictions.
3. Computer Vision: Use UpTrain to measure drifts in the properties of your input image (brightness, intensity, temperature, model outputs etc.).
4. LLMs: Use UpTrain to measure drifts in your prompts and define rules to capture specific inputs to fine-tune upon.


## Stay Updated
We are continuously improving the package by simplifying the interface as well as adding tons of features. Support us by giving the project a star!

Please fill this form to provide your feedback:
https://forms.gle/PXd89D5LiFubro9o9
