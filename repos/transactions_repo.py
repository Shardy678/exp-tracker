from typing import Optional, Sequence
from db.conn import get_conn

def _build_filters(start=None, end=None, category_ids: Optional[Sequence[int]] = None):
    clauses, params = [], []
    if start is not None:
        clauses.append("t.tx_date >= ?")
        params.append(str(start))
    if end is not None:
        clauses.append("t.tx_date <= ?")
        params.append(str(end))
    if category_ids:
        placeholders = ",".join(["?"] * len(category_ids))
        clauses.append(f"t.category_id IN ({placeholders})")
        params.extend(category_ids)
    where_sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    return where_sql, params

def sum_expenses_between(start=None, end=None, category_ids: Optional[Sequence[int]] = None) -> float:
    where_sql, params = _build_filters(start, end, category_ids)
    # add the kind filter
    where_sql = f"{where_sql} AND c.kind = 'expense'" if where_sql else "WHERE c.kind = 'expense'"
    sql = f"""
        SELECT COALESCE(SUM(t.amount), 0)
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        {where_sql}
    """
    with get_conn() as conn:
        row = conn.execute(sql, params).fetchone()
    return float(row[0] or 0.0)

def count_transactions_between(start=None, end=None, category_ids: Optional[Sequence[int]] = None) -> int:
    where_sql, params = _build_filters(start, end, category_ids)
    sql = f"SELECT COUNT(*) FROM transactions t {where_sql}"
    with get_conn() as conn:
        row = conn.execute(sql, params).fetchone()
    return int(row[0] or 0)

def insert_transaction(tx_date, description, amount, category_name, account) -> None:
    # NOTE: if your categories table has UNIQUE(name, kind) (recommended),
    # you may want a kind argument here and match on (name, kind).
    sql = """
        INSERT INTO transactions (tx_date, description, amount, category_id, account)
        VALUES (
            ?, ?, ?, 
            (SELECT id FROM categories WHERE name = ? LIMIT 1),
            ?
        )
    """
    conn = get_conn()
    with conn:  # transaction
        conn.execute(sql, (str(tx_date), description or "", float(amount), category_name, account or "Cash"))

def insert_transaction_by_category_id(tx_date, description, amount, category_id, account) -> None:
    sql = """
        INSERT INTO transactions (tx_date, description, amount, category_id, account)
        VALUES (?, ?, ?, ?, ?)
    """
    conn = get_conn()
    with conn:
        conn.execute(sql, (str(tx_date), description or "", float(amount), int(category_id), account or "Cash"))
