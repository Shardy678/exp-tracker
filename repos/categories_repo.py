from typing import Optional, List, Dict
from sqlalchemy import text
from db.conn import get_engine

def list_categories_by_kind(kind: str) -> List[str]:
    sql = text("SELECT name FROM categories WHERE kind = :k ORDER BY name;")
    with get_engine().connect() as conn:
        return conn.execute(sql, {"k": kind}).scalars().all()

def insert_category(name: str, kind: str) -> None:
    sql = text("""
        INSERT INTO categories (name, kind)
        VALUES (:n, :k)
        ON CONFLICT (name, kind) DO NOTHING;
    """)
    with get_engine().begin() as conn:   
        conn.execute(sql, {"n": name, "k": kind})

def list_all_categories() -> List[Dict]:
    sql = text("SELECT id, name, kind FROM categories ORDER BY kind, name;")
    with get_engine().connect() as conn:
        rows = conn.execute(sql).mappings().all()
    return [{"id": int(r["id"]), "name": r["name"], "kind": r["kind"]} for r in rows]

def get_category_id_by_name(name: str, kind: str) -> Optional[int]:
    sql = text("SELECT id FROM categories WHERE name = :n AND kind = :k;")
    with get_engine().connect() as conn:
        val = conn.execute(sql, {"n": name, "k": kind}).scalar()
    return int(val) if val is not None else None

def get_or_create_category(name: str, kind: str) -> int:
    sql = text("""
        INSERT INTO categories (name, kind)
        VALUES (:n, :k)
        ON CONFLICT (name, kind)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
    """)
    with get_engine().begin() as conn:
        cat_id = conn.execute(sql, {"n": name, "k": kind}).scalar_one()
    return int(cat_id)
