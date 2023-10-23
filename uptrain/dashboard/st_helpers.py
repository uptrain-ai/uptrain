import os
import sys
import typing as t
import numpy as np

from loguru import logger
import polars as pl
import pandas as pd

from uptrain.utilities import lazy_load_dep

px = lazy_load_dep("plotly.express", "plotly>=5.0.0")
st = lazy_load_dep("streamlit", "streamlit>=1.23")

from uptrain.framework import CheckSet, Check, Settings
from uptrain.operators import Table
from uptrain.utilities import polars_to_pandas


# -----------------------------------------------------------
# Utility functions
# NOTE: functions with prefix `st_` create streamlit elements
# -----------------------------------------------------------

CONSOLIDATED_CHECK = Check(
    name="Consolidated Results",
    operators=[],
    plots=[Table(title="Consolidated Results")],
)


def st_setup_layout(title: str = "UpTrain Dashboard"):
    st.set_page_config(
        page_title="UpTrain Dashboard",
        layout="wide",
        page_icon="https://github.com/uptrain-ai/uptrain/raw/dashboard/uptrain/core/classes/logging/uptrain_logo_icon.png",
    )  # TODO: find another source for the icon
    st.title(title)
    st_style = """<style> footer {visibility: hidden;} </style>"""
    st.markdown(st_style, unsafe_allow_html=True)


def read_checkset(logs_folder: str):
    """read the uptrain configuration for this run"""
    config_path = os.path.join(logs_folder, "config.json")
    return CheckSet.deserialize(config_path)


def read_settings(logs_folder: str):
    """read the settings used for this run"""
    config_path = os.path.join(logs_folder, "settings.json")
    return Settings.deserialize(config_path)


def st_make_check_selector(checkset: "CheckSet"):
    """Make a selector for a checkset"""
    # Pick a check from the checkset to view
    checks = checkset.checks + [CONSOLIDATED_CHECK]
    with st.sidebar:
        select_check_index = st.sidebar.selectbox(
            "Select a check to view",
            options=list(range(len(checks))),
            format_func=lambda x: checks[x].name,
        )  # streamlit is being weird with classes, so iterate over their indices
    check = checks[select_check_index]  # type: ignore
    return check


def st_filter_template(df, attribute, default_all=False):
    container = st.container()
    all = st.checkbox(f"Select all {attribute}", value=default_all)
    values = list(df[attribute].unique().sort())

    if all:
        selected_options = container.multiselect(
            "Select one or more options:", values, values
        )
    else:
        selected_options = container.multiselect("Select one or more options:", values)
    return selected_options


def st_show_table(data: pl.DataFrame):
    # Add a column for index
    data = data.insert_at_idx(0, pl.Series("index", np.arange(1, data.height + 1)))

    # Add a column with all values as 1
    data = data.with_columns(pl.lit("").alias("default"))

    # Hide Columns
    hide_columns = st.multiselect("Choose columns to hide", data.columns, default=[])

    # Filter Columns
    # TODO: Add support for datatypes other than categorical
    filter_columns = st.multiselect(
        "Choose columns to filter", data.columns, default=[]
    )
    filters = {}
    for column in filter_columns:
        filters[column] = st_filter_template(data, column)
    for column, values in filters.items():
        data = data.filter(pl.col(column).is_in(values))

    pd_data = polars_to_pandas(data.drop(hide_columns))
    st.dataframe(pd_data, hide_index=True)

    # Pivot Table
    st.write("Pivot Table")
    pivot = {"index": [], "values": [], "columns": [], "aggfunc": "mean"}
    pivot["index"] = st.multiselect("Choose Index", pd_data.columns, default=[])
    pivot["values"] = st.multiselect("Choose values", pd_data.columns, default=[])
    pivot["columns"] = st.multiselect(
        "Choose columns", pd_data.columns, default=["default"]
    )
    pivot["aggfunc"] = st.selectbox(
        "Choose aggfunc",
        ["mean", "sum", "count", "min", "max", "median", "first", "last"],
    )

    aggfunc = dict()
    if pivot["aggfunc"] not in ["count", "first", "last"]:
        remove_values = []
        for value in pivot["values"]:
            if pd_data[value].dtype == "object":
                if "count" not in aggfunc.values():
                    aggfunc[value] = "count"
                else:
                    remove_values.append(value)
            else:
                aggfunc[value] = pivot["aggfunc"]
        for value in remove_values:
            pivot["values"].remove(value)
    if not aggfunc:
        aggfunc = pivot["aggfunc"]

    if pivot["index"] and pivot["values"] and pivot["columns"]:
        st.dataframe(
            pd.pivot_table(
                pd_data,
                index=pivot["index"],
                values=pivot["values"],
                columns=pivot["columns"],
                aggfunc=aggfunc,
            )
        )
