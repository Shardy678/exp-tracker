import streamlit as st
from db import ping, get_conn, seed


def main():
    st.set_page_config(page_title="Hello Expense", page_icon="💸", layout="centered")
    st.title("💸 Hello, Expense Tracker")
    st.caption("check check")

    ok, info = ping()
    if ok:
        st.success("Connected to Postgres")
        st.code(info)
    else:
        st.error("Could not connect to Postgres")
        st.exception(info)
        
    seed()

    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM categories")
            count = cur.fetchone()[0]
        st.info(f"Number of categories: {count}")
    except Exception as e:
        st.warning(f"Could not fetch category count: {e}")
    
    dp = st.date_input("Select a date")
    desc = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0)
    category = st.text_input("Category")
    account = st.text_input("Account", value="Cash")

    if st.button("Add Transaction"):
        try:
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
    
    if st.button("Show Recent Transactions"):
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT t.tx_date, t.description, t.amount, c.name AS category, t.account
                    FROM transactions t
                    LEFT JOIN categories c ON t.category_id = c.id
                    ORDER BY t.tx_date DESC
                    LIMIT 5;
                """)
                rows = cur.fetchall()
            if rows:
                for row in rows:
                    st.table(
                        [{"Date": row[0], "Description": row[1], "Amount": row[2], "Category": row[3], "Account": row[4]} for row in rows]
                    )
                    break  # Show table once, not per row
            else:
                st.info("No transactions found.")
        except Exception as e:
            st.error(f"Error fetching transactions: {e}")
        finally:
            if conn:
                conn.close()



if __name__ == "__main__":
    main()


