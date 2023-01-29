import streamlit as st
import pandas as pd
from glob import glob
import os
import sys
import plotly.graph_objects as go


def return_plotly_fig(y_axis, x_axis='Num predictions', x_log=False, y_log=False):
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

# Getting the list of all csv files in streamlit logs 
all_csv_files = [file for path,_,_ in os.walk(log_folder)
                for file in glob(os.path.join(path, "*.csv"))]

st.set_page_config(
    page_title="UpTrain AI Dashboard",
    layout="wide",
)
st.title("UpTrain AI Live Dashboard")
st_style = """
            <style>
            footer {visibility: hidden;}
            </style>
           """
st.markdown(st_style, unsafe_allow_html=True)

for csv_file in all_csv_files:
    # Reading the csv file
    df = pd.read_csv(csv_file)

    # Getting dashboard name from csv filename
    dashboard_name = csv_file.split('/')[-1].split('.')[0]

    st.markdown(f"### Visualization dashboard for {dashboard_name}")

    ############ View Data ##################
    st.caption(f"View logged data for {dashboard_name}")
    if st.checkbox(f"View {dashboard_name} data", help="View the uploaded data"):
        st.markdown(f"### Uploaded Data")
        st.dataframe(df, height=250)

    ############ View Line Plots ############
    st.caption(f"Line plot for {dashboard_name}")
    if st.checkbox(f"Line plot {dashboard_name}", help="View the line plot"):
        st.markdown(f"### Line chart for {dashboard_name}")
        scol1, scol2 = st.columns(2)
        with scol1:
            x_log = st.checkbox(
                "log x", help="Plot x-axis in log-scale",
                key=dashboard_name + 'x'
            )
        with scol2:
            y_log = st.checkbox(
                "log y", help="Plot y-axis in log-scale",
                key=dashboard_name + 'y'
                )
        fig = return_plotly_fig(dashboard_name, x_log=x_log, y_log=y_log)
        for y_axis in df.columns:
            if y_axis=='count':
                continue
            fig = fig.add_trace(go.Scatter(
                    x=df['count'],
                    y=df[y_axis],
                    name=y_axis,
                    ))
        st.plotly_chart(fig)

    ############ View Histograms ############
    st.caption(f"Histograms for {dashboard_name}")
    if st.checkbox(f"Histogram {dashboard_name}", help="View the line plot"):
        st.markdown(f"### Histogram for {dashboard_name}")
        fig = go.Figure()
        for y_axis in df.columns:
            if y_axis=='count':
                continue
            fig = fig.add_trace(go.Histogram(x=df[y_axis], name=y_axis))
        st.plotly_chart(fig)
