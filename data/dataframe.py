import pandas as pd
import streamlit as st
from datetime import date
from typing import Optional, List

from db.conn import get_conn

@st.cache_data(show_spinner=False)
def load_df(
    start: Optional[date] = None,
    end: Optional[date] = None,
    category_ids: Optional[List[int]] = None,
):
    """
    Return transactions joined with categories, optionally filtered by date range and category ids.
    Caches results until you call st.cache_data.clear() after any write.
    """
    parts = [
        "SELECT",
        "  t.id, t.tx_date, t.description, t.amount, t.account, t.category_id,",
        "  c.name AS category, c.kind AS category_kind",
        "FROM transactions t",
        "LEFT JOIN categories c ON c.id = t.category_id",  # LEFT JOIN so uncategorized rows still show
        "WHERE 1=1",
    ]
    params: list = []

    if start:
        parts.append("AND t.tx_date >= %s")
        params.append(start.isoformat())
    if end:
        parts.append("AND t.tx_date <= %s")
        params.append(end.isoformat())

    if category_ids:
        # Build an IN (%s, %s, ...) list safely
        placeholders = ",".join(["%s"] * len(category_ids))
        parts.append(f"AND t.category_id IN ({placeholders})")
        params.extend([int(x) for x in category_ids])

    parts.append("ORDER BY t.tx_date DESC, t.id DESC")
    sql = " ".join(parts)

    # pd.read_sql_query works with a psycopg2 connection
    with get_conn() as conn:
        df = pd.read_sql_query(sql, conn, params=params, parse_dates=["tx_date"])  # type: ignore[arg-type]
    return df
    