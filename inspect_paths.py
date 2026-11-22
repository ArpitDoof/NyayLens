from pathlib import Path
import pyarrow.dataset as ds

dataset_path = Path("data/raw")

print("Dataset exists:", dataset_path.exists())
print("Parquet files:", list(dataset_path.glob("*.parquet"))[:5])

dataset = ds.dataset(
    "data/raw/",
    format="parquet",
    partitioning=None
)

table = dataset.to_table(
    columns=["path", "year", "raw_html"]
)

df = table.to_pandas()

row = df[df["path"] == "1950_1_806_821"]

print(row[["path", "year", "raw_html"]].to_string(index=False))