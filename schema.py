import sqlite3

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    journey INTEGER,
    date TEXT NOT NULL,
    schedule_start TEXT NOT NULL,
    start TEXT NOT NULL,
    start_point TEXT NOT NULL,
    destination TEXT NOT NULL,
    transport TEXT NOT NULL,
    line TEXT NOT NULL,
    schedule_min INTEGER,
    duration_min INTEGER,
    schedule_arrival TEXT
);
""")

conn.commit()
conn.close()

print("Datenbank erstellt.")
