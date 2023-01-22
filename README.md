[<img src="https://user-images.githubusercontent.com/5287871/211485071-e959b10c-3a78-4b02-a636-2fe8db23a3fc.png" width= "20%" />](https://uptrain.ai)

## UpTrain -- Your Open-source toolkit to observe and refine ML models
[![GitHub license](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/uptrainai/uptrain/blob/main/LICENSE)

## What is UpTrain?
UpTrain is an open-source toolkit for ML practitioners to understand how their models are performing in production and continuously improve them over time by monitoring their performance, checking for (data) distribution shifts and collecting edge cases to retrain them upon. The toolkit serves two key functionalities: 

**ML Observability**
    1. Is the performance of my model degrading over time?
    2. Is my model encoutering cases which it was not trained upon?
    3. Is my input data distribution different from the one which I trained my model upon?
    4. Am I feeding the right data to my model or any of the data pre-processing pipelines are broken?

**ML Refinement**
    1. Select the best data-points to retrain your models   (Smart retraining to save costs)
    2. Proactively catch model issues and give you the ability to fix them or inform your customers (before they face issues due to incorrect model behavior)
    3. A fully automated model refinement loop (Observe => Retrain => Compare => Deploy => ... )

With ML models now being used almost everywhere, we strive to equip data scientists and ML engineers with the right tools to ensure they can adopt the best practices of observability and constant iteration which led to great advancement in the software domains. With UpTrain, they can define domain-specific signals and customized reports to continuously monitor, debug and improve their ML models. 

## Get Started
You can install upTrain via the GitHub repository:
```bash
# Clone the upTrain git repository
git clone https://github.com/uptrain-ai/uptrain.git

# Install the requirements and UpTrain package (recommended to do this in a new environment)
cd uptrain
python setup.py install

# Run your first example
cd examples/1_orientation_classification
jupyter lab
```

## How the UpTrain framework works?
UpTrain monitors the difference between the dataset the model was trained upon, and the real-world data points the model encounters during production (the wild!). This "difference" can be custom statistical measures designed by ML practitioners based on their use case. Additionally, it monitors for edge cases defined as rule-based smart signals on the model inputs. Whenever the framework sees a distribution shift or an increased frequency of edge cases, it raises an alert while identifying the subset of data that experienced these issues. Finally, it retrains the model by taking a balanced mixture of original training samples and the collected edge cases, improving its performance on the production samples.

![upTrain_flow_diagram](https://user-images.githubusercontent.com/5287871/200270401-13935ddb-111c-432d-bf4a-96849fb875ff.png)

## Integrate UpTrain to your ML pipeline in <5 minutes
After installing the UpTrain package, the user can define a config that tells the tool about the metrics to monitor and the signals to capture. The signals can be edge cases to check, and the metric can be data distribution shifts. Based on the monitoring results, the tool automatically refines the model by using the optimal subset of the real-world dataset. An illustration is provided below. 

![get started in 5 minutes](https://user-images.githubusercontent.com/5287871/200270545-79ac887f-7786-47c5-bc59-87a37ee83f63.png)

### Sample Use-cases:
**Recommendation Systems:** Use UpTrain to monitor popularity bias, recommendation quality across user groups etc.
**Prediction Systems:** Use UpTrain to monitor feature drift and the effectiveness of your predictions.
**Computer Vision:** Use UpTrain to measure drifts in the properties of your input image (brightness, intensity, temperature, model outputs etc.). 
**LLMs:** Use UpTrain to measure drifts in your prompts and define rules to capture specific inputs to fine-tune upon.


## Stay Updated
We are continuously improving the package by simplifying the interface as well as adding tons of features. Support us by giving the project a star!
