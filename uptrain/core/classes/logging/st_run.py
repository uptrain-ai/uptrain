from glob import glob
import os
import sys
import json
import random

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

from uptrain.core.lib.helper_funcs import make_dir_friendly_name


# -----------------------------------------------------------
# Read parameters for this run
# -----------------------------------------------------------


def read_config(log_folder: str):
    """read the uptrain configuration for this run"""
    config_file = os.path.join(log_folder, "config.json")
    with open(config_file, encoding="utf-8") as f:
        return json.loads(f.read())


CONFIG = read_config(sys.argv[1])


# -----------------------------------------------------------
# Plotting routines
# -----------------------------------------------------------


def make_plotly_figure(
    y_axis: str, x_axis: str = "Num predictions", x_log=False, y_log=False
):
    fig = go.Figure()
    fig.update_xaxes(title_text=x_axis)
    fig.update_yaxes(title_text=y_axis)
    if x_log:
        fig.update_xaxes(type="log")
    if y_log:
        fig.update_yaxes(type="log")
    return fig


def slice_dataset():
    pass


def get_logfile_addr_for_check(check: dict, distance_type: str) -> str:
    """get the path to the log file for the dashboard.

    TODO: this logic should be defined on the actual Check objects
    """
    log_folder = sys.argv[1]
    # TODO: this is true for statistic metrics, for the rest?
    dashboard_name = check["type"]
    plot_name = make_dir_friendly_name(
        distance_type
        if "reference" not in check
        else distance_type + "_" + check["reference"]
    )

    dashboard_name = make_dir_friendly_name(dashboard_name)
    plot_name = make_dir_friendly_name(plot_name)
    return os.path.join(log_folder, dashboard_name, f"{plot_name}.csv")


def plot_dashboard(check: dict, model_variant: dict, feature_filters: dict):
    for dist_type in check["distance_types"]:
        df = pd.read_csv(get_logfile_addr_for_check(check, dist_type))
        list_conds = []
        for feature, value in feature_filters.items():
            list_conds.append(df[feature] == value)
        for k, v in model_variant.items():
            list_conds.append(df[k] == v)
        df = df[np.logical_and.reduce(list_conds)]

        if len(df) == 0:
            st.warning("No data found for the specified filters.")
        else:
            pass


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

if not len(CONFIG["checks"]):
    st.warning("No checks found in the logs configured.")
    st.stop()


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
    st.subheader("Pick a specific slices of the logs")
    for i, feature in enumerate(selected_check["feature_args"]):
        feature_name = feature["feature_name"]
        selected_value = st.sidebar.selectbox(
            feature_name, ["All", *feature["allowed_values"]]
        )
        if selected_value != "All":
            feature_filters.update({feature_name: selected_value})

    # Pick out model variants to plot for
    model_args = selected_check["model_args"]

    # select a model variant from the cartesian product of all model args
    model_variant = {}
    st.subheader("Select model variant")
    for i, model in enumerate(model_args):
        model_name = model["feature_name"]
        selected_value = st.sidebar.selectbox(model_name, model["allowed_values"])
        model_variant.update({model_name: selected_value})


plot_dashboard(selected_check, model_variant, feature_filters)


