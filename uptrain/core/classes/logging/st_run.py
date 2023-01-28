import streamlit as st
import pandas as pd
import glob
import os
import sys

print("sys arguments", str(sys.argv))

st.set_page_config(
    page_title="UpTrain AI Dashboard",
    layout="wide",
)
st.title("UpTrain AI Live Dashboard")

# The following hides the footer "Made with Streamlit"
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
