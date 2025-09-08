from db.conn import get_conn

def sum_expenses_between(start, end) -> float:
    sql = """
        SELECT COALESCE(SUM(t.amount), 0)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE c.kind = 'expense'
          AND t.tx_date >= %s AND t.tx_date <= %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (start, end))
            return float(cur.fetchone()[0] or 0.0)

def count_transactions_between(start, end) -> int:
    sql = """
        SELECT COUNT(*)
        FROM transactions
        WHERE tx_date >= %s AND tx_date <= %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (start, end))
            return int(cur.fetchone()[0] or 0)

def insert_transaction(tx_date, description, amount, category_name, account) -> None:
    sql = """
        INSERT INTO transactions (tx_date, description, amount, category_id, account)
        VALUES (%s, %s, %s, (SELECT id FROM categories WHERE name = %s), %s)
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (tx_date, description, amount, category_name, account))
        conn.commit()
