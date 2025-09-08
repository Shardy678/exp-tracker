import streamlit as st
from datetime import date

from config import MONTHLY_BUDGET
from db.conn import seed
from utils.dates import month_range
from views.stats import render_stats
from views.add_transaction import render_add_transaction
from views.recent import render_recent

def main():
    st.set_page_config(page_title="Hello Expense", page_icon="💸", layout="wide")
    st.title("💸 Expense Tracker")
    st.caption("Track your expenses and stay on top of your finances.")

    today = date.today()
    month_start, month_end = month_range(today)

    seed()

    tab1, tab2, tab3 = st.tabs(["Stats", "Add Transaction", "Recent Transactions"])

    with tab1:
        render_stats(month_start, month_end, MONTHLY_BUDGET)

    with tab2:
        render_add_transaction()

    with tab3:
        render_recent()

if __name__ == "__main__":
    main()
