from db.conn import get_conn

def list_categories_by_kind(kind: str) -> list[str]:
    sql = "SELECT name FROM categories WHERE kind = %s ORDER BY name;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (kind,))
            return [row[0] for row in cur.fetchall()]

def insert_category(name: str, kind: str) -> None:
    sql = "INSERT INTO categories (name, kind) VALUES (%s, %s) ON CONFLICT DO NOTHING;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, kind))
        conn.commit()

def list_all_categories() -> list[dict]:
    sql = "SELECT id, name, kind FROM categories ORDER BY name;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return [{"id": row[0], "name": row[1], "kind": row[2]} for row in rows]