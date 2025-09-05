import os
import psycopg2

DB = dict(
    dbname=os.getenv("POSTGRES_DB", "finance"),
    user=os.getenv("POSTGRES_USER","expense_user"),
    password=os.getenv("POSTGRES_PASSWORD", "supersecret"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
)

def get_conn():
    return psycopg2.connect(**DB)

def ping():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                ver = cur.fetchone()[0]
        return True, ver
    except Exception as e:
        return False, e

def seed():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS categories (
                    id serial PRIMARY KEY,
                    name text NOT NULL UNIQUE,
                    kind TEXT NOT NULL
                    );
                    """)
                cur.execute("""CREATE TABLE IF NOT EXISTS transactions (
                    id serial PRIMARY KEY,
                    tx_date DATE NOT NULL,
                    description TEXT,
                    amount NUMERIC(12,2) NOT NULL,
                    category_id INTEGER,
                    account TEXT DEFAULT 'Cash',
                    created_at TIMESTAMPTZ DEFAULT NOW());
                """)
                cur.execute("""CREATE TABLE IF NOT EXISTS accounts (
                    id SERIAL PRIMARY  KEY,
                    name TEXT NOT NULL UNIQUE
                );
                """
                )
                cur.execute("""CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(tx_date);""")
                cur.execute("""CREATE INDEX IF NOT EXISTS idx_category_id ON transactions(category_id);""")
                cur.execute("""INSERT INTO categories (name, kind) VALUES
                    ('Salary', 'income'),
                    ('Freelance', 'income'),
                    ('Food', 'expense'),
                    ('Rent', 'expense'),
                    ('Utilities', 'expense'),
                    ('Entertainment', 'expense')
                    ON CONFLICT (name) DO NOTHING;
                """)
    except Exception as e:
        raise e