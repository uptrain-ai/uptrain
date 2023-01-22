## UpTrain: Measuring data drift in production data for automated retraining of ML model

In `uptrain_data_drift.ipynb`, we consider a binary classification task of human orientation while exercising. That is, given the location of 17 key-points of the body such as the nose, shoulders, wrist, hips, ankles, etc., the model tries to predict whether the person is in a horizontal (see image 1 below) or a vertical (see image 2 below) position.

![Horizontal_class](https://user-images.githubusercontent.com/5287871/213901036-ca3badd4-a464-41b0-8a15-5aa7c24b0814.png)
![Vertical_class](https://user-images.githubusercontent.com/5287871/213901039-19906445-fa31-43bf-aaaf-037f837d81a1.png)

**Input**: 34-dimensional vector that contains the x and y positions of the 17 key-points.\
**Output**: Orientation (horizontal or vertical)

In this example, we will see how we can use UpTrain package to identify data drift and out of distribution cases on real-world data. 

The example follows the following steps:
### Step 1: Train the Deep Neural Network model
Note: We use PyTorch in this example, but in other examples such as edge-case detection, we have also run UpTrain with Sklearn and Tensorflow. With the first version of this model, we observe an accuracy of 90.9% on the golden testing dataset. 

### Step 2: Define the list of checks to perform on model
In this example, we define a simple data drift check on the real-world data. To achieve this, we use clustering on training and real-world datasets to identify any distribution shift between real-world data and the reference dataset (the training dataset in this case).

```python
checks = [{
    'type': uptrain.Anomaly.DATA_DRIFT,
    'reference_dataset': orig_training_file,
    'is_embedding': True,
    "measurable_args": {
        'type': uptrain.MeasurableType.INPUT_FEATURE,
        'feature_name': 'kps'
    },
}]
```
Here, the `type` refers to the anamoly type, which is data drift in this case. The `reference_dataset` is the training dataset, while `is_embedding` refers to whether the data type on which drfit is being measured is in a vector/embedding form. Finally, `measurable_args` define the input features (or any function of them) on which the drift is to be measured.

### Step 3: Define the training and evaluation arguments
The next step is to define the existing training and evaluation arguments that can be passed to the UpTrain config.

### Step 4: Define the UpTrain Config
We are now ready to define the UpTrain config as follows
```python
cfg = {
    "checks": checks, 
    "training_args": training_args,
    "evaluation_args": evaluation_args,

    # Retrain when 200 datapoints are collected in the retraining dataset
    "retrain_after": 200,
    
    # A local folder to store the retraining dataset
    "retraining_folder": "uptrain_smart_data__data_drift",
    
    # A function to visualize clusters in the data
    "cluster_visualize_func": plot_all_cluster,
}
```

### Step 5: Deploy the model in production
Finally, we can ship the model to production worry-free because the UpTrain tool will ideantify any deta drifts, collect interesting data points and automatically retrain the model on them.

### Automated model retraining performance
After an automated retraining of the model was launched by UpTrain on points that caused the data drift, we observe that the error rate decreased by 20x. 
```
---------------------------------------------
---------------------------------------------
Old model accuracy:  90.9%
Retrained model accuracy (ie 201 smartly collected data-points added):  99.5%
---------------------------------------------
---------------------------------------------
```

