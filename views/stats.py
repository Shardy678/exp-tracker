import streamlit as st
from data.dataframe import load_df
from services.transactions import get_monthly_expenses, get_monthly_transaction_count
from datetime import date

def render_stats(month_start: date, month_end: date, monthly_budget: float):
    try:
        df = load_df()
        if df is None or df.empty:
            st.info("No transactions found.")
            return

        st.subheader("Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            try:
                total_expenses = get_monthly_expenses(month_start, month_end)
                st.metric("Total Spent (This Month)", f"${total_expenses:,.2f}")
            except Exception as e:
                st.error(f"Error calculating total expenses: {e}")

        with col2:
            spent = 0.0
            try:
                spent = get_monthly_expenses(month_start, month_end)
            except Exception as e:
                st.warning(f"Could not compute monthly spend: {e}")

            percent = min(100, (spent / monthly_budget) * 100) if monthly_budget > 0 else 0
            st.metric(
                label=f"Budget Left (Until {month_end.strftime('%d %b')})",
                value=f"${max(0, monthly_budget - spent):,.2f}",
            )
            st.progress(percent / 100, text=f"{percent:.1f}% of budget spent")

        with col3:
            try:
                total_tx = get_monthly_transaction_count(month_start, month_end)
                st.metric("Total Transactions (This Month)", total_tx)
            except Exception as e:
                st.warning(f"Could not fetch transaction count: {e}")

    except Exception as e:
        st.error(f"Error loading stats: {e}")
