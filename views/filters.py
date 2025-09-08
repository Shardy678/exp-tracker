from datetime import date
import streamlit as st
from services.categories import get_all_categories

def sidebar_filters():
    with st.sidebar:
        st.header("Filters")
        today = date.today()
        default_start = today.replace(day=1)
        default_end = today

        rng = st.date_input(
            "Date range",
            value=(default_start, default_end),
            help="Filter transactions between these dates (inclusive).",
            key="filters_date_range",
        )
        if isinstance(rng, tuple) and len(rng) == 2:
            start, end = rng
        else:
            start, end = default_start, default_end

        all_cats = get_all_categories() 
        cat_options = {
            f"{c['name']} ({c['kind'][0].upper()})": int(c["id"])
            for c in all_cats
        }
        selected = st.multiselect("Categories", options=list(cat_options.keys()))
        selected_ids = [cat_options[s] for s in selected]

        return start, end, selected_ids
