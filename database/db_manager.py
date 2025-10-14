# database/db_manager.py
import sqlite3

DB_NAME = "salon.db"  # database file name

def connect():
    """Create and return a database connection."""
    return sqlite3.connect(DB_NAME)

def execute_query(query, params=()):
    """Run INSERT, UPDATE, DELETE queries."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def execute_insert(query, params=()):
    """Run INSERT queries and return the inserted row id."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def fetch_one(query, params=()):
    """Run SELECT query and return one record."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return row

def fetch_all(query, params=()):
    """Run SELECT query and return all records."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone1 TEXT,
            phone2 TEXT,
            address TEXT,
            city TEXT,
            district TEXT,
            username TEXT UNIQUE,
            password TEXT,
            role INTEGER DEFAULT 2  -- 1: Admin, 2: Staff, 3: Viewer
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            event_type TEXT,
            guests INTEGER,
            salon TEXT,
            client_name TEXT,
            tc_identity TEXT,
            phone TEXT,
            address TEXT,
            contract_no TEXT,
            contract_date TEXT,
            status TEXT,
            event_price REAL,
            menu_price REAL,
            deposit_percent REAL,
            deposit_amount REAL,
            installments INTEGER,
            payment_type TEXT,
            tahsilatlar TEXT,
            menu_name TEXT,
            menu_detail TEXT,
            special_request TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reservations_event_date
        ON reservations (event_date)
    """)

    conn.commit()
    conn.close()
