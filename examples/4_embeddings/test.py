import pandas as pd
from datetime import datetime

df = pd.read_csv("sample_data_oodles.csv")
df = df[df["ffm_type"] == "realtime"]
df = df.drop_duplicates(subset=df.columns.tolist())
df = df.sort_values(by=["postId", "time"])
df = df.drop(['Unnamed: 0'], axis=1)

import uptrain

cfg = {
    "checks": [
    # {
    #     'type': uptrain.Anomaly.AGGREGATE,
    #     'aggregate_args': {
    #         'type': uptrain.MeasurableType.INPUT_FEATURE,
    #         'feature_name': 'postId'
    #     },
    #     "measurable_args": {
    #         'type': uptrain.MeasurableType.INPUT_FEATURE,
    #         'feature_name': 'embs'
    #     },
    #     'reference': "initial",
    #     "distance_types": ["cosine_distance", "norm_ratio", "l2_distance"],
    # },
    # {
    #     'type': uptrain.Anomaly.AGGREGATE,
    #     'aggregate_args': {
    #         'type': uptrain.MeasurableType.INPUT_FEATURE,
    #         'feature_name': 'postId'
    #     },
    #     "measurable_args": {
    #         'type': uptrain.MeasurableType.INPUT_FEATURE,
    #         'feature_name': 'embs'
    #     },
    #     'reference': "running_diff",
    #     "distance_types": ["cosine_distance", "norm_ratio", "l2_distance"],
    # },
    {
        'type': uptrain.Anomaly.DISTRIBUTION_STATS,
        'aggregate_args': {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'postId'
        },
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'embs'
        },
        "distance_types": ["cosine_distance", "l2_distance"],
        'count_checkpoints': [0, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 500000, 1000000]
    },
    {
        'type': uptrain.Anomaly.CONVERGENCE_STATS,
        'aggregate_args': {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'postId'
        },
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'embs'
        },
        'reference': "running_diff",
        "distance_types": ["cosine_distance", "norm_ratio", "l2_distance"],
        'count_checkpoints': [0, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 500000, 1000000]
    },
    {
        'type': uptrain.Anomaly.CONVERGENCE_STATS,
        'aggregate_args': {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'postId'
        },
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'embs'
        },
        'reference': "initial",
        "distance_types": ["cosine_distance", "norm_ratio", "l2_distance"],
        'count_checkpoints': [0, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 500000, 1000000]
    }
    ],
    "training_args": {
        "fold_name": "uptrain_smart_data"
    },
    "tb_logging": True,
    "use_cache": True
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

    if i == 10000:
        distribution_anomaly = list(filter(lambda x: x.anomaly_type == uptrain.Anomaly.DISTRIBUTION_STATS, framework.anomaly_manager.anomalies_to_check))[0]
        feats_to_cluster = []
        for count in [0, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 500000, 1000000]:
            feats_to_cluster.append(distribution_anomaly.get_feats_for_clustering(count))

    # Retrain only once
    if framework.version > 1:
        break
