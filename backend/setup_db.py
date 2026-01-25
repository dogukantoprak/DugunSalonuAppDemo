# setup_db.py
from backend.database.db_manager import create_tables

if __name__ == "__main__":
    create_tables()
    print("✅ Database and tables created successfully!")
