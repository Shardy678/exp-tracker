import streamlit as st
from data.dataframe import load_df

def bust_data_cache():
    try:
        load_df.clear()
    except Exception:
        st.cache_data.clear()
