import duckdb
import pandas as pd


# duckdb.read_parquet(["file1.parquet", "file2.parquet", "file3.parquet"])

# duckdb.read_parquet("https://some.url/some_file.parquet")

parquet_file = 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/latest/internal2025-03.parquet'

test_df = pd.read_parquet(parquet_file)
print(duckdb.sql("SELECT * FROM test_df").fetchall())