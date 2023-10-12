import os
import sys
import polars as pl

from uptrain.utilities import lazy_load_dep
st = lazy_load_dep("streamlit", "streamlit>=1.23")

from uptrain.operators import ColumnOp
from uptrain.framework import Settings, CheckSet, Check
from uptrain.dashboard.st_helpers import (
    st_make_check_selector,
    st_show_table,
    st_setup_layout,
    read_checkset,
    read_settings,
    CONSOLIDATED_CHECK,
)

# -----------------------------------------------------------
# Utility functions
# -----------------------------------------------------------

# TODO: Streamlit can't pickle custom operators, so we need to use a workaround to cache
# read_checkset = st.cache_data(read_checkset)


@st.cache_data
def load_data_for_check_local(_settings: "Settings", _check: "Check", check_name: str):
    from uptrain.operators import DeltaWriter, JsonWriter

    sink = CheckSet._get_sink_for_check(_settings, _check)
    if isinstance(sink, (DeltaWriter, JsonWriter)):
        source = sink.to_reader()
        source.setup(_settings)
    else:
        raise NotImplementedError(f"{type(sink)} is not supported for now.")
    output = source.run()
    return output["output"]


@st.cache_data
def load_data_for_checks_consolidated(_settings: "Settings", _checkset: "CheckSet"):
    all_cols = {}
    for _check in _checkset.checks:
        if not all(isinstance(op, ColumnOp) for op in _check.operators):
            continue
        data = load_data_for_check_local(_settings, _check, _check.name)
        for col in data.columns:
            all_cols[col] = data[col]

    return pl.DataFrame(all_cols)


# -----------------------------------------------------------
# Run code
# -----------------------------------------------------------


# Set up layout of the dashboard and the sidebar
st_setup_layout()

# Read parameters for this run
LOGS_DIR = sys.argv[1]
CHECK_SET = read_checkset(LOGS_DIR)
SETTINGS = read_settings(LOGS_DIR)

# Pick a check to view
check = st_make_check_selector(CHECK_SET)

# Check the plot operator for the check
plot_ops = check.plots
if len(plot_ops) == 0:
    st.warning("No plot operator specified for the check")
    st.stop()

# load data
if check.name == CONSOLIDATED_CHECK.name:
    data = load_data_for_checks_consolidated(SETTINGS, CHECK_SET)
else:
    data = load_data_for_check_local(SETTINGS, check, check.name)
if data is None:
    st.error("No data found per the specified config.")
    st.stop()

# Plot the data
for plot_op in plot_ops:
    st.header(plot_op.title)
    if plot_op.kind == "table":
        st_show_table(data)
    else:
        plot_op.setup(SETTINGS)
        output = plot_op.run(data)["extra"]["chart"]
        st.plotly_chart(output)
    st.divider()
