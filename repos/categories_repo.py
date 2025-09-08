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
        
def get_category_id_by_name(name: str, kind: str) -> int | None:
    sql = "SELECT id FROM categories WHERE name = %s AND kind = %s"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (name, kind))
        row = cur.fetchone()
        return int(row[0]) if row else None

def get_or_create_category(name: str, kind: str) -> int:
    insert_sql = "INSERT INTO categories (name, kind) VALUES (%s, %s) ON CONFLICT DO NOTHING"
    select_sql = "SELECT id FROM categories WHERE name = %s AND kind = %s"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(insert_sql, (name, kind))
        cur.execute(select_sql, (name, kind))
        row = cur.fetchone()
        if not row:
            # extremely rare race, try again
            cur.execute(select_sql, (name, kind))
            row = cur.fetchone()
        conn.commit()
        return int(row[0])
