
from pathlib import Path
import sqlite3
import shutil

ROOT_DIR = Path(__file__).resolve().parent

SOURCE_DB = ROOT_DIR / "data" / "processed" / "nyayalens_clean.db"
FTS_DB = ROOT_DIR / "data" / "processed" / "nyayalens_fts.db"


shutil.copy2(SOURCE_DB, FTS_DB)

conn = sqlite3.connect(FTS_DB)

try:
   
    conn.execute("""
        CREATE VIRTUAL TABLE judgments_fts USING fts5(
            title,
            petitioner,
            respondent,
            judge,
            citation,
            content='judgments',
            content_rowid='id'
        )
    """)

    
    conn.execute("""
        INSERT INTO judgments_fts(judgments_fts)
        VALUES ('rebuild')
    """)

    conn.commit()

    count = conn.execute(
        "SELECT COUNT(*) FROM judgments"
    ).fetchone()[0]

    print("FTS5 index created successfully!")
    print("Judgments indexed:", count)

finally:
    conn.close()
