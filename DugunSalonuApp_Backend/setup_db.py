# setup_db.py
from DugunSalonuApp_Backend.database.db_manager import create_tables

if __name__ == "__main__":
    create_tables()
    print("✅ Database and tables created successfully!")
