
import sqlite3
from pathlib import Path

DB_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "processed"
    / "nyayalens_fts.db"
)

conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row
#aise warna normal tuple form mai aati row and now we convert them into row form and now we access them using row["id"]

search_query = "Kant"

sql = """
    SELECT
        j.id,
        j.title,
        j.citation,
        bm25(judgments_fts) AS relevance_score
    FROM judgments_fts
    JOIN judgments AS j
        ON j.id = judgments_fts.rowid
    WHERE judgments_fts MATCH ?
    ORDER BY relevance_score
    LIMIT 10
"""
#BM25 is a ranking algorithm used to determine how relevant a document is to a search query. 
rows = conn.execute(sql, (search_query,)).fetchall()

for row in rows:
    print("-" * 70)
    print("ID:", row["id"])
    print("Title:", row["title"])
    print("Citation:", row["citation"])
    print("Relevance score:", row["relevance_score"])

print("\nTotal results shown:", len(rows))

conn.close()
