import duckdb
import pandas as pd
import geopandas as gpd

# duckdb.read_parquet(["file1.parquet", "file2.parquet", "file3.parquet"])

# duckdb.read_parquet("https://some.url/some_file.parquet")

# parquet_file = 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/mapfiles/internalmap2025-03.parquet'

# test_df = pd.read_parquet(parquet_file, engine='pyarrow')
# print(test_df)
# print(test_df['geometry'])
# print(set(test_df['status'].to_list())) 
# # print(duckdb.sql("SELECT * FROM test_df").fetchall())


# parquet_file_source_path = 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/'
# parquet_s3 = 'latest/GEM-GOIT-Oil-NGL-Pipelines-2025-03.parquet'
# test = pd.read_parquet(f'{parquet_file_source_path}{parquet_s3}')


# pf= 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/latest/GEM-EGT-Gas-Hydrogen-Pipelines-2025-02_DATA_TEAM_COPY.parquet'
pf = 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/latest/GEM-EGT-Terminals-2025-02_DATA_TEAM_COPY.parquet'

ggitegt = pd.read_parquet(pf)

for col in ggitegt.columns:
    print(col)