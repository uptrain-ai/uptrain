import os
import sys

import streamlit as st
import polars as pl
import plotly.express as px

from uptrain.io import DeltaReader, DeltaWriter, JsonReader, JsonWriter
import uptrain.operators
from uptrain.framework.config import Config, SimpleCheck

import pandas as pd

# -----------------------------------------------------------
# Set up layout of the dashboard and the sidebar
# -----------------------------------------------------------

st.set_page_config(
    page_title="UpTrain Dashboard",
    layout="wide",
    page_icon="https://github.com/uptrain-ai/uptrain/raw/dashboard/uptrain/core/classes/logging/uptrain_logo_icon.png",
)  # TODO: find another source for the icon
st.title("UpTrain Live Dashboard")
st_style = """<style> footer {visibility: hidden;} </style>"""
st.markdown(st_style, unsafe_allow_html=True)


# -----------------------------------------------------------
# Utility functions
# -----------------------------------------------------------


@st.cache_data
def read_config(logs_folder: str):
    """read the uptrain configuration for this run"""
    config_path = os.path.join(logs_folder, "config.json")
    return Config.deserialize(config_path)


# -----------------------------------------------------------
# Run code
# -----------------------------------------------------------

# Read parameters for this run
LOGS_DIR = sys.argv[1]
CONFIG = read_config(LOGS_DIR)

# Pick a check to view
select_check_index = st.sidebar.selectbox(
    "Select a check to view",
    options=list(range(len(CONFIG.checks))),
    format_func=lambda x: CONFIG.checks[x].name,
)  # streamlit is being weird with classes, so iterate over their indices
check = CONFIG.checks[select_check_index]
assert isinstance(check, SimpleCheck)

# Check the plot operator for the check
plot_op = check.plot
if plot_op is None:
    st.warning("No plot operator specified for the check")
    st.stop()

# Read the data


# @st.cache_data
def load_data(check):
    assert check.sink is not None
    if isinstance(check.sink, DeltaWriter):
        source = DeltaReader(fpath=check.sink.fpath)
        source_exec = source.make_executor(CONFIG.settings)
    elif isinstance(check.sink, JsonWriter):
        source = JsonReader(fpath=check.sink.fpath)
        source_exec = source.make_executor(CONFIG.settings)
    else:
        raise NotImplementedError(
            f"{type(check.sink)} is not supported for now."
        )
    output = source_exec.run()
    return output["output"]


data = load_data(check)
if data is None:
    st.error("No data found per the specified config.")
    st.stop()

# Apply filters
# credits - https://github.com/tylerjrichards/st-filter-dataframe/blob/main/streamlit_app.py
# Also, refer - https://pola-rs.github.io/polars/py-polars/html/reference/datatypes.html
# def apply_filters(data) -> None:
#     for col_name in plot_op.filter_on:
#         dtype = data.schema[col_name]
#         if dtype == pl.Categorical or data[col_name].n_unique() < 10:
#             options = data[col_name].unique().to_list()
#             select = st.multiselect(
#                 label=f"Filter on {col_name}", options=options, default=options[0]
#             )
#             data = data.filter(pl.col(col_name).is_in(select))
#         elif dtype in pl.NUMERIC_DTYPES:
#             min_val = float(data[col_name].min())
#             max_val = float(data[col_name].max())
#             step = (max_val - min_val) / 100
#             select = st.slider(
#                 label=f"Filter on {col_name}",
#                 min_value=min_val,
#                 max_value=max_val,
#                 value=(min_val, max_val),
#             )
#             data = data.filter(pl.col(col_name).is_between(select[0], select[1]))
#         elif dtype == pl.Date or dtype in pl.DATETIME_DTYPES:
#             select = st.date_input(
#                 label=f"Filter on {col_name}",
#                 value=(data[col_name].min(), data[col_name].max()),
#             )
#             if len(select) == 2:
#                 data = data.filter(pl.col(col_name).is_between(select[0], select[1]))
#         else:
#             # TODO: won't this fail for non-str types?
#             select = st.text_input(label=f"Substring or regex in {col_name}")
#             data = data.filter(pl.col(col_name).str.contains(select))
#     return data
        
# def show_pivot_tables(data):
#     for pivot in plot_op.pivot_args:
#         if st.checkbox(pivot["title"]):
#             st.dataframe(pd.pivot_table(data, index=pivot["index"], values=pivot["values"], columns=pivot["columns"], aggfunc=pivot["aggfunc"]))

def filter_template(df, attribute, default_all=False):
    container = st.container()
    all = st.checkbox(f"Select all {attribute}", value=default_all)
    values = list(df[attribute].unique().sort())

    if all:
        selected_options = container.multiselect("Select one or more options:", values, values)
    else:
        selected_options =  container.multiselect("Select one or more options:", values)
    return selected_options

def show_table(data):
    # Hide Columns
    hide_columns = st.multiselect(
        "Choose columns to hide", data.columns, default=[]
    )

    # Filter Columns
    filter_columns = st.multiselect(
        "Choose columns to filter", data.columns, default=[]
    )
    filters = {}
    for column in filter_columns:
        filters[column] = filter_template(data, column)
    for column, values in filters.items():
        data = data.filter(pl.col(column).is_in(values))

    data = data.drop(hide_columns).to_pandas()
    st.dataframe(data)

    # Pivot Table
    st.write("Pivot Table")
    pivot = {
        "index" : [],
        "values" : [],
        "columns" : [],
        "aggfunc" : "mean"
    }
    pivot["index"] = st.multiselect(
        "Choose Index", data.columns, default=[]
    )
    pivot["values"] = st.multiselect(
        "Choose values", data.columns, default=[]
    )
    pivot["columns"] = st.multiselect(
        "Choose columns", data.columns, default=[]
    )
    if pivot["index"] and pivot["values"] and pivot["columns"]:
        st.dataframe(pd.pivot_table(data, index=pivot["index"], values=pivot["values"], columns=pivot["columns"], aggfunc=pivot["aggfunc"]))

# Plot the data
st.header(plot_op.title)
if plot_op.kind == "table":
    show_table(data)
else:
    plot_exec = plot_op.make_executor(CONFIG.settings)
    output = plot_exec.run(data)["extra"]["chart"]
    st.plotly_chart(output)
