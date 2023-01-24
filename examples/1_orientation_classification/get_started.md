## Refining a binary blassification model by identifying data distribution shifts

In this example, we consider a binary classification task of human orientation while exercising. That is, given the location of 17 key-points of the body such as the nose, shoulders, wrist, hips, ankles, etc., the model tries to predict whether the person is in a horizontal (see image 1 below) or a vertical (see image 2 below) position. 

Input: 34-dimensional vector that contains the x and y positions of the 17 key-points.\
Output: Orientation (horizontal - class 0 or vertical - class 1)

![Horizontal_class.png](attachment:020c13d9-0eab-4a18-9d3a-fd645826319f.png)
![Vertical_class.png](attachment:5d35fb64-5f4b-4426-8756-2016a5ddc9a8.png)

In this notebook, we will see how we can use UpTrain package to identify data drift and identify out of distribution cases on real-world data.


```python
import os
import subprocess
import zipfile
import numpy as np
import torch
import uptrain

from helper_files import read_json, KpsDataset
from helper_files import body_length_signal, plot_all_cluster
```

Let's first download the example dataset


```python
data_dir = "data"
remote_url = "https://oodles-dev-training-data.s3.amazonaws.com/data.zip"
orig_training_file = 'data/training_data.json'
if not os.path.exists(data_dir):
    print("Starting to download example dataset...")
    try:
        # Most Linux distributions have Wget installed by default.
        # Below command is to install wget for MacOS
        wget_installed_ok = subprocess.call("brew install wget", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print("Successfully installed wget")
    except:
        dummy = 1
    try:
        if not os.path.exists("data.zip"):
            file_downloaded_ok = subprocess.call("wget " + remote_url, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print("Data downloaded")
        with zipfile.ZipFile("data.zip", 'r') as zip_ref:
            zip_ref.extractall("./")
        print("Prepared Example Dataset")
        os.remove("data.zip")
    except Exception as e:
        print(e)
        print("Could not load training data")
        print("Please follow following steps to manually download data")
        print("Step 1: Paste the link https://oodles-dev-training-data.s3.amazonaws.com/data.zip in your browser")
        print("Step 2: Once the zip file is downloaded, unzip it here (i.e. YOUR_LOC/uptrain/examples/1_orientation_classification/")
else:
    print("Example dataset already present")
```

    Example dataset already present


#### Type of data files

Let's define the training and testing datasets, and visualise some of the training samples.


