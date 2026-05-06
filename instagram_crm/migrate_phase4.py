"""
migrate_phase4.py — Run once: adds prev_status column to leads table.
Usage: python migrate_phase4.py
"""
import os, sqlite3
from app import create_app

app = create_app()
with app.app_context():
    db_path = os.path.join(app.instance_path, "app.db")
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    cols = [row[1] for row in cur.execute("PRAGMA table_info(leads)").fetchall()]
    if "prev_status" not in cols:
        cur.execute("ALTER TABLE leads ADD COLUMN prev_status VARCHAR(50)")
        conn.commit()
        print("[OK] Added prev_status column to leads table.")
    else:
        print("[--] prev_status already exists. Skipping.")

    conn.close()
    print("Migration complete.")
