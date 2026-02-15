import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/inventory.db")

def get_stockout_risk(store_id: str = "001", days_threshold: float = 7.0) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM inventory WHERE store_id = ?", conn, params=(store_id,))
    conn.close()

    df["avg_daily_sales"] = df["avg_daily_sales"].clip(lower=0.01)
    df["days_of_supply"] = df["on_hand"] / df["avg_daily_sales"]
    df["stockout_risk"] = df["days_of_supply"] < days_threshold

    return df.sort_values(["stockout_risk", "days_of_supply"], ascending=[False, True])
