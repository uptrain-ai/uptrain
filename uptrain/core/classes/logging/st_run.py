import streamlit as st
import pandas as pd
from glob import glob
import os
import sys
import plotly.graph_objects as go
import numpy as np
import json


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

sub_dirs = [path[0] for path in os.walk(log_folder)]
st.sidebar.title("Select dashboards to view")
for sub_dir in sub_dirs:
    if sub_dir.split('/')[-2] == 'line_plots':
        plot_name = sub_dir.split('/')[-1]
        
        if st.sidebar.checkbox(f"Line-plot for {plot_name}"):
            st.markdown(f"### Line chart for {plot_name}")

            # Getting the list of all csv files in streamlit logs 
            csv_files = [file for path,_,_ in os.walk(sub_dir)
                            for file in glob(os.path.join(path, "*.csv"))]

            scol1, scol2 = st.columns(2)
            with scol1:
                x_log = st.checkbox(
                    "log x", help="Plot x-axis in log-scale",
                    key=plot_name + 'x'
                )
            with scol2:
                y_log = st.checkbox(
                    "log y", help="Plot y-axis in log-scale",
                    key=plot_name + 'y'
                    )
            fig = return_plotly_fig(plot_name, x_log=x_log, y_log=y_log)
            for i, csv_file in enumerate(csv_files):
                # Reading the csv file
                df = pd.read_csv(csv_file)

                # Getting plot_id
                plot_id = csv_file.split('/')[-1].split('.')[0]
                fig = fig.add_trace(go.Scatter(
                                x=df['count'],
                                y=df[plot_id],
                                name=str(i) + ", " + plot_id,
                                ))
            st.plotly_chart(fig)

        st.sidebar.markdown("""---""")

# st.sidebar.title("Select dashboards to view")
# for csv_file in all_csv_files:
#     # Reading the csv file
#     df = pd.read_csv(csv_file)

#     # Getting dashboard name from csv filename
#     csv_file_list = csv_file.split('/')
#     plot_id = csv_file_list[-1].split('.')[0]
#     plot_name = csv_file_list[-2]
#     plot_type = csv_file_list[-3]

#     if st.sidebar.checkbox(f"Dashboard for {plot_name}"):

#         st.markdown(f"### Visualization dashboard for {plot_name}")

#         ############ View Line Plots ############
#         if plot_type == 'line_plots':
#             if st.sidebar.checkbox(f"Line-plot: {plot_name}", 
#                     help="View the line plot", value=True):
#                 st.markdown(f"#### Line chart for {plot_name}")
#                 scol1, scol2 = st.columns(2)
#                 with scol1:
#                     x_log = st.checkbox(
#                         "log x", help="Plot x-axis in log-scale",
#                         key=plot_name + 'x'
#                     )
#                 with scol2:
#                     y_log = st.checkbox(
#                         "log y", help="Plot y-axis in log-scale",
#                         key=plot_name + 'y'
#                         )
#                 fig = return_plotly_fig(plot_name, x_log=x_log, y_log=y_log)
#                 for y_axis in df.columns:
#                     if y_axis=='count':
#                         continue
#                     fig = fig.add_trace(go.Scatter(
#                             x=df['count'],
#                             y=df[y_axis],
#                             name=y_axis,
#                             ))
#                 st.plotly_chart(fig)

            # ############ View Data ##################
            # if st.sidebar.checkbox(f"Data: {plot_name}", help="View the uploaded data"):
            #     st.markdown(f"#### Uploaded Data")
            #     st.dataframe(df, height=250)

            # ############ View Histograms ############
            # if st.sidebar.checkbox(f"Histogram: {plot_name}", help="View the line plot"):
            #     st.markdown(f"#### Histogram for {plot_name}")
            #     fig = go.Figure()
            #     for y_axis in df.columns:
            #         if y_axis=='count':
            #             continue
            #         fig = fig.add_trace(go.Histogram(x=df[y_axis], name=y_axis))
            #     st.plotly_chart(fig)

    #     ############ View 3D Histograms ############
    #     if plot_type == 'histograms':
    #         if st.sidebar.checkbox(f"Histogram: {plot_name}", 
    #                 help="View the histogram", value=True):
    #             st.markdown(f"#### Histogram for {plot_name}")
    #             fig = go.Figure()
    #             for y_axis in df.columns:
    #                 if y_axis=='count':
    #                     continue
    #                 out = [json.loads(x) for x in df[y_axis]]
    #                 for i,row in enumerate(out):
    #                     hist_data = np.histogram(row, density=False)
    #                     a0, a1 = hist_data[0].tolist(), hist_data[1].tolist()
    #                     a0=np.repeat(a0,2).tolist()
    #                     a0.insert(0,0)
    #                     a0.pop()
    #                     a1=np.repeat(a1,2)
    #                     fig = fig.add_trace(go.Scatter3d(x=[df['count'][i]]*len(a0), y=a1, z=a0, mode='lines', name=df['count'][i]))
    #             st.plotly_chart(fig)

    # st.sidebar.markdown("""---""")
