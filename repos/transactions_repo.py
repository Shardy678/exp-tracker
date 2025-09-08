from typing import Optional, Sequence
from db.conn import get_conn

def _build_filters(start=None, end=None, category_ids: Optional[Sequence[int]] = None):
    clauses, params = [], []
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
    return where_sql, params

def sum_expenses_between(start=None, end=None, category_ids: Optional[Sequence[int]] = None) -> float:
    where_sql, params = _build_filters(start, end, category_ids)
    sql = f"""
        SELECT COALESCE(SUM(t.amount), 0)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        {where_sql}
        {"AND" if where_sql else "WHERE"} c.kind = 'expense'
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return float(cur.fetchone()[0] or 0.0)

def count_transactions_between(start=None, end=None, category_ids: Optional[Sequence[int]] = None) -> int:
    where_sql, params = _build_filters(start, end, category_ids)
    sql = f"SELECT COUNT(*) FROM transactions t {where_sql}"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return int(cur.fetchone()[0] or 0)

def insert_transaction(tx_date, description, amount, category_name, account) -> None:
    sql = """
        INSERT INTO transactions (tx_date, description, amount, category_id, account)
        VALUES (%s, %s, %s, (SELECT id FROM categories WHERE name = %s), %s)
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (tx_date, description, amount, category_name, account))
        conn.commit()
