import streamlit as st
import pandas as pd
from glob import glob
import os
import sys
import plotly.graph_objects as go
import numpy as np
import json
import plotly.express as px


st.set_page_config(
    page_title="UpTrain AI Dashboard",
    layout="wide",
    page_icon='https://github.com/uptrain-ai/uptrain/raw/dashboard/uptrain/core/classes/logging/uptrain_logo_icon.png'
)
st.title("UpTrain AI Live Dashboard")
st_style = """<style> footer {visibility: hidden;} </style>"""
st.markdown(st_style, unsafe_allow_html=True)

model_sig_types = ['vplay', 'unified', 'fav', 'like', 'share', 'vclick', 'vskip']

def return_plotly_fig(y_axis, x_axis="Num predictions", x_log=False, y_log=False):
    fig = go.Figure()
    fig.update_xaxes(title_text=x_axis)
    fig.update_yaxes(title_text=y_axis)
    if x_log:
        fig.update_xaxes(type="log")
    if y_log:
        fig.update_yaxes(type="log")
    return fig


def plot_line_charts(files, plot_name):
    # Getting plot metadata from the first file
    df = pd.read_csv(files[0])

    for key in df.keys():
        if key.startswith("x_"):
            x_axis = key
        if key.startswith("y_"):
            y_axis = key

    model_sig_type = st.selectbox("Select Signal Type", 
        model_sig_types, key=plot_name)

    col1, col2 = st.columns(2)
    with col1:
        x_log = st.checkbox(
            "log x", help="x-axis in log-scale", key=plot_name + "x"
        )
    with col2:
        y_log = st.checkbox(
            "log y", help="y-axis in log-scale", key=plot_name + "y"
        )
    
    fig = return_plotly_fig(y_axis, x_axis, x_log, y_log)
    cols = st.columns(2)
    for j,model_ffm_type in enumerate(['realtime', 'batch']):
        for i, csv_file in enumerate(files):
            # Reading the csv file
            df = pd.read_csv(csv_file)
            df = df[df['model_ffm_type'] == model_ffm_type]
            df = df[df['model_sig_type'] == model_sig_type]

            # Getting plot_id
            plot_id = csv_file.split("/")[-1].split(".")[0]
            fig = fig.add_trace(
                go.Scatter(
                    x=df[x_axis],
                    y=df[y_axis],
                    name=str(i) + ", " + plot_id,
                )
            )

        with cols[j]:
            st.subheader(f'Model: {model_ffm_type}')
            st.plotly_chart(fig, use_container_width=True)


def plot_histograms(files, plot_name):
    model_sig_type = st.selectbox("Select Signal Type", 
        model_sig_types, key=plot_name)
    
    fig = go.Figure()
    cols = st.columns(2)
    for j,model_ffm_type in enumerate(['realtime', 'batch']):
        for i, csv_file in enumerate(files):
            # Reading the csv file
            df = pd.read_csv(csv_file)
            df = df[df['model_ffm_type'] == model_ffm_type]
            df = df[df['model_sig_type'] == model_sig_type]

            # Getting plot_id
            plot_id = csv_file.split("/")[-1].split(".")[0]
            fig = fig.add_trace(go.Histogram(x=df["y_points"], name=plot_id))

        with cols[j]:
            st.subheader(f'Model: {model_ffm_type}')
            st.plotly_chart(fig, use_container_width=True)


def plot_histogram(file):
    with open(file, encoding='utf-8') as f:
        data = json.loads(f.read())
    if isinstance(data, dict):
        fig = go.Figure()
        for key in data.keys():
            fig = fig.add_trace(go.Histogram(x=data[key], name=key))
    else:
        fig = go.Figure(data=[go.Histogram(x=data)])
    st.plotly_chart(fig)


def plot_umap(file):
    with open(file, encoding='utf-8') as f:
        data = json.loads(f.read())
    arr = np.array(data["umap"])
    clusters = data["clusters"]
    x = arr[:, 0]
    y = arr[:, 1]
    if arr.shape[1] == 2:
        fig = px.scatter(x=x, y=y, color=clusters)
    elif arr.shape[1] == 3:
        z = arr[:, 2]
        fig = px.scatter_3d(x=x, y=y, z=z, color=clusters)
    else:
        raise ("Umap dimension not 2D or 3D.")
    st.plotly_chart(fig, use_container_width=True)
    st.write(
        f"Number of clusters: {len(set(clusters))}"
    )


