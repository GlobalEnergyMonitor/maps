from mimetypes import suffix_map
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString
from shapely import wkt
import math
# import polyline
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
from all_config import *
import re
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.styles import Alignment
import pickle
from collections import Counter


DATABASE_URL = 'postgresql://readonly:pc1d65885e80e7709675a2e635adcd9cb71bf91a375e5276f8ee143c623e2fb34@ec2-44-222-6-135.compute-1.amazonaws.com:5432/d8ik14rsae6026'
SQL = ''' 
    select unit_id, string_agg(all_entity_names, ', ') all_entity_names from (
    select 
    coalesce(pu.id, po.powerplant_unit_id) unit_id, 
    coalesce(c.name, '') || coalesce(c."nameOther"::text, '') || 
    coalesce(c.abbreviation, '') ||
    coalesce(c.name_local, '') all_entity_names
    from plant_owner po left join powerplant_unit pu on pu.plant_id = po.plant_id join company c on c.id = po.company_id) a
    group by unit_id;
    '''
# #### useful general functions ####

# def track_missing_data(dict_list_dfs_by_map, acro, maptype):
#     for mapname, list_dfs in dict_list_dfs_by_map.items():
#         if mapname == maptype:
#             for df in list_dfs:
#                 if df['tracker-acro'].iloc[0] == acro:    
#                     # print(f'This is the current count of all units for tracker {acro} in map: {mapname}:')
#                     # print(len(df[df['tracker-acro']==acro]))
#                     # input('Check that this number aligns with the number of units in the map')
#     return 


def remove_illegal_characters(value):
    if isinstance(value, str):
        # Define a regex pattern to match illegal characters
        illegal_characters = re.compile(r'[\x00-\x1F\x7F-\x9F]')
        # Replace illegal characters with an empty string
        return illegal_characters.sub('', value)
    return value

def set_up_df(df, t_name, acro, release):
    df['tracker-official'] = t_name
    df['tracker-acro'] = acro
    df['release-date'] = release
    
    df['tracker-official'] = df['tracker-official'].fillna('')
    df = df[df['tracker-official'] != '']
    # drop empty rows
    df = df.replace('*', pd.NA).replace('Unknown', pd.NA).replace('--', pd.NA)
    print(df)
    print(len(df))
    # input('Check df length, ggit-lng turns into a string?')
    # df = df.fillna('')
    df.columns = df.columns.str.strip()  # Strip blank spaces from column names

    # if acro == 'GNPT':
    #     print(df.columns)
    #     input('check columns in GNPT')
        
    # rename df 
    renaming_dict_sel = renaming_cols_dict[acro]
    df_renamed = df.rename(columns=renaming_dict_sel) 
    df_renamed.reset_index(drop=True, inplace=True)  # Reset index in place
    # print('and look into the default dict nonsense that will help')

    return df_renamed
                

def pull_from_db_sql():

    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    df = pd.read_sql(SQL, conn)
    # columns unit_id, string to search on for all entity name unit_id      all_entity_names
    # print(df.head())
    # print(df['unit_id'])
    # print(df.info())
    # input('CHECK IT WIHT DAVID HERE')
    
    return df

# pull_from_db_sql()


def split_multiple_delimiters(text, delimiters):
    regex_pattern = '|'.join(map(re.escape, delimiters))
    return re.split(regex_pattern, text)

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
    if 'Production & reserves' in tab_list:
        for tab in tab_list:
            if tab == 'Main data':
                gsheets = gspread_creds.open_by_key(key)
                spreadsheet = gsheets.worksheet(tab)
                main_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                print(main_df.info())
            elif tab == 'Production & reserves':
                gsheets = gspread_creds.open_by_key(key)
                spreadsheet = gsheets.worksheet(tab)
                prod_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                print(prod_df.info())
        
        df = process_goget_reserve_prod_data(main_df, prod_df)
        


    else:
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
                print(tab)
                wait_time = 5
                time.sleep(wait_time)
                gsheets = gspread_creds.open_by_key(key)
                # Access a specific tab
                # print(tab)
                # input('review tab to diagnose error')
                spreadsheet = gsheets.worksheet(tab)

                df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))

                list_of_dfs.append(df)
        if len(list_of_dfs) > 1: 
            # df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True).fillna('')
            
            df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True)

    return df
 
def create_prep_file(multi_tracker_log_sheet_key, prep_file_tab): # needed_map_list
    
    if local_copy:

        with open(f'local_pkl/prep_df{iso_today_date}.pkl', 'rb') as f:
            prep_df = pickle.load(f)
    else:
        prep_df = gspread_access_file_read_only(multi_tracker_log_sheet_key, prep_file_tab)
        # Add pickle format for prep_df
        prep_df = prep_df[prep_df['official release tab name'] != ''] # skips rows at bottom
        # Convert 'gspread_tabs' and 'sample_cols' to lists
        prep_df['gspread_tabs'] = prep_df['gspread_tabs'].apply(lambda x: x.split(';'))
        # df['sample_cols'] = df['sample_cols'].apply(lambda x: x.split(';'))
        prep_df['gspread_tabs'] = prep_df['gspread_tabs'].apply(lambda lst: [s.strip() for s in lst])
        # df['sample_cols'] = df['sample_cols'].apply(lambda lst: [s.strip() for s in lst])
        prep_df['official name'] = prep_df['official release tab name']

        prep_df.set_index('official release tab name', inplace=True) # sets index on offical name
        # prep_df['tracker-acro'] = prep_df['tracker-acro']
        
        with open(f'local_pkl/prep_df{iso_today_date}.pkl', 'wb') as f:
            pickle.dump(prep_df, f)
    return prep_df

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
    
    if local_copy:

        with open(f'local_pkl/gem_standard_country_names_{iso_today_date}.pkl', 'rb') as f:
            gem_standard_country_names = pickle.load(f)
    
    else:
        df = gspread_access_file_read_only(
            '1mtlwSJfWy1gbIwXVgpP3d6CcUEWo2OM0IvPD6yztGXI', 
            ['Countries'],
        )
        gem_standard_country_names = df['GEM Standard Country Name'].tolist()
        
        with open(f'local_pkl/gem_standard_country_names_{iso_today_date}.pkl', 'wb') as f:
            pickle.dump(gem_standard_country_names, f)
        
    
    return gem_standard_country_names

# gem_standard_country_names = get_standard_country_names()



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



def process_wkt_linestring(wkt_format_str, row):
    # split on commas to separate coordinate pairs from each other
    line = wkt_format_str.replace('LINESTRING', '').strip('() ')
    line_list = line.split(', ')

    line_list_rev = [] # initialize
    for pair in line_list:
        try:
            # in WKT, order is lon lat
            lon = pair.split(' ')[0]
            lat = pair.split(' ')[1]
            # put into Google Maps order & format
            line_list_rev += [f"{lat},{lon}:"]
        except:
            print(f"In process_wkt_linestring, couldn't process {pair} (in row {row})")

    google_maps_line = ''.join(line_list_rev).strip(':')

    return google_maps_line

def convert_wkt_to_google_maps(pipes_df):
    """
    GGIT official release has pipeline routes in WKT format only.
    For map file, need to convert to Google Maps format.
    Put Google Maps format into column 'Route'.

    In WKT:
    * Each coordinate pair is longitude then latitude, separated by spaces
    * Within linestrings: Coordinate pairs are separated by commas
    * Within multilinestrings: Linestrings are bookended by parentheses
    
    In Google Maps:
    * Each coordinate pair is latitude then longitude, separated by comma
    * Within linestrings: Coordinate pairs are separated by colons
    * Within multilinestrings: Linestrings are separated by semicolons
    """
    print("Running convert_wkt_to_google_maps")
    truncated = [] # initialize
    for row in pipes_df.index:
        # route = pipes_df.at[row, 'Route']
        wkt_format_str = pipes_df.at[row, 'WKTFormat']
        name = pipes_df.at[row, 'PipelineName']

        # if len(route) > 1:
            # print(f'ROUTE IS MORE THAN 1: {route}')
            # want to keep route information for few cases that it has it feb 2024
            # pass     
        if wkt_format_str == '--':
            # Known empty value
            pass
        else:
            if wkt_format_str.endswith(')') == True:
                # formatted correctly; not truncated
                pass
            elif wkt_format_str.endswith(')') == False:
                # it is truncated; need to get rid of partial coordinates
                truncated += [(
                    pipes_df.at[row, 'PipelineName'], 
                    pipes_df.at[row, 'Countries'], 
                    wkt_format_str[-30:]
                )]
                
                wkt_format_str = wkt_format_str.rsplit(',', 1)[0].strip()
                if wkt_format_str.startswith('LINESTRING'):
                    # close with single parentheses
                    wkt_format_str = f"{wkt_format_str})"
                elif wkt_format_str.startswith('MULTILINESTRING'):
                    # close with double parentheses
                    wkt_format_str = f"{wkt_format_str}))"

            if wkt_format_str.startswith('LINESTRING'):
                google_maps_str = process_wkt_linestring(wkt_format_str, row)
                pipes_df.at[row, 'Route'] = google_maps_str

            elif wkt_format_str.startswith('MULTILINESTRING'):
                wkt_multiline = wkt_format_str.replace('MULTILINESTRING', '').strip('() ')
                # split on '), '--marker of the end of a linestring
                wkt_multiline_list = wkt_multiline.split('), ')

                # clean up:
                wkt_multiline_list = [x.strip('(') for x in wkt_multiline_list]

                multiline_list_rev = [] # initialize
                for wkt_line in wkt_multiline_list:
                    google_maps_line = process_wkt_linestring(wkt_line, row)
                    multiline_list_rev += [google_maps_line]

                google_maps_str = ';'.join(multiline_list_rev)
                pipes_df.at[row, 'Route'] = google_maps_str

            else:
                print("Error!" + f" Couldn't convert to Google Maps: {wkt_format_str}")
                print((name, wkt_format_str))
            
                pass
    
    # after end of for row in pipes_df.index
    if len(truncated) > 0:
        print(f"WKTFormat was truncated for {len(truncated)} pipelines")
        print(truncated)

        for x in truncated:
            print(f"{x[0]} in {x[1]}; last 30 characters: {x[2]}")
            print('-'*40)
            
    return pipes_df

def coordinate_qc(df):
    issues_coords = {} # acro, df line
    df = df.reset_index()
    tracker = df['tracker-acro'].loc[0]
    df.columns = df.columns.str.lower()
    # wait_time = 5
    # time.sleep(wait_time)
    # gsheets = gspread_creds.open_by_key(multi_tracker_countries_sheet)
    # spreadsheet = gsheets.worksheet('country_centroids')
    # country_centroids = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
    # split on comma, check valid lat lng, 
    # in a float valid range 
    
    # print(len(df))
    # df['WKTFormat'] = df['WKTFormat'].make_valid()
    # print(len(df))
    # input('After make valid')

    if 'WKTFormat' in df.columns: # special for hydrogen europe file
        # df['wktformat_clean'] = df['Route'].apply(lambda x: check_and_convert_float(x))
        pass


    else:
        df['float_col_clean_lat'] = df['latitude'].apply(lambda x: check_and_convert_float(x))
        
        df['float_col_clean_lng'] = df['longitude'].apply(lambda x: check_and_convert_float(x))
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
        # QC
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
                df.loc[row, 'latitude'] = df.loc[row, 'float_col_clean_lat']
                df.loc[row, 'longitude'] = df.loc[row, 'float_col_clean_lng']

    return df, issues_coords

# def find_missing_geometry(gdf,col_country_name):
#     if gdf['geometry'] == '':
#         gdf = find_missing_coords(gdf, col_country_name)
#     elif gdf['geometry'] == 'POINT(1 1)':
#         print('point 11 issue again')
#     return gdf
def split_countries(country_str):

    for sep in [';', '-', ',']:
        if sep in country_str:
            return country_str.strip().split(sep)
        return [country_str]
    
def create_filtered_df_list_by_map_eu(trackerdf, col_country_name, needed_geo):
    filtered_df = trackerdf.copy()

    filtered_df['country_to_check'] = filtered_df.apply(lambda row: split_countries(row[col_country_name]), axis=1)
    # print(filtered_df['country_to_check'])
    # input('check this')
    filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]

    return filtered_df

def filter_goget_for_europe(df):
    europe_countries = [
        'Åland Islands', 'Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium',
        'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Czech Republic',
        'Denmark', 'Estonia', 'Faroe Islands', 'Finland', 'France', 'Germany',
        'Gibraltar', 'Greece', 'Guernsey', 'Holy See', 'Hungary', 'Iceland',
        'Ireland', 'Isle of Man', 'Italy', 'Jersey', 'Kosovo', 'Latvia',
        'Liechtenstein', 'Lithuania', 'Luxembourg', 'North Macedonia', 'Malta',
        'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'Norway', 'Poland',
        'Portugal', 'Romania', 'Israel', 'San Marino', 'Serbia', 'Slovakia',
        'Slovenia', 'Spain', 'Svalbard and Jan Mayen', 'Sweden', 'Switzerland',
        'Ukraine', 'United Kingdom', 'Cyprus', 'Türkiye'
    ]

    drop_row = []
    for row in df.index:

        if df.loc[row, 'Fuel type'] == 'oil':
            drop_row.append(row)
    print(f'Length of goget before oil drop: {len(df)}')
    df.drop(drop_row, inplace=True)
    print(f'Length of goget after oil drop: {len(df)}')

    df = create_filtered_df_list_by_map_eu(df, 'Country/Area', europe_countries)

    return df


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

