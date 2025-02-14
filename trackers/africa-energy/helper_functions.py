import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString
from shapely import wkt
import polyline
# import pygsheets
import gspread
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


# #### useful general functions ####

# def track_missing_data(dict_list_dfs_by_map, acro, maptype):
#     for mapname, list_dfs in dict_list_dfs_by_map.items():
#         if mapname == maptype:
#             for df in list_dfs:
#                 if df['tracker acro'].iloc[0] == acro:    
#                     # print(f'This is the current count of all units for tracker {acro} in map: {mapname}:')
#                     # print(len(df[df['tracker acro']==acro]))
#                     # input('Check that this number aligns with the number of units in the map')
#     return 

def gspread_access_file_read_only(key, tab_list):
    """
    key = Google Sheets unique key in the URL
    title = name of the sheet you want to read
    returns a df of the sheet
    """
    gspread_creds = gspread.oauth(
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        credentials_filename=client_secret_full_path,
        # authorized_user_filename=json_token_name,
    )
    list_of_dfs = []
       # # add in an exponential backoff 

    for tab in tab_list:
        if tab == gcmt_closed_tab:
            # print(tab)
            wait_time = 5
            time.sleep(wait_time)
            gsheets = gspread_creds.open_by_key(key)
            # Access a specific tab
            spreadsheet = gsheets.worksheet(tab)

            df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            if 'Status' in df.columns:
                print('Look at GCMT closed tab status col should not be there but is?')
            else:
                df['Status'] = 'Retired'
            list_of_dfs.append(df)
        else: 
            # print(tab)
            wait_time = 5
            time.sleep(wait_time)
            gsheets = gspread_creds.open_by_key(key)
            # Access a specific tab
            spreadsheet = gsheets.worksheet(tab)

            df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))

            list_of_dfs.append(df)
    if len(list_of_dfs) > 1: 
        # df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True).fillna('')
        
        df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True)

    return df
 


# # #### useful geo functions ####

def geom_to_polyline(geom):
    if geom.geom_type == 'MultiLineString':
        # Convert each LineString within the MultiLineString to a polyline
        return [polyline.encode(list(line.coords)) for line in geom.geoms] # problem TypeError: 'MultiLineString' object is not iterable
    elif geom.geom_type == 'LineString':
        return polyline.encode(list(geom.coords))
    elif geom.geom_type == 'Point':
        return Point.encode(list(geom.coords)) # maybe? 
    else:
        raise ValueError("Unsupported geometry type")


def clean_dfs(df):
    # remove uknown, *, etc
    # print(f'length of df at start of cleaned_dfs: {len(df)}')

    non_numeric_rows = []

    cleaned_df = df.copy()
    cleaned_df['Latitude'] = cleaned_df['Latitude'].astype(str)
    cleaned_df['Longitude'] = cleaned_df['Longitude'].astype(str)
    non_numeric_rows = cleaned_df[
        cleaned_df['Latitude'].str.contains(',') |
        cleaned_df['Longitude'].str.contains(',')].index.tolist()
    non_numeric_rows2 = cleaned_df[
        cleaned_df['Latitude'].str.contains('-') |
        cleaned_df['Longitude'].str.contains('-')].index.tolist()
            
    non_numeric_rows = non_numeric_rows + non_numeric_rows2 # + cleaned_df_missing
    # print(f'length of :{len(non_numeric_rows)}')
    cleaned_df = cleaned_df.drop(non_numeric_rows)
    # print("Rows to drop:", non_numeric_rows)
    # print("\nCleaned DataFrame:")
    # print(cleaned_df)
    
    # Create new DataFrames from the lists
    non_numeric_df = pd.DataFrame(non_numeric_rows)

    # print("\nNon-Numeric DataFrame:")
    # print(non_numeric_df)
    non_numeric_df.to_csv(f'{path_for_test_results}non_numeric_df_coords_{today_date}.csv')

                
    # print(f'length of df at end of cleand_dfs removed lat and long empty which is good because all point data:{len(cleaned_df)}')
    return cleaned_df

def df_to_gdf(df, geometry_col, crs='EPSG:4326'):
    # Ensure the geometry column contains valid geometries
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df[geometry_col]))
    # print(crs)
    gdf = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)

    return gdf

