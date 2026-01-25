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
            bride_name TEXT,
            groom_name TEXT,
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
            region TEXT,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reservations_event_date
        ON reservations (event_date)
    """)

    # Backward-compatible column additions
    for column in ("bride_name", "groom_name", "region", "note"):
        try:
            cursor.execute(f"ALTER TABLE reservations ADD COLUMN {column} TEXT")
        except sqlite3.OperationalError:
            # Column already exists
            pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings_salons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            capacity INTEGER,
            price_factor REAL DEFAULT 1.0,
            color TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings_menus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            content TEXT,
            price_per_person REAL DEFAULT 0.0,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings_event_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            default_duration INTEGER,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    # Seed default data if empty
    cursor.execute("SELECT COUNT(*) FROM settings_salons")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO settings_salons (name) VALUES (?)", [("Salon A",), ("Salon B",), ("Salon C",)])

    cursor.execute("SELECT COUNT(*) FROM settings_menus")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO settings_menus (name) VALUES (?)", [("Standart Menu",), ("Luks Menu",)])

    cursor.execute("SELECT COUNT(*) FROM settings_event_types")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO settings_event_types (name) VALUES (?)", [("Düğün",), ("Nişan",), ("Kına",), ("Toplantı",), ("Mezuniyet",)])

    # --- Personnel Tables ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT,
            phone TEXT,
            staff_type TEXT DEFAULT 'full_time',  -- 'full_time' or 'part_time'
            wage REAL DEFAULT 0.0,  -- Daily rate for part-time, monthly for full-time
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reservation_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            payment_status TEXT DEFAULT 'pending',  -- 'pending', 'paid'
            notes TEXT,
            FOREIGN KEY (reservation_id) REFERENCES reservations(id),
            FOREIGN KEY (staff_id) REFERENCES staff(id)
        )
    """)

    # --- Financial Tables ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            reservation_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reservation_id) REFERENCES reservations(id)
        )
    """)

    conn.commit()
    conn.close()
