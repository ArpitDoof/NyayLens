from pathlib import Path
import sqlite3
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT_DIR/"data"/"raw"/"metadata_2025.parquet"
DB_FILE = ROOT_DIR/"data"/"processed"/"nyayalens.db"

REQUIRED_COLUMNS = [
    "title",
    "petitioner",
    "respondent",
    "description",
    "judge",
    "author_judge",
    "citation",
    "case_id",
    "cnr",
    "decision_date",
    "disposal_nature",
    "court",
    "available_languages",
    "path",
    "year",
    "coram",
    "case_number",
    "bench",
    "direction_issue",
]

#These columns we have Picked after filtering and checking all the data in the data_exploration_phase

def clean_text(value):
    #Here we are converting the missing values to none and trimming surrounding whitespaces
    if pd.isna(value):
        return None

    if isinstance(value,str):
        value = value.strip()
        return value if value else None

    return str(value)


def build_database():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Datset not found :{DATA_FILE}")

    DB_FILE.parent.mkdir(parents = True,exist_ok=True)

    #Loading the parquet dataset
    df = pd.read_parquet(DATA_FILE)

    #we are keeping the Columns that actually exist in the dataset

    columns = [
        col for col in REQUIRED_COLUMNS
        if col in df.columns
    ]

    df = df[columns].copy()

    if "path" not in df.columns:
        raise ValueError("Datset has no 'path' column.")

    #cleaning the text fields now
    for col in df.columns:
        df[col] = df[col].map(clean_text)

    #storing dates in YYYY-MM-DD format
    if "decision_date" in df.columns:
        dates = pd.to_datetime(
            df["decision_date"],
            dayfirst=True,
            errors="coerce"
        )
        df["decision_date"] = dates.dt.strftime("%Y-%m-%d")
        df["decision_date"] = df["decision_date"].where(
            dates.notna(),None
        )

    #A missing or repeated path makes the source identifier unreliable
    if df["path"].isna().any():
        raise ValueError("Some records are having a missing path. ")
    
    if df["path"].duplicated().any():
        raise ValueError("Duplicate. paths found.Inspect before Importing")
    
        #Now we will build the SQLlit table using the available metadata columns.
    column_definitions = [
        '"id" INTEGER PRIMARY KEY AUTOINCREMENT'
        ]
    
    for col in df.columns:
        if col == "path":
            column_definitions.append('"path" TEXT NOT NULL UNIQUE')
        else:
            column_definitions.append(f'"{col}" TEXT')

    create_table_sql = (
        "CREATE TABLE judgments (" + ", ".join(column_definitions)+")"
    )

    with sqlite3.connect(DB_FILE) as conn:
        #Recreating the table the for this dev
        conn.execute("DROP TABLE IF EXISTS judgments")
        conn.execute(create_table_sql)

        columns_sql = ", ".join(f'"{col}"' for col in df.columns)
        placeholders = ", ".join("?" for _ in df.columns)

        insert_sql = (
            f"INSERT INTO judgments ({columns_sql})"
            f"VALUES ({placeholders})"
        )
        records = [
            tuple(None if pd.isna(value) else value for value in row)
            for row in df.itertuples(index=False,name = None)
        ]
        conn.executemany(insert_sql,records)

        total = conn.execute("SELECT COUNT(*) FROM judgments").fetchone()[0]

    print(f"Database created : {DB_FILE}")
    print(f"Judgments imported: {total}")
    print(f"Columns imported: {len(df.columns)}")

if __name__ == "__main__":
    build_database()
                               
    
        
            

        



