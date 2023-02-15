import uptrain
import pandas as pd
import numpy as np


def clean_df(df):
    print("Originial length", len(df))
    df["views"] = df["views"].fillna(0)
    df = df.drop_duplicates(subset=df.columns.tolist())
    print("After dropping duplicates", len(df))
    df = df.drop(['Unnamed: 0', 'post_valid'], axis=1)
    return df

# df = pd.read_csv("sample_data.csv")
# df = pd.read_csv("sample_data_unified.csv")
df = pd.read_csv("sample_data_unified_small.csv")
df = clean_df(df)
print(f"Total Entries: {len(df)}, Unique Posts: {len(np.unique(df['postId']))}")

views_checkpoints = [0, 200, 500, 1000, 5000, 20000]
cfg = {
    "checks": [
    # Check the distance of feature_name
    {
        'type': uptrain.Statistic.DISTANCE,
        'aggregate_args': {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'postId'
        },
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'embs'
        },
        "count_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'views',
            'dtype': int
        },
        # "model_args": {
        #     'type': uptrain.MeasurableType.INPUT_FEATURE,
        #     'feature_name': 'ffm_type',
        #     'allowed_values': ['batch', 'realtime']
        # },        
        "model_args": [{
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'sig_type',
            'allowed_values': ['fav', 'like', 'share', 'vclick', 'vplay', 'vskip', 'unified']
        },
        {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'ffm_type',
            'allowed_values': ['batch', 'realtime']
        }],        
        "feature_args": [{
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'tagGenre'
        }],
        'reference': "initial",
        "distance_types": ["norm_ratio", "l2_distance", "cosine_distance"],
    },
    {
        'type': uptrain.Statistic.DISTRIBUTION_STATS,
        'aggregate_args': {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'postId'
        },
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'embs'
        },
        "count_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'views',
            'dtype': int
        },
        # "model_args": {
        #     'type': uptrain.MeasurableType.INPUT_FEATURE,
        #     'feature_name': 'ffm_type',
        #     'allowed_values': ['batch', 'realtime']
        # },
        "model_args": [{
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'sig_type',
            'allowed_values': ['fav', 'like', 'share', 'vclick', 'vplay', 'vskip', 'unified']
        },
        {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'ffm_type',
            'allowed_values': ['batch', 'realtime']
        }],        
        "feature_args": [{
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'tagGenre'
        }],
        "distance_types": ["cosine_distance"],
        'count_checkpoints': views_checkpoints,
    },
    {
        'type': uptrain.Statistic.CONVERGENCE_STATS,
        'aggregate_args': {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'postId'
        },
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'embs'
        },
        "count_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'views',
            'dtype': int
        },
        # "model_args": {
        #     'type': uptrain.MeasurableType.INPUT_FEATURE,
        #     'feature_name': 'ffm_type',
        #     'allowed_values': ['batch', 'realtime']
        # },        
        "model_args": [{
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'sig_type',
            'allowed_values': ['fav', 'like', 'share', 'vclick', 'vplay', 'vskip', 'unified']
        },
        {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'ffm_type',
            'allowed_values': ['batch', 'realtime']
        }],        
        "feature_args": [{
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'tagGenre'
        }],
        'reference': "running_diff",
        "distance_types": ["cosine_distance", "norm_ratio"],
        'count_checkpoints': views_checkpoints,
    },
    {
        'type': uptrain.Statistic.CONVERGENCE_STATS,
        'aggregate_args': {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'postId'
        },
        "measurable_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'embs'
        },
        "count_args": {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'views',
            'dtype': int
        },
        # "model_args": {
        #     'type': uptrain.MeasurableType.INPUT_FEATURE,
        #     'feature_name': 'ffm_type',
        #     'allowed_values': ['batch', 'realtime']
        # },        
        "model_args": [{
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'sig_type',
            'allowed_values': ['fav', 'like', 'share', 'vclick', 'vplay', 'vskip', 'unified']
        },
        {
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'ffm_type',
            'allowed_values': ['batch', 'realtime']
        }],        
        "feature_args": [{
            'type': uptrain.MeasurableType.INPUT_FEATURE,
            'feature_name': 'tagGenre'
        }],
        'reference': "initial",
        "distance_types": ["cosine_distance", "norm_ratio"],
        'count_checkpoints': views_checkpoints,
    },
    # {
    #     'type': uptrain.Visual.UMAP,
    #     'aggregate_args': {
    #         'type': uptrain.MeasurableType.INPUT_FEATURE,
    #         'feature_name': 'postId'
    #     },
    #     "measurable_args": {
    #         'type': uptrain.MeasurableType.INPUT_FEATURE,
    #         'feature_name': 'embs'
    #     },
    #     'count_checkpoints': views_checkpoints,
    #     'min_dist': 0.1,
    #     'n_neighbors': 2,
    #     'metric_umap': 'cosine',
    #     'dim': '3D',
    #     'min_samples': 5,
    #     'eps': 2.0,
    # },
    ],
    "training_args": {
        "fold_name": "uptrain_smart_data"
    },
    "st_logging": True,
    "use_cache": True
}
framework = uptrain.Framework(cfg_dict=cfg)

batch_size = min(256*32, len(df))
cols = ['ffm_type', 'postId', 'embs', 'tagGenre', 'views', 'sig_type']
for idx in range(int(len(df)/batch_size)):
    this_elems = df[idx*batch_size: (idx+1)*batch_size]
    print(idx*batch_size)
    dictn = {}
    for col in cols:
        dictn.update({col: list(this_elems[col])})
        if col == 'embs':
            dictn[col] = [eval(x) for x in dictn[col]]
    inputs = {'data': dictn}
    idens = framework.log(inputs=inputs)

print("Done")
