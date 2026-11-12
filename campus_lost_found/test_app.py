"""Unit and integration test suite for UniTrace Flask application.
Tests authentication, reporting, search/filtering, item management, and access control.
"""
import os
import unittest
import tempfile
import shutil

# Set test environment before importing app
os.environ["UNITRACE_SECRET_KEY"] = "test-secret-key-12345"

from campus_lost_found.app import app, get_db
from campus_lost_found import app as app_module
import campus_lost_found.seed as seed


class UniTraceTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a clean temporary database and test client for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_database.db")
        app.config["TESTING"] = True
        app.config["DATABASE"] = self.db_path
        app.config["WTF_CSRF_ENABLED"] = False

        # Seed the temporary database using seed.py's seed_database function
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        seed.seed_database(db_path=self.db_path, schema_path=schema_path)

        # Patch app.py's DATABASE path for the test run
        self.original_db = app_module.DATABASE
        app_module.DATABASE = self.db_path

        self.client = app.test_client()

    def tearDown(self):
        """Clean up the temporary directory."""
        app_module.DATABASE = self.original_db
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def login(self, email, password):
        """Helper to log in a user."""
        return self.client.post("/login", data={
            "email": email,
            "password": password
        }, follow_redirects=True)

    def logout(self):
        """Helper to log out."""
        return self.client.get("/logout", follow_redirects=True)

    # --- Tests ---

    def test_home_page_loads(self):
        """Verify homepage renders successfully with seeded statistics and items."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Uni", response.data)
        self.assertIn(b"Trace", response.data)
        self.assertIn(b"Casio FX-991EX Scientific Calculator", response.data)

    def test_search_and_filter(self):
        """Verify search query and filters return relevant items."""
        # Search by keyword
        response = self.client.get("/?q=Calculator")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Casio FX-991EX", response.data)
        self.assertNotIn(b"AirPods", response.data)

        # Filter by type Lost
        response = self.client.get("/?type=Lost")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Casio FX-991EX", response.data)

        # Filter by category
        response = self.client.get("/?category=Electronics")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sony WH-1000XM4", response.data)

    def test_user_registration(self):
        """Verify new user registration works and enforces password requirements."""
        # Short password should fail
        response = self.client.post("/register", data={
            "name": "New Student",
            "email": "newstudent@campus.edu",
            "password": "short"
        }, follow_redirects=True)
        self.assertIn(b"at least 8 characters", response.data)

        # Valid registration
        response = self.client.post("/register", data={
            "name": "New Student",
            "email": "newstudent@campus.edu",
            "password": "password123"
        }, follow_redirects=True)
        self.assertIn(b"Account created", response.data)

        # Duplicate email should fail
        response = self.client.post("/register", data={
            "name": "Another Student",
            "email": "newstudent@campus.edu",
            "password": "password123"
        }, follow_redirects=True)
        self.assertIn(b"already exists", response.data)

    def test_login_and_logout(self):
        """Verify login with correct credentials and rejection of invalid passwords."""
        # Invalid password
        response = self.login("alice@campus.edu", "wrongpassword")
        self.assertIn(b"Email or password is incorrect", response.data)

        # Valid password
        response = self.login("alice@campus.edu", "password123")
        self.assertIn(b"Welcome back, Alice Smith", response.data)

        # Logout
        response = self.logout()
        self.assertIn(b"You have been logged out", response.data)

    def test_report_item_requires_auth(self):
        """Verify unauthenticated user is redirected to login when trying to report."""
        response = self.client.get("/report")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_report_item_success(self):
        """Verify logged in user can report a lost or found item."""
        self.login("alice@campus.edu", "password123")
        response = self.client.post("/report", data={
            "title": "Lost Graphing Notebook",
            "description": "Black spiral bound notebook left in Room 204",
            "item_type": "Lost",
            "category": "Books & Notes",
            "location": "Room 204",
            "item_date": "2026-11-12"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your item report has been published", response.data)
        self.assertIn(b"Lost Graphing Notebook", response.data)

    def test_item_details_and_reporter_email(self):
        """Verify item details page shows item info and contact email when logged in."""
        # Unauthenticated view
        response = self.client.get("/item/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Casio FX-991EX", response.data)
        self.assertIn(b"Log in to contact reporter", response.data)

        # Authenticated view as another user (Bob)
        self.login("bob@campus.edu", "password123")
        response = self.client.get("/item/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"alice@campus.edu", response.data)

    def test_item_not_found(self):
        """Verify 404 is returned for non-existent item."""
        response = self.client.get("/item/99999")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404", response.data)

    def test_dashboard_and_item_status_update(self):
        """Verify user dashboard lists user's items and allows status updates."""
        self.login("alice@campus.edu", "password123")
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Casio FX-991EX", response.data)

        # Update status of item 1
        response = self.client.post("/item/1/status", data={"status": "Claimed"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Item status updated", response.data)

    def test_status_update_forbidden_for_non_owner(self):
        """Verify a user cannot update someone else's item status."""
        self.login("bob@campus.edu", "password123")
        # Item 1 belongs to Alice
        response = self.client.post("/item/1/status", data={"status": "Claimed"})
        self.assertEqual(response.status_code, 403)

    def test_delete_item_owner_and_forbidden(self):
        """Verify item owner can delete report, but non-owner gets 403."""
        # Non-owner attempt
        self.login("bob@campus.edu", "password123")
        response = self.client.post("/item/1/delete")
        self.assertEqual(response.status_code, 403)

        # Owner attempt
        self.logout()
        self.login("alice@campus.edu", "password123")
        response = self.client.post("/item/1/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your report has been deleted", response.data)

    def test_favicon_route(self):
        """Verify /favicon.ico serves the icon without error."""
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