# def insert_incomplete_WKTformat_ggit_eu(df_to_drop):
#     # df_to_drop = df_to_drop.copy() # df to drop
#     # by project id that we know were cut off because not json file
#     # insert json into geometry
#     # create geometry column 
#     for col in df_to_drop.columns:
#         print(col)
#     input('find ProjectID in df_map / df_to_drop')
#     # set up fixed ggit file pd
#     ggit_routes = gpd.read_file(ggit_routes_updated)    
#     ggit_routes = ggit_routes[['ProjectID', 'geometry']]
#     # print(ggit_routes['geometry'])
#     # input('this should not be empty ggit routes geo')
#     # df_to_drop.to_csv(f'issues/check_out_df_to_drop_cols_before_merge_routes {iso_today_date}.csv')

#     # Merge ggit_routes with the main gdf on 'id'
#     for col in df_to_drop.columns:
#         print(col)
#     input('find ProjectID in df_to_drop')
#     df_to_drop = df_to_drop.merge(ggit_routes[['ProjectID', 'geometry']], on='ProjectID', how='left', suffixes=('', '_new'))    
    
#     merged_df = df_to_drop.drop(columns='geometry').merge(ggit_routes, on='ProjectID', how='left')
#     # Update the 'route' column in gdf with the new values where there is a match
#     # print(f'this is length of df_to_drop {len(df_to_drop)} should be 10')
#     # input('check')
#     # df_to_drop.drop(columns=['geometry'], inplace=True)
#     # df_to_drop['geometry'] = df_to_drop['geometry_new']
#     # # Drop the temporary 'route_new' column
#     # df_to_drop.drop(columns=['geometry_new'], inplace=True)
#     df_to_drop.to_csv(f'issues/check_out_df_to_drop_cols_after_merge_routes {iso_today_date}.csv')
#     print(f'done issues/check_out_df_to_drop_cols_after_merge_routes {iso_today_date}.csv')
#     # drop row if geometry equals none
#     # df_to_drop = df_to_drop[df_to_drop['geometry'].notna()]
#     # print(df_to_drop['tracker-acro'])
#     # print(df_to_drop)
#     # input('check this after merge and drop geo, should be 10!')

#     return merged_df

def drop_internal_tabs(df):
    df = df.drop(['tracker-acro','official_name','country_to_check'], axis=1)
    print(df.columns)
    # input('Check to see that tracker-acro and other internal cols are gone')
    return df

def convert_google_to_gdf(df):
    # TODO DOCUMENT HOW EU PIPELINES HY DATA PROCESSED UNTIL HAVE GEOJSON FILE
    df_initial = df.copy()
    print(df.columns)
    # input('check if WKTFormat is there, and also PipelineName')
    df = df[df['WKTFormat'] != '--']
    print(df[['PipelineName', 'WKTFormat']]) # or name
    df['WKTFormat'].fillna('')
    df = df[df['WKTFormat'] != '']
    print(df[['PipelineName', 'WKTFormat']])

    to_drop = []
    for row in df.index:
        if pd.isna(df.loc[row, 'WKTFormat']): 
            to_drop.append(row)
    # df['geometry'] = df['WKTFormat'].apply(lambda x: wkt.loads(x))
    # print(df['geometry'])
    to_drop_again = []
    to_drop_pid = []
    for index, row in df.iterrows():
        # try:
        value = row["WKTFormat"]
        pid = row["ProjectID"]
        try:
            wkt.loads(value)
            # print(value)
                
        except Exception as e:
            print(e)
            # input('DROPPING THIS INDEX IN CONVERT WKFORMAT/GOOGLE TO GDF FUNCTION')
            to_drop_again.append(index)
            to_drop_pid.append(pid)
        # print(f'{index} {value!r}')
    # input('Dropped pipeline')

    df_to_drop = df.loc[to_drop_again]
# print(df_to_drop)
# input('Inspect that it is a df and only 10')
# then add geometry column from separate file and drop wkt, 
# then concat later in two steps after this main df is a gdf  
# df_to_drop = insert_incomplete_WKTformat_ggit_eu(df_to_drop)

# for col in df_to_drop.columns:
#     print(col)

# for col in df.columns:
#     print(col)

    df = df.drop(to_drop_again) 
    
    df['geometry'] = df['WKTFormat'].apply(lambda x: wkt.loads(x))
    
    print(len(df))
    df = pd.concat([df, df_to_drop])
    print(len(df))
    input('length after of length of df')
    
    # print(df['geometry'])
    # print(df['PCI5'])
    # input('CHECK PCI5')

    input(f'Check size before and after: now | {len(df)} then | {len(df_initial)}')
    
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    return gdf


diacritic_map = {
    'a': ["a", "á", "à", "â", "ã", "ä", "å"],
    'e': ["e", "é", "è", "ê", "ë"],
    'i': ["i", "í", "ì", "î", "ï"],
    'o': ["o", "ó", "ò", "ô", "õ", "ö", "ø"],
    'u': ["u", "ú", "ù", "û", "ü"],
    'c': ["c", "ç"],
    'n': ["n", "ñ"],
}


def remove_diacritics(name_value):
    # name_value = name_value.fillna('')
    no_diacritics_name_value = ''
    if type(name_value) != float:
        no_diacritics_name_value = name_value[:]
        for char in no_diacritics_name_value:
            for k, v in diacritic_map.items():
                if char in v:
                    no_diacritics_name_value = no_diacritics_name_value.replace(char, k)

    return no_diacritics_name_value

def split_goget_ggit_eu(df):

    if df['tracker'].iloc[0] == 'extraction':
        # df_goget_missing_units.to_csv('compilation_output/missing_gas_oil_unit_goget.csv')
        # gdf['tracker_custom'] = gdf.apply(lambda row: 'GOGET - gas' if row['Production - Gas (Million m³/y)'] != '' else 'GOGET-oil', axis=1)
        df['tracker_custom'] = 'GOGET-oil'

    elif df['tracker'].iloc[0] == 'term':
        # gdf_ggit_missing_units = df[df['facilitytype']=='']
        # gdf_ggit_missing_units.to_csv('/content/drive/MyDrive/output_from_colab/missing_gas_oil_unit_ggit.csv')
        # df = df[df['facilitytype']!='']
        df['tracker_custom'] = df.apply(lambda row: 'GGIT-import' if row['facilitytype'] == 'Import' else 'GGIT-export', axis=1)

    elif df['tracker'].iloc[0] == 'plants':
        df['tracker_custom'] = 'GOGPT'

    elif df['tracker'].iloc[0] == 'pipes':
        df['tracker_custom'] = 'GGIT'
    elif df['tracker'].iloc[0] == 'plants_hy':
        df['tracker_custom'] = 'GOGPT'

    return df


def create_conversion_df(conversion_key, conversion_tab):
    if local_copy:

        # Load the list of GeoDataFrames from the pickle file
        with open('local_pkl/conversion_df.pkl', 'rb') as f:
            df = pickle.load(f)

        print("DataFrames have been loaded from conversion_df.pkl")        
                
    else:
        df = gspread_access_file_read_only(conversion_key, conversion_tab)
        # # # printf'this is conversion df: {df}')
        
        df = df[['tracker', 'type', 'original units', 'conversion factor (capacity/production to common energy equivalents, TJ/y)']]
        df = df.rename(columns={'conversion factor (capacity/production to common energy equivalents, TJ/y)': 'conversion_factor', 'original units': 'original_units'})
        df['tracker'] = df['tracker'].apply(lambda x: x.strip())
        
        with open('local_pkl/conversion_df.pkl', 'wb') as f:
            pickle.dump(df, f)
        print("DataFrames have been saved to conversion_df.pkl")

    return df  

def assign_conversion_factors(df, conversion_df):

    for row in df.index:
        print(df.columns)
        if df.loc[row, 'tracker_custom'] == 'GOGET-oil':
            df.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['original_units'].values[0]
            df.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['conversion_factor'].values[0]

        elif df.loc[row, 'tracker_custom'] == 'GGIT-export':
            df.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-export']['original_units'].values[0]
            df.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-export']['conversion_factor'].values[0]
        elif df.loc[row, 'tracker_custom'] == 'GGIT-import':
            df.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-import']['original_units'].values[0]
            df.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-import']['conversion_factor'].values[0]

        elif df.loc[row, 'tracker_custom'] == 'GGIT':
            df['original_units'] = conversion_df[conversion_df['tracker']=='GGIT']['original_units'].values[0]
            df['conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT']['conversion_factor'].values[0]
        elif df.loc[row, 'tracker_custom'] == 'GOGPT':
            df['original_units'] = conversion_df[conversion_df['tracker']=='GOGPT']['original_units'].values[0]
            df['conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGPT']['conversion_factor'].values[0]

    return df


def rename_gdfs(df):
    # df.columns = df.columns.str.lower() # TEST but this shouldn't be here
    # df.columns = df.columns.str.replace(' ', '-')

    tracker_sel = df['tracker'].iloc[0] # plants, term, pipes, extraction

    renaming_dict_sel = renaming_cols_dict[tracker_sel]
    # rename the columns!
    df = df.rename(columns=renaming_dict_sel)
    df.reset_index(drop=True, inplace=True)
    
    
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '-')
    # find any duplicated column names
    all_columns = df.columns
    column_counts = Counter(all_columns)
    duplicate_columns = [name for name, count in column_counts.items() if count > 1]
    if len(duplicate_columns) > 0:
        print(f"Duplicate column names found: {duplicate_columns} for {tracker_sel}")
        input('FIX')
    else:
        print("No duplicate column names found.")
    print(duplicate_columns)  # Output: ['geometry', 'tracker', 'capacity', ...]
    # for i, col in enumerate(duplicate_columns):
    #     df.rename(columns={col: f"{col}_{i+1}"}, inplace=True)

    return df



def maturity(df):
  df['maturity'] = 'none' # starts as none

  for row in df.index:
      if df.loc[row, 'fuel-filter'] == 'methane':
          df.loc[row, 'maturity'] = 'none'
      else:
        if df.loc[row, 'tracker'] == 'plants_hy':
            df['maturity'] = np.where((df['status'] == 'Construction') | (df['mou-for-h2-supply?'] == 'Y') | (df['contract-for-h2-supply?'] == 'Y') | (df['financing-for-supply-of-h2?'] == 'Y') | (df['co-located-with-electrolyzer/h2-production-facility?'] == 'Y'), 'y','n')

        elif df.loc[row, 'tracker'] == 'term':
            # if df.loc[row, 'fuel-filter'] == 'methane':
            #     df.loc[row, 'maturity'] = 'none'
            # else:
              df['maturity'] = np.where((df['status'] == 'Construction') | (df['fidstatus'] == 'FID') | (df['altfuelprelimagreement'] == 'yes') | (df['altfuelcallmarketinterest'] == 'yes'), 'y','n')

        elif df.loc[row, 'tracker'] == 'pipes':
            # if df.loc[row, 'fuel-filter'] != 'methane':
                # df.loc[row, 'maturity'] = 'none'
                # break out of this for loop and go to the next row
                df['maturity'] = np.where((df['status'] == 'Construction') | (df['pci5'] == 'yes') | (df['pci6'] == 'yes'), 'y','n')

  # override any where fuel is methane
  for row in df.index:
      if df.loc[row, 'fuel-filter'] == 'methane':
          df.loc[row, 'maturity'] = 'none'

  return df

def fuel_filter(df):
  df.columns = df.columns.str.lower()
  df.columns = df.columns.str.replace(' ', '-')
  df['fuel-filter'] = 'methane'
  if df['tracker'].iloc[0] == 'extraction':
      df['fuel-filter'] = 'methane'

  elif df['tracker'].iloc[0] == 'plants_hy':
    # if hydrogen in the fuel column then if H2 usage proposed % to see if it's blend or 100% hydrogen
    # df['fuel-filter'] = np.where(df['fuel'].str.lower().str.contains('hydrogen'), df['h2-usage-proposed-%'], 'methane')
    # find all fuels that have hydrogen and [100] in h2-usage-proposed-%
    for row in df.index:
      # if hydrogen in fuel column
      if 'hydrogen' in df.loc[row, 'fuel'].lower():
        # print(df.loc[row, 'h2-usage-proposed-%'])
        if df.loc[row, 'h2-usage-proposed-%'] == 100:
          df.loc[row, 'fuel-filter'] = 'hy'
        else:
          df.loc[row, 'fuel-filter'] = 'blend'

  elif df['tracker'].iloc[0] == 'plants':
    df['fuel-filter'] = 'methane'

  elif df['tracker'].iloc[0] == 'term':
    df['fuel'] = df['fuel'].str.lower()
    df['fuel-filter'] = np.where((df['fuel'] != 'lng') & (df['fuel'] != 'oil'), 'hy', df['fuel-filter'])

  elif df['tracker'].iloc[0] == 'pipes':
    df['h2%'].fillna('', inplace=True)

    for row in df.index:
      if df.loc[row, 'fuel'].lower().strip() == 'hydrogen':
        # print(df.loc[row, 'h2%']) # h2 does not exist in json or dd so making them all blend
        # convert the column to a string after filling na
        df.loc[row, 'h2%'] = str(df.loc[row, 'h2%'])
        # print(df.loc[row, 'h2%']) # h2 does not exist in json or dd so making them all blend
        if df.loc[row, 'h2%'] == '100.00%':
          df.loc[row, 'fuel-filter'] = 'hy'
        elif df.loc[row, 'h2%'] == '':
          df.loc[row, 'fuel-filter'] = 'hy'
        else:
          df.loc[row, 'fuel-filter'] = 'blend'

  return df

