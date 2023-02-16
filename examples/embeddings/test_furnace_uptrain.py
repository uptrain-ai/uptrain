import uptrain
import pandas as pd
import numpy as np


def clean_df(df):
    print("Originial length", len(df))
    df["views"] = df["views"].fillna(0)
    # df = df[df['sig_type'] == 'vplay']
    df = df.drop_duplicates(subset=df.columns.tolist())
    print("After dropping duplicates", len(df))
    df = df.drop(['Unnamed: 0', 'post_valid'], axis=1)
    return df

df = pd.read_csv("sample_data500.csv")
df = clean_df(df)
print(f"Total Entries: {len(df)}, Unique Posts: {len(np.unique(df['postId']))}")
# import pdb; pdb.set_trace() 

views_checkpoints = [0, 200, 500, 1000, 5000, 20000]
aggregate_args = {
    'type': uptrain.MeasurableType.INPUT_FEATURE,
    'feature_name': 'postId'
}
measurable_args = {
    'type': uptrain.MeasurableType.INPUT_FEATURE,
    'feature_name': 'embs'
}
count_args = {
    'type': uptrain.MeasurableType.INPUT_FEATURE,
    'feature_name': 'views',
    'dtype': int
}
model_args_ffm_type = {
    'type': uptrain.MeasurableType.INPUT_FEATURE,
    'feature_name': 'ffm_type',
    'allowed_values': ['batch', 'realtime']
}
model_args_sig_type = {
    'type': uptrain.MeasurableType.INPUT_FEATURE,
    'feature_name': 'sig_type',
    'allowed_values': ['fav', 'like', 'share', 'vclick', 'vplay', 'vskip', 'unified']
}
feature_args_genre = {
    'type': uptrain.MeasurableType.INPUT_FEATURE,
    'feature_name': 'tagGenre'
}

cfg = {
    "checks": [
    # Check the distance of feature_name
    {
        'type': uptrain.Statistic.DISTANCE,
        'aggregate_args': aggregate_args,
        "measurable_args": measurable_args,
        "count_args": count_args,
        "model_args": [model_args_ffm_type, model_args_sig_type],
        "feature_args": [feature_args_genre],
        'reference': "initial",
        "distance_types": ["cosine_distance"],
    },
    {
        'type': uptrain.Statistic.DISTANCE,
        'aggregate_args': aggregate_args,
        "measurable_args": measurable_args,
        "count_args": count_args,
        "model_args": [model_args_ffm_type, model_args_sig_type],
        "feature_args": [feature_args_genre],
        'reference': "running_diff",
        "distance_types": ["cosine_distance"],
    },
    {
        'type': uptrain.Statistic.DISTRIBUTION_STATS,
        'aggregate_args': aggregate_args,
        "measurable_args": measurable_args,
        "count_args": count_args,
        "model_args": [model_args_ffm_type, model_args_sig_type],
        "feature_args": [feature_args_genre],
        "distance_types": ["norm_ratio", "cosine_distance"],
        'count_checkpoints': views_checkpoints,
    },
    {
        'type': uptrain.Statistic.CONVERGENCE_STATS,
        'aggregate_args': aggregate_args,
        "measurable_args": measurable_args,
        "count_args": count_args,
        "model_args": [model_args_ffm_type, model_args_sig_type],
        "feature_args": [feature_args_genre],
        'reference': "running_diff",
        "distance_types": ["cosine_distance", "norm_ratio"],
        'count_checkpoints': views_checkpoints,
    },
    {
        'type': uptrain.Statistic.CONVERGENCE_STATS,
        'aggregate_args': aggregate_args,
        "measurable_args": measurable_args,
        "count_args": count_args,
        "model_args": [model_args_ffm_type, model_args_sig_type],
        "feature_args": [feature_args_genre],
        'reference': "initial",
        "distance_types": ["cosine_distance", "norm_ratio"],
        'count_checkpoints': views_checkpoints,
    },
    {
        'type': uptrain.Visual.UMAP,
        'aggregate_args': aggregate_args,
        "measurable_args": measurable_args,
        "model_args": [model_args_ffm_type, model_args_sig_type],        
        'count_checkpoints': views_checkpoints,
        'min_dist': 0.1,
        'n_neighbors': 2,
        'metric_umap': 'cosine',
        'dim': '3D',
        'min_samples': 5,
        'eps': 2.0,
    },
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
