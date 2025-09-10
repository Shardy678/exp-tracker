from typing import Optional, Sequence, Tuple, Dict, Any
from sqlalchemy import text, bindparam
from db.conn import get_engine

def _build_filters(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category_ids: Optional[Sequence[int]] = None,
) -> Tuple[str, Dict[str, Any], list]:
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


def sum_expenses_between(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category_ids: Optional[Sequence[int]] = None,
) -> float:
    where_sql, params, bindparams = _build_filters(start, end, category_ids)
    where_sql = f"{where_sql} AND c.kind = 'expense'" if where_sql else "WHERE c.kind = 'expense'"

    sql = f"""
        SELECT COALESCE(SUM(t.amount), 0) AS total
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        {where_sql}
    """
    stmt = text(sql).bindparams(*bindparams)

    with get_engine().connect() as conn:
        total = conn.execute(stmt, params).scalar() or 0
    return float(total)


def count_transactions_between(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category_ids: Optional[Sequence[int]] = None,
) -> int:
    where_sql, params, bindparams = _build_filters(start, end, category_ids)
    sql = f"SELECT COUNT(*) AS n FROM transactions t {where_sql}"
    stmt = text(sql).bindparams(*bindparams)

    with get_engine().connect() as conn:
        n = conn.execute(stmt, params).scalar() or 0
    return int(n)


def insert_transaction(tx_date, description, amount, category_name, account) -> None:
    stmt = text("""
        INSERT INTO transactions (tx_date, description, amount, category_id, account)
        VALUES (
            :tx_date, :description, :amount,
            (SELECT id FROM categories WHERE name = :cat_name LIMIT 1),
            :account
        )
    """)

    params = {
        "tx_date": str(tx_date),
        "description": description or "",
        "amount": float(amount),
        "cat_name": category_name,
        "account": account or "Cash",
    }

    with get_engine().begin() as conn:   
        conn.execute(stmt, params)


def insert_transaction_by_category_id(tx_date, description, amount, category_id, account) -> None:
    stmt = text("""
        INSERT INTO transactions (tx_date, description, amount, category_id, account)
        VALUES (:tx_date, :description, :amount, :category_id, :account)
    """)

    params = {
        "tx_date": str(tx_date),
        "description": description or "",
        "amount": float(amount),
        "category_id": int(category_id),
        "account": account or "Cash",
    }

    with get_engine().begin() as conn:
        conn.execute(stmt, params)
