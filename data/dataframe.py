import pandas as pd
import streamlit as st
from db.conn import get_conn

@st.cache_data(ttl=30)
def load_df(start=None, end=None, category_ids=None, limit: int = 200) -> pd.DataFrame:
    clauses = []
    params = []

    if start is not None:
        clauses.append("t.tx_date >= %s")
        params.append(start)
    if end is not None:
        clauses.append("t.tx_date <= %s")
        params.append(end)
    if category_ids:
        clauses.append("t.category_id = ANY(%s)")
        params.append(category_ids)  

    where_sql = "WHERE " + " AND ".join(clauses) if clauses else ""

    sql = f"""
        SELECT
            t.id,
            t.tx_date,
            t.description,
            t.amount,
            t.category_id,
            t.account,
            t.created_at,
            c.name AS category,
            c.kind AS category_kind
        FROM transactions t
        LEFT JOIN categories c ON c.id = t.category_id
        {where_sql}
        ORDER BY t.id DESC
        LIMIT %s;
    """
    params.append(limit)

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)