def check_in_range(value, min_val, max_val):
    # doesn't handle na because already was handled
    if min_val <= value <= max_val:

        return value

    else:
        print('problem with coords:')
        print(f'value:{value}, min_val:{min_val}, max_val:{max_val}')
        return np.nan

def make_sure_methane_is_none_maturity(gdf):
    print('in maturity')

    # gdf['maturity'] = gdf.apply(lambda row: 'none' if row['fuel-filter'] == 'methane' else row['maturity'])

    return gdf

def create_map_file_eu(one_gdf_by_maptype_fixed):
    finalcols = ['status-legend','status', 'fuel-filter', 'tracker-custom', 'maturity', 'pci-list', 'scaling-capacity', 'name', 'areas',
        'unit-name', 'owner', 'parent', 'capacity-table', 'units-of-m','start-year', 'prod-gas', 'prod-year-gas', 'tracker-display',
        'areas-subnat-sat-display','other-name', 'local-name', 'geometry', 'url', 'id', 'pid']
    
    final_cols_eu = ['unit_id', 'mapname','tracker-acro','url', 'areas','name', 'unit_name', 'capacity', 'status', 'subnat', 'region', 'owner', 'parent', 'tracker', 'tracker_custom',
        'original_units', 'conversion_factor', 'geometry', 'river', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2',
        'prod-coal', 'pid','id', 'prod_oil', 'prod_gas', 'prod_year_oil', 'prod_year_gas', 'fuel', 'pci5', 'pci6', 'geometry', 'tracker', 'start_year', 'region2', 'subnat2', 'other-local', 'other-name',
        'fuel-filter', 'maturity', 'tracker_custom', 'original_units','mult_countries', 'prod_start_year',
        'conversion_factor', 'capacity', 'location', 'prefecture/district', 'state/province', 'search', 'operator(s)_search', 'name_search',
        'owner_search', 'parent_search']
    final_dict_gdfs = {}
    for mapname, gdf in one_gdf_by_maptype_fixed.items():
        # gdf = gdf.copy()
        if 'fuel-filter' not in gdf.columns:
            input('issue here')
        elif 'geometry' not in gdf.columns:
            input('issue here')

        # filter by finalcols
        cols_to_drop = [col for col in gdf.columns if col not in (finalcols + final_cols_eu)]
        # print(gdf.columns)

        gdf.drop(columns=cols_to_drop, inplace=True)

        print(gdf.columns)
        if 'fuel-filter' not in gdf.columns:
            input('issue here')
        elif 'geometry' not in gdf.columns:
            input('issue here')
        print(mapname)
        print(f'Saving file for map {mapname}')
        print(f'This is len of gdf {len(gdf)}')
        path_for_download_and_map_files_eu = gem_path + 'europe' + '/compilation_output/'

        # gdf.to_file("/tmp/output.geojson", driver="GeoJSON")
        # if mapname in gas_only_maps: # will probably end up making all regional maps all energy I would think
        #     gdf = gdf.drop(['count-of-semi', 'multi-country', 'original-units', 'conversion-factor', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1) # 'multi-country', 'original-units', 'conversion-factor', 'cleaned-cap', 'wiki-from-name', 'tracker-legend']

        # else:
        #     gdf = gdf.drop(['count-of-semi','multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1) #  'multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend']

        check_for_lists(gdf)

        print(gdf['geometry'])
        # df.set_geometry(gpd.GeoSeries.from_wkt(df['geometry']), inplace=True)
        # gdf = gdf.to_crs(epsg=4326)
        print(f'this is fuel filter {gdf["fuel-filter"]}')
        gdf = make_sure_methane_is_none_maturity(gdf)
        gdf.to_file(f'{path_for_download_and_map_files_eu}europe_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
        gdf.to_csv(f'{path_for_download_and_map_files_eu}europe_{iso_today_date}.csv', encoding='utf-8')
        gdf.to_file(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/europe_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
        final_dict_gdfs[mapname] = gdf

    # print(final_dict_gdfs.keys())
    return final_dict_gdfs



def map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions):
    cleaned_dict_by_map_one_gdf_with_better_statuses = {}
    for mapname, gdf in cleaned_dict_map_by_one_gdf_with_conversions.items():
        print(gdf.columns.to_list())
        input('inspect cols no tracker-acro?')
        path_for_test_results = gem_path + mapname + '/test_results/'           

        # print(set(gdf['status'].to_list()))
        # mask_gbpt = gdf['tracker-acro'] == 'GBPT'
        # print(gdf.loc[mask_gbpt, 'status'])
        # #(input('check statuses of bio before')
        
        gdf['status'] = gdf['status'].fillna('Not Found') # ValueError: Cannot mask with non-boolean array containing NA / NaN values
        gdf['status'] = gdf['status'].replace('', 'Not Found') # ValueError: Cannot mask with non-boolean array containing NA / NaN values
        # print(set(gdf['status'].to_list()))
        gdf_map_ready = fix_status_inferred(gdf)
        
        # Create masks for the 'tracker-acro' conditions
        mask_gcmt = gdf_map_ready['tracker-acro'] == 'GCMT'
        mask_goget = gdf_map_ready['tracker-acro'] == 'GOGET'
        # mask_gbpt = gdf_map_ready['tracker-acro'] == 'GBPT'
        
        # Update 'status' to 'Retired' where both masks are True
        gdf_map_ready['status'].fillna('', inplace=True)
        mask_status_empty = gdf_map_ready['status'] == ''
        # print(mask_status_empty)
        # # #(input('check the above for empty statuses')
        # print(gdf_map_ready.loc[mask_gbpt, 'status'])
        # #(input('check statuses of bio')
        
        # Update 'status' to 'Not Found' where both masks are True
        gdf_map_ready.loc[mask_status_empty & mask_gcmt, 'status'] = 'retired'
        gdf_map_ready.loc[mask_status_empty & mask_goget, 'status'] = 'not found'
        gdf_map_ready['status_legend'] = gdf_map_ready.copy()['status'].str.lower().replace({
                    # proposed_plus
                    'proposed': 'proposed_plus',
                    'announced': 'proposed_plus',
                    'discovered': 'proposed_plus',
                    # pre-construction_plus
                    'pre-construction': 'pre-construction_plus',
                    'pre-permit': 'pre-construction_plus',
                    'permitted': 'pre-construction_plus',
                    # construction_plus
                    'construction': 'construction_plus',
                    'in development': 'construction_plus',
                    # mothballed
                    'mothballed': 'mothballed_plus',
                    'idle': 'mothballed_plus',
                    'shut in': 'mothballed_plus',
                    # retired
                    'retired': 'retired_plus',
                    'closed': 'retired_plus',
                    'decommissioned': 'retired_plus',
                    'not found': 'not-found'})


        # Create a mask for rows where 'status' is empty

        gdf_map_ready_no_status = gdf_map_ready.loc[mask_status_empty]
        # # # ##(input(f'check no status df: {gdf_map_ready_no_status}')

        gdf_map_ready_no_status.to_csv(f'issues/no-status-{mapname}_{iso_today_date}.csv')
        # make sure all statuses align with no space rule
        # gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.strip().replace(' ','-'))
        gdf_map_ready['status_legend'] = gdf_map_ready['status_legend'].apply(lambda x: x.strip().replace('_','-'))
        # # printset(gdf_map_ready['status'].to_list()))
        gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.lower())
        # # printset(gdf_map_ready['status'].to_list()))
        
        print(set(gdf_map_ready['areas'].to_list()))
        
        
        cleaned_dict_by_map_one_gdf_with_better_statuses[mapname] = gdf_map_ready
    
    # # printcleaned_dict_by_map_one_gdf_with_better_statuses.keys())
    # # # ##(input('check that there are enough maps')
    return cleaned_dict_by_map_one_gdf_with_better_statuses



def map_ready_countries(cleaned_dict_by_map_one_gdf_with_better_statuses):
    cleaned_dict_by_map_one_gdf_with_better_countries = {}
    for mapname, gdf in cleaned_dict_by_map_one_gdf_with_better_statuses.items():
        print(f'We are on mapname: {mapname}')
        
        # check that areas isn't empty
        tracker_sel = gdf['tracker-acro'].iloc[0]
        if tracker_sel == 'GOGET':
            print(gdf['areas'])
            input('check goget areas in map ready countries')
        gdf['areas'] = gdf['areas'].fillna('')

        empty_areas = gdf[gdf['areas']=='']
        if len(empty_areas) > 0:
            print(f'Check out which rows are empty for countries for map: {mapname}')
            print(empty_areas)
            # #(input('Remove above')
            empty_areas.to_csv(f'issues/empty-areas-{tracker_sel}{iso_today_date}.csv')

        # this formats subnational area for detail maps
        # we would also want to overwrite the subnat and say nothing ""
        gdf['count-of-semi'] = gdf.apply(lambda row: row['areas'].strip().split(';'), axis=1) # if len of list is more than 2, then split more than once
        gdf['count-of-semi'] = gdf.apply(lambda row: row['areas'].strip().split('-'), axis=1) # for goget
        gdf['count-of-semi'] = gdf.apply(lambda row: row['areas'].strip().split(','), axis=1) # just adding in case

        gdf['multi-country'] = gdf.apply(lambda row: 't' if len(row['count-of-semi']) > 1 else 'f', axis=1)
        # # printgdf['multi-country'])
        # if t then make areas-display 
        gdf['subnat'].fillna('', inplace=True)
        # if one country and subnat exists TEST THIS
        gdf['areas-subnat-sat-display'] = gdf.apply(lambda row: f"{row['subnat'].strip().strip('')}, {row['areas'].strip().strip('')}" if row['multi-country'] == 'f' and row['subnat'] != '' else row['areas'].strip(), axis=1) # row['areas'].strip()
        # if more than one country replace the '' with mult countries
        
        # print('Printing all count of semi more than 1')
        # print(gdf[gdf['count-of-semi'].apply(len) > 1])
        # print('Printing multi-country t')
        # print(gdf[gdf['multi-country']=='t'])
        
        # print(gdf[gdf['name']== 'Mexico-Northern Central America Gas Pipeline'])
        # #(input('This should be not empty!')
        maskt = gdf['multi-country']=='t'
        # print(len(maskt))
        # #(input('check more than just hydro')
        gdf.loc[maskt, 'areas-subnat-sat-display'] = 'multiple areas/countries'
        # print(gdf[gdf['areas-subnat-sat-display']!=''])
        # print(gdf[gdf['id']=='P0539'])
        # #(input('check subnat mult countries test')
        # just need to make sure all countries are separated by a comma and have a comma after last country as well
        # GOGET has a hyphen in countries
        # GOIT has comma separated in countries
        # hydropower has two columns country1 and country2
        # GGIT has comma separated in countries
        # grouped_tracker_before = gdf.groupby('tracker-acro', as_index=False)['id'].count()
        # # # printf'In map ready before adjustment: {grouped_tracker_before}')
        # # no return

        # gdf_map_ready['area2'] = gdf_map_ready['area2'].fillna('')
            
        if mapname in gas_only_maps:
            # handle for gas only maps
            print('In not map only area of function')
            gdf['areas'] = gdf['areas'].fillna('')
            gdf['areas'] = gdf['areas'].apply(lambda x: x.replace(',', ';')) # try this to fix geojson multiple country issue
            gdf['areas'] = gdf['areas'].apply(lambda x: f"{x.strip()};")
            print(gdf['areas'])
            # input('check above has semicolon')
        
        else: 
            
            # print(gdf_map_ready[['areas', 'tracker-acro', 'name']])
            # print(set(gdf_map_ready['areas'].to_list()))
            # print(set(gdf_map_ready['area2'].to_list()))
            gdf['area2'] = gdf['area2'].fillna('')
            gdf['areas'] = gdf['areas'].fillna('')
            
            gdf['areas'] = gdf['areas'].apply(lambda x: x.replace(',', ';')) # try this to fix geojson multiple country issue
            gdf['areas'] = gdf['areas'].apply(lambda x: f"{x.strip()};")
            # print(set(gdf['areas'].to_list()))
            # print(set(gdf['area2'].to_list()))
            # nan_areas = gdf[gdf['areas']=='']
            # print(f'Nan areas: {len(nan_areas)}')
            # # print(nan_areas)
            # input('check nan areas')
            # issues = []
            # tracker_issues = []
            # for row in gdf.index:
            #     if gdf.loc[row, 'areas'] == '':
            #         issues.append(row)
            #         tracker_issues.append(gdf.loc[row, 'tracker-acro'])
            # # if len(issues) >0 :
            # #     print(f'No areas here for these trackers:')
            # #     print(set(tracker_issues))
            # gdf = gdf.drop(issues)
            # issues_df = {'missing_country': issues}
            # issues_df = pd.DataFrame(issues_df)
            # issues_df.to_csv(f'issues/missing_county{mapname}{iso_today_date}.csv')
            # print('Printed issues_df to file and dropped themf rom the df.')
            
            # # ##(input('All area2s in gdf check if any are numbers')
            # if mapname == 'Global':
            #     gdf['areas'] = f"{gdf['areas']};"
                
            # else:
            #     for row in gdf.index:

            #         if gdf.loc[row, 'area2'] != '':
        
            #             gdf.at[row, 'areas'] = f"{gdf.loc[row, 'areas'].strip()};{gdf.loc[row, 'area2'].strip()};"
            #             # print(f"Found a area2! Hydro? {gdf.loc[row, 'areas']} {gdf.loc[row, 'tracker-acro']} {gdf.loc[row, 'name']}")
            #             print(gdf.loc[row,'areas'])
            #             input('check above is ; ; not ,; mult country')
            #         else:
            #             # make it so all areas even just one end with a semincolon 
            #             gdf['areas'] = gdf['areas'].fillna('')
            #             # nan_areas = gdf[gdf['areas']=='']
            #             # print(f'in else: {set(gdf["areas"].to_list())}') # find the rows that are nan or float
            #             ser = gdf['areas']
            #             try:
            #                 ser_str = ser.astype(str)
            #             except:
            #                 for row in ser.index:
            #                     val = ser.iloc[row]
            #                     try:
            #                         val_str = str(val)
            #                     except:
            #                         print("Error!" + f" val couldn't be converted to str: {val}")
                        
            #             gdf.at[row, 'areas'] = f"{gdf.loc[row, 'areas'].strip()};"

        # grouped_tracker_after = gdf.groupby('tracker-acro', as_index=False)['id'].count()

        # # # printf'In map ready after adjustment: {grouped_tracker_after}')
        # print(gdf.head())
        # print(gdf.columns)
        # #(input('check if semi and multi here?')
        cleaned_dict_by_map_one_gdf_with_better_countries[mapname] = gdf  
    # # printcleaned_dict_by_map_one_gdf_with_better_countries.keys())
    # # # ##(input('check that there are enough maps')
    return cleaned_dict_by_map_one_gdf_with_better_countries


