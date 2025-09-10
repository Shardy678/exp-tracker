import os
import streamlit as st
import psycopg2
import psycopg2.extras

DB_URL = os.environ["DATABASE_URL"]  

@st.cache_resource
def get_conn():
    conn = psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def ping():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            row = cur.fetchone()
            return True, row["version"]
    except Exception as e:
        return False, str(e)

def seed():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("""
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
        """)

        cur.executemany(
            "INSERT INTO categories (name, kind) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            [
                ("Salary", "income"),
                ("Freelance", "income"),
                ("Food", "expense"),
                ("Rent", "expense"),
                ("Utilities", "expense"),
                ("Entertainment", "expense"),
            ],
        )
        cur.execute("INSERT INTO accounts (name) VALUES (%s) ON CONFLICT DO NOTHING", ("Cash",))
