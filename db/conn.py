import sqlite3
from pathlib import Path
import streamlit as st

DB_DEFAULT = "data/finance.db"

@st.cache_resource
def get_conn():
    db_path = DB_DEFAULT
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ping():
    try:
        conn = get_conn()
        row = conn.execute("SELECT sqlite_version()").fetchone()
        ver = row[0] if row else "unknown"
        return True, f"SQLite {ver}"
    except Exception as e:
        return False, str(e)


def seed():
    conn = get_conn()
    with conn: 
        conn.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS categories (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kind TEXT NOT NULL CHECK (kind IN ('expense','income')),
            UNIQUE(name, kind)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_date     TEXT NOT NULL,                -- 'YYYY-MM-DD'
            description TEXT NOT NULL DEFAULT '',
            amount      REAL NOT NULL CHECK (amount >= 0),
            category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
            account     TEXT NOT NULL DEFAULT 'Cash',
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE INDEX IF NOT EXISTS idx_tx_date      ON transactions(tx_date);
        CREATE INDEX IF NOT EXISTS idx_category_id  ON transactions(category_id);
        """)

        # Seed defaults (ignore if already present)
        conn.executemany(
            "INSERT OR IGNORE INTO categories (name, kind) VALUES (?, ?)",
            [
                ("Salary", "income"),
                ("Freelance", "income"),
                ("Food", "expense"),
                ("Rent", "expense"),
                ("Utilities", "expense"),
                ("Entertainment", "expense"),
            ],
        )
        conn.execute("INSERT OR IGNORE INTO accounts (name) VALUES (?)", ("Cash",))