import streamlit as st
import pandas as pd
from glob import glob
import os
import sys
import plotly.graph_objects as go
import numpy as np
import json
import plotly.express as px


def return_plotly_fig(y_axis, x_axis="Num predictions", x_log=False, y_log=False):
    fig = go.Figure()
    fig.update_xaxes(title_text=x_axis)
    fig.update_yaxes(title_text=y_axis)
    if x_log:
        fig.update_xaxes(type="log")
    if y_log:
        fig.update_yaxes(type="log")
    return fig


# Getting the streamlit log folder
log_folder = sys.argv[1]

st.set_page_config(
    page_title="UpTrain AI Dashboard",
    layout="wide",
    page_icon='https://github.com/uptrain-ai/uptrain/raw/dashboard/uptrain/core/classes/logging/uptrain_logo_icon.png'
)
st.title("UpTrain AI Live Dashboard")
st_style = """
            <style>
            footer {visibility: hidden;}
            </style>
           """
st.markdown(st_style, unsafe_allow_html=True)

sub_dirs = [path[0] for path in os.walk(log_folder)]
st.sidebar.title("Select dashboards to view")
for sub_dir in sub_dirs:
    sub_dir_split = sub_dir.split("/")

    ######### Line Plots ###########

    if sub_dir_split[-2] == "line_plots":
        plot_name = sub_dir_split[-1]

        if st.sidebar.checkbox(f"Line-plot for {plot_name}", value=True):
            st.markdown(f"### Line chart for {plot_name}")

            # Getting the list of all csv files in streamlit logs
            csv_files = [
                file
                for path, _, _ in os.walk(sub_dir)
                for file in glob(os.path.join(path, "*.csv"))
            ]

            scol1, scol2 = st.columns(2)
            with scol1:
                x_log = st.checkbox(
                    "log x", help="Plot x-axis in log-scale", key=plot_name + "x"
                )
            with scol2:
                y_log = st.checkbox(
                    "log y", help="Plot y-axis in log-scale", key=plot_name + "y"
                )
            fig = return_plotly_fig(plot_name, x_log=x_log, y_log=y_log)
            for i, csv_file in enumerate(csv_files):
                # Reading the csv file
                df = pd.read_csv(csv_file)

                # Getting plot_id
                plot_id = csv_file.split("/")[-1].split(".")[0]
                fig = fig.add_trace(
                    go.Scatter(
                        x=df["count"],
                        y=df[plot_id],
                        name=str(i) + ", " + plot_id,
                    )
                )
            st.plotly_chart(fig)
            st.markdown("""---""")    

        st.sidebar.markdown("""---""")

    ######### Plotting histograms ###########

    elif sub_dir_split[-2] == "histograms":
        plot_name = sub_dir_split[-1]

        if plot_name != "umap_and_clusters":
            if st.sidebar.checkbox(f"Histogram for {plot_name}", value=True):
                st.markdown(f"### Histogram for {plot_name}")

                # Getting the list of all files in streamlit logs
                files = [
                    file
                    for path, _, _ in os.walk(sub_dir)
                    for file in glob(os.path.join(path, "*.json"))
                ]

                for i, file in enumerate(files):
                    count = file.split("/")[-1].split(".")[0]
                    if int(count) < 0:
                        with open(file, encoding='utf-8') as f:
                            data = json.loads(f.read())
                        if isinstance(data, dict):
                            fig = go.Figure()
                            for key in data.keys():
                                fig = fig.add_trace(go.Histogram(x=data[key], name=key))
                        else:
                            fig = go.Figure(data=[go.Histogram(x=data)])
                        st.plotly_chart(fig)
                        st.markdown("""---""")   
                    else:
                        if st.checkbox(f"{plot_name} histogram for count {count}"):
                            f = open(file)
                            data = json.load(f)
                            fig = go.Figure(data=[go.Histogram(x=data, name=count)])
                            st.plotly_chart(fig)
                            st.markdown("""---""")   
                        
        else:
            if st.sidebar.checkbox(f"{plot_name}"):
                st.markdown(f"### {plot_name}")

                # Getting the list of all files in streamlit logs
                files = [
                    file
                    for path, _, _ in os.walk(sub_dir)
                    for file in glob(os.path.join(path, "*.json"))
                ]

                for i, file in enumerate(files):
                    count = file.split("/")[-1].split(".")[0]
                    if st.checkbox(f"{plot_name} UMAP and Clusters for count {count}"):
                        f = open(file)
                        data = json.loads(json.load(f))
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
                            f"Number of clusters for count {count}: {len(set(clusters))-1}"
                        )
                        st.markdown("""---""")   
        st.sidebar.markdown("""---""")

    ######### Showing Alerts ###########

    elif sub_dir_split[-1] == "alerts":
        if st.sidebar.checkbox(f"Show Alerts for {sub_dir_split[-2]}", value=True):
            files = [
                        file
                        for path, _, _ in os.walk(sub_dir)
                        for file in glob(os.path.join(path, "*.json"))
                    ]
            for i, file in enumerate(files):
                alert_name = file.split("/")[-1].split(".")[0]
                f = open(file)
                alert = json.load(f)
                st.subheader(alert_name)
                st.markdown("##### " + alert)
                st.markdown("""---""")

        st.sidebar.markdown("""---""")

