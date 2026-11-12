"""CampusFind — Root Workspace Launcher
Allows starting the application directly from the workspace root.
"""
import os
import sys

# Ensure campus_lost_found is in Python path and working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "campus_lost_found")

if os.path.exists(APP_DIR):
    os.chdir(APP_DIR)
    sys.path.insert(0, APP_DIR)
    from app import app, init_db

    if __name__ == "__main__":
        init_db()
        print("Starting CampusFind from root workspace launcher...")
        print("Opening: http://127.0.0.1:5000")
        app.run(debug=True)
else:
    raise FileNotFoundError(f"Could not find campus_lost_found directory at {APP_DIR}")