def workarounds_eg_interim_goget_gcmt_eu(cleaned_dict_by_map_one_gdf_with_better_countries):
    # this function mostly creates a new col for correctly formatted info when there is multiple countries, especially for the details card
    # it also handles oil and gas for goget, TODO should add removal of oil for gas only map maybe?
    one_gdf_by_maptype = {}
    for mapname, gdf in cleaned_dict_by_map_one_gdf_with_better_countries.items():
        gdf = gdf.copy()

        list_invalid_goget = []
        list_invalid_gcmt = []
        if mapname in ['GIPT', 'Global']:
            # does not have goget
            one_gdf_by_maptype[mapname] = gdf

        else:
            # # # printgdf.columns)
            # # # ##(input('Check if prod-oil is there in columns')
            for row in gdf.index:

                tracker = (gdf.loc[row, 'tracker'])
                #if goget then make capacity table and capacity details empty


                if tracker == 'extraction':
                    gdf.loc[row, 'capacity-table'] = np.nan
                    gdf.loc[row, 'capacity-details'] = ''
                    prod_oil = gdf.loc[row, 'prod_oil']
                    prod_gas = gdf.loc[row, 'prod_gas']
                    prod_oil = check_and_convert_float(prod_oil) # NEW TO TEST FOR ROUNDING ALL GETTING CAUGH TIN INVALID GOGET
                    prod_gas = check_and_convert_float(prod_gas)

                else:
                    continue
        one_gdf_by_maptype[mapname] = gdf
    # # printone_gdf_by_maptype.keys())
    return one_gdf_by_maptype


def capacity_conversions_eu(cleaned_dict_map_by_one_gdf):

# you could multiply all the capacity/production values in each tracker by the values in column C,
# "conversion factor (capacity/production to common energy equivalents, TJ/y)."
# For this to work, we have to be sure we're using values from each tracker that are standardized
# to the same units that are stated in this sheet (column B, "original units").

# need to get nuances for each tracker, it's just GGIT if point then do lng terminal if line then do pipeline
    cleaned_dict_map_by_one_gdf_with_conversions = {}
    for mapname, one_gdf in cleaned_dict_map_by_one_gdf.items():
        gdf_converted = one_gdf.copy()
        if mapname in gas_only_maps:
            print('no need to handle for hydro having two capacities')
            print(gdf_converted.columns)
            print(set(gdf_converted['areas'].to_list()))
            # continue
        # else:
        #     # first let's get GHPT cap added
        #     # # printmapname) # africa
        #     # # printset(gdf_converted['tracker-acro'].to_list())) # only pipeline
        #     ghpt_only = gdf_converted[gdf_converted['tracker-acro']=='GHPT'] # for GGPT we need to re run it to get it
        #     print(len(ghpt_only))
        #     print(mapname)
        #     # ##(input('check')
        #     gdf_converted = gdf_converted[gdf_converted['tracker-acro']!='GHPT']
        #     # # printlen(ghpt_only['capacity']))
        #     # # printlen(ghpt_only['capacity1']))
        #     # # printlen(ghpt_only['capacity2']))
        #     # # # ##(input('Check that they are all equal GHPT')
        #     ghpt_only['capacity'] = ghpt_only.apply(lambda row: row['capacity'] + row['capacity2'], axis=1)
        #     gdf_converted = pd.concat([gdf_converted, ghpt_only],sort=False).reset_index(drop=True)
        # # # printlen(gdf_converted))

        gdf_converted['cleaned_cap'] = pd.to_numeric(gdf_converted['capacity'], errors='coerce')

        total_counts_trackers = []
        avg_trackers = []
        print(gdf_converted.columns)
        # print(f"this is all trackers: {set(gdf_converted['tracker-acro'].to_list())}")

        # gdf_converted['tracker-acro'] = gdf_converted['tracker-acro']
        # # printf"this is all trackers: {set(gdf_converted['tracker-acro'].to_list())}")

        gdf_converted = gdf_converted[gdf_converted['tracker']!=''] # new to filter out nan


        for tracker in set(gdf_converted['tracker'].to_list()):
            # for singular map will only go through one
            total = len(gdf_converted[gdf_converted['tracker'] == tracker])
            sum = gdf_converted[gdf_converted['tracker'] == tracker]['cleaned_cap'].sum()
            avg = sum / total
            total_pair = (tracker, total)
            total_counts_trackers.append(total_pair)
            avg_pair = (tracker, avg)
            avg_trackers.append(avg_pair)

        for row in gdf_converted.index:
            cap_cleaned = gdf_converted.loc[row, 'cleaned_cap']
            tracker = gdf_converted.loc[row, 'tracker']
            if pd.isna(cap_cleaned):
                for pair in avg_trackers:
                    if pair[0] == tracker:
                        gdf_converted.loc[row, 'cleaned_cap'] = pair[1]
            cap_cleaned = gdf_converted.loc[row, 'cleaned_cap']
            # if pd.isna(cap_cleaned):
                # print'still na')
                # # ##(input('still na')


        pd.options.display.float_format = '{:.0f}'.format
        # gdf_converted['ea_scaling_capacity'] = gdf_converted.apply(lambda row: conversion_equal_area(row), axis=1) # square root(4 * capacity / pi)

        gdf_converted['scaling_capacity'] = gdf_converted.apply(lambda row: conversion_multiply(row), axis=1)
        # must be float for table to sort
        gdf_converted['capacity-table'] = gdf_converted.apply(lambda row: pd.Series(workaround_table_float_cap(row, 'capacity')), axis=1)
        gdf_converted['units-of-m'] = gdf_converted.apply(lambda row: pd.Series(workaround_table_units(row)), axis=1)
        # gdf_converted['units-of-m'] = gdf_converted.apply(lambda row: '' if 'GOGET' in row['tracker-acro'] else row['units-of-m'], axis=1)

        # below doesn't work cap details was empty all the time
        # gdf_converted = workaround_no_sum_cap_project(gdf_converted) # adds capacity-details for singular maps we can just disregard
        # TODO nov 13 test this I think it now adds all cap for a project and applies the original units to it
        # gdf_converted['capacity-details-unit'] = gdf_converted.apply(lambda row: workaround_display_cap(row, 'capacity-details'), axis=1)

        cleaned_dict_map_by_one_gdf_with_conversions[mapname] = gdf_converted


    # # printcleaned_dict_map_by_one_gdf_with_conversions.keys())
    # # # ##(input('check that there are enough maps')
    return cleaned_dict_map_by_one_gdf_with_conversions


    
    
    
     


def create_search_column(dict_of_gdfs):
    # this can be one string with or without spaces 
    # this creates a new column for project and project in local language
    # in the column it'll be removed of any diacritics 
    # this allows for quick searching
    #     for mapname, one_gdf in cleaned_dict_map_by_one_gdf.items():
    dict_of_gdfs_with_search = {}
    for mapname, one_gdf in dict_of_gdfs.items():

        # check that areas isn't empty
        tracker_sel = one_gdf['tracker-acro'].iloc[0]
        if tracker_sel == 'GOGET':
            print(one_gdf['areas'])
            input('check goget areas in create_search_column')

        # print('testing create_search_column with no diacritics for first time')
        col_names = ['plant-name', 'parent(s)', 'owner(s)', 'operator(s)', 'name', 'owner', 'parent']
        for col in col_names:
            if col in one_gdf.columns:
                # print(one_gdf[col].head(10))
                new_col_name = f'{col}_search'
                one_gdf[new_col_name] = one_gdf[col].apply(lambda x: remove_diacritics(x))
                # print(one_gdf[new_col_name].head(10))
        
        dict_of_gdfs_with_search[mapname] = one_gdf
        
        print(set(one_gdf['areas'].to_list()))
        # print(dict_of_gdfs_with_search.keys)
        # print('above are keys in dict_of_gdfs_with_search')
    return dict_of_gdfs_with_search

# def last_min_fixes_eu(one_gdf_by_maptype):
#     one_gdf_by_maptype_fixed = {}
#     # # printone_gdf_by_maptype.keys())
#     # # # ##(input('check that GIPT is in the above')
#     for mapname, gdf in one_gdf_by_maptype.items():            # do filter out oil
#         gdf = gdf.copy()
#         # handle situation where Guinea-Bissau IS official and ok not to be split into separate countries
#         gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau'))

#         # something is happening when we concat, we lose goget's name ...
#         # gdf_empty_name = gdf[gdf['name']=='']
#         # # # printf"This is cols for gdf: {gdf.columns}")
#         gdf['name'].fillna('',inplace=True)
#         gdf['name'] = gdf['name'].astype(str)
#         gdf['capacity'].fillna('',inplace=True)

#         gdf['wiki-from-name'] = gdf.apply(lambda row: f"https://www.gem.wiki/{row['name'].strip().replace(' ', '_')}", axis=1)
#         # row['url'] if row['url'] != '' else
#         # handles for empty url rows and also non wiki cases SHOULD QC FOR THIS BEFOREHAND!! TO QC
#         # need to switch to '' not nan so can use not in
#         gdf['url'].fillna('',inplace=True)
#         gdf['url'] = gdf.apply(lambda row: row['wiki-from-name'] if 'gem.wiki' not in row['url'] else row['url'], axis=1)


#         gdf.columns = [col.replace('_', '-') for col in gdf.columns]
#         gdf.columns = [col.replace('  ', ' ') for col in gdf.columns]
#         gdf.columns = [col.replace(' ', '-') for col in gdf.columns]


#         # if 'fuel-filter' not in gdf.columns:
#         #     input('issue here')
#         # gdf['tracker-acro'] = gdf['tracker-acro']
#         # let's also look into empty url, by tracker I can assign a filler

#         # gdf['url'] = gdf['url'].apply(lambda row: row[filler_url] if row['url'] == '' else row['url'])

#         # gdf['capacity'] = gdf['capacity'].apply(lambda x: x.replace('--', '')) # can't do that ...

#         # translate acronyms to full names

#         gdf['tracker-display'] = gdf['tracker-custom'].map(tracker_to_fullname)
#         gdf['tracker-legend'] = gdf['tracker-custom'].map(tracker_to_legendname)
#         # # # printset(gdf['tracker-display'].to_list()))
#         # # # printf'Figure out capacity dtype: {gdf.dtypes}')
#         gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('--', ''))
#         gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('*', ''))


#         # print all na rows to csv
#         # na_rows = gdf[gdf['geometry'].isna()]
#         # print(len(na_rows))
#         # na_rows.to_csv(f'/content/drive/MyDrive/output_from_colab/na-rows-{mapname}.csv')
#         # input('check length of na rows')
#         # for row in na_rows.index:
#         #     # find situations where lat and lng are both null
#         #     lat = gdf.loc[row, 'latitude']
#         #     lng = gdf.loc[row, 'longitude']
#         #     if pd.isna(lat) and pd.isna(lng):
#         #       print(row)

