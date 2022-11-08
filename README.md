[<img src="https://user-images.githubusercontent.com/5287871/200270081-69863fc2-8537-4736-915d-193f9e9112cd.png" width= "20%" />](https://oodles.ai)

## OODLES.AI -- A framework to facilitate retraining of ML models
[![GitHub license](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/Oodles-ai/oodles/blob/main/LICENSE)

## What is Oodles.ai?
With ML models now being used almost everywhere, the mindset is shifting from a “research-first” to a “product-first” approach. Data (being the new oil) is collected continuously, which implies that models need to be trained continuously. 

**Oodles.ai is an automated machine-learning model refinement tool.**

Oodles.ai is designed for ML practitioners who want to improve the performance of an already deployed model. With Oodles.ai, they can define domain-specific signals and customized reports to continuously monitor, debug and improve their ML models. 

You can install oodles via the GitHub repository:
```bash
# Clone the oodles git repository
git clone https://github.com/Oodles-ai/oodles.git

# Install the Oodles.ai package.
cd oodles
python setup.py install
```
## How the Oodles.ai framework works?
Oodles.ai monitors the difference between the dataset the model was trained upon, and the real-world data points the model encounters during production (the wild!). This "difference" can be custom statistical measures designed by ML practitioners based on their use case. Additionally, it monitors for edge cases defined as rule-based smart signals on the model input. Whenever the framework sees a distribution shift or an increased frequency of edge cases, it raises an alert while identifying the subset of data that experienced these issues. Finally, it retrains the model on that data, improving its performance in the wild.
![oodles_flow_diagram](https://user-images.githubusercontent.com/5287871/200270401-13935ddb-111c-432d-bf4a-96849fb875ff.png)

## Integrate Oodles.ai to your ML pipeline in <5 minutes
After installing the Oodles.ai package, the user can define a config that tells the tool about the metrics to monitor and the signals to capture. The signals can be edge cases to check, and the metric can be data distribution shifts. Based on the monitoring results, the tool automatically refines the model by using the optimal subset of the real-world dataset. An illustration is provided below. 

![get started in 5 minutes](https://user-images.githubusercontent.com/5287871/200270545-79ac887f-7786-47c5-bc59-87a37ee83f63.png)