```python
# Training data
training_file = 'data/training_data.json'

# A testing dataset to evaluate model performance
golden_testing_file = 'data/golden_testing_data.json'

# The data-points which the models sees in production
real_world_test_cases = 'data/real_world_testing_data.json'

# To annotate the collected data points, we extract the ground truth from a master annotation file 
# (we can also import from any other annotation pipelines such as an annotation job on Mechanical turk).
annotation_args = {'master_file': 'data/master_annotation_data.json'}

# Let's visualize some of the training examples
training_data = read_json(training_file, dataframe=True)
training_data.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>kps</th>
      <th>id</th>
      <th>gt</th>
      <th>Nose_X</th>
      <th>Nose_Y</th>
      <th>Left_Eye_X</th>
      <th>Left_Eye_Y</th>
      <th>Right_Eye_X</th>
      <th>Right_Eye_Y</th>
      <th>Left_Ear_X</th>
      <th>...</th>
      <th>Right_Hip_X</th>
      <th>Right_Hip_Y</th>
      <th>Left_Knee_X</th>
      <th>Left_Knee_Y</th>
      <th>Right_Knee_X</th>
      <th>Right_Knee_Y</th>
      <th>Left_Ankle_X</th>
      <th>Left_Ankle_Y</th>
      <th>Right_Ankle_X</th>
      <th>Right_Ankle_Y</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[333.10994563476123, 76.16168807503908, 338.56...</td>
      <td>18100306191</td>
      <td>0</td>
      <td>333.109946</td>
      <td>76.161688</td>
      <td>338.565022</td>
      <td>71.526141</td>
      <td>328.198963</td>
      <td>72.194832</td>
      <td>345.656490</td>
      <td>...</td>
      <td>313.925120</td>
      <td>186.053571</td>
      <td>335.013894</td>
      <td>253.606162</td>
      <td>309.011228</td>
      <td>249.226721</td>
      <td>333.654654</td>
      <td>311.513965</td>
      <td>311.760718</td>
      <td>294.100708</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[373.0438346822569, 207.9342362388681, 378.278...</td>
      <td>12100004003</td>
      <td>1</td>
      <td>373.043835</td>
      <td>207.934236</td>
      <td>378.278397</td>
      <td>205.678759</td>
      <td>373.341256</td>
      <td>206.135385</td>
      <td>380.165081</td>
      <td>...</td>
      <td>326.157557</td>
      <td>227.332505</td>
      <td>351.341468</td>
      <td>228.657224</td>
      <td>328.581103</td>
      <td>226.218648</td>
      <td>340.983916</td>
      <td>240.702033</td>
      <td>327.240044</td>
      <td>241.339998</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[289.1160206784009, 218.50299194624307, 294.33...</td>
      <td>17100400995</td>
      <td>0</td>
      <td>289.116021</td>
      <td>218.502992</td>
      <td>294.331203</td>
      <td>212.576996</td>
      <td>284.066039</td>
      <td>212.259060</td>
      <td>301.216267</td>
      <td>...</td>
      <td>276.756049</td>
      <td>255.008508</td>
      <td>345.230291</td>
      <td>273.285718</td>
      <td>237.498075</td>
      <td>272.014232</td>
      <td>349.413545</td>
      <td>315.731031</td>
      <td>237.181977</td>
      <td>317.784665</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[320.89799794070035, 71.87346792197232, 325.16...</td>
      <td>18100102279</td>
      <td>0</td>
      <td>320.897998</td>
      <td>71.873468</td>
      <td>325.167727</td>
      <td>67.468033</td>
      <td>317.188621</td>
      <td>67.689969</td>
      <td>329.814255</td>
      <td>...</td>
      <td>297.857163</td>
      <td>154.614716</td>
      <td>329.598707</td>
      <td>197.955873</td>
      <td>299.710591</td>
      <td>203.663761</td>
      <td>327.663990</td>
      <td>231.684086</td>
      <td>298.525798</td>
      <td>251.789836</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[486.1227614375234, 218.36389575646785, 495.50...</td>
      <td>12100500969</td>
      <td>1</td>
      <td>486.122761</td>
      <td>218.363896</td>
      <td>495.503172</td>
      <td>225.783665</td>
      <td>493.671955</td>
      <td>223.923930</td>
      <td>495.000279</td>
      <td>...</td>
      <td>337.222705</td>
      <td>236.111076</td>
      <td>258.045097</td>
      <td>167.009500</td>
      <td>264.609213</td>
      <td>167.154231</td>
      <td>210.604750</td>
      <td>260.979533</td>
      <td>224.932744</td>
      <td>251.462142</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 37 columns</p>
</div>



![2.jpg](attachment:27ccdf5e-4706-4ee9-bcce-c7a0c262f488.jpg)

### Step 1: Train our Neural Network model

We have defined a simple Neural Net comprised of a fully-connected layer with relu activation followed by a fully-connected layer to transfer latent features into model outputs. We compute Binary Entropy loss and are using Adam optimiser to train the model

![model.png](attachment:4d0b8efb-e059-4dad-8939-300423c98847.png)




```python
from helper_files import get_accuracy_torch, train_model_torch, BinaryClassification
train_model_torch(training_file, 'version_0')
```

Next, let's see how our model performs on the golden testing dataset


```python
get_accuracy_torch(golden_testing_file, 'version_0')
```

    Evaluating model: version_0  on  15731  data-points





    0.9092873943169538



Great, we have successfully trained our Neural Network which is giving more than 90% accuracy. We will now how we can use UpTrain package to identify data distribution shifts, collect edge cases and retrain the model to improve its accuracy 

### Step 2: Define the list of checks to perform on model

In this example, we define a simple data drift check to identify any distribution shift between real-world test set and the reference dataset (the training dataset in this case). To achieve this, we set 'kps' (Keypoints) as the input variable, the framework performs clustering on the training dataset and checks if the real-world test set is following the similar distribution


```python
checks = [{
        'type': uptrain.Anomaly.DATA_DRIFT,
        'reference_dataset': orig_training_file,
        'is_embedding': True,
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'kps'   # keypoints
        },
    }]

print("Data Drift checks: ", checks)
```

    Data Drift checks:  [{'type': <Anomaly.DATA_DRIFT: 'data_drift'>, 'reference_dataset': 'data/training_data.json', 'is_embedding': True, 'measurable_args': {'type': <MeasurableType.INPUT_FEATURE: 'input_feature'>, 'feature_name': 'kps'}}]


### Step 3: Define the training and evaluation arguments

We now attach the model training and evaluation pipelines so that UpTrain framework can automatically retrain the model in case it sees that the model is facing significant data drift


```python
# Define the training pipeline to annotate collected edge cases and retrain the model automatically
training_args = {
    "annotation_method": {"method": uptrain.AnnotationMethod.MASTER_FILE, "args": annotation_args}, 
    "training_func": train_model_torch, 
    "orig_training_file": orig_training_file,
}

