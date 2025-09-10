from typing import Optional, Sequence, Tuple, List
from db.conn import get_conn

def _build_filters(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category_ids: Optional[Sequence[int]] = None,
) -> Tuple[str, List[object]]:

    clauses, params = [], []

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
    return where_sql, params


def sum_expenses_between(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category_ids: Optional[Sequence[int]] = None,
) -> float:
    where_sql, params = _build_filters(start, end, category_ids)
    where_sql = f"{where_sql} AND c.kind = 'expense'" if where_sql else "WHERE c.kind = 'expense'"

    sql = f"""
        SELECT COALESCE(SUM(t.amount), 0) AS total
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        {where_sql}
    """

    with get_conn().cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
    total = row["total"] if isinstance(row, dict) else row[0]
    return float(total or 0.0)


def count_transactions_between(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category_ids: Optional[Sequence[int]] = None,
) -> int:
    where_sql, params = _build_filters(start, end, category_ids)
    sql = f"SELECT COUNT(*) AS n FROM transactions t {where_sql}"

    with get_conn().cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()

    n = row["n"] if isinstance(row, dict) else row[0]
    return int(n or 0)


def insert_transaction(tx_date, description, amount, category_name, account) -> None:

    sql = """
        INSERT INTO transactions (tx_date, description, amount, category_id, account)
        VALUES (
            %s, %s, %s,
            (SELECT id FROM categories WHERE name = %s LIMIT 1),
            %s
        )
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (str(tx_date), description or "", float(amount), category_name, account or "Cash"),
            )


def insert_transaction_by_category_id(tx_date, description, amount, category_id, account) -> None:
    sql = """
        INSERT INTO transactions (tx_date, description, amount, category_id, account)
        VALUES (%s, %s, %s, %s, %s)
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (str(tx_date), description or "", float(amount), int(category_id), account or "Cash"),
            )
