import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString
from shapely import wkt


eupath = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/europe/'
file = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/europe/ggit-pipeline-pci-hydrogen-dec-2023.csv'
mapfile = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/europe/compilation_output/europe_2024-10-02.geojson'
hyfile = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/europe/Copy of Pipelines (Gas_Oil_NGL) - main - for EGT briefing in Feb 2024 - Gas pipelines.csv'
release_file = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GGIT-Gas-Pipelines-2023-12 copy.geojson'


# europe data from last time
eu_hy = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/testing/final/data-eu-hydrogen.csv'
# remove all that is not gas_pipeline from type
eu_hy_df = pd.read_csv(eu_hy, encoding='utf-16')
eu_hy_df = eu_hy_df[eu_hy_df['type'].isin(['gas_pipeline', 'hydrogen_pipeline'])]
print(eu_hy_df[eu_hy_df['pci5']=='yes'])
print(eu_hy_df.columns)

# create needed cols for eg map
eu_hy_df['status-legend'] = eu_hy_df['status']
eu_hy_df['status'] = eu_hy_df['status_tabular']
# concat with existing europe eg map file
# convert route to linestring 

# I think we'll do both ggit, ggit-hy, and ggit-lng.
# then concat ggit and ggithy together, deduplicate on id
# use hydrogen where relevant, and pci, and use both for the data download


# eu_hy_df['geometry'] = eu_hy_df['route'].apply(lambda x: google_to_gdf(x))

# eu_hy_gdf = gpd.GeoDataFrame(eu_hy_df, geometry=geometry, crs="EPSG:4326")


# hy_df = pd.read_csv(hyfile)
# print(hy_df.columns)
# print(hy_df[['PipelineName', 'WKTFormat']])
# hy_df = hy_df[hy_df['WKTFormat'] != '--']
# print(hy_df[['PipelineName', 'WKTFormat']])
# hy_df['WKTFormat'].fillna('')
# hy_df = hy_df[hy_df['WKTFormat'] != '']
# print(hy_df[['PipelineName', 'WKTFormat']])

# to_drop = []
# for row in hy_df.index:
#     if pd.isna(hy_df.loc[row, 'WKTFormat']): 
#         to_drop.append(row)


# # hy_df['geometry'] = hy_df['WKTFormat'].apply(lambda x: wkt.loads(x))
# # print(hy_df['geometry'])
# to_drop_again = []
# for index, row in hy_df.iterrows():
#     try:
#         value = row["WKTFormat"]
#         wkt.loads(value)
#         print(value)
#     except Exception:
#         to_drop_again.append(index)
#         print(f'{index} {value!r}')
        
# hy_df = hy_df.drop(to_drop_again) 

# hy_df['geometry'] = hy_df['WKTFormat'].apply(lambda x: wkt.loads(x))
# print(hy_df['geometry'])
# hy_gdf = gpd.GeoDataFrame(hy_df, geometry='geometry', crs="EPSG:4326")
# print(len(hy_gdf))
# print(hy_gdf.columns)

# eu_map_df = gpd.read_file(mapfile)

# print(eu_map_df.columns)

