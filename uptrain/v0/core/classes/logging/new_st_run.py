import os
import sys
import json
import random

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

from uptrain.v0.core.lib.helper_funcs import make_dir_friendly_name

# -----------------------------------------------------------
# Set up layout of the dashboard and the sidebar
# -----------------------------------------------------------

st.set_page_config(
    page_title="UpTrain Dashboard",
    layout="wide",
    page_icon="https://github.com/uptrain-ai/uptrain/raw/dashboard/uptrain/core/classes/logging/uptrain_logo_icon.png",
)
st.title("UpTrain Live Dashboard")
st_style = """<style> footer {visibility: hidden;} </style>"""
st.markdown(st_style, unsafe_allow_html=True)


# -----------------------------------------------------------
# Read parameters for this run
# -----------------------------------------------------------


def read_config(log_folder: str):
    """read the uptrain configuration for this run"""
    config_file = os.path.join(log_folder, "config.json")
    with open(config_file, encoding="utf-8") as f:
        return json.loads(f.read())


INPUT_LOG_FOLDER = sys.argv[1]
LOG_FOLDER = INPUT_LOG_FOLDER  # for partitioned datasets, this could be a subdirectory of INPUT_LOG_FOLDER

if "config.json" in os.listdir(INPUT_LOG_FOLDER):
    CONFIG = read_config(INPUT_LOG_FOLDER)
else:
    print(
        f"Could not find an Uptrain config at {INPUT_LOG_FOLDER}. Looking into sub-dirs."
    )
    all_sub_dirs = [
        os.path.join(INPUT_LOG_FOLDER, d) for d in os.listdir(INPUT_LOG_FOLDER)
    ]
    valid_sub_dirs = [
        d for d in all_sub_dirs if os.path.isdir(d) and "config.json" in os.listdir(d)
    ]
    if not len(valid_sub_dirs):
        st.warning("No uptrain config found. Please check the log folder.")
        st.stop()
    else:
        with st.sidebar:
            st.subheader("Select the dataset partition to analyze")
            LOG_FOLDER = st.selectbox(
                "Partition",
                [""] + valid_sub_dirs,
                format_func=lambda x: x.split("/")[-1],
            )
        if LOG_FOLDER == "":
            st.stop()
        else:
            assert LOG_FOLDER is not None
            CONFIG = read_config(LOG_FOLDER)

# verify there are checks in the config
if not len(CONFIG["checks"]):
    st.warning("No checks found in the logs configured.")
    st.stop()

# -----------------------------------------------------------
# Plotting routines
# -----------------------------------------------------------


def get_plotname_n_file_for_statistic(
    check: dict, distance_type: str
) -> tuple[str, str]:
    """get the path to the log file for the dashboard.

    TODO: this logic should be defined on the actual Check objects. This only works for Statistics.
    """
    dashboard_name = make_dir_friendly_name(check["type"])
    plot_name = make_dir_friendly_name(
        distance_type
        if "reference" not in check
        else "_".join([distance_type, check["reference"]])
    )

    return (
        f"{dashboard_name} - {plot_name}",
        os.path.join(LOG_FOLDER, dashboard_name, f"{plot_name}.csv"),
    )


def apply_model_n_feature_filters(
    df: pd.DataFrame, model_variant: dict, feature_filters: dict
) -> pd.DataFrame:
    list_conds = []
    for feature, value in feature_filters.items():
        list_conds.append(df[feature] == value)
    for k, v in model_variant.items():
        list_conds.append(df[k] == v)
    return df[np.logical_and.reduce(list_conds)]


def plot_check_distance(check: dict, model_variant: dict, feature_filters: dict):
    x_log = st.checkbox(
        "log x", help="See x-axes in log-scale", key=check["type"] + "log_x"
    )
    for dist_type in check["distance_types"]:
        plot_title, fname = get_plotname_n_file_for_statistic(check, dist_type)
        st.markdown(f"### Line chart for {plot_title}")

        if os.path.getsize(fname) == 0:
            st.warning("No data found for the specified check.")
            return
        else:
            df = pd.read_csv(fname)

        df = apply_model_n_feature_filters(df, model_variant, feature_filters)
        if len(df) == 0:
            st.warning("No data found for the specified filters.")
            return

        grouping_col = check["aggregate_args"]["feature_name"]
        xaxis = check["count_args"]["feature_name"]
        yaxis = "check"

        if df[grouping_col].nunique() > 1000:
            # pick 1000 random values
            unique_values = df[grouping_col].unique()
            random.seed(42)
            random.shuffle(unique_values)
            df = df[df[grouping_col].isin(unique_values[:1000])]

        df[grouping_col] = df[grouping_col].astype(str)
        fig = px.line(df, x=xaxis, y=yaxis, color=grouping_col, log_x=x_log)
        st.plotly_chart(fig, use_container_width=True)