def gdf_to_geojson(gdf, output_file):
    gdf.to_file(output_file, driver='GeoJSON')
    # print(f"GeoJSON file saved to {output_file}")


def geojson_to_gdf(geojson_file):
    """
    convert to gdf
    """
    
    # Load GeoJSON file into a GeoDataFrame
    gdf = gpd.read_file(geojson_file)

    # get crs for final export
    crs = gdf.crs

    pipes_without_geo = gdf[gdf['geometry']==None]

    return gdf, crs



def get_standard_country_names():
    
    df = gspread_access_file_read_only(
        '1mtlwSJfWy1gbIwXVgpP3d6CcUEWo2OM0IvPD6yztGXI', 
        ['Countries'],
    )
    gem_standard_country_names = df['GEM Standard Country Name'].tolist()
    
    return gem_standard_country_names

gem_standard_country_names = get_standard_country_names()



def is_number(n):
    is_number = True
    try:
        num = float(n)
        # check for "nan" floats
        is_number = num == num   # or use `math.isnan(num)`
    except ValueError:
        is_number = False
    return is_number

def check_and_convert_int(x):
    if is_number(x):
        return int(x)
    else:
        return np.nan

def check_and_convert_float(x):
    if is_number(x):
        return float(x)
    else:
        return np.nan

def check_in_range(value, min_val, max_val):
    # doesn't handle na because already was handled
    if min_val <= value <= max_val:
         
        return value

    else:
        print('problem with coords:')
        print(f'value:{value}, min_val:{min_val}, max_val:{max_val}')
        return np.nan
    
def coordinate_qc(df, col_country_name):
    issues_coords = {} # acro, df line
    df = df.reset_index()
    tracker = df['tracker acro'].loc[0]
    # wait_time = 5
    # time.sleep(wait_time)
    # gsheets = gspread_creds.open_by_key(multi_tracker_countries_sheet)
    # spreadsheet = gsheets.worksheet('country_centroids')
    # country_centroids = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
    # split on comma, check valid lat lng, 
    # in a float valid range 
    df['float_col_clean_lat'] = df['Latitude'].apply(lambda x: check_and_convert_float(x))
    
    df['float_col_clean_lng'] = df['Longitude'].apply(lambda x: check_and_convert_float(x))
    
    # after converting all to float nan, we filter out nan
    # this assumes source data has gone through qc in separate file to find the comma situations
    for row in df.index:
        if pd.isna(df.loc[row, 'float_col_clean_lat']): 
            issues_coords[tracker] = df.loc[row]
            df.drop(index=row, inplace=True)
        elif pd.isna(df.loc[row, 'float_col_clean_lng']): 
            issues_coords[tracker] = df.loc[row]
            df.drop(index=row, inplace=True)

               
    # check that the numbers fall within a range
    acceptable_range = {
        'lat': {'min': -90, 'max': 90},
        'lng': {'min': -180, 'max': 180}
    }
    
    df['float_col_clean_lat'] = df['float_col_clean_lat'].apply(
        lambda x: check_in_range(x, acceptable_range['lat']['min'], acceptable_range['lat']['max'])
    )
    # print(df['float_col_clean_lat'])
    # input('check after check in range or nan')
    df['float_col_clean_lng'] = df['float_col_clean_lng'].apply(
        lambda x: check_in_range(x, acceptable_range['lng']['min'], acceptable_range['lng']['max'])
    )
    # check_in_range could return nan if out of range so need to drop nans
    # this should have been handled in QC the range stuff 
    for row in df.index:
        if pd.isna(df.loc[row, 'float_col_clean_lat']):
            print(df.loc[row]) 
            issues_coords[tracker] = df.loc[row]
            df.drop(index=row, inplace=True)
        elif pd.isna(df.loc[row, 'float_col_clean_lng']): 
            print(df.loc[row])
            issues_coords[tracker] = df.loc[row]
            df.drop(index=row, inplace=True)
 

        else:
            df.loc[row, 'Latitude'] = df.loc[row, 'float_col_clean_lat']
            df.loc[row, 'Longitude'] = df.loc[row, 'float_col_clean_lng']

    return df, issues_coords

