import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("UNITRACE_SECRET_KEY", "change-this-development-key")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB maximum upload

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    """Open a database connection for the current request context."""
    try:
        if "db" not in g:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db
    except RuntimeError:
        connection = sqlite3.connect(DATABASE)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection


@app.teardown_appcontext
def close_db(exception=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tables if they do not exist yet."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                item_type TEXT NOT NULL CHECK (item_type IN ('Lost', 'Found')),
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                item_date TEXT NOT NULL,
                image_filename TEXT,
                status TEXT NOT NULL DEFAULT 'Open'
                    CHECK (status IN ('Open', 'Claimed', 'Returned')),
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
    conn.close()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "info")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}


@app.route("/")
def home():
    search = request.args.get("q", "").strip()
    item_type = request.args.get("type", "").strip()
    category = request.args.get("category", "").strip()

    query = """
        SELECT items.*, users.name AS reporter_name
        FROM items JOIN users ON items.user_id = users.id
        WHERE items.status = 'Open'
    """
    params = []
    if search:
        query += " AND (items.title LIKE ? OR items.description LIKE ? OR items.location LIKE ?)"
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern])
    if item_type in ("Lost", "Found"):
        query += " AND items.item_type = ?"
        params.append(item_type)
    if category:
        query += " AND items.category = ?"
        params.append(category)
    query += " ORDER BY items.created_at DESC"

    with get_db() as db:
        items = db.execute(query, params).fetchall()
        categories = [
            row["category"] for row in db.execute(
                "SELECT DISTINCT category FROM items ORDER BY category"
            ).fetchall()
        ]
        counts = {
            "lost": db.execute("SELECT COUNT(*) FROM items WHERE item_type='Lost' AND status='Open'").fetchone()[0],
            "found": db.execute("SELECT COUNT(*) FROM items WHERE item_type='Found' AND status='Open'").fetchone()[0],
            "returned": db.execute("SELECT COUNT(*) FROM items WHERE status='Returned'").fetchone()[0],
        }
    return render_template(
        "index.html", items=items, categories=categories, counts=counts,
        search=search, selected_type=item_type, selected_category=category
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password of at least 8 characters.", "error")
            return render_template("register.html")
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                    (name, email, generate_password_hash(password), datetime.now().isoformat(timespec="seconds"))
                )
            flash("Account created! You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with that email already exists.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            next_url = request.args.get("next", "")
            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect(url_for("home"))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/report", methods=["GET", "POST"])
@login_required
def report_item():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        item_type = request.form.get("item_type", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        item_date = request.form.get("item_date", "").strip()
        image = request.files.get("image")
        if not all([title, description, item_type, category, location, item_date]):
            flash("Please fill in all required fields.", "error")
            return render_template("report_item.html")
        if item_type not in ("Lost", "Found"):
            abort(400)
        image_filename = None
        if image and image.filename:
            if not allowed_file(image.filename):
                flash("Please upload a PNG, JPG, JPEG, GIF or WEBP image.", "error")
                return render_template("report_item.html")
            safe_name = secure_filename(image.filename)
            unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))
            image_filename = unique_name
        with get_db() as db:
            db.execute("""
                INSERT INTO items
                (user_id, title, description, item_type, category, location, item_date, image_filename, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session["user_id"], title, description, item_type, category,
                location, item_date, image_filename,
                datetime.now().isoformat(timespec="seconds")
            ))
        flash("Your item report has been published.", "success")
        return redirect(url_for("home"))
    return render_template("report_item.html")


@app.route("/item/<int:item_id>")
def item_details(item_id):
    with get_db() as db:
        item = db.execute("""
            SELECT items.*, users.name AS reporter_name, users.email AS reporter_email
            FROM items JOIN users ON items.user_id = users.id
            WHERE items.id = ?
        """, (item_id,)).fetchone()
    if item is None:
        abort(404)
    return render_template("item_details.html", item=item)


@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        items = db.execute(
            "SELECT * FROM items WHERE user_id = ? ORDER BY created_at DESC",
            (session["user_id"],)
        ).fetchall()
    return render_template("dashboard.html", items=items)


@app.route("/item/<int:item_id>/status", methods=["POST"])
@login_required
def update_status(item_id):
    status = request.form.get("status", "")
    if status not in ("Open", "Claimed", "Returned"):
        abort(400)
    with get_db() as db:
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if item is None:
            abort(404)
        if item["user_id"] != session["user_id"]:
            abort(403)
        db.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
    flash("Item status updated.", "success")
    return redirect(url_for("dashboard"))


@app.route("/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    with get_db() as db:
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if item is None:
            abort(404)
        if item["user_id"] != session["user_id"]:
            abort(403)
        db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    flash("Your report has been deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="We couldn't find that page."), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template("error.html", code=403, message="You don't have permission to do that."), 403


@app.errorhandler(413)
def file_too_large(error):
    flash("That image is too large. Please choose an image under 5 MB.", "error")
    return redirect(url_for("report_item"))


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", code=500, message="An internal server error occurred. Please try again later."), 500


init_db()

if __name__ == "__main__":
    app.run(debug=True)
