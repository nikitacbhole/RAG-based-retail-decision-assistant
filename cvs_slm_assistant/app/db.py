import sqlite3
from pathlib import Path

DB_PATH = Path("data/inventory.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        store_id TEXT,
        sku TEXT,
        on_hand INTEGER,
        on_order INTEGER,
        avg_daily_sales REAL,
        last_updated TEXT
    )
    """)

    cur.execute("DELETE FROM inventory")

    rows = [
        ("001", "SKU-A", 10, 0, 3.0, "2026-02-12"),
        ("001", "SKU-B", 40, 20, 2.0, "2026-02-12"),
        ("001", "SKU-C", 5,  0, 1.5, "2026-02-12"),
        ("001", "SKU-D", 60, 0, 8.0, "2026-02-12"),
    ]
    cur.executemany("INSERT INTO inventory VALUES (?,?,?,?,?,?)", rows)

    conn.commit()
    conn.close()
    print("✅ SQLite DB initialized at data/inventory.db")

if __name__ == "__main__":
    init_db()
