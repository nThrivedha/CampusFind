"""CampusFind — Root Workspace & Production WSGI Entrypoint
Allows running locally or deploying on cloud platforms (Render, Railway, Fly.io, etc.).
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "campus_lost_found")

if os.path.exists(APP_DIR):
    os.chdir(APP_DIR)
    if APP_DIR not in sys.path:
        sys.path.insert(0, APP_DIR)
    
    from app import app, init_db
    import seed

    # Ensure database exists and is initialized in new cloud environments
    db_file = os.path.join(APP_DIR, "database.db")
    if not os.path.exists(db_file) or os.path.getsize(db_file) == 0:
        seed.seed_database()
    else:
        init_db()

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        host = os.environ.get("HOST", "127.0.0.1")
        print(f"Starting CampusFind server on http://{host}:{port}...")
        app.run(host=host, port=port, debug=False)
else:
    raise FileNotFoundError(f"Could not find campus_lost_found directory at {APP_DIR}")
