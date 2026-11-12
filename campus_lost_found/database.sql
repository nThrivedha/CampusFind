-- UniTrace SQLite Database Dump
-- Compatible with SQLite3, DB Browser for SQLite, and GitHub web viewer.
-- This file allows viewing the full database structure and sample data directly as text in Git.
-- To import into SQLite: sqlite3 database.db < database.sql

BEGIN TRANSACTION;
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('Lost', 'Found')),
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    item_date TEXT NOT NULL,
    image_filename TEXT,
    status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Claimed', 'Returned')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
INSERT INTO "items" VALUES(1,1,'Casio FX-991EX Scientific Calculator','Left behind in Science Block Lab 3 on bench 4 after afternoon lab session. Has a small white sticker on the back cover.','Lost','Electronics','Science Block, Lab 3','2026-11-10','calculator.png','Open','2026-11-10T19:11:25');
INSERT INTO "items" VALUES(2,1,'Student ID Card - Alice Smith','Standard university ID card with photo and student registration number. Lost somewhere between Central Library and Cafeteria.','Lost','ID / Cards','Central Library 1st Floor','2026-11-11','idcard.png','Open','2026-11-11T17:11:25');
INSERT INTO "items" VALUES(3,2,'Blue Hydro Flask Water Bottle (32oz)','Cobalt blue Hydro Flask with a black straw lid. Covered in national park and computer club stickers.','Lost','Other','Sports Complex Gym / Bleachers','2026-11-09','waterbottle.png','Open','2026-11-09T21:11:25');
INSERT INTO "items" VALUES(4,3,'Black The North Face Backpack','Black Borealis backpack containing notebooks, graph paper, and blue pens. Accidentally left on a cafeteria chair during lunch.','Lost','Bags','Main Cafeteria, East Entrance','2026-11-08','backpack.png','Open','2026-11-08T20:11:25');
INSERT INTO "items" VALUES(5,2,'Sony WH-1000XM4 Noise-Cancelling Headphones','Found black over-ear wireless headphones sitting on Row F seat 12 after the guest lecture. Turned in for safekeeping.','Found','Electronics','Main Auditorium, Row F','2026-11-11','headphones.png','Open','2026-11-11T20:11:25');
INSERT INTO "items" VALUES(6,3,'Dorm Key Ring with Red Lanyard','Ring with 3 silver keys and a red ''Campus Residence Hall'' fabric lanyard found on the couch near the ping pong table.','Found','Keys','Student Center Lounge','2026-11-12','keys.png','Open','2026-11-12T18:11:25');
INSERT INTO "items" VALUES(7,1,'Organic Chemistry (8th Edition) Textbook','Hardcover textbook by Paula Yurkanis Bruice. Found on desk 14 with yellow bookmarks inside chapter 6.','Found','Books & Notes','East Wing Study Hall B','2026-11-10','textbook.png','Open','2026-11-10T21:11:25');
INSERT INTO "items" VALUES(8,2,'Toyota Remote Key Fob with Carabiner','Found on the tarmac walkway near Parking Lot B space #42. Attached to a small black carabiner clip.','Found','Keys','North Campus Parking Lot B','2026-11-07','keyfob.png','Open','2026-11-07T16:11:25');
INSERT INTO "items" VALUES(9,3,'Navy Blue Windbreaker Jacket','Nike lightweight windbreaker jacket, size M, found draped over the top bleacher bench.','Lost','Clothing','Soccer Field Bleachers','2026-11-06','jacket.png','Claimed','2026-11-06T18:11:25');
INSERT INTO "items" VALUES(10,1,'Apple AirPods Pro (2nd Generation)','Found white charging case with AirPods inside. Owner verified their serial number and claimed the item.','Found','Electronics','IT Helpdesk / Computer Lab A','2026-11-05','airpods.png','Returned','2026-11-05T20:11:25');
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);
INSERT INTO "users" VALUES(1,'Alice Smith','alice@campus.edu','scrypt:32768:8:1$LAbieO2YfOEa2fEO$593fc6aec9aea9e08b44d87329545af4f8967dff9ac4938df091233e4a6a169bfb8553816200a1c075945592110949b037d0ad809e2adaa62883d1d41db3ef56','2026-11-12T22:11:25');
INSERT INTO "users" VALUES(2,'Bob Johnson','bob@campus.edu','scrypt:32768:8:1$LAbieO2YfOEa2fEO$593fc6aec9aea9e08b44d87329545af4f8967dff9ac4938df091233e4a6a169bfb8553816200a1c075945592110949b037d0ad809e2adaa62883d1d41db3ef56','2026-11-12T22:11:25');
INSERT INTO "users" VALUES(3,'Charlie Davis','charlie@campus.edu','scrypt:32768:8:1$LAbieO2YfOEa2fEO$593fc6aec9aea9e08b44d87329545af4f8967dff9ac4938df091233e4a6a169bfb8553816200a1c075945592110949b037d0ad809e2adaa62883d1d41db3ef56','2026-11-12T22:11:25');
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_item_type ON items(item_type);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_created_at ON items(created_at DESC);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('users',3);
INSERT INTO "sqlite_sequence" VALUES('items',10);
COMMIT;
