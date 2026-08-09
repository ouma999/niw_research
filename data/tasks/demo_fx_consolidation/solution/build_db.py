"""
Builds environment/data/subsidiary_data.db -- source artifact for
demo_fx_consolidation, mirroring the real Dynamo task's structure
(multiple subsidiaries, exchange rates, multi-year local inflation
data, one subsidiary crossing the highly-inflationary threshold).
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "environment" / "data" / "subsidiary_data.db"


def build():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE subsidiary_inflation (
            subsidiary TEXT,
            fiscal_year_offset INTEGER,  -- 0 = current year, -1, -2 = prior years
            annual_inflation_rate REAL
        )
    """)
    cur.executemany(
        "INSERT INTO subsidiary_inflation VALUES (?, ?, ?)",
        [
            ("Subsidiary Norte", -2, 0.030),
            ("Subsidiary Norte", -1, 0.040),
            ("Subsidiary Norte", 0, 0.035),
            ("Subsidiary Turqueza", -2, 0.420),
            ("Subsidiary Turqueza", -1, 0.350),
            ("Subsidiary Turqueza", 0, 0.280),
        ],
    )

    cur.execute("""
        CREATE TABLE subsidiary_financials (
            subsidiary TEXT,
            translated_net_income_before_remeasurement_usd REAL,
            remeasurement_loss_on_net_monetary_position_usd REAL
        )
    """)
    cur.executemany(
        "INSERT INTO subsidiary_financials VALUES (?, ?, ?)",
        [
            ("Subsidiary Norte", 240_000.00, 0.00),
            ("Subsidiary Turqueza", 510_000.00, 85_000.00),
        ],
    )

    conn.commit()
    conn.close()
    print(f"Wrote {DB_PATH}")


if __name__ == "__main__":
    build()
