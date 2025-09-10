import pandas as pd
import streamlit as st
from typing import Optional, Sequence, Dict, Any, Tuple, List
from sqlalchemy import text, bindparam
from db.conn import get_engine

def _build_filters(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category_ids: Optional[Sequence[int]] = None,
) -> Tuple[str, Dict[str, Any], List]:
    clauses, params, bindparams = [], {}, []

    if start is not None:
        clauses.append("t.tx_date >= :start")
        params["start"] = str(start)

    if end is not None:
        clauses.append("t.tx_date <= :end")
        params["end"] = str(end)

    if category_ids:
        clauses.append("t.category_id IN :cids")
        params["cids"] = [int(c) for c in category_ids]
        bindparams.append(bindparam("cids", expanding=True))

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where_sql, params, bindparams

@st.cache_data(ttl=30)
def load_df(start=None, end=None, category_ids=None, limit: int = 200) -> pd.DataFrame:
    where_sql, params, bindparams = _build_filters(start, end, category_ids)

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
        LIMIT :lim
    """
    params["lim"] = int(limit)
    stmt = text(sql).bindparams(*bindparams)

    with get_engine().connect() as conn:
        rows = conn.execute(stmt, params).mappings().all()

    df = pd.DataFrame(rows)
    if not df.empty:
        df["tx_date"] = pd.to_datetime(df["tx_date"], errors="coerce")
    return df
