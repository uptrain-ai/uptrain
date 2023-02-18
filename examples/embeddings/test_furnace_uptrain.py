import uptrain
import pandas as pd
import numpy as np
import datetime

def clean_df(df):
    print("Originial length", len(df))
    df["views"] = df["views"].fillna(0)
    df = df.drop_duplicates(subset=df.columns.tolist())
    print("After dropping duplicates", len(df))
    return df

df = pd.read_csv("sample_data_vplay_small.csv")
df = clean_df(df)
print(f"Total Entries: {len(df)}, Unique Posts: {len(np.unique(df['postId']))}")
print(np.unique(np.array(df['ffm_type'].tolist()),return_counts=True))

t1 = datetime.datetime.utcnow()

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
    'feature_name': 'tagGenre',
    'allowed_values': ['AGT', 'Arts (self perform)', 'Cinema & TV', 
    'Culture (Nation/state/dialects)', 'Devotion', 'Education',
    'Fashion and Makeup', 'Humour & Fun', 'Kids', 'LifeStyle',
    'Literature', 'Music & Dance', 'News', 'Personal',
    'Romance & Relationships', 'Sports', 'Status and Stories',
    'Wellbeing', 'Wishes']
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
        "distance_types": ["cosine_distance", "norm_ratio", "l2_distance"],
    },
    {
        'type': uptrain.Statistic.DISTRIBUTION_STATS,
        'aggregate_args': aggregate_args,
        "measurable_args": measurable_args,
        "count_args": count_args,
        "model_args": [model_args_ffm_type, model_args_sig_type],
        "feature_args": [feature_args_genre],
        "distance_types": ["cosine_distance"],
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
        "distance_types": ["cosine_distance", "norm_ratio", "l2_distance"],
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
        "distance_types": ["cosine_distance", "norm_ratio", "l2_distance"],
        'count_checkpoints': views_checkpoints,
    },
    {
        'type': uptrain.Visual.UMAP,
        'aggregate_args': aggregate_args,
        "measurable_args": measurable_args,
        "model_args": [model_args_ffm_type, model_args_sig_type],        
        'count_checkpoints': views_checkpoints,
        'min_dist': 0,
        'n_neighbors': 5,
        'metric_umap': 'cosine',
        'dim': '2D', # Use '2D' or '3D'
        'clustering': False, # Set True for DBSCAN clustering
        'feature_name': 'tagGenre', # Feature with which clusters are labeled
    },
    ],
    "training_args": {
        "fold_name": "uptrain_smart_data"
    },
    "st_logging": True,
    "use_cache": True
}
framework = uptrain.Framework(cfg_dict=cfg)

batch_size = min(100, len(df))
cols = ['ffm_type', 'postId', 'embs', 'tagGenre', 'views', 'sig_type']
for idx in range(int(len(df)/batch_size)):
    t_s = datetime.datetime.utcnow()
    this_elems = df[idx*batch_size: (idx+1)*batch_size]
    dictn = {}
    for col in cols:
        dictn.update({col: list(this_elems[col])})
        if col == 'embs':
            dictn[col] = [eval(x) for x in dictn[col]]
    inputs = {'data': dictn}
    idens = framework.log(inputs=inputs)
    t_f = datetime.datetime.utcnow()
    print(idx*batch_size, (t_f-t_s).total_seconds())

print("Done")
t2 = datetime.datetime.utcnow()
print([len(df), (t2-t1).total_seconds()/60, t1, t2])