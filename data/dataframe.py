import pandas as pd
import streamlit as st
from db.conn import get_conn

@st.cache_data(ttl=30)
def load_df(start=None, end=None, category_ids=None, limit: int = 200) -> pd.DataFrame:
    clauses = []
    params = []

    if start is not None:
        clauses.append("t.tx_date >= %s")
        params.append(str(start)) 

    if end is not None:
        clauses.append("t.tx_date <= %s")
        params.append(str(end))

    if category_ids:
        placeholders = ",".join(["%s"] * len(category_ids))
        clauses.append(f"t.category_id IN ({placeholders})")
        params.extend([int(cid) for cid in category_ids])

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

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
    params.append(int(limit))

    with get_conn().cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        cols = [desc.name for desc in cur.description]  

    df = pd.DataFrame(rows, columns=cols)
    if not df.empty:
        df["tx_date"] = pd.to_datetime(df["tx_date"], errors="coerce")

    return df