#         test = gdf[gdf['name']=='Montoir LNG Terminal']
#         print(test['geometry'])
#         print(len(gdf))
#         gdf.dropna(subset=['geometry'],inplace=True)
#         print(len(gdf))
#         # gdf_null_geo = gdf[gdf['geometry']== 'null']
#         gdf = gdf[gdf.geometry.notnull()]
#         # drop null geo
#         # gdf.drop(gdf_null_geo.index, inplace=True)
#         # print(len(gdf_null_geo))
#         print(len(gdf))
#         # input('check after dropped null')

#         # issues_coords.to_df.to_csv(f'/content/drive/MyDrive/output_from_colab/issue_coords.csv')
#         # put dict to df to csv
#         issues_coords_df = pd.DataFrame.from_dict(issues_coords, orient='index')
#         issues_coords_df.to_csv(f'{tracker_folder_path}/issues/issue_coords.csv')

#         year_cols = ['start-year', 'prod-year-gas']

#         for col in year_cols:
#             gdf[col] = gdf[col].apply(lambda x: str(x).split('.')[0])
#             gdf[col].replace('-1', 'not stated')

#         if mapname == 'europe':
#             # print(mapname)
#             gdf = pci_eu_map_read(gdf)
#             # gdf = assign_eu_hydrogen_legend(gdf)
#             # gdf = manual_lng_pci_eu_temp_fix(gdf)
#             # gdf = swap_gas_methane(gdf)
#             print(gdf['areas'])
#             input('check areas for europe goget')

#         one_gdf_by_maptype_fixed[mapname] = gdf

#     return one_gdf_by_maptype_fixed


def last_min_fixes(one_gdf_by_maptype):
    one_gdf_by_maptype_fixed = {}
    # # printone_gdf_by_maptype.keys())
    # # # ##(input('check that GIPT is in the above')
    for mapname, gdf in one_gdf_by_maptype.items():            # do filter out oil
        gdf = gdf.copy()
        # handle situation where Guinea-Bissau IS official and ok not to be split into separate countries 
        gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) 
        gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Timor,Leste','Timor-Leste')) 
        
        # something is happening when we concat, we lose goget's name ... 
        # gdf_empty_name = gdf[gdf['name']=='']
        # # # printf"This is cols for gdf: {gdf.columns}")
        gdf['name'].fillna('',inplace=True)
        gdf['name'] = gdf['name'].astype(str)

        gdf['wiki-from-name'] = gdf.apply(lambda row: f"https://www.gem.wiki/{row['name'].strip().replace(' ', '_')}", axis=1)
        # row['url'] if row['url'] != '' else 
        # handles for empty url rows and also non wiki cases SHOULD QC FOR THIS BEFOREHAND!! TO QC
        # need to switch to '' not nan so can use not in
        gdf['url'].fillna('',inplace=True)
        gdf['url'] = gdf.apply(lambda row: row['wiki-from-name'] if 'gem.wiki' not in row['url'] else row['url'], axis=1)

        gdf.columns = [col.replace('_', '-') for col in gdf.columns] 
        gdf.columns = [col.replace('  ', ' ') for col in gdf.columns] 
        gdf.columns = [col.replace(' ', '-') for col in gdf.columns] 

        gdf['tracker-display'] = gdf['tracker-custom'].map(tracker_to_fullname)
        gdf['tracker-legend'] = gdf['tracker-custom'].map(tracker_to_legendname)
        # # # printset(gdf['tracker-display'].to_list()))
        # # # printf'Figure out capacity dtype: {gdf.dtypes}')
        gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('--', ''))
        gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('*', ''))

        gdf.dropna(subset=['geometry'],inplace=True)
        # gdf['capacity'] = gdf['capacity'].fillna('')
        # gdf['capacity'] = gdf['capacity'].apply(lambda x: x.replace('', pd.NA))
        # gdf['capacity'] = gdf['capacity'].astype(float) # Stuck with concatting like strings for now? ValueError: could not convert string to float: ''
                # remove units-of-m if no capacity value ... goget in particular
        for row in gdf.index:
            if gdf.loc[row, 'capacity'] == '':
                gdf.loc[row, 'units-of-m'] = ''
            elif gdf.loc[row, 'capacity-details'] == '':
                gdf.loc[row, 'units-of-m'] = ''
            elif gdf.loc[row, 'capacity-table'] == np.nan:
                gdf.loc[row, 'units-of-m'] = ''

        year_cols = ['start-year', 'prod-year-gas', 'prod-year-oil']

        for col in year_cols:
            gdf[col] = gdf[col].apply(lambda x: str(x).split('.')[0])
            gdf[col].replace('-1', 'not stated')
        # TODO add check that year isn't a -1 ... goget.. for egt
        
        if mapname == 'europe':
            print(mapname)
            gdf = pci_eu_map_read(gdf)

        
        one_gdf_by_maptype_fixed[mapname] = gdf
    # # printone_gdf_by_maptype_fixed.keys())
    return one_gdf_by_maptype_fixed

def merge_all_gdfs_eu(final_list):

    # one_gdf = pd.concat(final_list, sort=False, verify_integrity=True, ignore_index=True)
    for df in final_list:
        # print(df.columns)
        print(df.index)
        df = df.reset_index()
        # print(len(df))
        # find any duplicate rows between all dfs in the final_list
        # df.drop_duplicates(inplace=True)
        # print(len(df))
        # input('check')
        # # print(df.index)
        if 'geometry' not in df.columns:
            df = convert_coords_to_point(df)

        # tracker = df['tracker'].iloc[0]
        # na_rows_df = df[df['geometry'].isna()]
        # print(len(na_rows_df))
        # na_rows_df.to_csv(f'/content/drive/MyDrive/output_from_colab/na-rows-{tracker}.csv')
        # input(f'check length of na rows for {tracker} before main merge')

    one_gdf = pd.concat(final_list, sort=False, ignore_index=True)

    # one_gdf.drop_duplicates(inplace=True)
    one_gdf.reset_index(drop=True, inplace=True)


    # print(one_gdf.columns)
    # na_rows_one_gdf = one_gdf[one_gdf['geometry'].isna()]
    # print(len(na_rows_one_gdf))
    # na_rows_one_gdf.to_csv(f'/content/drive/MyDrive/output_from_colab/na-rows-{na_rows_one_gdf}.csv')
    # input(f'check length of na rowsafter main merge')
    return one_gdf

def adjusting_geometry(df):
    # convert to gdf
    tracker = df['tracker'].iloc[0]
    # print(tracker)
    # input('check')
    df.columns = df.columns.str.lower()
    print(df.columns)

    if 'geometry' not in df.columns:
        if 'latitude' in df.columns and 'longitude' in df.columns:

            df = convert_coords_to_point(df)
            crs = 'EPSG: 4326'
            geometry_col = 'geometry'
            df = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)
        else:
            print(df.columns)
            input('no lat long or geo?')


    else:
      # if geometry is null or empty then use lat long to conver to a point

        df['geometry'] = df.apply(lambda x: Point(x['longitude'], x['latitude']) if x['geometry'] is None or x['geometry'] == '' or x['geometry'] == 'null' else x['geometry'], axis=1)
        crs = 'EPSG: 4326'
        geometry_col = 'geometry'
        df = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)
        print(len(df))
        df = df.dropna(subset='geometry')
        # print(len(df))
        # input('check change in length after dropping na')

    return df

def accomodate_egt_GOGPT_dd(df):
    # this will pull in the two tabs from EGT for goget updates after EGT 
    # it can also accomodate adjustments made to GOGPT europe for GOGPT release so we can update EGT as well
    return df


def convert_coords_to_point(df):
    crs = 'EPSG: 4326'
    geometry_col = 'geometry'
    df = df.reset_index(drop=True)
    df.columns = df.columns.str.lower()
    for row in df.index:
        df.loc[row,'geometry'] = Point(df.loc[row,'longitude'], df.loc[row,'latitude'])
    gdf = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)
    
    return gdf

def process_gmaps_linestring(gmap_format_str):
    """
    Convert from Google Maps format to WKT format
    """
    
    # split on colons to separate coordinate pairs from each other
    line_list = gmap_format_str.strip().split(':')
    # clean up
    line_list = [x.strip() for x in line_list]

    line_list_rev = [] # initialize
    for pair in line_list:
        # in Google Maps, order is lat, lon
        lat = pair.split(',')[0].strip()
        lon = pair.split(',')[1].strip()
        # put into WKT order & format
        line_list_rev += [f"{lon} {lat},"]

    wkt_line = ' '.join(line_list_rev).strip(',')

    return wkt_line

def convert_google_maps_to_wkt(
    pipes_df, 
):
    """
    GFIT has pipeline routes in Google Maps format (renamed in this notebook to 'Route (Google Maps)'
    For download file, want to use WKT format to be consistent with GGIT.
    Put WKT format into column 'WKTFormat'.

    In WKT:
    * Each coordinate pair is longitude then latitude, separated by spaces
    * Within linestrings: Coordinate pairs are separated by commas
    * Within multilinestrings: Linestrings are bookended by parentheses
    
    In Google Maps:
    * Each coordinate pair is latitude then longitude, separated by comma
    * Within linestrings: Coordinate pairs are separated by colons
    * Within multilinestrings: Linestrings are separated by semicolons
    """
    
    # rename column if not already in this format
    pipes_df = pipes_df.rename(columns={'Route': 'Route (Google Maps)'})
    
    for row in pipes_df.index:
        val = pipes_df.at[row, 'Route (Google Maps)']
        if pd.isna(val)==True:
            # can't convert
            pass
        
        else:
            gmap_format_str = val

            if ';' in gmap_format_str:
                # split on ';' -- the marker of the end of a linestring
                gmap_multiline_list = gmap_format_str.split(';')

                # clean up:
                gmap_multiline_list = [x.strip() for x in gmap_multiline_list]

                multiline_list_rev = [] # initialize

                for gmap_line in gmap_multiline_list:
                    wkt_line = process_gmaps_linestring(gmap_line)
                    # put parentheses around wkt lines
                    wkt_line = f"({wkt_line})"
                    multiline_list_rev += [wkt_line]

                wkt_str = ', '.join(multiline_list_rev)
                # add MULTILINESTRING wrapper
                wkt_str = f"MULTILINESTRING({wkt_str})"
                pipes_df.at[row, 'WKTFormat'] = wkt_str

            elif ';' not in gmap_format_str and ':' in gmap_format_str:
                wkt_str = process_gmaps_linestring(gmap_format_str)
                # add LINESTRING wrapper
                wkt_str = f"LINESTRING({wkt_str})"
                pipes_df.at[row, 'WKTFormat'] = wkt_str

            # elif gmap_format_str in no_route_entries:
            #     # Known values for no route
            #     pass

            else:
                print("Error!" + f" Couldn't convert to WKT format: {gmap_format_str}")
    
    return pipes_df

def convert_WKT_to_geo(df):
    crs = 'EPSG: 4326'
    geometry_col = 'WKTFormat'
    df = df.reset_index(drop=True)
    print(df['WKTFormat'])
    # input('inspect')
    
    # for row in df.index:
    #     df.loc[row,'geometry'] = LineString(df.loc[row,'Route'])
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
    tracker = df['tracker-acro'].loc[0]
    if tracker in tracker_mult_countries: # GGIT GOIT
        col_country_name = ['StartCountry', 'EndCountry']
        # col_reg_name = ['StartRegion', 'EndRegion'] # Ask Baird if this is reasonable
    # elif df['tracker-acro'].loc[0] == 'GOGET':
    #     col_country_name = 'Country' # not Country List because that is only relevant for some rows 
    elif tracker == 'GHPT':
        col_country_name = ['Country 1', 'Country 2']
        # col_reg_name = ['Region 1', 'Region 2']    
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
                # elif df tracker is pipeline or goget use countries col always!  tracker-acro
                else:
                    col_country_name = col
                    # print(f'this is country col: {col_country_name} to filter on  for {tracker}!')
                    # input('Check country col')
                    continue
    return col_reg_name, col_country_name    

# Define a function to check for valid values
# def is_valid_goget(x):

def create_df_goget(key, tabs):
    if 'Production & reserves' in tabs:
        for tab in tabs:
            print(tab)
            if tab == 'Main data':
                gsheets = gspread_creds.open_by_key(key)
                spreadsheet = gsheets.worksheet(tab)
                main_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                print(main_df.info())
            elif tab == 'Production & reserves':
                gsheets = gspread_creds.open_by_key(key)
                spreadsheet = gsheets.worksheet(tab)
                prod_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                print(prod_df.info())
        return main_df, prod_df    


#     return isinstance(x, (int, float)) and not pd.isna(x) and x != '' and x != 0 and x != 0.0
def handle_goget_gas_only_workaround(goget_orig_file):
    list_ids = []
    df = pd.read_excel(goget_orig_file, sheet_name='Main data')
    # df = df[df['Fuel type']!= 'oil'] # 7101
    df = df[df['Fuel type'].str.contains('Gas', case=False, na=False)]
    print(len(df))
    input(f'Check length after filtering out oil try lowercase g for Gas')
    # goget_gas_only_all_regions_march_2024 = []
    list_ids = df['Unit ID'].to_list()
    return list_ids

