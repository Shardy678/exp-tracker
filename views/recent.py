import streamlit as st
from data.dataframe import load_df

def render_recent(start=None, end=None, category_ids=None):
    try:
        df = load_df(start, end, category_ids)
        if df is None or df.empty:
            st.info("No transactions found.")
            return

        for col in ['category_id', 'id', 'created_at']:
            if col in df.columns:
                df = df.drop(columns=[col])

        rename_map = {
            "tx_date": "Date",
            "description": "Description",
            "amount": "Amount",
            "category": "Category",
            "account": "Account",
            "category_kind": "Type",
        }
        df = df.rename(columns=rename_map)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
