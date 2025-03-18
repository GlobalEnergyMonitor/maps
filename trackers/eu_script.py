from datetime import datetime, timedelta
from all_config import *
import os
import io
import gspread
from creds import client_secret
import creds
import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import date
from helper_functions import *
from shapely.geometry import Point, LineString
import pickle
from collections import Counter


conversion_df = create_conversion_df(conversion_key, conversion_tab)

# maybe add tracker-acro or figure out why failing but didn't have it in egt colab. FEB 25th 

term = gpd.read_file(egt_ggit_terminals)
term['tracker'] = 'term'
term['tracker-acro'] = 'GGIT-lng'

pipes = gpd.read_file(egt_ggit_pipes)
pipes['tracker'] = 'pipes'
pipes['tracker-acro'] = 'GGIT'

gogpt_hy = gspread_access_file_read_only(egt_dd_key, ['H2 Proposals at Oil & Gas Plant'])
gogpt_hy['tracker'] = 'plants_hy'
gogpt_hy['tracker-acro'] = 'GOGPT-hy'
gogpt = gspread_access_file_read_only(egt_dd_key, ['Oil & Gas Plants'])
gogpt['tracker'] = 'plants'
gogpt['tracker-acro'] = 'GOGPT'
goget_global = gspread_access_file_read_only(goget_global_key, ['Main data','Production & reserves'])
goget = filter_goget_for_europe(goget_global)
# save goget
save_goget_datafile_eu(goget)

goget['tracker'] = 'extraction'
goget['tracker-acro'] = 'GOGET'
# convert term and pipes to gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

pipes = gpd.GeoDataFrame(pipes, geometry='geometry', crs="EPSG:4326")
term = gpd.GeoDataFrame(term, geometry='geometry', crs="EPSG:4326")


list_to_be_merged = [term, pipes, gogpt, goget, gogpt_hy]

gdf_to_be_merged = []
for df in list_to_be_merged:
    df = adjusting_geometry(df)
    print(df['geometry'])
    # how can I make sure this updated gdf is now
    gdf_to_be_merged.append(df)
    


for df in gdf_to_be_merged:
    df = fuel_filter(df)
    print(df['tracker'].iloc[0])
    print(set(df['fuel-filter'].to_list()))
  # show methane pipes that have ['pci6'] or pci 5
    if df['tracker'].iloc[0] == 'pipes':

        test = df[df['fuel-filter']=='methane']
        test.fillna('',inplace=True)
        test1 = test[test['pci5'] != '']
        test2 = test[test['pci6'] != '']
        test = pd.concat([test1, test2])
        print(test[['pci5', 'pci6', 'fuel-filter', 'tracker']])
        print(len(test))
        
    

for df in gdf_to_be_merged:
    df = maturity(df)
    print(df['tracker'].iloc[0])
    print(set(df['maturity'].to_list()))
    # count of maturity equal none by tracker
    print(df[df['maturity']=='none'][['maturity', 'tracker']].groupby('tracker').count())
    # count of maturity equal y by tracker
    # print(df[['maturity', 'tracker']].groupby('tracker').count())


for df in gdf_to_be_merged:
    df = split_goget_ggit_eu(df)
    # print(df['tracker'].iloc[0])
    # print(df.columns)


for df in gdf_to_be_merged:
    df = assign_conversion_factors(df, conversion_df)
    print(df['tracker'].iloc[0])
    print(df.columns)
    if 'fuel-filter' not in df.columns:
        input('issue here')
    elif 'geometry' not in df.columns:
        input('issue here')


final_list = []
for df in gdf_to_be_merged:
    df = rename_gdfs(df)
    final_list.append(df)
    print(df['tracker'].iloc[0])
    print(df.columns)
    tracker_sel = df['tracker-acro'].iloc[0]
    if tracker_sel == 'GOGET':
        print(df['areas'])
        input('check goget areas after rename_gdfs')

    

one_gdf = merge_all_gdfs_eu(final_list)
# one_gdf['areas']

# make sure the gogpt hy row stays and the other one ids removed with drop duplicate

# sort by tracker so we know if gogpt-hy or gogpt is first
one_gdf = one_gdf.sort_values(by='tracker', ascending=True, axis=0)
print(set(one_gdf['tracker'].to_list()))
# check how many total count by tracker after drop duplicates
print(one_gdf[['id', 'tracker']].groupby('tracker').count())

one_gdf.drop_duplicates(subset='id', inplace=True, keep='last') # add logic so it defaults to keeping the gogpt-hy ones over the gogpt ones, so if yes in gogpt data remove
one_gdf.reset_index(drop=True, inplace=True)
# filter down one_gdf to just id
print(one_gdf[['id', 'tracker']].groupby('tracker').count())

# print(set(one_gdf['areas'].to_list()))
# input('Check areas after one_gdf to test this') # worked

renamed_one_gdf_by_map = {'europe': one_gdf}
# print(set(one_gdf['areas'].to_list()))
tracker_sel = one_gdf['tracker-acro'].iloc[0]
if tracker_sel == 'GOGET':
    print(one_gdf['areas'])
    input('check goget areas after renamed_one_gdf_by_map')
# input('Check areas after renamed_one_gdf_by_map_with_search') # worked

renamed_one_gdf_by_map_with_search = create_search_column(renamed_one_gdf_by_map)

# input('Check areas in create search col for one_gdf')#worked

cleaned_dict_map_by_one_gdf_with_conversions = capacity_conversions_eu(renamed_one_gdf_by_map_with_search)
# input('Check areas in create capacity_conversions_eu for one_gdf') # worked

cleaned_dict_by_map_one_gdf_with_better_statuses = map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions)
# input('Check areas in create map_ready_statuses for one_gdf') #worked

cleaned_dict_by_map_one_gdf_with_better_countries = map_ready_countries(cleaned_dict_by_map_one_gdf_with_better_statuses)
one_gdf_by_maptype = workarounds_eg_interim_goget_gcmt_eu(cleaned_dict_by_map_one_gdf_with_better_countries)
one_gdf_by_maptype_fixed = last_min_fixes(one_gdf_by_maptype)
final_dict_gdfs = create_map_file_eu(one_gdf_by_maptype_fixed)