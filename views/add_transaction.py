import streamlit as st
from services.categories import get_categories
from services.transactions import add_transaction

def render_add_transaction():
    col1, col2 = st.columns(2)  

    with col1:
        dp = st.date_input("Select a date")
        desc = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")

    with col2:
        selected_kind = st.radio("Type", ["expense", "income"], horizontal=True)

        categories = []
        try:
            categories = get_categories(selected_kind)
        except Exception as e:
            st.error(f"Error loading categories: {e}")

        if categories:
            category = st.selectbox("Category", categories, key=f"cat_{selected_kind}")
        else:
            st.info(f"No {selected_kind} categories yet — add one below.")
            category = st.text_input("Category")

        account = st.text_input("Account", value="Cash")


    if st.button("Add Transaction"):
        try:
            add_transaction(dp, desc, amount, category, account)
            st.success("Transaction added!")
        except Exception as e:
            st.error(f"Error adding transaction: {e}")
