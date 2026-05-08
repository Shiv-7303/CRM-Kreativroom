import sqlite3

conn = sqlite3.connect('instagram_crm/instance/app.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)
for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = cur.fetchall()
    print(f"\n=== {t} ===")
    for c in cols:
        print(f"  {c[1]} ({c[2]})")
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  --> {cur.fetchone()[0]} rows")
conn.close()
