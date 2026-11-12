"""Database seeder for UniTrace.
Populates the database with demo users and realistic campus lost & found reports.
Also ensures sample upload images exist in static/uploads/.
"""
import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")


def create_sample_image(filename, title, category, color_bgr):
    """Generate a clean placeholder image using OpenCV if available, or write a minimal PNG."""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return

    try:
        import cv2
        import numpy as np

        width, height = 640, 420
        # Background
        img = np.full((height, width, 3), color_bgr, dtype=np.uint8)
        
        # Subtle top banner / border
        cv2.rectangle(img, (0, 0), (width, 80), (24, 49, 83), -1)
        cv2.rectangle(img, (0, height - 12), (width, height), (57, 120, 198), -1)

        # Header text
        cv2.putText(img, "UniTrace Item Preview", (24, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

        # Center card
        cv2.rectangle(img, (40, 120), (width - 40, height - 40), (255, 255, 255), -1)
        cv2.rectangle(img, (40, 120), (width - 40, height - 40), (200, 215, 235), 2)

        # Category badge
        cv2.rectangle(img, (60, 145), (60 + len(category) * 14 + 20, 175), (234, 242, 255), -1)
        cv2.putText(img, category.upper(), (70, 166),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (57, 120, 198), 1, cv2.LINE_AA)

        # Item title
        cv2.putText(img, title[:30], (60, 230),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (24, 49, 83), 2, cv2.LINE_AA)
        if len(title) > 30:
            cv2.putText(img, title[30:60], (60, 265),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (24, 49, 83), 2, cv2.LINE_AA)

        # Bottom tip
        cv2.putText(img, "Reported on campus * Check item details", (60, 340),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (120, 135, 155), 1, cv2.LINE_AA)

        cv2.imwrite(filepath, img)
    except Exception:
        # Minimal 1x1 fallback PNG if cv2 fails
        minimal_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0'
            b'\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        with open(filepath, "wb") as f:
            f.write(minimal_png)


def seed_database(db_path=DATABASE_PATH, schema_path=SCHEMA_PATH):
    """Seed the database with users and items."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with open(os.path.join(UPLOAD_FOLDER, ".gitkeep"), "w") as f:
        f.write("")

    # 1. Initialize schema
    print(f"Applying schema to {db_path}...")
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    with open(schema_path, "r", encoding="utf-8") as f:
        connection.executescript(f.read())

    cursor = connection.cursor()

    # 2. Clear old data if reseeding
    cursor.execute("DELETE FROM items;")
    cursor.execute("DELETE FROM users;")

    # 3. Insert demo users
    hashed_password = generate_password_hash("password123")
    now_str = datetime.now().isoformat(timespec="seconds")

    users_data = [
        ("Alice Smith", "alice@campus.edu", hashed_password, now_str),
        ("Bob Johnson", "bob@campus.edu", hashed_password, now_str),
        ("Charlie Davis", "charlie@campus.edu", hashed_password, now_str),
    ]

    cursor.executemany(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        users_data
    )
    connection.commit()

    # Fetch inserted user IDs
    user_rows = cursor.execute("SELECT id, email FROM users").fetchall()
    user_map = {row["email"]: row["id"] for row in user_rows}

    # 4. Generate sample upload images
    sample_images = [
        ("calculator.png", "Casio FX-991EX Calculator", "Electronics", (230, 240, 248)),
        ("idcard.png", "Student ID Card - Alice Smith", "ID / Cards", (245, 235, 235)),
        ("waterbottle.png", "Blue Hydro Flask 32oz", "Other", (248, 242, 230)),
        ("backpack.png", "North Face Backpack", "Bags", (235, 235, 242)),
        ("headphones.png", "Sony WH-1000XM4 Headphones", "Electronics", (230, 245, 240)),
        ("keys.png", "Dorm Key Ring with Red Lanyard", "Keys", (242, 235, 248)),
        ("textbook.png", "Organic Chemistry 8th Ed", "Books & Notes", (240, 248, 235)),
        ("keyfob.png", "Toyota Car Key Fob", "Keys", (245, 240, 230)),
        ("jacket.png", "Navy Blue Windbreaker", "Clothing", (235, 242, 248)),
        ("airpods.png", "Apple AirPods Pro", "Electronics", (248, 248, 248)),
    ]

    for img_name, title, cat, bgr in sample_images:
        create_sample_image(img_name, title, cat, bgr)

    # 5. Insert demo items
    today = datetime.now().date()
    items_data = [
        (
            user_map["alice@campus.edu"],
            "Casio FX-991EX Scientific Calculator",
            "Left behind in Science Block Lab 3 on bench 4 after afternoon lab session. Has a small white sticker on the back cover.",
            "Lost",
            "Electronics",
            "Science Block, Lab 3",
            (today - timedelta(days=2)).isoformat(),
            "calculator.png",
            "Open",
            (datetime.now() - timedelta(days=2, hours=3)).isoformat(timespec="seconds")
        ),
        (
            user_map["alice@campus.edu"],
            "Student ID Card - Alice Smith",
            "Standard university ID card with photo and student registration number. Lost somewhere between Central Library and Cafeteria.",
            "Lost",
            "ID / Cards",
            "Central Library 1st Floor",
            (today - timedelta(days=1)).isoformat(),
            "idcard.png",
            "Open",
            (datetime.now() - timedelta(days=1, hours=5)).isoformat(timespec="seconds")
        ),
        (
            user_map["bob@campus.edu"],
            "Blue Hydro Flask Water Bottle (32oz)",
            "Cobalt blue Hydro Flask with a black straw lid. Covered in national park and computer club stickers.",
            "Lost",
            "Other",
            "Sports Complex Gym / Bleachers",
            (today - timedelta(days=3)).isoformat(),
            "waterbottle.png",
            "Open",
            (datetime.now() - timedelta(days=3, hours=1)).isoformat(timespec="seconds")
        ),
        (
            user_map["charlie@campus.edu"],
            "Black The North Face Backpack",
            "Black Borealis backpack containing notebooks, graph paper, and blue pens. Accidentally left on a cafeteria chair during lunch.",
            "Lost",
            "Bags",
            "Main Cafeteria, East Entrance",
            (today - timedelta(days=4)).isoformat(),
            "backpack.png",
            "Open",
            (datetime.now() - timedelta(days=4, hours=2)).isoformat(timespec="seconds")
        ),
        (
            user_map["bob@campus.edu"],
            "Sony WH-1000XM4 Noise-Cancelling Headphones",
            "Found black over-ear wireless headphones sitting on Row F seat 12 after the guest lecture. Turned in for safekeeping.",
            "Found",
            "Electronics",
            "Main Auditorium, Row F",
            (today - timedelta(days=1)).isoformat(),
            "headphones.png",
            "Open",
            (datetime.now() - timedelta(days=1, hours=2)).isoformat(timespec="seconds")
        ),
        (
            user_map["charlie@campus.edu"],
            "Dorm Key Ring with Red Lanyard",
            "Ring with 3 silver keys and a red 'Campus Residence Hall' fabric lanyard found on the couch near the ping pong table.",
            "Found",
            "Keys",
            "Student Center Lounge",
            today.isoformat(),
            "keys.png",
            "Open",
            (datetime.now() - timedelta(hours=4)).isoformat(timespec="seconds")
        ),
        (
            user_map["alice@campus.edu"],
            "Organic Chemistry (8th Edition) Textbook",
            "Hardcover textbook by Paula Yurkanis Bruice. Found on desk 14 with yellow bookmarks inside chapter 6.",
            "Found",
            "Books & Notes",
            "East Wing Study Hall B",
            (today - timedelta(days=2)).isoformat(),
            "textbook.png",
            "Open",
            (datetime.now() - timedelta(days=2, hours=1)).isoformat(timespec="seconds")
        ),
        (
            user_map["bob@campus.edu"],
            "Toyota Remote Key Fob with Carabiner",
            "Found on the tarmac walkway near Parking Lot B space #42. Attached to a small black carabiner clip.",
            "Found",
            "Keys",
            "North Campus Parking Lot B",
            (today - timedelta(days=5)).isoformat(),
            "keyfob.png",
            "Open",
            (datetime.now() - timedelta(days=5, hours=6)).isoformat(timespec="seconds")
        ),
        (
            user_map["charlie@campus.edu"],
            "Navy Blue Windbreaker Jacket",
            "Nike lightweight windbreaker jacket, size M, found draped over the top bleacher bench.",
            "Lost",
            "Clothing",
            "Soccer Field Bleachers",
            (today - timedelta(days=6)).isoformat(),
            "jacket.png",
            "Claimed",
            (datetime.now() - timedelta(days=6, hours=4)).isoformat(timespec="seconds")
        ),
        (
            user_map["alice@campus.edu"],
            "Apple AirPods Pro (2nd Generation)",
            "Found white charging case with AirPods inside. Owner verified their serial number and claimed the item.",
            "Found",
            "Electronics",
            "IT Helpdesk / Computer Lab A",
            (today - timedelta(days=7)).isoformat(),
            "airpods.png",
            "Returned",
            (datetime.now() - timedelta(days=7, hours=2)).isoformat(timespec="seconds")
        ),
    ]

    cursor.executemany("""
        INSERT INTO items (
            user_id, title, description, item_type, category,
            location, item_date, image_filename, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, items_data)

    connection.commit()
    connection.close()

    print("\n[SUCCESS] Database seeded successfully!")
    print(f"Database location: {db_path}")
    print("\nDemo Accounts (password for all is 'password123'):")
    print("  - alice@campus.edu")
    print("  - bob@campus.edu")
    print("  - charlie@campus.edu")
    print(f"\nTotal users created: {len(users_data)}")
    print(f"Total items created: {len(items_data)}")


if __name__ == "__main__":
    seed_database()
