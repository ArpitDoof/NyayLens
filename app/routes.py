
from pathlib import Path
import sqlite3

from flask import Blueprint, jsonify, request
from flask import send_from_directory

main = Blueprint("main", __name__)

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_FILE = ROOT_DIR / "data" / "processed" / "nyayalens_clean.db"


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn



@main.route("/api/judgments", methods=["GET"])
def get_judgments():

    query = request.args.get("q", "").strip()
    year = request.args.get("year", "").strip()

    where_clause = "WHERE 1=1"
    params = []

    if query:
        where_clause += """
            AND (
                title LIKE ?
                OR petitioner LIKE ?
                OR respondent LIKE ?
                OR citation LIKE ?
                OR judge LIKE ?
            )
        """
        search_term = f"%{query}%"
        params.extend([search_term] * 5)

    if year:
        if not year.isdigit() or len(year) != 4:
            return jsonify({"error": "Invalid year"}), 400

        where_clause += " AND year = ?"
        params.append(year)

    with get_db_connection() as conn:

        # Count all matching records.
        total = conn.execute(
            f"SELECT COUNT(*) FROM judgments {where_clause}",
            params
        ).fetchone()[0]

        # Retrieve only the first 100 records.
        rows = conn.execute(
            f"""
            SELECT id, title, petitioner, respondent,
                   citation, decision_date, judge, disposal_nature
            FROM judgments
            {where_clause}
            ORDER BY decision_date DESC
            LIMIT 100
            """,
            params
        ).fetchall()

    return jsonify({
        "total": total,
        "returned": len(rows),
        "results": [dict(row) for row in rows]
    })


@main.route("/")
def home():
    frontend_dir = ROOT_DIR / "frontend"
    return send_from_directory(frontend_dir, "index.html")