import os
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_URL = os.getenv("DATABASE_URL") or os.environ["DB_URL"]

@st.cache_resource
def get_engine() -> Engine:
    return create_engine(
        DB_URL,
        pool_pre_ping=True,   
        pool_recycle=300,     
        pool_size=5,
        max_overflow=0,
    )

def ping():
    try:
        with get_engine().connect() as conn:
            ver = conn.execute(text("SELECT version();")).scalar_one()
            return True, ver
    except Exception as e:
        return False, str(e)

def seed():
    ddl = """
    CREATE TABLE IF NOT EXISTS categories (
        id   SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        kind TEXT NOT NULL CHECK (kind IN ('expense','income')),
        UNIQUE(name, kind)
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id          SERIAL PRIMARY KEY,
        tx_date     DATE NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        amount      NUMERIC NOT NULL CHECK (amount >= 0),
        category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
        account     TEXT NOT NULL DEFAULT 'Cash',
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS accounts (
        id   SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );

    CREATE INDEX IF NOT EXISTS idx_tx_date     ON transactions(tx_date);
    CREATE INDEX IF NOT EXISTS idx_category_id ON transactions(category_id);
    """

    with get_engine().begin() as conn:  
        conn.execute(text(ddl))

        conn.execute(
            text("""
                INSERT INTO categories (name, kind)
                VALUES (:name, :kind)
                ON CONFLICT (name, kind) DO NOTHING
            """),
            [
                {"name": "Salary",      "kind": "income"},
                {"name": "Freelance",   "kind": "income"},
                {"name": "Food",        "kind": "expense"},
                {"name": "Rent",        "kind": "expense"},
                {"name": "Utilities",   "kind": "expense"},
                {"name": "Entertainment","kind": "expense"},
            ],
        )

        conn.execute(
            text("""
                INSERT INTO accounts (name)
                VALUES (:name)
                ON CONFLICT (name) DO NOTHING
            """),
            {"name": "Cash"},
        )
