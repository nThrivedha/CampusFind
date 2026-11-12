# UniTrace — Campus Lost & Found Management System

UniTrace is a student full-stack web project that lets campus users create accounts, report lost or found belongings, browse and search reports, and manage their own listings.

## Technology
- HTML5 and CSS3
- JavaScript
- Python with Flask
- SQLite
- VS Code

## Run on Windows

### Quickest: Double-click `run.bat`
You can simply double-click or run `run.bat` (or `.\run.ps1` in PowerShell). It automatically handles the virtual environment, installs dependencies, verifies the pre-populated database, and boots up the Flask server.

### Manual Setup:
1. Open this `campus_lost_found` folder in VS Code or your terminal.
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
3. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks script execution, use Command Prompt:
   ```bat
   .venv\Scripts\activate.bat
   ```
4. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Start the application:
   ```powershell
   python app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database (`database.db`) comes pre-seeded with sample users and items. Uploaded images are stored in `static/uploads/`.

## Demo Accounts

You can log in immediately using any of these test accounts (password for all is `password123`):
- `alice@campus.edu`
- `bob@campus.edu`
- `charlie@campus.edu`

Or create a new account via the **Register** page.

## Database & Utilities
- `database.db`: SQLite database file with tables (`users`, `items`) and seeded listings.
- `schema.sql`: Clean SQL DDL schema definitions, foreign key constraints, and performance indexes.
- `seed.py`: Seeder script that resets and populates the database with realistic demo accounts and sample reports.
- `init_db.py`: Initializes the database tables directly from `schema.sql`.
- `test_app.py`: Automated test suite covering auth, reporting, search/filtering, and permissions. Run via:
  ```powershell
  python -m unittest test_app.py -v
  ```

## Main features
- Register and log in with hashed passwords.
- Report lost or found items with optional photos.
- Search by title, description, or location.
- Filter by report type and category.
- View item details and contact the reporter via email.
- View and manage your own reports from the dashboard.
- Update a report's status (Open / Claimed / Returned) or delete your own report.

## Viva overview
- `app.py`: Flask routes, input validation, login sessions, database operations and upload handling.
- `schema.sql`: Relational database schema with foreign keys and indexes.
- `database.db`: SQLite relational database.
- `templates/`: HTML pages rendered by Flask using Jinja templates.
- `static/css/style.css`: Visual design, color palette, and responsive layout.
- `static/js/script.js`: Mobile navigation toggle, delete confirmations, and auto-dismiss alerts.
- `static/uploads/`: Storage for item images.
