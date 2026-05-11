import sqlite3

conn = sqlite3.connect("parsed_pages.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        title TEXT,
        approach TEXT
    )
""")
conn.commit()
conn.close()
print("БД готова")
