"""Database initialization script for UniTrace.
Executes schema.sql to set up database tables and indexes.
"""
import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")


def init_database(db_path=DATABASE_PATH, schema_path=SCHEMA_PATH):
    """Initialize the SQLite database with schema.sql."""
    print(f"Connecting to database at: {db_path}")
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    connection.executescript(schema_sql)
    connection.commit()
    connection.close()
    print("Database schema successfully applied.")


if __name__ == "__main__":
    init_database()
