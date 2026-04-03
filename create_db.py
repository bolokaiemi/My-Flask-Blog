import sqlite3

conn = sqlite3.connect("testimonies.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS testimonies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    content TEXT
)
""")

conn.commit()
conn.close()