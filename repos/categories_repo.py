from typing import Optional, List, Dict
from db.conn import get_conn

def list_categories_by_kind(kind: str) -> List[str]:
    sql = "SELECT name FROM categories WHERE kind = %s ORDER BY name;"
    with get_conn().cursor() as cur:
        cur.execute(sql, (kind,))
        rows = cur.fetchall()
    return [r["name"] for r in rows]

def insert_category(name: str, kind: str) -> None:
    sql = """
        INSERT INTO categories (name, kind)
        VALUES (%s, %s)
        ON CONFLICT (name, kind) DO NOTHING;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, kind))

def list_all_categories() -> List[Dict]:
    sql = "SELECT id, name, kind FROM categories ORDER BY kind, name;"
    with get_conn().cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [{"id": int(r["id"]), "name": r["name"], "kind": r["kind"]} for r in rows]

def get_category_id_by_name(name: str, kind: str) -> Optional[int]:
    sql = "SELECT id FROM categories WHERE name = %s AND kind = %s;"
    with get_conn().cursor() as cur:
        cur.execute(sql, (name, kind))
        row = cur.fetchone()
    return int(row["id"]) if row else None

def get_or_create_category(name: str, kind: str) -> int:

    sql = """
        INSERT INTO categories (name, kind)
        VALUES (%s, %s)
        ON CONFLICT (name, kind)
        DO UPDATE SET name = EXCLUDED.name  -- no-op to enable RETURNING
        RETURNING id;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, kind))
            row = cur.fetchone()
            return int(row["id"])
