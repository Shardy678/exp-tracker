import pandas as pd
import streamlit as st
from db.conn import get_conn

@st.cache_data(ttl=30)
def load_df(limit: int = 200) -> pd.DataFrame:
    sql = """
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
    -- no WHERE that drops empty descriptions or specific kinds
    ORDER BY t.id DESC         -- newest first; or t.created_at DESC, t.id DESC
    LIMIT %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (limit,))
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)
