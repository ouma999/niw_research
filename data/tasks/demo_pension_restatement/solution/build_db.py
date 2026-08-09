"""
Builds environment/data/plan_data.db -- source artifacts for
demo_pension_restatement.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "environment" / "data" / "plan_data.db"


def build():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE census_summary (
            group_name TEXT,
            hire_date_cutoff TEXT,
            participant_count INTEGER,
            full_year_service_cost REAL
        )
    """)
    cur.executemany(
        "INSERT INTO census_summary VALUES (?, ?, ?, ?)",
        [
            ("Group A", "hired before 2010-01-01", 64, 180000.00),
            ("Group B", "hired on or after 2010-01-01", 111, 360000.00),
        ],
    )

    cur.execute("""
        CREATE TABLE separations_log (
            group_name TEXT,
            separation_reason TEXT,
            participant_count INTEGER,
            separation_effective_date TEXT,
            full_year_equivalent_service_cost REAL
        )
    """)
    cur.executemany(
        "INSERT INTO separations_log VALUES (?, ?, ?, ?, ?)",
        [
            ("Group B", "vested termination", 30, "2024-03-31", 90000.00),
        ],
    )

    cur.execute("""
        CREATE TABLE prior_period_ledger (
            component TEXT,
            amount REAL
        )
    """)
    cur.executemany(
        "INSERT INTO prior_period_ledger VALUES (?, ?)",
        [
            ("service_cost", 402500.00),
            ("interest_cost", 285000.00),
            ("expected_return_on_assets", -241000.00),
            ("amortization_net_actuarial_loss", 47500.00),
            ("total_booked_expense_prior_period", 494000.00),
        ],
    )

    conn.commit()
    conn.close()
    print(f"Wrote {DB_PATH}")


if __name__ == "__main__":
    build()
