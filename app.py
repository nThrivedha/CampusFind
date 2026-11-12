"""CampusFind — Root Workspace & Production WSGI Entrypoint
Imports the Flask application from campus_lost_found and initializes database if needed.
"""
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
APP_DIR = os.path.join(BASE_DIR, "campus_lost_found")

# Ensure campus_lost_found is in sys.path
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from campus_lost_found.app import app, get_db, init_db, DATABASE, UPLOAD_FOLDER
import campus_lost_found.seed as seed

# Ensure database exists and is initialized in new cloud environments
db_file = os.path.join(APP_DIR, "database.db")
if not os.path.exists(db_file) or os.path.getsize(db_file) == 0:
    schema_file = os.path.join(APP_DIR, "schema.sql")
    seed.seed_database(db_path=db_file, schema_path=schema_file)
else:
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting CampusFind server on http://{host}:{port}...")
    app.run(host=host, port=port, debug=False)
