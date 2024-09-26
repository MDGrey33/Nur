import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def create_table():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pages
                      (id TEXT PRIMARY KEY, content TEXT)''')
    conn.commit()
    conn.close()

def add_or_update_page(file_id, content):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO pages (id, content)
                      VALUES (?, ?)''', (file_id, content))
    conn.commit()
    conn.close()