def plot_umaps(files, plot_name, sub_dir):
    col1, col2 = st.columns(2)
    with col1:
        model_sig_type = st.selectbox("Signal Type", 
            model_sig_types, key=plot_name)
    with col2:
        view_arr = [0,200,500,1000,5000,20000]
        selected_count = st.selectbox(f"Cluster View Point", view_arr, key=plot_name+'count')
    # for file in files:
    #     file_name = file.split("/")[-1]
    #     count, model_ffm_type_file, model_sig_type_file = file_name.split("_")
    #     model_sig_type_file = model_sig_type_file.split(".")[0]
    #     cols = st.columns(2)
    #     for j,model_ffm_type in enumerate(['realtime', 'batch']):
    #         print("1", count, model_ffm_type_file, model_sig_type_file)
    #         print("2",selected_count, model_ffm_type, model_sig_type)
    #         if model_ffm_type_file==model_ffm_type:
    #             if selected_count == int(count):
    #                 if model_sig_type_file==model_sig_type:
    #                     with cols[j]:
    #                         st.subheader(f'Model: {model_ffm_type}, Count: {count}')
    #                         plot_umap(file) 
    cols = st.columns(2)
    for j,model_ffm_type in enumerate(['realtime', 'batch']):
        file_name = str(selected_count) + '_' + model_ffm_type + '_' + model_sig_type + '.json'
        file_name = sub_dir + '/' + file_name
        with cols[j]:
            st.subheader(f'Model: {model_ffm_type}, Signal: {model_sig_type}, Count: {selected_count}')
            if os.path.exists(file_name):
                plot_umap(file_name) 
            else:
                st.write("Not sufficient data.")


def plot_bar(file):
    with open(file, encoding='utf-8') as f:
        data = json.loads(f.read())
    fig = go.Figure()
    for bar_name in data:
        bar_dict = data[bar_name]
        keys, values = zip(*bar_dict.items())
        fig = fig.add_trace(
            go.Bar(
                x=list(keys),
                y=list(values),
                name=bar_name,
            )
        )
    st.plotly_chart(fig)


def plot_for_count(files, plot_func, plot_name):
    for file in files:
        count = file.split("/")[-1].split(".")[0]
        if int(count) < 0:
            plot_func(file) 
        else:
            if st.checkbox(f"For count {count}", key=plot_name+str(count)):
                plot_func(file)          


def plot_dashboard(dashboard_name):
    st.header(f"Dashboard {dashboard_name}")
    sub_dirs = [path[0] for path in os.walk(os.path.join(log_folder, dashboard_name))]
    for sub_dir in sub_dirs:
        sub_dir_split = sub_dir.split("/")
        if sub_dir_split[-1] == "umap_and_clusters":
            ext = "*.json"
        else:
            ext = "*.csv"

        # Getting the list of relevant files in streamlit logs
        files = [file for path, _, _ in os.walk(sub_dir)
                    for file in glob(os.path.join(path, ext))]
        plot_name = sub_dir_split[-1]

        ######### Showing Alerts ###########

        if sub_dir_split[-1] == "alerts":  
            for file in files:
                alert_name = file.split("/")[-1].split(".")[0]
                f = open(file)
                alert = json.load(f)
                st.subheader(alert_name)
                st.markdown("##### " + alert)
                st.markdown("""---""")

        ######### Line Plots ###########

        elif sub_dir_split[-2] == "line_plots":
            if st.sidebar.checkbox(f"Line-plot for {plot_name}", value=True):
                st.markdown(f"### Line chart for {plot_name}")
                plot_line_charts(files, plot_name)
                st.markdown("""---""")    

        ######### Plotting histograms ###########

        elif sub_dir_split[-2] == "histograms":
            if plot_name != "umap_and_clusters":
                if st.sidebar.checkbox(f"Histogram for {plot_name}", value=True):
                    st.markdown(f"### Histogram for {plot_name}")
                    # plot_for_count(files, plot_histogram, plot_name) 
                    plot_histograms(files, plot_name)
                    st.markdown("""---""") 
                            
            else:
                if st.sidebar.checkbox(f"UMAP for {plot_name}", value=True):
                    st.markdown(f"### UMAP for {plot_name}")
                    plot_umaps(files, plot_name, sub_dir)
                    st.markdown("""---""")   

        ######### Plotting Bar Graphs ###########

        elif sub_dir_split[-2] == "bar_graphs":
            if st.sidebar.checkbox(f"Bar graph for {plot_name}", value=True):
                st.markdown(f"### Bar graph for {plot_name}")
                plot_for_count(files, plot_bar, plot_name) 
                st.markdown("""---""")   


# Getting the streamlit log folder
log_folder = sys.argv[1]
st.sidebar.title("Select dashboards to view")
dashboard_names = next(os.walk(log_folder))[1]

for dashboard_name in dashboard_names:
    if st.sidebar.checkbox(f"Dashboard: {dashboard_name}"):
        plot_dashboard(dashboard_name)
    st.sidebar.markdown("""---""")