def save_goget_datafile_eu(goget):
    # make sure no average is in the data, but according to process_goget_reserve_prod_data the column Production for Map Scaling is never used or included so just an option
    print('saving GOGET tab for data download for europe')
    # terminals and pipelines get handled by Rob
    # GOGPT is unknown
    # GOGET I handle
    # filter filter_goget_for_europe 
    # drop some columns
    goget.drop(columns=['Fuel type', 'country_to_check'], inplace=True)
    # save as file
    file_name = f'{tracker_folder_path}/europe/eu_goget_tab_{iso_today_date}.xlsx'
    
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        goget.to_excel(writer, sheet_name=f'Oil & Gas Extraction', index=False)

    # input('check file')

    

def process_goget_reserve_prod_data(main, prod):
    # output is to return df with scott's code adjustments
    # first run process_goget_reserve_prod_data_dd to save for data download
    # split into two dfs
    main_data_df = main
    production_reserves_df = prod
    filtered_main_data_df = main_data_df
    # Convert 'Data year' to integers in the 'production_reserves_df'
    production_reserves_df['Data year'] = pd.to_numeric(production_reserves_df['Data year'], errors='coerce').fillna(-1).astype(int)

    # Update for Production - Oil and its year
    filtered_main_data_df[["Production - Oil", "Production Year - Oil"]] = filtered_main_data_df.apply(
        lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million bbl/y", production_reserves_df)),
        axis=1
    )
    # Update for Production - Gas and its year
    filtered_main_data_df[["Production - Gas", "Production Year - Gas"]] = filtered_main_data_df.apply(
        lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million m³/y", production_reserves_df)),
        axis=1
    )

    # Update for Production - Hydrocarbons (unspecified) and its year
    filtered_main_data_df[["Production - Hydrocarbons (unspecified)", "Production Year - Hydrocarbons (unspecified)"]] = filtered_main_data_df.apply(
        lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million boe/y", production_reserves_df)),
        axis=1
    )

    # Calculate total reserves and production
    #filtered_main_data_df['Reserves- Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_reserves, axis=1)
    filtered_main_data_df['Production - Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_production_goget, axis=1)


    # Convert Discovery Year to String
    filtered_main_data_df['Discovery year'] = filtered_main_data_df['Discovery year'].astype(object)

    # Ensure there are no NaN values in the year columns before conversion to avoid errors
    filtered_main_data_df['Production Year - Oil'].fillna('', inplace=True)
    filtered_main_data_df['Production Year - Gas'].fillna('', inplace=True)
    filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'].fillna('', inplace=True)

    filtered_main_data_df['Production Year - Oil'] = filtered_main_data_df['Production Year - Oil'].astype(str)
    filtered_main_data_df['Production Year - Gas'] = filtered_main_data_df['Production Year - Gas'].astype(str)
    filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'] = filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'].astype(str)

    # remove .0 -1.0
    for col in ['Production Year - Oil', 'Production Year - Gas','Production Year - Hydrocarbons (unspecified)']:
        filtered_main_data_df[col] = filtered_main_data_df[col].apply(lambda x: x.replace('.0',''))
        filtered_main_data_df[col] = filtered_main_data_df[col].apply(lambda x: x.replace('-1','not stated'))

    # Convert to integer first to remove the trailing zero, then to string
    # filtered_main_data_df['Production Year - Oil'] = filtered_main_data_df['Production Year - Oil'].astype(int).astype(str)
    # filtered_main_data_df['Production Year - Gas'] = filtered_main_data_df['Production Year - Gas'].astype(int).astype(str)
    # filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'] = filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'].astype(int).astype(str)

    # Ensure there are no nan in status, this is before renaming so still uppercase
    filtered_main_data_df['Status'].fillna('', inplace=True)
    
    # Replace "0" with np.nan or a placeholder if you had NaN values initially
    # filtered_main_data_df.replace('0', np.nan, inplace=True)

    # Check the conversion by printing the dtypes again
    # column_data_types = filtered_main_data_df.dtypes
    # print(column_data_types)
    
    # Apply the function to create a new column 'Country List'
    filtered_main_data_df['Country List'] = filtered_main_data_df['Country/Area'].apply(get_country_list)
    # print(filtered_main_data_df[['Country List','Country/Area']]) 
    # print(set(filtered_main_data_df['Country List'].to_list()))
    # print(set(filtered_main_data_df['Country/Area'].to_list()))
    # input('Check country list and country/area after apply')   
    
    dropped_filtered_main_data = filtered_main_data_df.drop(['Government unit ID',  'Basin', 'Concession / block'], axis=1)
    # average_production_total = filtered_main_data_df["Production - Total (Oil, Gas and Hydrocarbons)"].mean()
    # print("Average Production - Total (Oil, Gas and Hydrocarbons):", average_production_total)
    # input('check avg production total seems right, previous was 6.3041')

    # # Create new column for scaling where there is a fill in value based on average when data is not there.
    # dropped_filtered_main_data["Production for Map Scaling"] = np.where(dropped_filtered_main_data["Production - Total (Oil, Gas and Hydrocarbons)"] != 0,
    #                                                             dropped_filtered_main_data["Production - Total (Oil, Gas and Hydrocarbons)"],
    #                                                             average_production_total)

    dropped_production_Wiki_name = create_goget_wiki_name(dropped_filtered_main_data)
    regions_df = pull_in_official_gem_region_mapping(region_key, region_tab)
    # print(set(dropped_production_Wiki_name['Country List'].to_list()))
    # print(set(dropped_production_Wiki_name['Country/Area'].to_list()))
    # input('Check country list and country/area before merge') 
    
    # print(regions_df['GEM Standard Country Name'])
    # input('inspect list of GEM standard names')


    dropped_production_Wiki_name = pd.merge(
        dropped_production_Wiki_name,
        regions_df[['GEM Standard Country Name', 'GEM region']],
        left_on='Country/Area',
        right_on='GEM Standard Country Name',
        how='left'
    )

    
    # After the merge, you might have an extra column 'GEM Standard Country Name' which is a duplicate of 'Country'.
    # You can drop this extra column if it's not needed.
    dropped_production_Wiki_name.drop('GEM Standard Country Name', axis=1, inplace=True)
    # print(dropped_production_Wiki_name.head())
    # input('check that it matches Scotts after dropped_production_Wiki_name')
    # print(dropped_production_Wiki_name.dtypes)
    # input('check thosul be objects for all but prod oil prod gas prod hydrocarbons prod total prod for map scaling, lat and lng')
    # drop superfluous columns
    clean_export = dropped_production_Wiki_name.drop(['Unit type'], axis=1) # Fuel type
    
    # Use not centroid but descriptive point
    # Set up DF of Units without locations
    clean_export[['Longitude', 'Latitude']] = clean_export[['Longitude', 'Latitude']].fillna('')
    missing_location_df = clean_export[clean_export['Latitude']=='']
    # Get unique entries from the 'Country/Area' column
    unique_countries_with_missing_locations = missing_location_df['Country/Area'].unique()

    # Display the unique countries
    unique_countries_df = pd.DataFrame(unique_countries_with_missing_locations, columns=['Country/Area'])
    # print(unique_countries_df)
    # input('check unique countries that need descriptive points')
    # normally would use descriptive point
    
    centroid_df = gspread_access_file_read_only(centroid_key, centroid_tab) # TODO update this with descriptive point on subregion
    # print(centroid_df.head())
    # input('check centroid df')
    centroid_df.rename(columns={'Latitude':'Latitude-centroid', 'Longitude':'Longitude-centroid'},inplace=True)
    
    clean_export_center = pd.merge(clean_export, centroid_df, how='left', on='Country/Area')

    # Update 'Location accuracy' for filled-in values
    print(clean_export_center.columns)
    clean_export_center['Location accuracy'] = clean_export_center.apply(lambda row: 'country level only' if pd.isna(row['Latitude']) or pd.isna(row['Longitude']) else row['Location accuracy'], axis=1)

    # mask to check if merge fills in missing coordinates
    empty_coord_mask = clean_export_center[clean_export_center['Latitude']=='']
    print(f'How many missing coords before?: {len(empty_coord_mask)}')
    
    # Fill in missing latitudes and longitudes if lat lng is '' blank string
    clean_export_center[['Latitude', 'Longitude']] = clean_export_center[['Latitude', 'Longitude']].fillna('')
     
    clean_export_center['Latitude'] = clean_export_center.apply(lambda row: row['Latitude-centroid'] if (row['Latitude'] == '') else row['Latitude'], axis=1)
    clean_export_center['Longitude'] = clean_export_center.apply(lambda row: row['Longitude-centroid'] if (row['Longitude'] == '') else row['Longitude'], axis=1)

    #drop centroid fill in columns
    clean_export_center_clean = clean_export_center.drop(['Latitude-centroid', 'Longitude-centroid'], axis=1)
    
    # mask to check if merge fills in missing coordinates
    empty_coord_mask = clean_export_center_clean[clean_export_center_clean['Latitude']=='']
    # print(f'How many missing coords after?: {len(empty_coord_mask)}')
    # input('Check before and after for empty coord logic!')
    
    # Define a dictionary with old column names as keys and new names with units as values
    column_rename_map = {
        'Production - Oil': 'Production - Oil (Million bbl/y)',
        'Production - Gas': 'Production - Gas (Million m³/y)',
        'Production - Total (Oil, Gas and Hydrocarbons)': 'Production - Total (Oil, Gas and Hydrocarbons) (Million boe/y)',
        # Add other columns you wish to rename similarly here
    }
    
    # Set output order, dropping more columns
    desired_column_order = [
        'Unit ID',
        'Fuel type',
        'Wiki name',
        'Status',
        'Country/Area',
        'Country List',
        'Subnational unit (province, state)',
        'GEM region',
        'Latitude',
        'Longitude',
        'Location accuracy',
        'Discovery year',
        'FID Year',
        'Production start year',
        'Operator',
        'Owner',
        'Parent',
        'Project or complex',
        'Production - Oil (Million bbl/y)',
        'Production Year - Oil',
        'Production - Gas (Million m³/y)',
        'Production Year - Gas',
        'Production - Total (Oil, Gas and Hydrocarbons) (Million boe/y)',
        'Wiki URL',
    ]
 

    # Rename the columns
    clean_export_center_clean_rename = clean_export_center_clean.rename(columns=column_rename_map)
    
    # Reorder the columns
    clean_export_center_clean_reorder_rename = clean_export_center_clean_rename[desired_column_order]

    
    return clean_export_center_clean_reorder_rename

def create_goget_wiki_name(df):
    # df['Wiki name'] = df['Unit Name'] + ' Oil and Gas Field ('+ df['Country'] + ')'
    
    df['Wiki name'] = df.apply(lambda row: f"{row['Unit Name']} Oil and Gas Field ({row['Country/Area']})", axis=1)
    # 'Wiki name'
    # print(df[['Country/Area', 'Unit Name', 'Wiki name']].head())
    # input('Check that Wiki name came out alright')
    return df 

def pull_in_official_gem_region_mapping(key, tab):
    # 1yaKdLauJ2n1FLSeqPsYNxZiuF5jBngIrQOIi9fXysAw
    # mapping 
    df = gspread_access_file_read_only(key, tab)
    return df

# # test
# df = pull_in_official_gem_region_mapping(region_key, region_tab)
# From scott's script
#Define functions for getting the most recent value, calculate the total reserves, calculate the total production and define the conversion factor
# Function to get the most recent value based on the criteria
def get_most_recent_value_and_year_goget(unit_id, prod_res, units, df):
    # Filter based on Unit ID, Production/reserves, and Units (converted)
    filtered = df[
        (df["Unit ID"] == unit_id) &
        (df["Production/reserves"] == prod_res) &
        (df["Units (converted)"] == units)
    ]

    # Sort by Data year and get the most recent entry
    filtered = filtered.sort_values(by="Data year", ascending=False)
    if not filtered.empty:
        most_recent = filtered.iloc[0]
        return most_recent["Quantity (converted)"], most_recent["Data year"]
    else:
        return np.nan, np.nan

# Function to calculate the total production = from Scott's script https://colab.research.google.com/drive/1HbBp2H7TWkrhWzUkOjnGrFyEss5Hka7k#scrollTo=SWmVCIzhnvap 
def calculate_total_production_goget(row):
    # Conversion factor from million m³ to million boe for gas
    conversion_factor = 5.883 / 1000 
    if pd.notna(row['Production - Hydrocarbons (unspecified)']):
        return row['Production - Hydrocarbons (unspecified)']
    else:
        # Convert gas production to boe
        gas_in_boe = row['Production - Gas'] * conversion_factor if pd.notna(row['Production - Gas']) else 0
        oil_production = row['Production - Oil'] if pd.notna(row['Production - Oil']) else 0
        return gas_in_boe + oil_production

