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

    conn.commit()
    conn.close()