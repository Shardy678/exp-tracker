from datetime import date
import streamlit as st
from db import get_conn, seed
from dataframe import load_df
from dateutil.relativedelta import relativedelta

def main():
    st.set_page_config(page_title="Hello Expense", page_icon="💸", layout="wide")
    st.title("💸 Expense Tracker")
    st.caption("Track your expenses and stay on top of your finances.")

    MONTHLY_BUDGET = 1000.00
    today = date.today()
    month_start = today.replace(day=1)
    month_end = (month_start + relativedelta(months=1)) - relativedelta(days=1)
    seed()

    tab1, tab2, tab3 = st.tabs(["Stats", "Add Transaction", "Recent Transactions"])

    with tab1:
        try:
            df = load_df()
            if not df.empty:
                st.subheader("Summary")

                

                col1, col2, col3 = st.columns(3)
                with col1:
                    try:
                        conn = get_conn()
                        with conn.cursor() as cur:
                            cur.execute("""SELECT SUM(t.amount)
                                            FROM transactions t
                                            JOIN categories c ON t.category_id = c.id
                                            WHERE c.kind = 'expense';
                                            """)
                            total_expenses = cur.fetchone()[0] or 0
                            st.metric("Total Spent", f"${total_expenses:,.2f}")
                    except Exception as e:
                        st.error(f"Error calculating total expenses: {e}")
                    finally:
                        if conn:
                            conn.close()
                
                with col2:
                    spent = 0.0
                    try:
                        with get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute(
                                    """
                                    SELECT COALESCE(SUM(t.amount), 0)
                                    FROM transactions t
                                    JOIN categories c ON c.id = t.category_id
                                    WHERE c.kind = 'expense'
                                    AND t.tx_date >= %s
                                    AND t.tx_date <= %s
                                    """,
                                    (month_start, month_end),
                                )
                                spent = float(cur.fetchone()[0] or 0.0)
                    except Exception as e:
                        st.warning(f"Could not compute monthly spend: {e}")

                    left = max(0, MONTHLY_BUDGET - spent)
                    st.metric(
                        label=f"Budget Left (Until {month_end.strftime('%d %b')})",
                        value=f"${left:,.2f}",
                        delta=f"Spent ${spent:,.2f}",
                        delta_color="normal" if left > 0 else "inverse",
                    )



        except Exception as e:
            st.error(f"Error loading stats: {e}")
                    

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            dp = st.date_input("Select a date")
            desc = st.text_input("Description")
            amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")

        with col2:
            selected_kind = st.radio("Type", ["expense", "income"], horizontal=True)

            conn = None
            categories: list[str] = []
            try:
                conn = get_conn()
                with conn.cursor() as cur:
                    cur.execute("SELECT name FROM categories WHERE kind = %s ORDER BY name;",(selected_kind,))
                    categories = [row[0] for row in cur.fetchall()]
            except Exception as e:
                st.error(f"Error loading categories: {e}")
            finally:
                if conn:
                    conn.close()

            if categories:
                category = st.selectbox("Category", categories, key=f"cat_{selected_kind}")
            else:
                st.info(f"No {selected_kind} categories yet — add one below.")
                category = st.text_input("Category")

            account = st.text_input("Account", value="Cash")


        if st.button("Add Transaction"):
            conn = None
            try:
                conn = get_conn()
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO transactions (tx_date, description, amount, category_id, account)
                        VALUES (%s, %s, %s, 
                            (SELECT id FROM categories WHERE name = %s), %s)
                    """, (dp, desc, amount, category, account))
                    conn.commit()
                st.success("Transaction added!")
            except Exception as e:
                st.error(f"Error adding transaction: {e}")
            finally:
                if conn:
                    conn.close()

    with tab3:
        try:
            df = load_df()
            if not df.empty:
                st.table(df)
            else:
                st.info("No transactions found.")
        except Exception as e:
            st.error(f"Error fetching transactions: {e}")

if __name__ == "__main__":
    main()
