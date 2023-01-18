[<img src="https://user-images.githubusercontent.com/5287871/211485071-e959b10c-3a78-4b02-a636-2fe8db23a3fc.png" width= "20%" />](https://uptrain.ai)

## upTrain.ai -- A framework to facilitate retraining of ML models
[![GitHub license](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/uptrainai/uptrain/blob/main/LICENSE)

## What is upTrain.ai?
With ML models now being used almost everywhere, the mindset is shifting from a “research-first” to a “product-first” approach. Data (being the new oil) is collected continuously, which implies that models need to be trained continuously. 

**upTrain.ai is an automated machine-learning model refinement tool.**

upTrain.ai is designed for ML practitioners who want to improve the performance of an already deployed model. With upTrain.ai, they can define domain-specific signals and customized reports to continuously monitor, debug and improve their ML models. 

You can install upTrain via the GitHub repository:
```bash
# Clone the upTrain git repository
git clone https://github.com/uptrainai/uptrain.git

# Install the requirements (recommended to do this in a new environment)
cd uptrain
pip install -r requirements.txt

# Install the upTrain.ai package.
python setup.py install

# Run your first example
cd examples/orientation_classification
jupyter lab
```
## How the upTrain.ai framework works?
upTrain.ai monitors the difference between the dataset the model was trained upon, and the real-world data points the model encounters during production (the wild!). This "difference" can be custom statistical measures designed by ML practitioners based on their use case. Additionally, it monitors for edge cases defined as rule-based smart signals on the model input. Whenever the framework sees a distribution shift or an increased frequency of edge cases, it raises an alert while identifying the subset of data that experienced these issues. Finally, it retrains the model on that data, improving its performance in the wild.

![upTrain_flow_diagram](https://user-images.githubusercontent.com/5287871/200270401-13935ddb-111c-432d-bf4a-96849fb875ff.png)

## Integrate upTrain.ai to your ML pipeline in <5 minutes
After installing the upTrain.ai package, the user can define a config that tells the tool about the metrics to monitor and the signals to capture. The signals can be edge cases to check, and the metric can be data distribution shifts. Based on the monitoring results, the tool automatically refines the model by using the optimal subset of the real-world dataset. An illustration is provided below. 

![get started in 5 minutes](https://user-images.githubusercontent.com/5287871/200270545-79ac887f-7786-47c5-bc59-87a37ee83f63.png)

## Stay Updated
We are continuously improving the package by simplifying the interface as well as adding tons of features. Support us by giving the project a star!