# def find_missing_geometry(gdf,col_country_name):
#     if gdf['geometry'] == '':
#         gdf = find_missing_coords(gdf, col_country_name)
#     elif gdf['geometry'] == 'POINT(1 1)':
#         print('point 11 issue again')
#     return gdf
   
def find_missing_cap(df):
    
    # GOGET does not have capacity 
    if df['tracker'].loc[0] == 'GOGET':
        pass
    else:
        df['float_col_clean_cap'] = df['capacity'].apply(lambda x: check_and_convert_float(x))
        
        # # print("Check which rows will be dropped because nan capacity:")
        # print(df[df.isna().any(axis=1)])
        nan_df = df[df.isna().any(axis=1)]
        # nan_df.to_csv(f'{path_for_test_results}{df["tracker"].loc[0]}_nan_capacity_{today_date}.csv')
        # df = df.dropna(subset = ['float_col_clean_cap'])
        
    return df

def convert_coords_to_point(df):
    crs = 'EPSG: 4326'
    geometry_col = 'geometry'
    df = df.reset_index(drop=True)

    for row in df.index:
        df.loc[row,'geometry'] = Point(df.loc[row,'Longitude'], df.loc[row,'Latitude'])
    gdf = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)
    
    return gdf

def find_about_page(tracker,key):

        gspread_creds = gspread.oauth(
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
            credentials_filename=client_secret_full_path,
            # authorized_user_filename=json_token_name,
        )
        wait_time = 5
        time.sleep(wait_time)
        gsheets = gspread_creds.open_by_key(key)
            
        # List all sheet names
        sheet_names = [sheet.title for sheet in gsheets.worksheets()]
        # print(f"{tracker} Sheet names:", sheet_names)
        # Access a specific sheet by name
        first_tab = sheet_names[0]
        first_sheet = gsheets.worksheet(first_tab)  # Access the first sheet
        
        last_tab = sheet_names[-1]
        last_sheet = gsheets.worksheet(last_tab)  # Access the last sheet

        # print("First sheet name:", sheet.title)
        if 'About' not in first_sheet.title:
            # print('Looking for about page in last tab now, first one no.')
            # handle for goget and ggit, goit who put it in the last tab
            if 'About' not in last_sheet.title:
                if 'Copyright' not in last_sheet.title:
                    print('Checked first and last tab, no about page found not even for copyright. Pausing.')
                    # input("Press Enter to continue...")
                else:
                    # print(f'Found about page in last tab: {last_tab}')
                    sheet = last_sheet
            else:
                # print(f'Found about page in last tab: {last_tab}')
                sheet = last_sheet
        else:
            # print(f'Found about page in first tab: {first_tab}')
            sheet = first_sheet
        
        data = pd.DataFrame(sheet.get_all_records(expected_headers=[]))
        about_df = data.copy()
    
        return about_df

def find_region_country_colname(df):
    continent_list = ['Africa', 'Americas', 'Oceania', 'Asia', 'Europe']
    cols = df.columns
    col_reg_name = '' # initialize 
    col_country_name = ''
    tracker = df['tracker acro'].loc[0]
    if tracker in tracker_mult_countries: # GGIT GOIT
        col_country_name = 'Countries'
        col_reg_name = ['StartRegion', 'EndRegion'] # Ask Baird if this is reasonable
    # elif df['tracker acro'].loc[0] == 'GOGET':
    #     col_country_name = 'Country' # not Country List because that is only relevant for some rows 
    elif tracker == 'GHPT':
        col_country_name = ['Country 1', 'Country 2']
        col_reg_name = ['Region 1', 'Region 2']    
    else:
        for col in cols:
            # random row
            random = int(len(df) / 2)
            # print(random)
            
            if df[col].loc[random] in continent_list and 'region' in col.lower():
                col_reg_name = col 
                # print(f'this is region col: {col_reg_name} to filter on for {tracker}!')
                # input('Check region col')
                continue

            elif df[col].loc[random] in full_country_list and 'country' in col.lower():
                if col == 'ParentHQCountry':
                    continue
                # elif df tracker is pipeline or goget use countries col always!  tracker acro
                else:
                    col_country_name = col
                    # print(f'this is country col: {col_country_name} to filter on  for {tracker}!')
                    # input('Check country col')
                    continue
                

                
    return col_reg_name, col_country_name    

