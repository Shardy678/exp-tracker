import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
from data.dataframe import load_df
from services.transactions import (
    get_monthly_expenses,          
    get_monthly_transaction_count, 
)
import plotly.express as px
import pandas as pd

def _month_span(any_start: date, any_end: date):
    if any_start > any_end:
        any_start, any_end = any_end, any_start

    span_start = any_start.replace(day=1)
    last_month_start = any_end.replace(day=1)
    months = 1 + (last_month_start.year - span_start.year) * 12 + (last_month_start.month - span_start.month)
    span_end = (last_month_start + relativedelta(months=1)) - relativedelta(days=1)
    return span_start, span_end, months

def _format_daterange(a: date, b: date) -> str:
    return f"{a.strftime('%d %b %Y')} – {b.strftime('%d %b %Y')}"

def render_stats(start: date, end: date, monthly_budget: float, category_ids=None):
    try:
        df = load_df(start=start, end=end, category_ids=category_ids)
        if df is None or df.empty:
            st.info("No transactions found for the selected filters.")
            return

        st.subheader("Summary")
    
        col1, col2, col3 = st.columns(3)

        with col1:
            try:
                total_spent_filtered = get_monthly_expenses(start, end, category_ids)
                st.metric(f"Total Spent ({_format_daterange(start, end)})", f"${total_spent_filtered:,.2f}")
            except Exception as e:
                st.error(f"Error calculating total spent: {e}")

        with col2:
            span_start, span_end, months_count = _month_span(start, end)
            total_budget = monthly_budget * months_count
            try:
                spent_unfiltered_span = get_monthly_expenses(span_start, span_end, category_ids=None)
            except Exception as e:
                st.warning(f"Could not compute unfiltered monthly spend: {e}")
                spent_unfiltered_span = 0.0

            percent = (spent_unfiltered_span / total_budget) if total_budget > 0 else 0.0
            st.metric(
                label=f"Budget Left ({months_count} month{'s' if months_count != 1 else ''}: {_format_daterange(span_start, span_end)})",
                value=f"${max(0.0, total_budget - spent_unfiltered_span):,.2f}",
            )
            st.progress(min(1.0, percent), text=f"{percent*100:.1f}% of budget used")

        with col3:
            try:
                total_tx = get_monthly_transaction_count(start, end, category_ids)
                st.metric(f"Total Transactions ({_format_daterange(start, end)})", total_tx)
            except Exception as e:
                st.warning(f"Could not fetch transaction count: {e}")

        
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            cat_df = (
                df[df["category_kind"] == "expense"]
                .groupby("category", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )

            if cat_df.empty:
                st.info("No expenses found for this period.")
            else:
                fig = px.bar(
                    cat_df,
                    x="amount",
                    y="category",
                    orientation="h",
                    text="amount",
                    color="category",
                    labels={"amount": "Amount Spent", "category": "Category"},
                    title="Expenses by Category",
                )
                fig.update_traces(texttemplate="$%{text:,.2f}", textposition="outside")
                fig.update_layout(yaxis=dict(autorange="reversed"))  
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            if df.empty:
                st.info("No data available for the selected period.")
            else:
                df["tx_date"] = pd.to_datetime(df["tx_date"], errors="coerce")

                weekly_df = (
                    df[df["category_kind"] == "expense"]
                    .groupby(pd.Grouper(key="tx_date", freq="W"))["amount"]
                    .sum()
                    .reset_index()
                    .sort_values("tx_date")
                )

                if weekly_df.empty:
                    st.info("No expenses found.")
                else:
                    fig = px.line(
                        weekly_df,
                        x="tx_date",
                        y="amount",
                        labels={"tx_date": "Week", "amount": "Amount Spent"},
                        title="Weekly Expenses",
                    )
                    fig.update_traces(mode="lines+markers", line=dict(width=2))
                    fig.update_yaxes(tickprefix="$")
                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading stats: {e}")