def plot_line_chart(df, y_axis, x_axis):
    col1, col2 = st.columns(2)
    with col1:
        x_log = st.checkbox("log x", help="x-axis in log-scale", key=plot_name + "x")
    with col2:
        y_log = st.checkbox("log y", help="y-axis in log-scale", key=plot_name + "y")

    cols = st.columns(2)
    fig = make_plotly_figure(y_axis, x_axis, x_log, y_log)
    fig = fig.add_trace(
        go.Scatter(
            x=df[x_axis],
            y=df[y_axis],
        )
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_histogram(files, plot_name):
    cols = st.columns(2)
    for j in range(num_models_compare):
        fig = go.Figure()
        for i, csv_file in enumerate(files):
            # Reading the csv file
            df = pd.read_csv(csv_file)
            df = slice_data(df, features_to_slice, model_to_compare, other_models, j)

            # Getting plot_id
            plot_id = os.path.split(csv_file)[-1].split(".")[0]
            df_y = df["y_points"]
            # if len(df_y) > 1000:
            # df_y = np.random.choice(df_y, 1000)
            fig = fig.add_trace(go.Histogram(x=df_y, name=plot_id))

        with cols[j % 2]:
            if model_to_compare is not None:
                model_name = model_to_compare["allowed_values"][j]
                st.subheader(f"Model: {model_name}")
            st.plotly_chart(fig, use_container_width=True)


def plot_histogram(file):
    with open(file, encoding="utf-8") as f:
        data = json.loads(f.read())
    if isinstance(data, dict):
        fig = go.Figure()
        for key in data.keys():
            fig = fig.add_trace(go.Histogram(x=data[key], name=key))
    else:
        fig = go.Figure(data=[go.Histogram(x=data)])
    st.plotly_chart(fig)


def plot_bar(file):
    with open(file, encoding="utf-8") as f:
        data = json.loads(f.read())
    fig = go.Figure()
    for bar_name in data:
        if bar_name == "hover_text":
            continue
        bar_dict = data[bar_name]
        keys, values = zip(*bar_dict.items())
        if "hover_text" in data:
            hover_text = data["hover_text"][bar_name]
        else:
            hover_text = {}
        hover_text = list(hover_text.values())
        fig = fig.add_trace(
            go.Bar(x=list(keys), y=list(values), name=bar_name, hovertext=hover_text)
        )
    st.plotly_chart(fig)


def plot_for_count(files, plot_func, plot_name):
    for file in files:
        count = os.path.split(file)[-1].split(".")[0]
        if int(count) < 0:
            plot_func(file)
        else:
            if st.checkbox(f"For count {count}", key=plot_name + str(count)):
                plot_func(file)


def plot_dashboard(dashboard_name):
    st.header(f"Dashboard {dashboard_name}")
    sub_dirs = [path[0] for path in os.walk(os.path.join(log_folder, dashboard_name))]
    for sub_dir in sub_dirs:
        sub_dir_split = os.path.normpath(sub_dir).split(os.path.sep)
        c1 = sub_dir_split[-1] == "UMAP"
        c2 = sub_dir_split[-2] == "bar_graphs"
        c3 = sub_dir_split[-1] == "alerts"
        c4 = sub_dir_split[-1] == "t_SNE"
        if c1 or c2 or c3 or c4:
            ext = "*.json"
        else:
            ext = "*.csv"

        # Getting the list of relevant files in streamlit logs
        files = [
            file
            for path, _, _ in os.walk(sub_dir)
            for file in glob(os.path.join(path, ext))
        ]
        plot_name = sub_dir_split[-1]

        ######### Showing Alerts ###########

        if sub_dir_split[-1] == "alerts":
            for file in files:
                alert_name = os.path.split(file)[-1].split(".")[0]
                f = open(file)
                alert = json.load(f)
                st.subheader(alert_name)
                st.markdown("##### " + alert)
                st.markdown("""---""")

        ######### Line Plots ###########

        elif sub_dir_split[-2] == "line_plots":
            if st.sidebar.checkbox(
                f"Line-plot for {plot_name}", key=plot_name + dashboard_name
            ):
                st.markdown(f"### Line chart for {plot_name}")
                plot_line_charts(files, plot_name)
                st.markdown("""---""")

        # ######### Plotting histograms ###########

        elif sub_dir_split[-2] == "histograms":
            if plot_name == "UMAP":
                if st.sidebar.checkbox(f"UMAP plot"):
                    st.markdown(f"### UMAP plot")
                    if model_args is not None:
                        plot_umaps(files, plot_name, sub_dir)
                    else:
                        for file in files:
                            plot_umap(file)
                    st.markdown("""---""")
            elif plot_name == "t_SNE":
                if st.sidebar.checkbox(f"t-SNE plot"):
                    st.markdown(f"### t-SNE plot")
                    if model_args is not None:
                        plot_umaps(files, plot_name, sub_dir)
                    else:
                        for file in files:
                            plot_umap(file)
                    st.markdown("""---""")
            else:
                if st.sidebar.checkbox(f"Histogram for {plot_name}"):
                    st.markdown(f"### Histogram for {plot_name}")
                    # plot_for_count(files, plot_histogram, plot_name)
                    plot_histograms(files, plot_name)
                    st.markdown("""---""")

        ######### Plotting Bar Graphs ###########

        elif sub_dir_split[-2] == "bar_graphs":
            if st.sidebar.checkbox(f"Bar graph for {plot_name}"):
                st.markdown(f"### Bar graph for {plot_name}")
                plot_for_count(files, plot_bar, plot_name)
                st.markdown("""---""")

        ######### Plotting Images ###########

        # elif sub_dir_split[-1] == "images":
        if True:
            png_files = [
                file
                for path, _, _ in os.walk(sub_dir)
                for file in glob(os.path.join(path, "*.png"))
            ]
            for i, png_file in enumerate(png_files):
                # Getting image name
                image_name = png_file.split("/")[-1].split(".")[0]
                st.subheader(image_name)
                st.image(png_file)
