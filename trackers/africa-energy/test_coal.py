import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString
from shapely import wkt
import polyline
# import pygsheets
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
# import xlwings
import json
from gspread.exceptions import APIError
import time
from itertools import permutations
import copy
import os
from datetime import date
import openpyxl
import xlsxwriter
from config import *
import re
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.styles import Alignment
from helper_functions import *
import pyogrio



def pull_gsheet_data_for_coal(tracker):
    

    df = gspread_access_file_read_only(prep_dict[tracker]['gspread_key'], prep_dict[tracker]['gspread_tabs'])
    print(f'Shape of df: {df.shape}')
    # col_reg_name = 'Region'
    # col_country_name = 'Country'
    # df[col_reg_name] = df[col_reg_name].str.strip().str.lower()
    # df[col_country_name] = df[col_country_name].str.strip().str.lower()
    # value_counts = df[col_reg_name].fillna('empty').value_counts()
    # print(value_counts)
    df = df[df['Region']=='Africa']
    # insert function to filter on area/country / assign
    # then can compare filter on country vs region

    # col_reg_name, col_country_name = find_region_country_colname(df)

    # col_reg_name, col_country_name = find_region_country_colname(df)

    # # TODO add in a check to compare filtering by country versus filtering by region column where applicable
    # filtered_geo_df = create_filtered_df_list_by_map(df,col_country_name, col_reg_name, mapname=test, needed_geo=test)
    # # filter by needed_geo 
    # filtered_geo_df = filtered_geo_df.fillna('')
    # filtered_geo_df.dropna()
    # df_info(filtered_geo_df, mapname)
    # filtered_geo_df = find_missing_coords(filtered_geo_df)
    # # append df to list of dfs for data download
    # list_dfs_by_map.append(filtered_geo_df)
    # filtered_geo_df.to_excel(f'{path_for_test_results}{mapname}_{tracker}_df_{iso_today_date}.xlsx', index=False)
    # print(f'Added df {tracker} for map {mapname} to list_dfs_by_map for data download and saved to {path_for_test_results}{mapname}_{tracker}_df_{iso_today_date}.xlsx.')
    # gdf = convert_coords_to_point(filtered_geo_df)
    # # append gdf to list of gdfs for map - though now we can have it as a csv for faster AET non tile load
    # list_gdfs_by_map.append(gdf)
    # gdf_to_geojson(gdf, f'{path_for_test_results}{mapname}_{tracker}_gdf_{iso_today_date}.geojson')
    # print(f'Added gdf {tracker} for map {mapname} to list of gdfs for map and saved to {path_for_test_results}{mapname}_{tracker}_gdf_{iso_today_date}.geojson.')


    return None

## CALL FUNCTIONS
# pull_gsheet_data_for_coal(['1zrVobNcD0HiBfko4Z8N9BUaMXxEvNNrXFxzk42q2ZBI'], ['Units'])
pull_gsheet_data_for_coal('GCMT')