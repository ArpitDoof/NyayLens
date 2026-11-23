# NyayaLens

**Making Indian Supreme Court judgments easier to discover and access.**

NyayaLens is a web-based legal judgment search application. It provides
keyword-based full-text search, BM25 relevance ranking, year filtering,
sorting, pagination, judgment metadata, and links to original English
judgment PDFs.

-   **Repository:** https://github.com/ArpitDoof/NyayLens
-   **Dataset:** [Indian Supreme Court
    Judgments](https://huggingface.co/datasets/labofsahil/Indian-Supreme-Court-Judgments)
-   **Dataset licence:** [CC BY
    4.0](https://creativecommons.org/licenses/by/4.0/)

## Features

-   Full-text keyword search using SQLite FTS5.
-   BM25 relevance ranking with configured weights for title,
    petitioner, respondent, judge, and citation.
-   Optional year-range filtering.
-   Sorting by relevance, newest, oldest, or case title (A--Z).
-   Paginated search results.
-   Display of available judgment metadata.
-   Direct links to original English judgment PDFs hosted on AWS S3.
-   An About page describing the project, data source, and limitations.

## Technology stack

  Layer               Technologies
  ------------------- -----------------------
  Frontend            HTML, CSS, JavaScript
  Backend             Python, Flask
  Database            SQLite
  Full-text search    SQLite FTS5
  Ranking             BM25
  Data preparation    Pandas, PyArrow
  HTML parsing        BeautifulSoup
  Production server   Gunicorn
  Deployment          Render
  Version control     Git, GitHub

## Repository structure

``` text
NyayaLens/
├── app.py
├── wsgi.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── static/
│   └── templates/
│
├── frontend/
│   ├── index.html
│   └── about.html
│
├── data/
│   └── processed/
│       ├── nyayalens_clean.db
│       ├── nyayalens_fts.db
│       ├── nyayalens_full.db
│       └── cases_2025.parquet
│
├── src/
│   ├── database/
│   │   └── import_data.py
│   ├── scraper/
│   │   └── scraper.py
│   ├── analysis/
│   └── data/
│
├── notebooks/
│   └── 01_data_exploration.ipynb
│
├── buildfts.py
├── create_indexes.py
├── inspect_paths.py
├── testfts.py
├── test_pdf_links.py
│
└── tests/
```

## Code organisation and file responsibilities

### Root-level files

  -----------------------------------------------------------------------
  File                                Role
  ----------------------------------- -----------------------------------
  `app.py`                            Local Flask entry point. Calls
                                      `create_app()` and runs the
                                      development server when executed
                                      directly.

  `wsgi.py`                           Exposes the Flask application as
                                      `application` for Gunicorn or
                                      another WSGI server.

  `requirements.txt`                  Lists the Python packages and
                                      versions used by the project
                                      environment.

  `.gitignore`                        Excludes the virtual environment,
                                      Python cache, raw data directory,
                                      environment variables, and
                                      editor-specific files.

  `README.md`                         Project overview, setup
                                      instructions, and code-organisation
                                      documentation.
  -----------------------------------------------------------------------

### `app/` --- Flask backend

  -----------------------------------------------------------------------
  File / directory                    Role
  ----------------------------------- -----------------------------------
  `app/__init__.py`                   Defines the application factory
                                      `create_app()`, creates the Flask
                                      instance, imports the `main`
                                      blueprint, and registers it.

  `app/routes.py`                     Defines the web routes and
                                      `/api/judgments` endpoint. It
                                      validates request parameters,
                                      queries SQLite/FTS5, applies year
                                      filters and sorting, handles
                                      pagination, constructs PDF URLs,
                                      and returns JSON.

  `app/static/`                       Reserved for Flask static assets.
                                      The committed directory currently
                                      contains only a `.gitkeep`
                                      placeholder.

  `app/templates/`                    Reserved for Flask/Jinja templates.
                                      The committed directory currently
                                      contains only a `.gitkeep`
                                      placeholder; the current pages are
                                      served from `frontend/`.
  -----------------------------------------------------------------------

### `frontend/` --- User interface

  -----------------------------------------------------------------------
  File                                Role
  ----------------------------------- -----------------------------------
  `frontend/index.html`               Main search page. Contains the
                                      search form, year filters, sorting
                                      controls, result display,
                                      pagination, CSS, and JavaScript
                                      that calls the Flask API and
                                      renders results.

  `frontend/about.html`               About page describing NyayaLens,
                                      its features, operation, dataset
                                      attribution, and legal-information
                                      disclaimer.
  -----------------------------------------------------------------------

The frontend uses JavaScript `fetch()` requests to call the backend. The
backend returns JSON, which is rendered in the browser.

### `src/` --- Data preparation and supporting modules

  -----------------------------------------------------------------------
  File / directory                    Role
  ----------------------------------- -----------------------------------
  `src/database/import_data.py`       Reads the configured Parquet input,
                                      selects required metadata columns,
                                      cleans text and missing values,
                                      normalises decision dates, checks
                                      document paths, and imports records
                                      into a SQLite `judgments` table.

  `src/scraper/scraper.py`            Defines
                                      `extract_case_details(html)`, which
                                      uses BeautifulSoup to extract the
                                      case title, coram information, and
                                      key-value case details from
                                      supplied HTML.

  `src/analysis/`                     Reserved for analysis code;
                                      currently contains only a
                                      `.gitkeep` placeholder.

  `src/data/`                         Reserved for data-related source
                                      files; currently contains only a
                                      `.gitkeep` placeholder.
  -----------------------------------------------------------------------

**Raw-data input note:** `src/database/import_data.py` expects
`data/raw/metadata_2025.parquet`. The `data/raw/` directory is ignored
by Git, so this input must be obtained separately before running the
import utility.

### `data/processed/` --- Processed data

  -----------------------------------------------------------------------
  File                                Role
  ----------------------------------- -----------------------------------
  `nyayalens_clean.db`                Cleaned SQLite database containing
                                      structured judgment records. It is
                                      the source database used by
                                      `buildfts.py`.

  `nyayalens_fts.db`                  Search database used by the web
                                      application. It contains the
                                      `judgments` table and the FTS5
                                      virtual table `judgments_fts`.

  `nyayalens_full.db`                 Additional database retained in the
                                      processed-data directory. It is not
                                      the database path currently
                                      configured in `app/routes.py`.

  `cases_2025.parquet`                Processed Parquet data file
                                      retained in the repository.
  -----------------------------------------------------------------------

The application currently connects to `data/processed/nyayalens_fts.db`.

### Database and testing utilities

  -----------------------------------------------------------------------
  File                                Role
  ----------------------------------- -----------------------------------
  `buildfts.py`                       Copies `nyayalens_clean.db` to
                                      `nyayalens_fts.db`, creates an
                                      external-content FTS5 virtual table
                                      over selected fields, and rebuilds
                                      the full-text index.

  `create_indexes.py`                 Creates SQLite indexes on selected
                                      columns/expressions in the clean
                                      database, including year, case ID,
                                      path, and a date-ordering
                                      expression.

  `inspect_paths.py`                  Uses PyArrow to inspect selected
                                      Parquet fields and the HTML
                                      associated with a document path.
                                      Expects the raw dataset under
                                      `data/raw/`.

  `testfts.py`                        Runs a sample FTS5 query, joins
                                      matches to judgment metadata, and
                                      prints BM25 relevance scores.

  `test_pdf_links.py`                 Reads sample document paths and
                                      years from the FTS database and
                                      prints their corresponding AWS S3
                                      PDF URLs.
  -----------------------------------------------------------------------

### `notebooks/` and `tests/`

-   `notebooks/01_data_exploration.ipynb` --- Jupyter notebook used for
    dataset exploration.
-   `tests/` --- Reserved for application tests; currently contains a
    `.gitkeep` placeholder. The standalone test utilities are located at
    the repository root.

## Application workflow

1.  The user enters a keyword query and optionally selects a year range
    and sort order.
2.  `frontend/index.html` sends an HTTP GET request to `/api/judgments`.
3.  `app/routes.py` validates the request parameters and constructs the
    SQL/FTS5 query.
4.  SQLite FTS5 searches the indexed fields. For relevance sorting with
    a query, the backend uses the BM25 function with configured column
    weights.
5.  The backend applies year filters, sorting, and pagination, then
    returns judgment metadata and pagination details as JSON.
6.  For results with a document path and year, the backend constructs an
    English PDF URL. The frontend displays a link to open the original
    PDF hosted on AWS S3.

### FTS5 indexed fields and BM25 weights

The `judgments_fts` virtual table indexes:

-   `title`
-   `petitioner`
-   `respondent`
-   `judge`
-   `citation`

The current API configures these BM25 weights:

  Field          Weight
  ------------ --------
  Title             5.0
  Petitioner        3.0
  Respondent        3.0
  Judge             2.0
  Citation          5.0

The backend orders BM25 scores in ascending order; lower scores indicate
a better match.

## API reference

### `GET /api/judgments`

  Parameter     Description
  ------------- ------------------------------------------------------
  `q`           Optional keyword query.
  `year_from`   Optional lower year bound.
  `year_to`     Optional upper year bound.
  `sort`        `relevance`, `newest`, `oldest`, or `az`.
  `page`        1-based page number; default is `1`.
  `per_page`    Results per page; default is `20`, maximum is `100`.

Example:

``` text
/api/judgments?q=fundamental%20rights&year_from=2000&year_to=2024&sort=relevance&page=1&per_page=20
```

The JSON response contains `total`, `returned`, `page`, `per_page`,
`total_pages`, `has_next`, `has_prev`, and `results`. Each result
contains judgment metadata and a `pdf_url` when its document path and
year are available.

## Run locally

### 1. Clone the repository

``` bash
git clone https://github.com/ArpitDoof/NyayLens.git
cd NyayLens
```

### 2. Create and activate a virtual environment

macOS / Linux:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

``` powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Run the Flask application

``` bash
python app.py
```

Open the local URL printed by Flask (usually `http://127.0.0.1:5000/`).

The repository includes the processed SQLite database files. The web
application specifically uses `data/processed/nyayalens_fts.db`; this
file must be present for the search API to work.

### Production serving

The WSGI entry point is `wsgi.py`. The production server command used
for deployment is:

``` bash
gunicorn wsgi:application
```

## Dataset and attribution

NyayaLens uses the [Indian Supreme Court Judgments
dataset](https://huggingface.co/datasets/labofsahil/Indian-Supreme-Court-Judgments)
published by `labofsahil`. The dataset is identified as being
distributed under the [Creative Commons Attribution 4.0 International
licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
Consult the dataset page for complete attribution details and applicable
conditions.

The original English judgment PDFs are linked using the public AWS S3
object paths associated with the dataset.

## Scope and limitations

-   The application searches the available indexed metadata fields; it
    does not currently perform semantic search.
-   Search results depend on the records and fields present in the
    dataset and FTS5 index.
-   The `src/analysis/` directory is reserved for possible future work;
    an analytics dashboard is not part of the currently implemented
    feature set.
-   NyayaLens is an information-retrieval application. It does not
    provide legal advice or replace consultation with a qualified legal
    professional.

## Disclaimer

NyayaLens is an academic project intended to make publicly available
Indian Supreme Court judgment information easier to search and access.
Users should consult the original judgment and authoritative legal
sources before relying on information for legal purposes.
