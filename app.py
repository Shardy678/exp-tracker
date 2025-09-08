import streamlit as st
from config import MONTHLY_BUDGET
from db.conn import seed
from views.imports import render_imports
from views.stats import render_stats
from views.add_transaction import render_add_transaction
from views.recent import render_recent
from views.filters import sidebar_filters

def main():
    st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")
    st.title("💸 Expense Tracker")
    st.caption("Track your expenses and stay on top of your finances.")

    seed()

    start, end, selected_ids = sidebar_filters()

    tab1, tab2, tab3, tab4 = st.tabs(["Stats", "Add Transaction", "Recent Transactions", "Import"])

    with tab1:
        render_stats(start, end, MONTHLY_BUDGET, selected_ids)

    with tab2:
        render_add_transaction()

    with tab3:
        render_recent(start, end, selected_ids)

    with tab4:
        render_imports()

if __name__ == "__main__":
    main()
