
from pathlib import Path
import sqlite3
import math

from flask import Blueprint, jsonify, request, send_from_directory

main = Blueprint("main", __name__)

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_FILE = ROOT_DIR / "data" / "processed" / "nyayalens_fts.db"


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@main.route("/api/judgments", methods=["GET"])
def get_judgments():
    order_params = []
    where_params = []
    query = request.args.get("q", "").strip()
    year_from = request.args.get("year_from", "").strip()
    year_to = request.args.get("year_to", "").strip()

    
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Invalid page or per_page"}), 400

    offset = (page - 1) * per_page

    
    sort = request.args.get("sort", "newest")

    if sort not in ("relevance", "newest", "oldest", "az"):
        return jsonify({"error": "Invalid sort option"}), 400

    where_clause = "WHERE 1=1"
    params = []

    if query:
        where_clause += """
            AND id IN(
                SELECT rowid FROM judgments_fts where judgments_fts MATCH ?
            )
        """
        fts_query = '"' + query.replace('"', '""') + '"'
        where_params.append(fts_query)

    
    for value in (year_from, year_to):
        if value and (not value.isdigit() or len(value) != 4):
            return jsonify({"error": "Invalid year"}), 400

    if year_from and year_to and year_from > year_to:
        return jsonify({"error": "Start year cannot exceed end year"}), 400

    if year_from:
        where_clause += " AND year >= ?"
        where_params.append(year_from)

    if year_to:
        where_clause += " AND year <= ?"
        where_params.append(year_to)

    # decision_date is stored as DD-MM-YYYY.
    # Convert it to YYYY-MM-DD for correct chronological sorting.
    date_expr = """
        substr(decision_date, 7, 4) || '-' ||
        substr(decision_date, 4, 2) || '-' ||
        substr(decision_date, 1, 2)
    """

    if sort == "az":
        order_clause = "title COLLATE NOCASE ASC, id ASC"
        # COLLATE NOCASE ASCmaking the sorting case-insensitive and sorted in ASCending order

    elif sort == "oldest":
        order_clause = f"{date_expr} ASC, id ASC"
        #as the data is sorted with year first so sorting in ASC results in the older ones before

    elif sort == "relevance" and query:
        order_clause = """
            CASE
                WHEN LOWER(title) = LOWER(?) THEN 0
                WHEN LOWER(citation) = LOWER(?) THEN 1
                WHEN LOWER(title) LIKE LOWER(?) THEN 2
                ELSE 3
            END,
            (
                SELECT bm25(judgments_fts, 5.0, 3.0, 3.0, 2.0, 5.0)
                FROM judgments_fts
                WHERE judgments_fts.rowid = judgments.id
            ) ASC,
            id DESC
            """

        order_params.extend([
            query,
            query,
            f"{query}%"
        ])

    else:
        order_clause = f"{date_expr} DESC, id DESC"

    with get_db_connection() as conn:

        total = conn.execute(
            f"SELECT COUNT(*) FROM judgments {where_clause}",
            where_params
        ).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT id, title, petitioner, respondent,
                   citation, decision_date, judge, disposal_nature,path,year
            FROM judgments
            {where_clause}
            ORDER BY {order_clause}
            LIMIT ? OFFSET ?
            """,
            where_params + order_params + [per_page, offset]
        ).fetchall()

    total_pages = math.ceil(total / per_page) if total else 0

    results = []

    for row in rows:
        judgment = dict(row)

        path = judgment["path"]
        year = judgment["year"]

        if path and year:
            judgment["pdf_url"] = (
                "https://indian-supreme-court-judgments.s3.amazonaws.com/"
                f"data/pdf/year={year}/english/{path}_EN.pdf"
            )
        else:
            judgment["pdf_url"] = None

        results.append(judgment)

    return jsonify({
        "total": total,
        "returned": len(rows),
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "results": results
    })

   


@main.route("/")
def home():
    frontend_dir = ROOT_DIR / "frontend"
    return send_from_directory(frontend_dir, "index.html")

@main.route("/about")
def about():
    frontend_dir = ROOT_DIR/"frontend"
    return send_from_directory(frontend_dir,"about.html")