# GEM Standard Country Name and Area List mappings
gem_country_area_mapping = {
    'Azerbaijan-Turkmenistan': 'Azerbaijan; Turkmenistan',
    'Iran-Iraq': 'Iran; Iraq',
    'Kuwait-Saudi Arabia': 'Kuwait; Saudi Arabia',
    'Kuwait-Saudi Arabia-Iran': 'Kuwait; Saudi Arabia; Iran',
    'Angola-Republic of the Congo': 'Angola; Republic of the Congo',
    'Saudi Arabia-Bahrain': 'Saudi Arabia; Bahrain',
    'Saudi Arabia-Iran': 'Saudi Arabia; Iran',
    'Senegal-Mauritania': 'Senegal; Mauritania',
    'South China Sea': 'China; Taiwan; Philippines',
    'Thailand-Malaysia': 'Thailand; Malaysia',
    'Timor Gap': 'East Timor; Australia; Indonesia',
    'United Arab Emirates-Iran': 'United Arab Emirates; Iran',
    'Venezuela-Trinidad and Tobago': 'Venezuela; Trinidad and Tobago',
}

# Function to find Area List based on GEM Standard Country Name
def get_country_list(gem_name):
    return gem_country_area_mapping.get(gem_name, '')

# end of Scott's script 

def find_most_granular_loc(df):
    '''This will find the most granular location for each row so we can find the best coordinates 
    for the project. For now we will just use the country as the most granular polygon. In the future
    we will make it more robust.'''
    
    # gadm file of all country and province polygon geometries
    # convert all gem data to align with country and province spelling
    
    return df

def apply_representative_point(df):
    '''This will apply representative point function to all rows that have missing coordinates'''
    polygon_name_loc = find_most_granular_loc(df)
    
    
    return df

def pci_eu_map_read(gdf):
    # take columns PCI5 and pci6 
    # create one column, both, 5, 6, none, all as strings

    gdf['pci-list'] = ''
    for row in gdf.index:
        pci5 = gdf.loc[row, 'pci5']
        pci6 = gdf.loc[row, 'pci6']
        if pci5 == 'yes' and pci6 == 'yes':
            gdf.at[row, 'pci-list'] = 'both'
        elif pci5 == 'yes':
            gdf.at[row, 'pci-list'] = '5'
        elif pci6 == 'yes':
            gdf.at[row, 'pci-list'] = '6'
        else:
            gdf.at[row, 'pci-list'] = 'none'
        
    return gdf


def assign_eu_hydrogen_legend(gdf):
    # take column fuel and tracker-custom
    # if column == hydrogen and tracker-custom == ggit-eu
    # change tracker-custom to ggit-euhy
    for row in gdf.index:
        fuel = gdf.loc[row, 'fuel']
        tracker_cust = gdf.loc[row, 'tracker-custom']
        if fuel == 'Hydrogen' and tracker_cust == 'GGIT-eu':
            gdf.at[row, 'tracker-custom'] = 'GGIT-euhy'
        elif fuel == 'Hydrogen':
            print('Odd fuel type for infrastructure type')
            print(row)
            input('check the above')

    return gdf

def format_values(df):
    """this will lowercase status values, 
    and replace dashes and stars with blanks, 
    and create display capacity field as string to hide nan"""
    
    df['status'] = df['status'].apply(lambda x: x.lower())
    df['status'] = df['status'].replace(' ', '_')
    
    # df[['start-year', 'retired-year', 'owner', 'parent-port-name']] = df[['start-year', 'retired-year',  'owner', 'parent-port-name']].replace('-', '', regex=True)
        
    # df['capacity-mt-display'] = df['capacity-(mt)'].fillna('').replace('*', '')

    return df

# from GOGPT make, check that its not gogpt specific

def replace_old_date_about_page_reg(df):
    """ Finds a month and replaces it along with the next five characters (a space and year) with the current release date"""

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    # Convert the entire dataframe to string
    df = df.astype(str)
    
    # find month in about_df string
    # multi_tracker_data is df of main about page for regional dd
    # print(f'INFO: {df.info()}')
    # print(f'COLS: {df.columns}')
    # input('Check out what this about page df is')
    # bold the first row
    # find replace the month and year
    # convert df column to string
    for row in df.index:
        for month in months:
            sub = str(month + ' 20')
            year_chars = len(month) + 5
            if sub in df.iloc[row,0]:
                print(f'Row is: {df.iloc[row,0]}')
                # replace the substring in the value (row string)
                index = df.iloc[row,0].find(sub)
                print(index)
                print(df.iloc[row,0][index-1])
                check = df.iloc[row,0][index-1]
                # input('Check if it has ( before')
                if check == '(':
                    pass
                else:
                    end = index + year_chars
                    input(f'Found a month! at index: {index}')
                    startbit = df.iloc[row,0][:(index)]
                    endbit = df.iloc[row,0][end:]
                    df.iloc[row,0] = startbit + new_release_date + endbit
                    # df.iloc[row,0] = df.iloc[row,0].replace(sub, new_release_date)
                    print(df.iloc[row,0])
                    input('Check find replace did the right thing')
                        
    return df

def harmonize_countries(df, countries_dict):
    df = df.copy()

    region_col = set(df['region'].to_list())
    results = []
    for region in region_col:
        df_mask = df[df['region']==region]
        df_mask['country-harmonize-pass'] = df_mask['country/area'].apply(lambda x: 'true' if x in countries_dict[region] else f"false because {x}")
        results_len = df_mask[df_mask['country-harmonize-pass'] == 'false']
        results.append((region, len(results_len)))
        print(f'\nWe want this to be 0: {results}\n')
        
    # df['areas-subnat-sat-display'] = df.apply(lambda row: f"{row['country']}" if row['state/province'] == '' else f"{row['state/province']}, {row['country']}", axis=1)   
    return df

def remove_implied_owner(df):
    # filter df where owner or parent contains no semicolon
    # filter furhter where owner parent contains 0 or 100 %
    df = df.copy()
    # mask2 = df['owner'].str.contains('[0%]')
    mask2 = ~df['owner(s)'].str.contains(';')
    mask3 = df['owner(s)'].str.contains('[100%]')
    mask4 = ~df['owner(s)'].str.contains(',')
    mask5 = df['owner(s)'].str.contains('[100.0%]')


    maskimplied = mask2 & mask3 & mask4 & mask5
    df.loc[maskimplied, 'owner(s)'] = df.loc[maskimplied, 'owner(s)'].str.replace('[100%]', '', regex=False).replace('[100.0%]', '', regex=False)
    
    print(df['owner(s)'])
    # input('check mask 100% owner')
    print(df['parent(s)'])
    input('check mask 100% parent')
    
    # loop through each row of df
    # if the parent or owner value contains no semicolon so is a single value
    # then remove the implied owner of 0 or 100 otherwise keep it
    return df

def formatting_checks(df): # gogpt
    df = df.copy()    
    # make sure date is not a float
    df['start-year'] = df['start-year'].replace('not found', np.nan)
    # df['start_year'] = df['start_year'].replace('', np.nan)
    # mask2 = np.isfinite(df['start_year'])
    mask_notna = df['start-year'].notna()
    mask_notstring = ~df['start-year'].apply(lambda x: isinstance(x, str))
    df.loc[mask_notna & mask_notstring, 'start-year'] = df.loc[mask_notna & mask_notstring, 'start-year'].astype(int)
    # round the capacity float
    # replace nans with ''
    # check country and region harmonization
    # harmonize_countries(df, full_country_list)
    df['capacity-mw-display'] = df['capacity-(mw)'].fillna('').replace('*', '')

    return df


# Function to check if any item in the row's list is in needed_geo
def check_list(row_list, needed_geo):
    return any(item in needed_geo for item in row_list)