# Define a function to check for valid values
# def is_valid_goget(x):

#     return isinstance(x, (int, float)) and not pd.isna(x) and x != '' and x != 0 and x != 0.0

# Function to check if any item in the row's list is in needed_geo
def check_list(row_list, needed_geo):
    return any(item in needed_geo for item in row_list)

def create_filtered_df_list_by_map(trackerdf, col_country_name, col_reg_name, maptype, needed_geo):
    
    # double check clean country and region columns and list of countries
    filtered_df = trackerdf.copy()
    tracker = filtered_df['tracker acro'].loc[0]
    print(tracker)
    print(maptype)
    print(len(filtered_df))

    if maptype == 'GIPT':
        # print('For GIPT we do not filter by geo')

        pass
    elif maptype == 'latam':
        if tracker in tracker_mult_countries: # currently no lists like with regions since goit and ggit created countries a list from start and end countries
            # if any of the countries in the country column list is in the needed geo list then keep it if none then filter out
            for sep in ',;-':
                # I want to break up any multiple countries into a list of countries
                # then check if any of those are in the needed_geo list
                filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip().str.split(sep) 

            # filter the df on the country column to see if any of the countries in that list is in the needed geo
            filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
            # print(tracker)
            # print(maptype)
            # print(filtered_df)
            # input(f'Check length for tracker ggit goit after filter')
            filtered_df = filtered_df.drop(columns=['country_to_check'])

        else:
            # # TODO now that we are only filtering on country for latam we can probalby remove this if else
            if isinstance(col_country_name, list): # hydro more than one
                # print(col_country_name)
                filtered_df['country_to_check'] = [[] for _ in range(len(filtered_df))]

                for col in col_country_name:
                    # TEST THIS
                    # filtered_df['country_to_check'] = filtered_df[col].str.strip()
                    filtered_df['country_to_check'] = filtered_df.apply(lambda row: row['country_to_check'] + [row[col].strip()], axis=1)

                filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                filtered_df = filtered_df.drop(columns=['country_to_check'])

            else:
                filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip()

                # need this by country because not a GEM region, problematic since goget uses region and numbers when filtered by country in the gem region do not match 636 versus 578 for africa
                filtered_df = filtered_df[filtered_df['country_to_check'].isin(needed_geo)]
            
                filtered_df = filtered_df.drop(columns=['country_to_check'])
              
    # elif tracker in tracker_mult_countries:
    #     # if any of the countries in the country column list is in the needed geo list then keep it if none then filter out
    #     for sep in ',;-':
    #         # I want to break up any multiple countries into a list of countries
    #         # then check if any of those are in the needed_geo list
    #         filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip().str.split(sep) 

    #     # filter the df on the country column to see if any of the countries in that list is in the needed geo
    #     filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
    #     print(tracker)
    #     print(maptype)
    #     print(filtered_df)
    #     input(f'Check length for tracker ggit goit after filter')
    else:
        if isinstance(col_reg_name, list):
            maptype_list = maptype.title().split(' ')
            print(maptype_list)
            print(type(maptype_list))
            print(col_reg_name)
            # initialize a list in that column! 
            filtered_df['region_to_check'] = [[] for _ in range(len(filtered_df))]

            for col in col_reg_name:
                # we want to add the row's region in that col to a new column's list of all regions 
                filtered_df['region_to_check'] = filtered_df.apply(lambda row: row['region_to_check'] + [row[col].strip()], axis=1)
                # print(filtered_df['region_to_check'])
            # TEST THIS so africa becomes ['africa']
            # print(filtered_df['region_to_check'])
            filtered_df = filtered_df[filtered_df['region_to_check'].apply(lambda x: check_list(x, maptype_list))]
            filtered_df = filtered_df.drop(columns=['region_to_check'])
        else:

            filtered_df[col_reg_name] = filtered_df[col_reg_name].str.strip()

            filtered_df = filtered_df[filtered_df[col_reg_name] == maptype.title()]
    # print(len(filtered_df))
    # input('check')
    return filtered_df

