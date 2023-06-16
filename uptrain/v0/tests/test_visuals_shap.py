import time
import uptrain.v0 as v0
import matplotlib
import pandas as pd

from sklearn import model_selection
from lightgbm import LGBMRegressor
from test_helpers import download_dataset, process

matplotlib.use("TkAgg")

data_file = "trip_duration_dataset.csv"
download_dataset(data_file)
df_train = pd.read_csv(data_file)

# Divide the data into input data to the model and targets
y = df_train["trip_duration"]
X = df_train.drop(["trip_duration"], axis=1)

# Divide data into train-test splits
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.1)

# Get ids for data to locate them with their ids in the UpTrain dashboard
test_ids = list(X_test["id"])

# Clean up data
X_train = process(X_train)
X_test = process(X_test)

# Train the model
model = LGBMRegressor(n_estimators=500)
model.fit(X_train, y_train)

# Create a shap visualization
shap_visual = {
    "type": v0.Visual.SHAP,
    "model": model,
    "shap_num_points": 10000,
}

cfg = {
    "checks": [shap_visual],
    "logging_args": {"st_logging": True},
}

framework = v0.Framework(cfg_dict=cfg)

batch_size = 2000
cols = list(X_test.columns)
for idx in range(int(len(X_test) / batch_size)):
    indices = range(idx * batch_size, (idx + 1) * batch_size)
    this_elems = X_test.iloc[idx * batch_size : (idx + 1) * batch_size, :]
    this_preds = abs(model.predict(this_elems))

    # Add ids to corresponding data points to preserve them in dashboard
    this_elems = this_elems.assign(
        id=list(test_ids[idx * batch_size : (idx + 1) * batch_size])
    )

    # Log input and outputs to the UpTrain framework
    ids = framework.log(inputs=this_elems, outputs=this_preds)

    # Attach ground truth
    ground_truth = list(y_test[idx * batch_size : (idx + 1) * batch_size])
    framework.log(identifiers=ids, gts=ground_truth)

    time.sleep(0.01)