# Define evaluation pipeline to test retrained model against original model
evaluation_args = {
    "inference_func": get_accuracy_torch,
    "golden_testing_dataset": golden_testing_file,
}

print("Training Pipelines: ", training_args, "\n")
print("Evaluation Pipelines: ", evaluation_args)
```

    Training Pipelines:  {'annotation_method': {'method': <AnnotationMethod.MASTER_FILE: 1>, 'args': {'master_file': 'data/master_annotation_data.json'}}, 'training_func': <function train_model_torch at 0x7ff33b262b00>, 'orig_training_file': 'data/training_data.json'} 
    
    Evaluation Pipelines:  {'inference_func': <function get_accuracy_torch at 0x7ff33b2628c0>, 'golden_testing_dataset': 'data/golden_testing_data.json'}


### Step 4: Initialize the UpTrain Framework


```python
cfg = {
    "checks": checks, 
    "training_args": training_args,
    "evaluation_args": evaluation_args,

    # Retrain when 200 datapoints are collected in the retraining dataset
    "retrain_after": 200,
    
    # A local folder to store the retraining dataset
    "retraining_folder": "uptrain_smart_data",
    
    # A function to visualize clusters in the data
    "cluster_visualize_func": plot_all_cluster,
}

# Initialize the UpTrain framework object with config 
framework = uptrain.Framework(cfg)
print("Successfully Initialized UpTrain Framework")
```

    Successfully Initialized UpTrain Framework


### Step 5: Deploy the model in production

Ship the model to production worry-free because the UpTrain tool will identify any data drifts, collect interesting data points and automatically retrain the model on them. To mimic deployment behavior, we are running the model on a 'real-world test set' and logging model inputs with UpTrain framework.


```python
inference_batch_size = 16
model_dir = 'trained_models_torch/'
model_save_name = 'version_0'
real_world_dataset = KpsDataset(
    real_world_test_cases, batch_size=inference_batch_size, is_test=True
)
model = BinaryClassification()
model.load_state_dict(torch.load(model_dir + model_save_name))
model.eval()

for i,elem in enumerate(real_world_dataset):

    # Do model prediction
    inputs = {"data": {"kps": elem[0]["kps"]}, "id": elem[0]["id"]}
    x_test = torch.tensor(inputs["data"]["kps"]).type(torch.float)
    test_logits = model(x_test).squeeze() 
    preds = torch.round(torch.sigmoid(test_logits)).detach().numpy()

    # Log model inputs and outputs to the uptrain Framework to monitor data drift
    idens = framework.log(inputs=inputs, outputs=preds)

    # Retrain only once
    if framework.version > 1:
        break
```

    51  edge cases identified out of  11840  total samples
    100  edge cases identified out of  13360  total samples
    150  edge cases identified out of  14864  total samples
    201  edge cases identified out of  21632  total samples
    
    Kicking off re-training
    Creating retraining dataset: uptrain_smart_data/1/training_dataset.json  by merging  data/training_data.json  and collected edge cases.
    
    Model retraining done...
    
    Generating comparison report...
    Evaluating model: version_0  on  15731  data-points
    Evaluating model: version_1  on  15731  data-points
    ---------------------------------------------
    ---------------------------------------------
    Old model accuracy:  0.9092873943169538
    Retrained model accuracy (ie 201 smartly collected data-points added):  0.9952323437797979
    ---------------------------------------------
    ---------------------------------------------


#### Hurray! Our model after retraining performs significantly better.

Let's try to understand how UpTrain helped to improve our classification model.

#### Training data clusters
While initializing the UpTrain framework, it clusters the reference dataset (i.e. training dataset in our case). We are plotting the centroids and support (ie number of data-points belonging to that cluster) of all the 20 clusters in our training dataset.

![training_dataset_clusters.png](attachment:56779bcd-7f8b-4e7a-8af3-c87a83bb0883.png)

#### Edge cases clusters
As we see, the UpTrain framework identifies out-of-distribution data-points and collects the edge-cases which are sparsely present in the training dataset.

![collected_edge_cases_clusters.png](attachment:5a57b1ed-6cff-4482-a60a-b04bba3c40a5.png)

From the above plot generated while monitoring the model in production, we see that data drift occurs for many cases when the person is in a horizontal position. Specifically, cases when the person is in push-ups position are very sparse in our training dataset, causing the model predictions to go wrong for them. In the example of edge-case detection, we will see that how we can use this insight to define a "Pushup" signal, collect all push-up related data-points and specifically retrain on them.

## Do more with UpTrain

Apart from data drift, UpTrain has many other features such as 
1. Checking for edge-cases and collecting them for automated retraining
2. Verifying data integrity, 
3. Monitoring model performance and accuracy of predictions, etc. 

To dig deeper into it, we recommend you checkout the other examples in the folder "deepdive_examples".
