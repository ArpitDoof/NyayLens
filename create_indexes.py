
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DB_FILE = ROOT_DIR / "data" / "processed" / "nyayalens_clean.db"

conn = sqlite3.connect(DB_FILE)

indexes = [
    """
    CREATE INDEX IF NOT EXISTS idx_judgments_year
    ON judgments(year)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_judgments_case_id
    ON judgments(case_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_judgments_path
    ON judgments(path)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_judgments_date_order
    ON judgments(
        (substr(decision_date, 7, 4) || '-' ||
         substr(decision_date, 4, 2) || '-' ||
         substr(decision_date, 1, 2))
    )
    """
]

for sql in indexes:
    conn.execute(sql)

conn.commit()

print("Indexes created successfully.")

print(conn.execute(
    "PRAGMA index_list(judgments)"
).fetchall())

conn.close()
