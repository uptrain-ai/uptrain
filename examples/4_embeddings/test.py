import pandas as pd
from datetime import datetime

df = pd.read_csv("sample_data_oodles.csv")
df = df[df["ffm_type"] == "realtime"]
df = df.drop_duplicates(subset=df.columns.tolist())
df = df.sort_values(by=["postId", "time"])
df = df.drop(['Unnamed: 0'], axis=1)

import uptrain

cfg = {
    "checks": [{
        'type': uptrain.Anomaly.AGGREGATE,
        'aggregate_args': {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'postId'
        },
        "measurable_args": {
            'type': uptrain.MeasurableType.COSINE_DISTANCE,
            'base': {
                'type': uptrain.MeasurableType.INPUT_FEATURE,
                'feature_name': 'embs'
            },
            'reference': "running_diff"
        },
    }],
    "training_args": {
        "fold_name": "uptrain_smart_data"
    },
    "tb_logging": True
}
framework = uptrain.Framework(cfg_dict=cfg)

for i in range(len(df)):
    row = dict(df.iloc[i])
    row['embs'] = eval(row['embs'])
    row['creation_time'] = datetime.strptime(row['creation_time'], "%Y-%m-%d %H:%M:%S UTC")
    row['time'] = datetime.strptime(row['time'], "%Y-%m-%d %H:%M:%S+00")
    for k in list(row.keys()):
        row[k] = [row[k]]


    # Do model prediction
    inputs = {'data': row}
    idens = framework.log(inputs=inputs)

    # Retrain only once
    if framework.version > 1:
        break
