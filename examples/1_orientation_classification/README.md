## UpTrain: Measuring data drift in production data for automated retraining of ML model

In `get_started.ipynb`, we consider a binary classification task of human orientation while exercising. That is, given the location of 17 key-points of the body such as the nose, shoulders, wrist, hips, ankles, etc., the model tries to predict whether the person is in a horizontal (see image 1 below) or a vertical (see image 2 below) position.

**Input**: 34-dimensional vector that contains the x and y positions of the 17 key-points.\
**Output**: Orientation (horizontal or vertical)

![Horizontal_class](https://user-images.githubusercontent.com/5287871/213901036-ca3badd4-a464-41b0-8a15-5aa7c24b0814.png)
![Vertical_class](https://user-images.githubusercontent.com/5287871/213901039-19906445-fa31-43bf-aaaf-037f837d81a1.png)

In this example, we will see how we can use UpTrain package to identify data drift and out of distribution cases on real-world data. 

#### Data Type Structure

Let's look at the training data features and visualise some of the training samples. Here, `id` is the training sample id, `gt` is the corresponding ground truth, and the rest of the features are the corresponding locations of the key-points of a human body.

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
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
<p>5 rows × 36 columns</p>
</div>

#### Visualizing some training samples for classifying human orientation
![training_data_examples](https://user-images.githubusercontent.com/5287871/214430440-85fced8e-234b-4341-92e7-1e001aea517e.jpeg)

The example follows the following steps for monitoring and retraining your model:
### Step 1: Train the Deep Neural Network model

We have defined a simple Neural Net comprised of a fully-connected layer with relu activation followed by a fully-connected layer to transfer latent features into model outputs. We compute Binary Entropy loss and are using Adam optimiser to train the model.\ 
Note: We use PyTorch in this example, but in other examples such as edge-case detection, we have also run UpTrain with Sklearn and Tensorflow.

![dnn_model_orientation_classification](https://user-images.githubusercontent.com/5287871/214430849-0e2df29f-bfea-43b5-aa7b-c7cbcaeea79c.png)

With the first version of this model, we observe an accuracy of 90.9% on the golden testing dataset. We will now how we can use UpTrain package to identify data distribution shifts, collect edge cases and retrain the model to improve its accuracy.

### Step 2: Define the list of checks to perform on model
In this example, we define a simple data drift check to identify any distribution shift between real-world test set and the reference dataset (the training dataset in this case). To achieve this, we set 'kps' (Keypoints) as the input variable, the framework performs clustering on the training dataset and checks if the real-world test set is following the similar distribution.

```python
checks = [{
    'type': uptrain.Anomaly.DATA_DRIFT,
    'reference_dataset': orig_training_file,
    'is_embedding': True,
    "measurable_args": {
        'type': uptrain.MeasurableType.INPUT_FEATURE,
        'feature_name': 'kps'  #keypoints
    },
}]
```
Here, the `type` refers to the anamoly type, which is data drift in this case. The `reference_dataset` is the training dataset, while `is_embedding` refers to whether the data type on which drfit is being measured is in a vector/embedding form. Finally, `measurable_args` define the input features (or any function of them) on which the drift is to be measured.

### Step 3: Define the training and evaluation arguments
We now attach the model training and evaluation pipelines so that UpTrain framework can automatically retrain the model in case it sees that the model is facing significant data drift.

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
```

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
Ship the model to production worry-free because the UpTrain tool will identify any data drifts, collect interesting data points and automatically retrain the model on them. To mimic deployment behavior, we are running the model on a 'real-world test set' and logging model inputs with UpTrain framework. The following is the pseudo-code. 

```python
# Load the trained model
model.load(trained_model_location)
model.eval()

for i, x_test in enumerate(real_world_dataset):
    # Do model prediction
    preds = model(x_test)

    # Log model inputs and outputs to the uptrain Framework to monitor data drift
    idens = framework.log(inputs=x_test, outputs=preds)
```

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

This is how the sample logs look like
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
   ```
   
#### Hurray! Our model after retraining performs significantly better.

Let's try to understand how UpTrain helped to improve our classification model.

#### Training data clusters
While initializing the UpTrain framework, it clusters the reference dataset (i.e. training dataset in our case). We are plotting the centroids and support (ie number of data-points belonging to that cluster) of all the 20 clusters in our training dataset.
![training_data_clusters](https://user-images.githubusercontent.com/5287871/214433144-c0f4e67d-001e-4206-89f2-e32b09075a93.png)

#### Edge cases clusters
As we see, the UpTrain framework identifies out-of-distribution data-points and collects the edge-cases which are sparsely present in the training dataset.
![edge_case_clusters](https://user-images.githubusercontent.com/5287871/214433163-068dab2d-5b57-4cb0-8283-d92a7a90c08b.png)

From the above plot generated while monitoring the model in production, we see that data drift occurs for many cases when the person is in a horizontal position. Specifically, cases when the person is in a push-up position are very sparse in our training dataset, causing the model predictions to go wrong for them. In the example of edge-case detection, we will see that how we can use this insight to define a "Pushup" signal, collect all push-up related data-points and specifically retrain on them.

## Do more with UpTrain

Apart from data drift, UpTrain has many other features such as 
1. Checking for edge-cases and collecting them for automated retraining
2. Verifying data integrity, 
3. Monitoring model performance and accuracy of predictions with standard statistical tools, 
4. Write your own custom monitors specific to your use-case, etc. 

To dig deeper into it, we recommend you checkout the other examples in the folder "deepdive_examples".