def plot_check_convergence(check: dict, model_variant: dict, feature_filters: dict):
    for dist_type in check["distance_types"]:
        plot_title, fname = get_plotname_n_file_for_statistic(check, dist_type)
        st.markdown(f"### Histogram for {plot_title}")

        if os.path.getsize(fname) == 0:
            st.warning("No data found for the specified check.")
            return
        else:
            df = pd.read_csv(fname)

        df = apply_model_n_feature_filters(df, model_variant, feature_filters)
        if len(df) == 0:
            st.warning("No data found for the specified filters.")
            return

        grouping_col = check["count_args"]["feature_name"]
        value_col = "check"
        df[grouping_col] = df[grouping_col].astype(str)
        fig = px.histogram(df, x=value_col, color=grouping_col)
        st.plotly_chart(fig, use_container_width=True)


def plot_visual_umap(check: dict, model_variant: dict, feature_filters: dict):
    dashboard_name = make_dir_friendly_name(check.get("dashboard_name", "visual"))
    plot_name = make_dir_friendly_name(check["type"])
    fname = os.path.join(sys.argv[1], dashboard_name, f"{plot_name}.json")

    plot_title = f"{dashboard_name} - {plot_name}"
    st.markdown(f"### {plot_title}")
    with open(fname, encoding="utf-8") as f:
        all_data = [json.loads(line) for line in f.readlines()]

    data = None
    for row in all_data:
        valid_model = all(
            row[model_arg] == model_variant[model_arg] for model_arg in model_variant
        )
        valid_features = all(
            row[feature_arg] == feature_filters[feature_arg]
            for feature_arg in feature_filters
        )
        if valid_model and valid_features:
            data = row
            break

    if data is None:
        st.warning("No data found for the specified filters.")
        st.stop()

    arr = np.array(data["umap"])
    labels_dict = data["labels"]
    color_type = st.selectbox("Select coloring type", labels_dict.keys())
    x = arr[:, 0]
    y = arr[:, 1]
    dictn = {"x": x, "y": y, "color": np.array(labels_dict[color_type])}
    if arr.shape[1] == 3:
        dictn.update({"z": arr[:, 2]})

    hover_data = []
    if "hover_texts" in data:
        dictn.update({"hover": data["hover_texts"]})
        if len(data["hover_texts"]):
            hover_data = list(data["hover_texts"][0].keys())

    for key in data.keys():
        if key not in ["umap", "labels", "hover_texts"]:
            dictn.update({key: data[key]})
    df = pd.DataFrame(dictn)

    if "hover" in list(df.columns):
        hover_df = pd.DataFrame(list(df["hover"]))
        for key in hover_data:
            if key not in hover_df.columns:
                df[key] = [""] * len(hover_df)
            else:
                df[key] = pd.Series(hover_df[key]).fillna("").tolist()
    else:
        hover_df = pd.DataFrame()

    if arr.shape[1] == 2:
        fig = px.scatter(df, x="x", y="y", color="color", hover_data=hover_data)
    elif arr.shape[1] == 3:
        z = list(df["z"])
        fig = px.scatter_3d(
            df, x="x", y="y", z="z", color="color", hover_data=hover_data
        )
    else:
        raise Exception("Umap dimension not 2D or 3D")
    st.plotly_chart(fig, use_container_width=True)


def plot_dashboard(check: dict, model_variant: dict, feature_filters: dict):
    if check["type"] == "distance":
        plot_check_distance(check, model_variant, feature_filters)
    elif check["type"] == "convergence_stats":
        plot_check_convergence(check, model_variant, feature_filters)
    elif check["type"] in ("UMAP", "t-SNE"):
        plot_visual_umap(check, model_variant, feature_filters)
    else:
        st.warning(f"Checks of type: {check['type']} are not supported yet.")


# -----------------------------------------------------------
# Create a sidebar for the user to specify what they wanna see
# -----------------------------------------------------------

with st.sidebar:
    st.subheader("Select the dashboard to view")
    selected_check = st.radio(
        "Checks",
        options=CONFIG["checks"],
        format_func=lambda x: str(x["type"]),
    )
    st.markdown("---")
    assert selected_check is not None

    # Work with a specific slice of the data
    feature_filters = {}
    if "feature_args" in selected_check:
        st.subheader("Pick a specific slice of the logged data")
        for i, feature in enumerate(selected_check["feature_args"]):
            feature_name = feature["feature_name"]
            selected_value = st.sidebar.selectbox(
                feature_name, ["All", *feature["allowed_values"]]
            )
            if selected_value != "All":
                feature_filters.update({feature_name: selected_value})

    # select a model variant from the cartesian product of all model args
    model_variant = {}
    if "model_args" in selected_check:
        st.subheader("Select model variant")
        for i, model in enumerate(selected_check["model_args"]):
            model_name = model["feature_name"]
            selected_value = st.sidebar.selectbox(model_name, model["allowed_values"])
            model_variant.update({model_name: selected_value})


plot_dashboard(selected_check, model_variant, feature_filters)
