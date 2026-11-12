# CampusFind — Campus Lost & Found Management System

CampusFind is a complete full-stack web application designed for university campuses. It allows students and campus staff to report lost and found belongings, browse and search community listings, filter by categories and report types, and manage their own reports.

---

## Quickstart (Windows)

### Option 1: One-Click Launch (Recommended)
Double-click or run `run.bat` (or `.\run.ps1` in PowerShell) in this directory:
```cmd
run.bat
```
This automatically sets up the Python virtual environment, installs dependencies, verifies the pre-populated database, and starts the server.

### Option 2: Manual Terminal Run
```powershell
# 1. Navigate to the application directory
cd campus_lost_found

# 2. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install required packages
python -m pip install -r requirements.txt

# 4. Start the application
python app.py
```

Open your browser to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## Demo Accounts

The database comes pre-seeded with sample users and realistic campus listings:

| Name | Email | Password | Role |
| :--- | :--- | :--- | :--- |
| **Alice Smith** | `alice@campus.edu` | `password123` | Student / Reporter |
| **Bob Johnson** | `bob@campus.edu` | `password123` | Student / Reporter |
| **Charlie Davis** | `charlie@campus.edu` | `password123` | Student / Reporter |

---

## Project Structure

```
CampusFind_Complete_Project/
├── app.py                      # Root launcher proxy (run: python app.py)
├── run.bat                     # Root Windows batch launcher
├── run.ps1                     # Root PowerShell launcher
├── README.md                   # Project overview & quickstart guide
├── .gitignore                  # Git ignore rules for root workspace
└── campus_lost_found/          # Main application package
    ├── app.py                  # Flask routes, auth, session & error handling
    ├── database.db             # Pre-populated SQLite database
    ├── schema.sql              # Standalone SQL schema DDL with indexes
    ├── seed.py                 # Database reset & demo seeder script
    ├── init_db.py              # Database schema initialization script
    ├── test_app.py             # Automated unit & integration test suite (12 tests)
    ├── requirements.txt        # Flask & Python dependencies
    ├── run.bat                 # App-level Windows batch launcher
    ├── run.ps1                 # App-level PowerShell launcher
    ├── .env.example            # Environment variables template
    ├── .gitignore              # App-level Git ignore rules
    ├── static/
    │   ├── css/
    │   │   └── style.css       # Responsive styling & design system
    │   ├── js/
    │   │   └── script.js       # Mobile navigation & interactions
    │   ├── favicon.svg         # Brand favicon (SVG)
    │   ├── favicon.ico         # Brand favicon (ICO)
    │   └── uploads/            # Uploaded photos & seeded item images
    │       ├── calculator.png
    │       ├── idcard.png
    │       ├── headphones.png
    │       ├── backpack.png
    │       └── ...
    └── templates/
        ├── base.html           # Base layout, navbar, flash alerts & footer
        ├── index.html          # Homepage with stats, search & item cards
        ├── report_item.html    # Form to post a lost/found item with photo
        ├── item_details.html   # Detailed view with photo & reporter contact
        ├── dashboard.html      # User dashboard to edit status & delete reports
        ├── login.html          # Authentication login page
        ├── register.html       # Student registration page
        └── error.html          # Error pages (403, 404, 500)
```

---

## Database Management & Seeding

- **Re-seed database anytime**:
  ```powershell
  python campus_lost_found/seed.py
  ```
- **Apply raw schema**:
  ```powershell
  python campus_lost_found/init_db.py
  ```

---

## Running Automated Tests

A comprehensive automated test suite covers homepage statistics, search/filtering, registration, login/logout, report publishing, ownership permissions, and status transitions:

```powershell
cd campus_lost_found
python -m unittest test_app.py -v
```
