# models/user_model.py
from backend.database.db_manager import execute_query, fetch_one

def create_table():
    """Ensure the users table exists."""
    from backend.database.db_manager import create_tables
    create_tables()

def add_user(data):
    """Add a new user to the database (role = 2 by default)."""
    execute_query("""
        INSERT INTO users (name, email, phone1, phone2, address, city, district, username, password, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["email"], data["phone1"], data["phone2"],
        data["address"], data["city"], data["district"],
        data["username"], data["password"], 2  # default: Staff
    ))

def get_user_by_username(username):
    """Find a user by username."""
    row = fetch_one("SELECT * FROM users WHERE username = ?", (username,))
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "phone1": row[3],
            "phone2": row[4],
            "address": row[5],
            "city": row[6],
            "district": row[7],
            "username": row[8],
            "password": row[9],
            "role": row[10]
        }
    return None

def get_user_by_email(email):
    """Find a user by email."""
    row = fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "phone1": row[3],
            "phone2": row[4],
            "address": row[5],
            "city": row[6],
            "district": row[7],
            "username": row[8],
            "password": row[9],
            "role": row[10]
        }
    return None
