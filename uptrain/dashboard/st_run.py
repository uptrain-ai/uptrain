import os
import sys

import streamlit as st
import polars as pl
import plotly.express as px

from uptrain.io import DeltaReader, DeltaWriter
import uptrain.operators
from uptrain.framework.config import Config, SimpleCheck


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
assert check.sink is not None
if isinstance(check.sink, DeltaWriter):
    source = DeltaReader(fpath=check.sink.fpath)
    source_exec = source.make_executor(CONFIG.settings)
else:
    raise NotImplementedError(
        f"Only DeltaWriter is supported for now. Found {type(check.sink)}."
    )


@st.cache_data
def load_data():
    output = source_exec.run()
    return output["output"]


data = load_data()
if data is None:
    st.error("No data found per the specified config.")
    st.stop()

# Apply filters
# credits - https://github.com/tylerjrichards/st-filter-dataframe/blob/main/streamlit_app.py
# Also, refer - https://pola-rs.github.io/polars/py-polars/html/reference/datatypes.html
with st.sidebar:
    for col_name in plot_op.filter_on:
        dtype = data.schema[col_name]

        if dtype == pl.Categorical or data[col_name].n_unique() < 10:
            options = data[col_name].unique().to_list()
            select = st.multiselect(
                label=f"Filter on {col_name}", options=options, default=options[0]
            )
            data = data.filter(pl.col(col_name).is_in(select))
        elif dtype in pl.NUMERIC_DTYPES:
            min_val = float(data[col_name].min())
            max_val = float(data[col_name].max())
            step = (max_val - min_val) / 100
            select = st.slider(
                label=f"Filter on {col_name}",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
            )
            data = data.filter(pl.col(col_name).is_between(select[0], select[1]))
        elif dtype == pl.Date or dtype in pl.DATETIME_DTYPES:
            select = st.date_input(
                label=f"Filter on {col_name}",
                value=(data[col_name].min(), data[col_name].max()),
            )
            if len(select) == 2:
                data = data.filter(pl.col(col_name).is_between(select[0], select[1]))
        else:
            # TODO: won't this fail for non-str types?
            select = st.text_input(label=f"Substring or regex in {col_name}")
            data = data.filter(pl.col(col_name).str.contains(select))


# Plot the data
st.header(plot_op.title)
if plot_op.kind == "table":
    st.dataframe(data.to_pandas())
else:
    plot_exec = plot_op.make_executor(CONFIG.settings)
    output = plot_exec.run(data)["extra"]["chart"]
    st.plotly_chart(output)
