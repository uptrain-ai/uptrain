import os
import sys

import streamlit as st

from uptrain.dashboard.st_helpers import (
    st_make_check_selector,
    read_checkset,
    read_settings,
    load_data_for_check_local,
    st_setup_layout,
    st_show_table,
)

# -----------------------------------------------------------
# Utility functions
# -----------------------------------------------------------

read_checkset = st.cache_data(read_checkset)

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
data = load_data_for_check_local(SETTINGS, check)
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
