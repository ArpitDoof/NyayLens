import sqlite3
from pathlib import Path

conn = sqlite3.connect(
    Path("data/processed/nyayalens_fts.db")
)

rows = conn.execute("""
    SELECT id, path, year, title
    FROM judgments
    LIMIT 10
""").fetchall()

for row in rows:
    id, path, year, title = row

    url = (
        "https://indian-supreme-court-judgments.s3.amazonaws.com/"
        f"data/pdf/year={year}/english/{path}_EN.pdf"
    )

    print(id, title)
    print(url)
    print()

conn.close()