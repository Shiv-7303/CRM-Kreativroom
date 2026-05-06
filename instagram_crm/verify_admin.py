import sqlite3
import os

db_path = 'instance/app.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT email, role FROM users WHERE email="admin@kr.com"')
    row = cur.fetchone()
    print("User found:", row)
    conn.close()
else:
    print("Database file not found at", db_path)
