<h1 align="center">
  <a href="https://uptrain.ai">
    <img width="300" src="https://user-images.githubusercontent.com/108270398/214240695-4f958b76-c993-4ddd-8de6-8668f4d0da84.png" alt="uptrain">
  </a>
</h1>

<h1 style="text-align: center;">Monitoring a Trip Time prediction model</h1>

**Overview**: In this example, we consider a regression task where we want to predict the trip time given the trip distance, number of passengers, booking date, vendor ID, etc. 

**Dataset**: We use the [New York City Taxi Trip Duration dataset](https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data) from Kaggle, where the data contains features such as vendor_id, pickup_datetime, passenger_count, pickup_location, drop_location, etc., and the trip durations (in seconds). We want to train and ML model that takes the input features and predicts the trip duration. 

**Monitoring**: In this notebook, we will see how we can use UpTrain package to monitor model accuracy, run data integrity checks, and add SHAP in UpTrain dashboard to explain model predictions.




```python
# Divide data into train-test splits
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.1)

# Get ids for data to locate them with their ids in the UpTrain dashboard
test_ids = list(X_test['id'])
```

#### Let's see how the input looks like


```python
# Let's see how the data looks
X_train.head(3)
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
      <th>vendor_id</th>
      <th>passenger_count</th>
      <th>store_and_fwd_flag</th>
      <th>dist</th>
      <th>pickup_year</th>
      <th>pickup_month</th>
      <th>pickup_day</th>
      <th>pickup_dow</th>
      <th>pickup_hour</th>
      <th>pickup_min</th>
      <th>pickup_sec</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>306046</th>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0.006330</td>
      <td>2016</td>
      <td>5</td>
      <td>6</td>
      <td>4</td>
      <td>12</td>
      <td>22</td>
      <td>21</td>
    </tr>
    <tr>
      <th>253777</th>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0.020341</td>
      <td>2016</td>
      <td>4</td>
      <td>15</td>
      <td>4</td>
      <td>14</td>
      <td>2</td>
      <td>12</td>
    </tr>
    <tr>
      <th>882330</th>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0.116831</td>
      <td>2016</td>
      <td>3</td>
      <td>18</td>
      <td>4</td>
      <td>9</td>
      <td>26</td>
      <td>43</td>
    </tr>
  </tbody>
</table>
</div>



### Train our LightGBM Regression model


```python
model = LGBMRegressor(n_estimators=500) 
model.fit(X_train, y_train)
```

#### Check the training MAPE (Mean Absolute Percentage Error) of our model


```python
preds = abs(model.predict(X_train))
mae_train = metrics.mean_absolute_error(y_train, preds)
print(f"Training Mean Percentage Error: {mae_train:.2f} seconds")
mape_train = metrics.mean_absolute_percentage_error(y_train, preds)
print(f"Training Mean Absolute Percentage Error: {mape_train*100:.2f} %")
```

    Training Mean Percentage Error: 421.72 seconds
    Training Mean Absolute Percentage Error: 74.38 %


### Defining Monitors over test data using the UpTrain Framework

Next, we define monitors over our ML model in test/production with UpTrain.

#### Accuracy monitors
We define Mean Absolute Error (MAE) and Mean Absolute Percentage Error (MAPE) accuracy monitors for our regression task


```python
# To monitor MAE
mae_monitor = {       
    "type": uptrain.Monitor.ACCURACY,
    "measurable_args": {
        'type': uptrain.MeasurableType.MAE,
    },
}

# To monitor  (MAPE)
mape_monitor = {
    "type": uptrain.Monitor.ACCURACY,
    "measurable_args": {
        'type': uptrain.MeasurableType.MAPE,
    },
}
```

#### SHAP explanability
SHAP (SHapley Additive exPlanations) is a game theoretic approach to explain the ML model predictions and it available as a [python package](https://github.com/slundberg/shap). Through UpTrain dashboard, we will use SHAP to explain our model's preditions.


```python
# To visualize the SHAP explanability in dashboard
shap_visual = {
    "type": uptrain.Visual.SHAP,
    "model": model,
    # Limit the number of points for which SHAP values are calculated to reduce runtime.
    "shap_num_points": 10000,
    # Tell the framework the column name that corresponds to data-point id
    "id_col": "id"
}
```

#### Data integrity monitor
We can also define data integrity checks over our test data. One obvious check is that the number of passengers should >= 1.


```python
# Data integrity monitor to check if feature 'pasenger_count' is >=1
data_integrity_monitor =  {
    "type": uptrain.Monitor.DATA_INTEGRITY,
    "measurable_args": {
        'type': uptrain.MeasurableType.INPUT_FEATURE,
        'feature_name': 'passenger_count'
    },
    "integrity_type": "greater_than",
    "threshold": 1
}
```

### Define the checks in config and pass it to the UpTrain framework


```python
cfg = {
    "checks": [mae_monitor, mape_monitor, data_integrity_monitor, shap_visual],
    "logging_args": {"st_logging": True},
}
framework = uptrain.Framework(cfg_dict=cfg)
```


### Launch the model in Production


```python
batch_size = 2000
cols = list(X_test.columns)
for idx in range(int(len(X_test)/batch_size)):
    
    indices = range(idx*batch_size, (idx+1)*batch_size)
    this_elems = X_test.iloc[idx*batch_size: (idx+1)*batch_size, :]
    this_preds = abs(model.predict(this_elems))
    
    # Add ids to corresponding data points to preserve them in dashboard
    this_elems = this_elems.assign(id=list(test_ids[idx*batch_size: (idx+1)*batch_size]))
    
    # Log input and outputs to the UpTrain framework
    ids = framework.log(inputs=this_elems, outputs=this_preds)
    
    # Attach ground truth
    ground_truth = list(y_test[idx*batch_size: (idx+1)*batch_size])
    framework.log(identifiers=ids, gts=ground_truth)

```

    


### SHAP Explanability at the UpTrain Dashboard

As we can notice from the dashboard, we get two plots for SHAP explainability. The plot on the left is the average weight of each feature. As expected, the feature "dist" (that represents the distance of the trip) has the biggest impact on the trip duration prediction. Moreover, pickup hour and taxi vendor id also somewhat affect the trip duration. 

On the right, we can see how the model arrives at the prediction for any data-point (in this case ID `id1787379`). Due to the low distance of the trip, the feature "dist" contributed `-256.06` to the overall trip duration. 

<img src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/shap_featurewise.png" width="450"/> <img src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/shap_datapoint.png" width="410"/> 

### Demo Video: SHAP explainability
We have added a small illustration on how it looks at the UpTrain dashboard below.

![gif](https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/4_Explanability_recording.gif)

### MAE and MAPE Accuracy

The following is how the MAE and MAPE accuracies are evolving with time on the UpTrain dashboard.

<img src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/mae.gif" width="400"/> <img src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/mape.gif" width="400"/> 

### Data Integrity
We added a data integrity check for feature passenger_count >=1. We observe that data integrity is maintained through the test dataset (as data integrity is close to one)


<img src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/data_integrity_passenger_count.png" width="500"/>
