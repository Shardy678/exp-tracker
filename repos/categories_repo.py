from db.conn import get_conn

def list_categories_by_kind(kind: str) -> list[str]:
    sql = "SELECT name FROM categories WHERE kind = %s ORDER BY name;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (kind,))
            return [row[0] for row in cur.fetchall()]