def conversion_multiply(row):
    cap = float(row['cleaned_cap'])
    factor = float(row['conversion_factor'])
    # print(f'this is factor! {factor}')
    result = float(cap * factor)
    # print(f'this is result! {result}')
    return result

def format_final(df_arg): # TO DO
    df = df_arg.copy()
    # make all years non float
    # round floats to 2
    # remove helper cols official_name & country to check 
    return df

def workaround_no_sum_cap_project(gdf):
    gdf = gdf.copy()
    
    # result = int()
    
    # group by id
    # summed cleaned cap
    # that's the project cap
    # print(gdf['name'].value_counts())
    for row in gdf.index:
        try:
            # groupby on that specifci row's name
            name = gdf.loc[row, 'name']
            capacity_details = gdf[gdf['name']==name].groupby('name', as_index=False)['capacity'].sum()
        except:
            capacity_details = ''

        gdf.loc[row, 'capacity-details'] = capacity_details
    # project_cap_df = gdf.groupby('name', as_index=False)['capacity'].sum()
    # print(f'this is cols of project_cap_df: {project_cap_df.columns}')
    # project_cap_df = project_cap_df.rename(columns={'capacity': 'capacity-details'})
    
    # # merge on name to gdf
    
    # gdf = pd.merge(left=gdf, right=project_cap_df, on='name', how='outer')
    
    return gdf

def workaround_display_cap(row):
    cap = row['capacity'] 
    cap = check_and_convert_float(cap)
    if pd.isna(cap):
        cap = '' 
    units_of_m = str(row['original_units'])
    if isinstance(cap, (int, float)):
        cap = str((round(cap, 3))) # handle rounding and converting from string to float to round later 
        result = f'{cap} {units_of_m}'
    else:
        result = ''
    return result
    
    

def workaround_display_cap_total(row):
    cap = row['capacity-details']
    cap = check_and_convert_float(cap)

    if pd.isna(cap):
        cap = '' 
    units_of_m = str(row['original_units'])
    if isinstance(cap, (int, float)):
        cap = str(float(round(cap, 3)))
        result = f'{cap} ({units_of_m})'
    else:
        result = ''
    return result
    
    
def fix_status_inferred(df):
    # print(f"Statuses before: {set(df['status'].to_list())}")
    inferred_statuses_cancelled = df['status'].str.contains('cancelled - inferred')
    inferred_statuses_shelved = df['status'].str.contains('shelved - inferred')
    
    # # print(inferred_statuses_cancelled['status']!=False)
    # # print(len(inferred_statuses_shelved))
    df.loc[inferred_statuses_cancelled, 'status'] = 'cancelled'
    df.loc[inferred_statuses_shelved,'status'] = 'shelved'
    # for row in df.index:
    #     if 'shelved - inferred' in df.loc[row, 'status']:
    #         df.loc[row, 'status'] = 'shelved'
    
    # print(f"Statuses after: {set(df['status'].to_list())}")

    return df

def check_countries_official(df,col_country_name, col_wiki, mapname, tracker):
    df = df.copy()
    problem_units_weird_country = []
    df_country_list = df[col_country_name].unique().tolist()
    df_country_wiki = df[[col_country_name, col_wiki]] # df wiht just these two columns
    for row in df_country_wiki.index:
        if df.loc[row,col_country_name] in full_country_list:
            pass
        else:
            problem_units_weird_country.append((df.loc[row,col_wiki], df.loc[row,col_country_name]))

    path_for_test_results = gem_path + mapname + '/test_results/'
    df = df.reset_index()
    problem_units_weird_country_df = pd.DataFrame(problem_units_weird_country, columns=['wiki', 'weird_country']).drop_duplicates()
    problem_units_weird_country_df.to_csv(f'{path_for_test_results}{tracker}_problem_units_weird_country_{iso_today_date}.csv', index=False)
    # print(f'There were {len(problem_units_weird_country_df)} found for this df {df["tracker acro"].iloc[0]}! Look at them here: {path_for_test_results}problem_units_weird_country_{iso_today_date}.csv')
    # input('Did you check it yet?')
    return None

def check_for_lists(gdf):
    for col in gdf.columns:
        if any(isinstance(val, list) for val in gdf[col]):
            print('Column: {0}, has a list in it'.format(col))
        else:
            pass
