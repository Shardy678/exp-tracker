from typing import Optional
from db.conn import get_conn

def list_categories_by_kind(kind: str) -> list[str]:
    sql = "SELECT name FROM categories WHERE kind = ? ORDER BY name;"
    with get_conn() as conn:
        rows = conn.execute(sql, (kind,)).fetchall()
    return [row[0] for row in rows]

def insert_category(name: str, kind: str) -> None:
    # Be explicit about the conflict target to match UNIQUE(name, kind)
    sql = "INSERT INTO categories (name, kind) VALUES (?, ?) ON CONFLICT(name, kind) DO NOTHING;"
    conn = get_conn()
    with conn:  # transaction; commits automatically
        conn.execute(sql, (name, kind))

def list_all_categories() -> list[dict]:
    sql = "SELECT id, name, kind FROM categories ORDER BY kind, name;"
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return [{"id": int(r[0]), "name": r[1], "kind": r[2]} for r in rows]

def get_category_id_by_name(name: str, kind: str) -> Optional[int]:
    sql = "SELECT id FROM categories WHERE name = ? AND kind = ?;"
    with get_conn() as conn:
        row = conn.execute(sql, (name, kind)).fetchone()
    return int(row[0]) if row else None

def get_or_create_category(name: str, kind: str) -> int:
    insert_sql = "INSERT INTO categories (name, kind) VALUES (?, ?) ON CONFLICT(name, kind) DO NOTHING;"
    select_sql = "SELECT id FROM categories WHERE name = ? AND kind = ?;"
    conn = get_conn()
    with conn:
        conn.execute(insert_sql, (name, kind))
        row = conn.execute(select_sql, (name, kind)).fetchone()
        if not row:
            # very unlikely if UNIQUE(name, kind) exists, but double-check
            row = conn.execute(select_sql, (name, kind)).fetchone()
        return int(row[0])