def create_filtered_df_list_by_map(trackerdf, col_country_name, col_reg_name, maptype, needed_geo):
    # this function takesa df and filters on appropriate geo for the regional map
    
    # double check clean country and region columns and list of countries
    filtered_df = trackerdf.copy()
    tracker = filtered_df['tracker-acro'].loc[0]
    # print(tracker)
    # print(maptype)
    # print(len(filtered_df))
    # print(needed_geo)
    # print(maptype)
    
    # input('check maptype')
    if maptype in ['GIPT', 'Global']:
        # print('For GIPT we do not filter by geo')
        pass
    else: #maptype == 'latam': # ['latam', 'asia']   
        # if tracker in tracker_mult_countries: # currently no lists like with regions since goit and ggit created countries a list from start and end countries
            # if any of the countries in the country column list is in the needed geo list then keep it if none then filter out
        # this is to go in and filter by country
        # mult and hydro have two columns in country col as a list
        # all others just one column name
        # add the items from the two or just check the two no ad GHPT
        # def split_countries(country_str):

        #     for sep in [';', '-', ',']:
        #         if sep in country_str:
        #             return country_str.strip().split(sep)
        #         return [country_str]
            
        if tracker == 'GHPT' or tracker in tracker_mult_countries:
            # list of cols to go through
            filtered_df['country_to_check'] = [[] for _ in range(len(filtered_df))]
            # for row in filtered_df.index:
            #     # for col in col_country_name:
            #     print(col_country_name[0])
            #     # add value to list in column country to check
            #     filtered_df['country_to_check'] += filtered_df.loc[row, col_country_name[0]]
            #     print(col_country_name[1]) 
            #     filtered_df['country_to_check'] += filtered_df.loc[row, col_country_name[1]]
            for row in filtered_df.index:                    
                for col in col_country_name:
                    # add value to list in column country_to_check
                    filtered_df.at[row, 'country_to_check'] += [filtered_df.at[row, col]]
            # print(filtered_df['country_to_check'])
            # input('check this')
            filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]

            
        else:
        # if isinstance(col_country_name, list): # hydro more than one
        #         # print(col_country_na
        #         # me)
        #         filtered_df['country_to_check'] = [[] for _ in range(len(filtered_df))] # makes it a list                # this pulls each country out from start and end country into one list, could also apply this to hydro?
        #         for col in col_country_name:
        #             # TEST THIS
        #             # filtered_df['country_to_check'] = filtered_df[col].str.strip()
        #             filtered_df['country_to_check'] = filtered_df.apply(lambda row: row['country_to_check'] + row[col].strip(), axis=1)

            filtered_df['country_to_check'] = filtered_df.apply(lambda row: split_countries(row[col_country_name]), axis=1)
            # print(filtered_df['country_to_check'])
            # input('check this')
            filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]


        # for sep in ',;-':
        #     # I want to break up any multiple countries into a list of countries
        #     # then check if any of those are in the needed_geo list
        #     filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip().str.split(sep) 

        # filter the df on the country column to see if any of the countries in that list is in the needed geo
        
        # filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
        # # print(tracker)
        # # print(maptype)
        # print(f'len after filter: {len(filtered_df)}')
        # # input(f'Check length for tracker ggit goit after filter')
        # filtered_df = filtered_df.drop(columns=['country_to_check'])

        # else:
        #     # # TODO now that we are only filtering on country for latam we can probalby remove this if else
        #     if isinstance(col_country_name, list): # hydro more than one
        #         # print(col_country_name)
        #         filtered_df['country_to_check'] = [[] for _ in range(len(filtered_df))]

        #         for col in col_country_name:
        #             # TEST THIS
        #             # filtered_df['country_to_check'] = filtered_df[col].str.strip()
        #             filtered_df['country_to_check'] = filtered_df.apply(lambda row: row['country_to_check'] + [row[col].strip()], axis=1)

        #         filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
        #         filtered_df = filtered_df.drop(columns=['country_to_check'])

        #     else:
        #         filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip()

        #         # need this by country because not a GEM region, problematic since goget uses region and numbers when filtered by country in the gem region do not match 636 versus 578 for africa
        #         filtered_df = filtered_df[filtered_df['country_to_check'].isin(needed_geo)]
            
        #         filtered_df = filtered_df.drop(columns=['country_to_check'])
    
    
    # non geo filter      
    if maptype in gas_only_maps:
        # filter out oil facilities
        print(f'len before gas only filter {tracker} {len(filtered_df)} for map {maptype}')                

        if tracker == 'GOGET':
            # input('in goget in create_filterd_df_list_by_map')
            # using this just to filter from columns not in map file but in official release
            # goget_orig_file = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/Global Oil and Gas Extraction Tracker - 2024-03-08_1205 DATA TEAM COPY.xlsx'

            # # filter out oil
            # list_ids = handle_goget_gas_only_workaround(goget_orig_file)
            # print(len(ndf)) # 3095 will be less because not all trackers
            # filter = (df['tracker-acro']=='GOGET') & (df['prod-gas']=='') #2788
            # filter = df['id'] in list_ids #2788
            # df = df[(df['tracker-acro']=='GOGET') & (df['id'] in list_ids)]
            drop_row = []
            # print(filtered_df.columns)
            # input('Check that Fuel type is in there or fuel')
            for row in filtered_df.index:
                # if df.loc[row, 'tracker-acro'] == 'GOGET':
                # if filtered_df.loc[row, 'Unit ID'] not in list_ids:
                #     drop_row.append(row)
                
                if filtered_df.loc[row, 'Fuel type'] == 'oil':
                    drop_row.append(row)
            # drop all rows from df that are goget and not in the gas list ids 
            print(f'Length of goget before oil drop: {len(filtered_df)}')
            filtered_df.drop(drop_row, inplace=True)        
            print(f'Length of goget after oil drop: {len(filtered_df)}')
            input('Check the above to see if gas only for goget!')
            # print(len(ndf)) # 3012 after removing goget 
        elif tracker in ['GGIT-eu', 'GGIT']:
            # filter for hydrogen only, but also gas for pci europe uses this instead of other release
            drop_row = []
            for row in filtered_df.index:
                # if df.loc[row, 'tracker-acro'] == 'GOGPT': # 1751 from 1966 after filter
                if filtered_df.loc[row, 'Fuel'] == 'Oil':
                    drop_row.append(row)
                elif filtered_df.loc[row, 'Fuel'] == '':
                    drop_row.append(row)

            filtered_df.drop(drop_row, inplace=True)  

             
        elif tracker == 'GOGPT':
            # filter2 = (df['tracker-acro']=='GOGPT') & (df['fuel'].contains('liquid')) #2788
            drop_row = []
            for row in filtered_df.index:
                # if df.loc[row, 'tracker-acro'] == 'GOGPT': # 1751 from 1966 after filter
                fuel_cat_list = filtered_df.loc[row, 'Fuel'].split(',')
                new_fuel_cat_list = []
                for fuel in fuel_cat_list:
                    fuel = fuel.split(':')[0]
                    new_fuel_cat_list.append(fuel)
                
                # for Alcudia does not contain gas, or only contains fossil liquids
                
                # fossil liquids: diesel, fossil gas: natural ga...      37.5  operating   
                if len(new_fuel_cat_list) > 1:
                    if new_fuel_cat_list.count('fossil liquids') == len(new_fuel_cat_list):
                            drop_row.append(row)
  
                elif new_fuel_cat_list == ['fossil liquids']:
                    drop_row.append(row)
                        
            # drop all rows from df that are goget and not in the gas list ids 
            filtered_df.drop(drop_row, inplace=True)  
            # print(len(ndf)) # should be 2797
            print(f'len after gas only filter {tracker} {len(filtered_df)}') 
            # input('Check')               
           
        
    #     if maptype == 'asia': 
    #         print(f'len after gas only filter {tracker} {len(filtered_df)}')                
    #         # input('check that gas pipes get in here')
    #         # use the actual list of countries from the sheets so no western asia
    #         needed_geo = asia_countries
    #         if tracker in tracker_mult_countries: # currently no lists like with regions since goit and ggit created countries a list from start and end countries
    #             # if any of the countries in the country column list is in the needed geo list then keep it if none then filter out
    #             for sep in ',;-':
    #                 # I want to break up any multiple countries into a list of countries
    #                 # then check if any of those are in the needed_geo list
    #                 filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip().str.split(sep) 

    #             # filter the df on the country column to see if any of the countries in that list is in the needed geo
    #             filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
    #             # print(tracker)
    #             # print(maptype)
    #             # print(filtered_df)
    #             # input(f'Check length for tracker ggit goit after filter')
    #             filtered_df = filtered_df.drop(columns=['country_to_check'])

    #         else:
    #             # # TODO now that we are only filtering on country for latam we can probalby remove this if else
    #             if isinstance(col_country_name, list): # hydro more than one
    #                 # print(col_country_name)
    #                 filtered_df['country_to_check'] = [[] for _ in range(len(filtered_df))]

    #                 for col in col_country_name:
    #                     # TEST THIS
    #                     # filtered_df['country_to_check'] = filtered_df[col].str.strip()
    #                     filtered_df['country_to_check'] = filtered_df.apply(lambda row: row['country_to_check'] + [row[col].strip()], axis=1)

    #                 filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
    #                 filtered_df = filtered_df.drop(columns=['country_to_check'])

    #             else:
    #                 filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip()

    #                 # need this by country because not a GEM region, problematic since goget uses region and numbers when filtered by country in the gem region do not match 636 versus 578 for africa
    #                 filtered_df = filtered_df[filtered_df['country_to_check'].isin(needed_geo)]
                
    #                 filtered_df = filtered_df.drop(columns=['country_to_check'])
    #         print(f'len after asia w asia filter {tracker} {len(filtered_df)}')  
    #         # input('check len after')              

    #     elif maptype == 'europe': 
    #         print(f'len after gas only filter {tracker} {len(filtered_df)}') 
    #         # input('check that gas pipes get in here')
    #         # use the actual list of countries from the sheets so no western asia
    #         needed_geo = europe_countries
    #         if tracker in tracker_mult_countries: # currently no lists like with regions since goit and ggit created countries a list from start and end countries
    #             # if any of the countries in the country column list is in the needed geo list then keep it if none then filter out
    #             for sep in ',;-':
    #                 # I want to break up any multiple countries into a list of countries
    #                 # then check if any of those are in the needed_geo list
    #                 filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip().str.split(sep) 

    #             # filter the df on the country column to see if any of the countries in that list is in the needed geo
    #             filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
    #             # print(tracker)
    #             # print(maptype)
    #             # print(filtered_df)
    #             # input(f'Check length for tracker ggit goit after filter')
    #             filtered_df = filtered_df.drop(columns=['country_to_check'])

    #         else:
    #             # # TODO now that we are only filtering on country for latam we can probalby remove this if else
    #             if isinstance(col_country_name, list): # hydro more than one
    #                 # print(col_country_name)
    #                 filtered_df['country_to_check'] = [[] for _ in range(len(filtered_df))]

    #                 for col in col_country_name:
    #                     # TEST THIS
    #                     # filtered_df['country_to_check'] = filtered_df[col].str.strip()
    #                     filtered_df['country_to_check'] = filtered_df.apply(lambda row: row['country_to_check'] + [row[col].strip()], axis=1)

    #                 filtered_df = filtered_df[filtered_df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
    #                 filtered_df = filtered_df.drop(columns=['country_to_check'])

    #             else:
    #                 filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip()

    #                 # need this by country because not a GEM region, problematic since goget uses region and numbers when filtered by country in the gem region do not match 636 versus 578 for africa
    #                 filtered_df = filtered_df[filtered_df['country_to_check'].isin(needed_geo)]
                
    #                 filtered_df = filtered_df.drop(columns=['country_to_check'])
    #         print(f'len after europe gem filter {tracker} {len(filtered_df)}')  
    #         # input('check len after')           
    
    # else:
    #     print('Filtering by region!')
    #     # input('Check that')
    #     if isinstance(col_reg_name, list):
    #         maptype_list = maptype.title().split(' ')
    #         print(maptype_list)
    #         print(type(maptype_list))
    #         print(col_reg_name)
    #         # initialize a list in that column! 
    #         filtered_df['region_to_check'] = [[] for _ in range(len(filtered_df))]

    #         for col in col_reg_name:
    #             # we want to add the row's region in that col to a new column's list of all regions 
    #             filtered_df['region_to_check'] = filtered_df.apply(lambda row: row['region_to_check'] + [row[col].strip()], axis=1)
    #             # print(filtered_df['region_to_check'])
    #         # TEST THIS so africa becomes ['africa']
    #         # print(filtered_df['region_to_check'])
    #         filtered_df = filtered_df[filtered_df['region_to_check'].apply(lambda x: check_list(x, maptype_list))]
    #         filtered_df = filtered_df.drop(columns=['region_to_check'])
    #     else:

    #         filtered_df[col_reg_name] = filtered_df[col_reg_name].str.strip()

    #         filtered_df = filtered_df[filtered_df[col_reg_name] == maptype.title()]
    # # print(len(filtered_df))
    # input('check')
    return filtered_df

# def conversion_equal_area(row):
#     cap = float(row['cleaned_cap'])
#     factor = float(row['conversion_factor'])
#     # print(f'this is factor! {factor}')
#     converted = float(cap * factor)
#     # result = math.sqrt((4 * converted) / np.pi) # CURRENT
#     result = (((4*converted)/np.pi))**(1/2)
#     return result
#     # result = math.sqrt(4 * (float(cap * factor)) / np.pi) # PREVIOUS

    
#     return result 

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
    # gdf['unit-name-status'] = ''
    # gdf['capacity'].fillna('')
    gdf['unit_name'].fillna('--')
    gdf['unit_name'].replace('','--')
    gdf['unit_name'].replace('nan','--')
    gdf['unit_name'].replace('nan ','--')
    for row in gdf.index:
        # try:
            # groupby on that specifci row's name
        tracker = gdf.loc[row, 'tracker-acro']
        name = gdf.loc[row, 'name']
        # pid = gdf.loc[row, 'pid'] add project id to all
        capacity = gdf.loc[row, 'capacity']

        # Convert blank string capacities to NaN
        gdf['capacity'] = gdf['capacity'].replace('', np.nan).replace('--', np.nan).replace('-', np.nan).astype(float)
        
        # Group by project name and sum the capacities
        capacity_details = gdf[gdf['name'] == name].groupby('name', as_index=False)['capacity'].sum()
        
        # If the sum is NaN, replace it with an empty string
        # capacity_details['capacity'] = capacity_details['capacity'].fillna('')
        # TODO WORK IN PROGRESS to help fix the summary cap bug affecting solar and all ... 
        all_unit_names_statuses = gdf[gdf['name'] == name].apply(lambda x: f"{x['unit_name']} ({x['status']})", axis=1).to_list()
        all_unit_names_statuses_str = ', '.join(all_unit_names_statuses)
        
        # print(all_unit_names_statuses_str)
        # input('check this uni status thing')
        # if capacity != capacity_details:
        #     print(f'This is a multi-unit project: {name} in {tracker}')
        #     # input('check the above for good test!')
        # else:
        #     print(f'This is not a multi-unit proejct: {name} in {tracker}')
            
        # except:
        #     print(f'capacity details is blank for {name} in {tracker}')
        #     input('check because cap detail is empty')
        #     capacity_details = ''
        # capacity_details = ''

        gdf.loc[row, 'capacity-details'] = capacity_details
        # gdf.loc[row, 'unit-name-status'] = all_unit_names_statuses  # ValueError: Must have equal len keys and value when setting with an iterable
    # project_cap_df = gdf.groupby('name', as_index=False)['capacity'].sum()
    # print(f'this is cols of project_cap_df: {project_cap_df.columns}')
    # project_cap_df = project_cap_df.rename(columns={'capacity': 'capacity-details'})
    
    # # merge on name to gdf
    
    # gdf = pd.merge(left=gdf, right=project_cap_df, on='name', how='outer')
     
    return gdf

def workaround_display_cap(row, cap_col):
    cap = row[cap_col] 
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
    
def workaround_table_float_cap(row, cap_col):
    cap = row[cap_col] 
    cap = check_and_convert_float(cap)
    if isinstance(cap, (int, float)):
        cap = float((round(cap, 3))) # handle rounding and converting from string to float to round later 
    else:
        print(f'issue cap should be a float')
        
    return cap
    
def workaround_table_units(row):

    units_of_m = str(row['original_units'])

    return units_of_m
        

# def workaround_display_cap_total(row):
#     # adds original units to the summedcapacity-details'from workaround_no_sum_cap_project
#     cap = row['capacity-details']
#     cap = check_and_convert_float(cap)

#     if pd.isna(cap):
#         cap = '' 
#     units_of_m = str(row['original_units'])
#     if isinstance(cap, (int, float)):
#         cap = str(float(round(cap, 3)))
#         result = f'{cap} ({units_of_m})'
#     else:
#         result = ''
#     return result
    
    
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

def fix_status_space(df):
    import logging

    # input('check all status options')
    # df['status'] = df['status'].replace('in development', 'in_development')
    # df['status'] = df['status'].replace('shut in','shut_in')
    df['status_display'] = df['status']
    df['status_display'] = df['status_display'].replace('', 'not found')
    df['status'] = df['status'].apply(lambda x: x.replace(' ', '_'))
    print(set(df['status'].to_list()))
    # input('inspect status with _')
    logging.basicConfig(level=logging.INFO)
    logging.info(set(df['status'].to_list()))
    print(set(df['status_display'].to_list()))
    # input('inspect status_display without _')

    return df

def fix_prod_type_space(df):
    import logging

    # input('check all status options')
    df['tab-type-display'] = df['tab-type']
    df['tab-type'] = df['tab-type'].apply(lambda x: x.replace(' ', '_'))
    print(set(df['tab-type'].to_list()))
    # input('inspect status with _')
    logging.basicConfig(level=logging.INFO)
    logging.info(set(df['tab-type'].to_list()))
    print(set(df['tab-type-display'].to_list()))
    # input('inspect status_display without _')

    return df
    
def split_coords(df):
    
    df['lat'] = df['Coordinates'].apply(lambda x: x.split(',')[0])
    df['lng'] = df['Coordinates'].apply(lambda x: x.split(',')[1])

    return df

def make_numerical(df, list_cols):
    df = df.copy()
    for col in list_cols:
        # Replace blank spaces, '>0', and 'unknown' with NaN
        df[col] = df[col].replace(['', '>0', 'unknown'], np.nan)
        
        # Fill NaN values with a default 
        df[col] = df[col].fillna(0)
        
        # Convert the column to integers
        df[col] = df[col].astype(int)

    print(df[list_cols].info())
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
    # print(f'There were {len(problem_units_weird_country_df)} found for this df {df["tracker-acro"].iloc[0]}! Look at them here: {path_for_test_results}problem_units_weird_country_{iso_today_date}.csv')
    # input('Did you check it yet?')
    return None

def check_for_lists(gdf):
    for col in gdf.columns:
        if any(isinstance(val, list) for val in gdf[col]):
            print('Column: {0}, has a list in it'.format(col))
        else:
            pass
