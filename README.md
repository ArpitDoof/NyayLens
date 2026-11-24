# NyayLens

**Making Indian Supreme Court judgments easier to discover and access.**

NyayLens is a web-based legal judgment search application. It provides keyword-based full-text search, BM25 relevance ranking, year filtering, sorting, pagination, judgment metadata, and links to original English judgment PDFs.

- **Repository:** https://github.com/ArpitDoof/NyayLens
- **Dataset:** [Indian Supreme Court Judgments](https://huggingface.co/datasets/labofsahil/Indian-Supreme-Court-Judgments)
- **Dataset licence:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

## Features

- Full-text keyword search using SQLite FTS5.
- BM25 relevance ranking with configurable weights for title, petitioner, respondent, judge, and citation.
- Optional year-range filtering.
- Sorting by relevance, newest, oldest, or case title (A–Z).
- Paginated search results.
- Display of available judgment metadata.
- Direct links to original English judgment PDFs hosted on AWS S3.
- An About page describing the project, data source, and limitations.

## Technology stack

| Layer | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Database | SQLite |
| Full-text search | SQLite FTS5 |
| Relevance ranking | BM25 |
| HTML parsing | BeautifulSoup |
| Data formats / exploration | Parquet, Jupyter Notebook |
| Production server | Gunicorn |
| Version control | Git, GitHub |

## Repository structure

The tree below reflects the files currently present on the `main` branch. A `.gitkeep` file is used in otherwise-empty directories to ensure Git tracks the directory.

```text
NyayLens/
├── app.py
├── wsgi.py
├── buildfts.py
├── create_indexes.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── templates/
│   │   └── .gitkeep
│   └── .gitkeep
│
├── frontend/
│   ├── index.html
│   └── about.html
│
├── src/
│   ├── scraper/
│   │   ├── scraper.py
│   │   └── .gitkeep
│   └── database/
│       └── .gitkeep
│
├── data/
│   └── processed/
│       ├── cases_2025.parquet
│       ├── nyayalens_clean.db
│       ├── nyayalens_fts.db
│       └── nyayalens_full.db
│
└── notebooks/
    └── 01_data_exploration.ipynb
```

## Code organisation and file responsibilities

### 1. Root-level application files

| File | Responsibility |
|---|---|
| `app.py` | Local development entry point. Imports `create_app()`, creates the Flask application, and starts Flask's development server when run directly. |
| `wsgi.py` | Exposes the Flask instance as `application` so a WSGI server such as Gunicorn can serve it. |
| `requirements.txt` | Lists the Python packages and pinned versions used by the project environment. |
| `.gitignore` | Prevents generated or machine-specific files from being tracked, including the virtual environment, Python cache, raw data, environment files, and editor settings. |
| `README.md` | Project overview, setup guide, API notes, and documentation of the repository structure. |

### 2. `app/` — Flask backend

This package contains the web application and its HTTP routes.

| File / directory | Responsibility |
|---|---|
| `app/__init__.py` | Defines the `create_app()` application factory. It creates the Flask instance, imports the `main` blueprint, registers it, and returns the configured app. |
| `app/routes.py` | Implements the website routes and the `GET /api/judgments` endpoint. It reads request parameters, validates pagination, sorting, and year filters, queries SQLite/FTS5, applies ordering and pagination, builds PDF URLs, and returns JSON results. |
| `app/templates/` | Reserved for Flask/Jinja templates. It currently contains only `.gitkeep`; the pages used by the application are in `frontend/` and are served directly. |
| `app/.gitkeep` | Keeps the package directory represented in Git; it has no runtime behaviour. |

The database path used by the API is defined in `app/routes.py`:

```python
data/processed/nyayalens_fts.db
```

The `get_db_connection()` helper opens this SQLite database and configures rows so they can be accessed by column name.

### 3. `frontend/` — user interface

The frontend consists of standalone HTML pages with their styling and browser-side JavaScript.

| File | Responsibility |
|---|---|
| `frontend/index.html` | Main search interface. It contains the search controls, year filters, sorting controls, results area, and pagination. Its JavaScript sends requests to the Flask API and renders the returned judgment records. |
| `frontend/about.html` | About page describing NyayLens, its features and workflow, dataset attribution, and the legal-information disclaimer. |

The Flask routes serve these pages:

- `/` serves `frontend/index.html`.
- `/about` serves `frontend/about.html`.

### 4. `src/` — supporting data and scraping code

| File / directory | Responsibility |
|---|---|
| `src/scraper/scraper.py` | Defines `extract_case_details(html)`. It parses supplied HTML with BeautifulSoup and extracts the case title, available coram information, and key-value case details from the relevant case-details element. |
| `src/scraper/.gitkeep` | Directory placeholder; no runtime behaviour. |
| `src/database/.gitkeep` | Keeps the database source directory in Git. No database import script is currently present in this directory on `main`. |

### 5. `data/processed/` — processed datasets and databases

| File | Responsibility |
|---|---|
| `nyayalens_clean.db` | Cleaned SQLite database containing the structured judgment records. It is the source database copied by `buildfts.py`. |
| `nyayalens_fts.db` | SQLite database used by the running application. It contains the judgment records and the FTS5 virtual table used for full-text search. |
| `nyayalens_full.db` | Additional processed database retained in the repository. The current API configuration does not connect to this file. |
| `cases_2025.parquet` | Processed Parquet dataset retained in the repository. |

The application reads from `nyayalens_fts.db`; the clean database is used as the starting point when generating the FTS-enabled database.

### 6. Database utility scripts

| File | Responsibility |
|---|---|
| `create_indexes.py` | Creates SQLite indexes on the clean database for frequently used lookup and ordering fields: `year`, `case_id`, `path`, and a date expression derived from `decision_date`. These indexes are intended to improve filtering and ordering performance. |
| `buildfts.py` | Copies `nyayalens_clean.db` to `nyayalens_fts.db`, creates an external-content FTS5 table named `judgments_fts`, and rebuilds the full-text index from the `judgments` table. |

**Important:** These scripts modify or create database files under `data/processed/`. Run them only when you intend to regenerate the relevant database or index.

### 7. `notebooks/` — exploration

| File | Responsibility |
|---|---|
| `notebooks/01_data_exploration.ipynb` | Jupyter notebook for exploring and inspecting the judgment dataset during development. |

## Application workflow

1. A user enters a search phrase and may select a year range, sort order, and page.
2. The browser-side code in `frontend/index.html` sends a GET request to `/api/judgments`.
3. The route in `app/routes.py` validates the request parameters.
4. For a non-empty keyword query, SQLite FTS5 matches records through the `judgments_fts` virtual table.
5. The backend applies the year filters, requested ordering, and pagination.
6. The API returns judgment metadata and pagination information as JSON.
7. When a record has a document path and year, the backend constructs a URL for its original English PDF on the public AWS S3 dataset endpoint. The frontend exposes that link to the user.

## Full-text search and relevance ranking

The FTS5 virtual table created by `buildfts.py` indexes these judgment metadata fields:

- `title`
- `petitioner`
- `respondent`
- `judge`
- `citation`

For relevance sorting, `app/routes.py` calls SQLite's BM25 ranking function with the following field weights:

| Field | Weight |
|---|---:|
| Title | 5.0 |
| Petitioner | 3.0 |
| Respondent | 3.0 |
| Judge | 2.0 |
| Citation | 5.0 |

The query orders by the BM25 value in ascending order; within SQLite FTS5, a numerically lower BM25 value represents a better match.

## API reference

### `GET /api/judgments`

| Parameter | Description |
|---|---|
| `q` | Optional keyword query. |
| `year_from` | Optional lower year bound. |
| `year_to` | Optional upper year bound. |
| `sort` | Sort order: `relevance`, `newest`, `oldest`, or `az`. Defaults to `newest`. |
| `page` | 1-based page number. Defaults to `1`. |
| `per_page` | Number of results per page. Defaults to `20`; maximum is `100`. |

Example request:

```text
/api/judgments?q=fundamental%20rights&year_from=2000&year_to=2024&sort=relevance&page=1&per_page=20
```

The JSON response includes:

- `total`: total number of matching records.
- `returned`: number of records in the current response.
- `page`, `per_page`, and `total_pages`: pagination details.
- `has_next` and `has_prev`: whether adjacent pages exist.
- `results`: the judgment metadata for the current page, including `pdf_url` when a PDF path can be constructed.

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/ArpitDoof/NyayLens.git
cd NyayLens
```

### 2. Create and activate a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

Open the local address printed by Flask (usually [http://127.0.0.1:5000/](http://127.0.0.1:5000/)).

The repository contains the processed SQLite databases. The search API specifically expects `data/processed/nyayalens_fts.db` to be present.

### Production serving

The WSGI application is exposed in `wsgi.py`. It can be served with Gunicorn:

```bash
gunicorn wsgi:application
```

## Dataset and attribution

NyayLens uses the [Indian Supreme Court Judgments dataset](https://huggingface.co/datasets/labofsahil/Indian-Supreme-Court-Judgments) published by `labofsahil`. The dataset page identifies the licence as [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). Refer to the original dataset page for complete attribution information and applicable conditions.

The application constructs links to original English judgment PDFs using the document path and year associated with each record.

## Scope and limitations

- The application performs full-text retrieval over the fields indexed in SQLite FTS5; it does not currently implement semantic search.
- Results depend on the metadata available in the dataset and the fields populated in the search index.
- `src/database/`, `app/templates/`, and other placeholder directories may be intended for future development; they currently contain no implemented modules beyond placeholders.
- NyayLens is a legal information retrieval project. It does not provide legal advice or replace consultation with a qualified legal professional.

## Disclaimer

NyayLens is an academic project intended to make publicly available Indian Supreme Court judgment information easier to search and access. Users should consult the original judgment and authoritative legal sources before relying on information for legal purposes.
