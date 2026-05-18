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
from openpyxl.styles import Font
from openpyxl.styles import Alignment
import pickle
from collections import Counter
import subprocess
# import yaml
import sys
import re
from pathlib import Path


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

def update_col_formatting_config(fcl, rd):
    # taking updated fc list and renaming dict as inputs
    # then convert to json
    # then write to json file same file name
    fcl_path = Path(__file__).parent / '_final_cols.json'
    rd_path = Path(__file__).parent / '_renaming_cols.json'
    
    if fcl:
        with open(fcl_path, 'w', encoding='utf-8') as f_fcl:
            json.dump(fcl, f_fcl, indent=4)
    else:
        print("Warning: fcl is empty, skipping write to file")
            
    if rd:
        
        with open(rd_path, 'w', encoding='utf-8') as rd_f:
            json.dump(rd, rd_f, indent=4)
    else:
        print("Warning: rd is empty, skipping write to file")
        

        


def save_to_s3(obj, df, filetype='', path_dwn=''):
    geojsonpath = f"{path_dwn}{obj.name}_map_{iso_today_date}.geojson" # for africa or regular    
    # Ensure geometry is properly handled before saving
    if 'geometry' in df.columns:
        if not isinstance(df, gpd.GeoDataFrame):
            # print("Converting DataFrame to GeoDataFrame...")
            df = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

        # Convert geometry to WKT format for saving as Parquet
        df['geometry'] = df['geometry'].apply(lambda geom: geom.wkt if geom else None)

    # Handle missing values and ensure the column is stored as a string
    # if 'unit-name' in df.columns:
    #     df['unit-name'] = df['unit-name'].fillna('').astype(str)
    for col in df.columns:
        # check if mixed dtype
        if df[col].apply(type).nunique() > 1:
            # if so, convert it to string
            df[col] = df[col].fillna('').astype(str)
        
    # TODO address parquet error Hannah
    # parquetpath = f"{path_dwn}{obj.name}{filetype}{releaseiso}.parquet"
    # df.to_parquet(parquetpath, index=False)
    # print('Parquet file is saved!')
    
    # # Determine S3 folder based on filetype
    # if filetype == 'map':
    #     s3folder = 'mapfiles'
    # elif filetype == 'datadownload':
    #     s3folder = 'latest'
    # else:
    #     s3folder = 'uncategorized'
    
    # Prepare and execute S3 upload command
    # if geojsonpath != '' and filetype == 'map':
        
        do_command_s3 = (
            f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            f'aws s3 cp {parquetpath} s3://$BUCKETEER_BUCKET_NAME/{obj.name}/{releaseiso}/{parquetpath} '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read && '
            f'aws s3 cp {geojsonpath} s3://$BUCKETEER_BUCKET_NAME/{obj.name}/{releaseiso}/{parquetpath} '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
        )
    else:
        do_command_s3 = (
            f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            f'aws s3 cp {parquetpath} s3://$BUCKETEER_BUCKET_NAME/{obj.name}/{releaseiso}/{parquetpath} '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
        )    
        
    process = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process


def save_raw_s3(map_obj, tracker_source_obj, TrackerObject):
    # metadata_dir = os.path.join(os.path.dirname(__file__), 'metadata_files')
    # os.makedirs(metadata_dir, exist_ok=True)
    # write to config file total length of dfs
    mfile_actual = os.path.join(metadata_dir, f'{map_obj.mapname}_{releaseiso}_{iso_today_date}_metadata.yaml')

     
    # save to metadata
    # print(f'this is mfile_actual: {mfile_actual}')
    # input('check if it matches')
    # Prepare dictionary representations, but do not convert tracker_source_obj.data or map_obj.trackers
    tracker_dict = tracker_source_obj.__dict__.copy()
    map_dict = map_obj.__dict__.copy()

    # Replace DataFrames/lists with their lengths for reporting
    if isinstance(tracker_dict.get('data', None), pd.DataFrame):
        df = tracker_dict['data']
        tracker_dict['data'] = {
        "info": f"DataFrame with {len(df)} rows",
        "columns": [{col: str(df[col].dtype)} for col in df.columns],
        "columns2": [df.info()]
        }
    if isinstance(map_dict.get('trackers', None), list):
        map_dict['trackers'] = f"List with {len(map_dict['trackers'])} TrackerObjects"

    # Remove DataFrames (not serializable) or convert to string
    for d in [tracker_dict, map_dict]:
        for k, v in list(d.items()):
            if isinstance(v, pd.DataFrame):
                d[k] = v.to_dict()  # or v.to_json() if preferred
            elif isinstance(v, list) and v and isinstance(v[0], TrackerObject):
                # For map_obj.trackers, store acros or dicts
                d[k] = [t.__dict__.copy() for t in v]

    # Append to YAML file instead of overwriting

    # Check if file exists and load existing data
    if os.path.exists(mfile_actual):
        with open(mfile_actual, "r") as f:
            try:
                existing_data = yaml.safe_load(f) or []
            except Exception:
                existing_data = []
    else:
        existing_data = []

    # Ensure existing_data is a list
    if not isinstance(existing_data, list):
        existing_data = [existing_data] if existing_data else []

    # Append new entry
    existing_data.append({'tracker': tracker_dict, 'map': map_dict})

    # Write back the updated list
    with open(mfile_actual, "w") as f:
        yaml.dump(existing_data, f, default_flow_style=False)

    # mapobj.name
    for trackerobj in map_obj.trackers: # list of tracker objeccts
        logger.info(f'This is trackerobj.name: {trackerobj.name}')
        try:
            originaldf = trackerobj.data

            # save locally then run process
            trackernamenospaceoraperand = trackerobj.name.replace(' ', '_').replace('&', 'and')
            iso_today_datenospace = iso_today_date.replace(' ', '_')

            originaldf.to_json(
                f"{trackers}/{map_obj.mapname}/{map_obj.mapname}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}.json",
                force_ascii=False,
                date_format='iso',
                orient='records',
                indent=2
                )
            
            originalfile = f'"{map_obj.mapname}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}.json"'
            originalfile_with_no_quote = f'{map_obj.mapname}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}.json' 
            do_command_s3 = (
                f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
                f'aws s3 cp {originalfile_with_no_quote} s3://$BUCKETEER_BUCKET_NAME/{map_obj.mapname}/{releaseiso}/{originalfile_with_no_quote} --endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
                )    
            
            subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # delete the locally saved file
            if os.path.exists(originalfile_with_no_quote):
                os.remove(originalfile_with_no_quote)            
                
        except AttributeError: 
            main_goget_df = trackerobj.data[0]
            prod_or_og_df = trackerobj.data[1]

            originaldfs = [main_goget_df, prod_or_og_df]
            for idx, df in enumerate(originaldfs):
                trackernamenospaceoraperand = trackerobj.name.replace(' ', '_').replace('&', '')
                
                iso_today_datenospace = iso_today_date.replace(' ', '_')
                df.to_json(
                    f"{map_obj.mapname}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}_{idx}.json",
                    force_ascii=False,
                    date_format='iso',
                    orient='records',
                    indent=2
                    )

                originalfile = f'"{map_obj.mapname}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}_{idx}.json"'
                originalfile_with_no_quote = f'{map_obj.mapname}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}_{idx}.json'
                
                do_command_s3 = (
                    f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
                    f'aws s3 cp {originalfile} s3://$BUCKETEER_BUCKET_NAME/{map_obj.mapname}/{releaseiso}/{originalfile} '
                    f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
                    )    
                    

                subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # delete the locally saved file
                if os.path.exists(originalfile):
                    os.remove(originalfile)
        except Exception as e:
            #pass
            print(f"Error {e}, but keep going.")
            
        
    logger.info('done with save_raw_s3')

def save_mapfile_s3(map_obj_name, tracker_name, filter, df1, df2=None):
    """
    Save map file to S3. df2 is optional.
    """
    
    # TODO move this os.path work to util or config file like Hannah does it!
    # metadata_dir = os.path.join(os.path.dirname(__file__), 'metadata_files')
    # os.makedirs(metadata_dir, exist_ok=True)
    # write to config file total length of dfs
    mfile_actual = os.path.join(metadata_dir, f'{map_obj_name}_{releaseiso}_{iso_today_date}_metadata.yaml')

    # Prepare metadata dictionary for logging
    meta_entry = {
        "df1_info_filtered": {
            "length": len(df1),
            "columns": [{col: str(df1[col].dtype)} for col in df1.columns],
            "filtered": filter
        }
    }
    if df2 is not None:
        meta_entry["df2_info_filtered"] = {
            "length": len(df2),
            "columns": [{col: str(df2[col].dtype)} for col in df2.columns],
            "filtered": filter

        }

    # Load existing YAML data if present
    if os.path.exists(mfile_actual):
        with open(mfile_actual, "r") as f:
            try:
                existing_data = yaml.safe_load(f) or []
            except Exception:
                existing_data = []
    else:
        existing_data = []

    # Ensure existing_data is a list
    if not isinstance(existing_data, list):
        existing_data = [existing_data] if existing_data else []

    # Append new entry and write back
    existing_data.append(meta_entry)
    with open(mfile_actual, "w") as f:
        yaml.dump(existing_data, f, default_flow_style=False)
    
    print(f'This is df2 {df2}')
    
    if df2 is not None:
        # do both
        dfs = [df1, df2]
        for idx, df in enumerate(dfs):
            trackernamenospaceoraperand = tracker_name.replace(' ', '_').replace('&','')
            iso_today_datenospace = iso_today_date.replace(' ', '_')
            try:
                folder_name = mapname_gitpages[official_tracker_name_to_mapname[tracker_name]]
            except KeyError as e:
                print(f'error was {e}')
                # sometimes there is no diffference between the inner dict and outer so would be keyerror because not in outer dict
                folder_name = official_tracker_name_to_mapname[tracker_name]
            df.to_json(
                f"{tracker_folder_path}{folder_name}/compilation_output/{map_obj_name}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}_{idx}.json",
                force_ascii=False,  # Ensures UTF-8 encoding for non-ASCII characters
                date_format='iso',  # Optional: formats dates in ISO format
                orient='records',   # Optional: controls the JSON structure
                indent=2            # Optional: pretty print with indentation
            )
            filt_file = f'"{tracker_folder_path}{folder_name}/compilation_output/{map_obj_name}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}_{idx}.json"'

            do_command_s3 = (
                f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
                f'aws s3 cp {filt_file} s3://$BUCKETEER_BUCKET_NAME/{map_obj_name}/{releaseiso}/{filt_file} '
                f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
                )    
            
            # TO LOOK OVER THIS SIMPLER boto3 way to push to s3, see if you can set public
            # https://github.com/GlobalEnergyMonitor/WikiURLProcessing/blob/main/upload_csv_to_s3bucket.py

            subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # delete the locally saved file
            if os.path.exists(filt_file):
                os.remove(filt_file)    

            
    else:
        # only df1
        df = df1
        trackernamenospaceoraperand = tracker_name.replace(' ', '_').replace('&','')
        iso_today_datenospace = iso_today_date.replace(' ', '_')
        try:
            folder_name = mapname_gitpages[official_tracker_name_to_mapname[tracker_name]]
        except KeyError as e:
            print(f'error was {e}')
            # sometimes there is no diffference between the inner dict and outer so would be keyerror because not in outer dict
            folder_name = official_tracker_name_to_mapname[tracker_name]
        if not isinstance(df, gpd.GeoDataFrame):
            df.to_json(
                f"{tracker_folder_path}{folder_name}/compilation_output/{map_obj_name}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}.json",
                force_ascii=False,  # Ensures UTF-8 encoding for non-ASCII characters
                date_format='iso',  # Optional: formats dates in ISO format
                orient='records',   # Optional: controls the JSON structure
                indent=2            # Optional: pretty print with indentation
            )
            filt_file = f'"{tracker_folder_path}{folder_name}/compilation_output/{map_obj_name}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}.json"'
        else:
        # except ValueError as e:
        #     print(f'error is {e}')
            # Save as GeoJSON using GeoDataFrame's to_file method
            # gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326") if not isinstance(df, gpd.GeoDataFrame) else df
            print('df is actually a gdf')
            df.to_file(
            f"{tracker_folder_path}{folder_name}/compilation_output/{map_obj_name}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}.geojson",
            driver='GeoJSON',
            encoding='utf-8'
            )
        
            filt_file = f'"{tracker_folder_path}{folder_name}/compilation_output/{map_obj_name}_{releaseiso}_{trackernamenospaceoraperand}_{iso_today_datenospace}.geojson"'

        do_command_s3 = (
            f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            f'aws s3 cp {filt_file} s3://$BUCKETEER_BUCKET_NAME/{map_obj_name}/{releaseiso}/{filt_file} '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
            )    
            

        subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # delete the locally saved file
        if os.path.exists(filt_file):
            os.remove(filt_file)     
 
    print('done with saving mapfile to s3')

def remove_illegal_characters(value):
    if isinstance(value, str):
        # Define a regex pattern to match illegal characters
        illegal_characters = re.compile(r'[\x00-\x1F\x7F-\x9F]')
        # Replace illegal characters with an empty string
        return illegal_characters.sub('', value)
    return value      

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

# used a lot
def gspread_access_file_read_only(key, tab_list):
    """
    key = Google Sheets unique key in the URL
    title = name of the sheet you want to read
    returns a df of the sheet
    """
    logger.info(f'this is key and tab list in gspread access file read only function:\n{key}{tab_list}')
    gspread_creds = gspread.oauth(
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        credentials_filename=client_secret_full_path,
        # authorized_user_filename=json_token_name,
    )
    list_of_dfs = []
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

            try:
                df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            except APIError:
                print(f'getting an APIError')
                print(f'this is spreadsheet after loading tab into gsheets.worksheet:\n{spreadsheet}')
                df = pd.DataFrame(spreadsheet.get_all_records())


            list_of_dfs.append(df)
    if len(list_of_dfs) > 1: 
        # df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True).fillna('')
        
        df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True)

    return df
 
def create_prep_file(multi_tracker_log_sheet_key, prep_file_tab): # needed_map_list
    
    # if local_copy:

    #     with open(f'local_pkl/prep_df{iso_today_date}.pkl', 'rb') as f:
    #         prep_df = pickle.load(f)
    # else:
    prep_df = gspread_access_file_read_only(multi_tracker_log_sheet_key, prep_file_tab)
    # Add pickle format for prep_df
    prep_df = prep_df[prep_df['tab name'] != ''] # skips rows at bottom
    # Convert 'gspread_tabs' and 'sample_cols' to lists
    prep_df['gspread_tabs'] = prep_df['gspread_tabs'].apply(lambda x: x.split(';'))
    # df['sample_cols'] = df['sample_cols'].apply(lambda x: x.split(';'))
    prep_df['gspread_tabs'] = prep_df['gspread_tabs'].apply(lambda lst: [s.strip() for s in lst])
    # df['sample_cols'] = df['sample_cols'].apply(lambda lst: [s.strip() for s in lst])
    # first copy the column because we need it
    prep_df['index_tabname'] = prep_df['tab name'].copy()

    # # then set it as an index
    prep_df.set_index('index_tabname', inplace=True) # sets index on tab name
    # prep_df['tracker-acro'] = prep_df['tracker-acro']
    
        # with open(f'local_pkl/prep_df{iso_today_date}.pkl', 'wb') as f:
        #     pickle.dump(prep_df, f)
    
    logger.info(f'This is prep_df {prep_df}')
    print(f'This is prep_df {prep_df}')
    return prep_df


def clean_capacity(df):
    # clean df
    if 'Capacity (MW)' in df.columns:
        df['Capacity (MW)'] = df['Capacity (MW)'].apply(lambda x: check_and_convert_float(x))
        # df = df.fillna('')
        
        # round all capacity cols to 
        df['Capacity (MW)'] = df['Capacity (MW)'].apply(lambda x: round(x, 4) if x != '' else x)    
    else:
        print(df.info())
        input('Check df.info for capacity name, Capacity (MW) not it!')
    
    return df

def semicolon_for_mult_countries_gipt(df):
    
    cols_to_consider = ['Country/area 1 (hydropower only)',  'Country/area 2 (hydropower only)']
    
    # end goal is we want the hydro cols to fit into country cols
    # only need to do that when there is a second country, in those cases cap2 is not 0
    # the country and cap cols (main) is the first country and combined cap
    # multiple countries separated by ;
    # df = df.fillna('')
    for row in df.index:
        if df.loc[row, 'Country/area 2 (hydropower only)'] != '':
            print(f"Country 1: {df.loc[row, 'Country/area 1 (hydropower only)']}")
            df.loc[row,'Country/area'] = f"{df.loc[row, 'Country/area 1 (hydropower only)']}; {df.loc[row, 'Country/area 2 (hydropower only)']};"
            
        else:
            df.loc[row,'Country/area'] = f"{df.loc[row, 'Country/area']};"

    return df



# def save_as_parquet(gdf, mapname, filetype, path_dwn):
#     # DataFrame.to_parquet(path=None, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, **kwargs)
#     # partition_colslist, optional, default None
#     # Column names by which to partition the dataset. Columns are partitioned in the order they are given. Must be None if path is not a string.
#     # partition by country into data lakes, and status
#     # explore storage storage_options dict, optional
#     gdf.fillna('', inplace=True)
#     print(type(gdf))
        
#     gdf.to_parquet(f"{path_dwn}{mapname}{filetype}{releaseiso}.parquet", index=False)  # partition_cols=["country/area"],
#     print('Parquet file is saved!')
    
#     return f"{path_dwn}{mapname}{releaseiso}.parquet"

# def get_standard_country_names():
    
#     if local_copy:

#         with open(f'local_pkl_dir/gem_standard_country_names_{iso_today_date}.pkl', 'rb') as f:
#             gem_standard_country_names = pickle.load(f)
    
#     else:
#         df = gspread_access_file_read_only(
#             '1mtlwSJfWy1gbIwXVgpP3d6CcUEWo2OM0IvPD6yztGXI', 
#             ['Countries'],
#         )
#         gem_standard_country_names = df['GEM Standard Country Name'].tolist()
        
#         with open(f'local_pkl_dir/gem_standard_country_names_{iso_today_date}.pkl', 'wb') as f:
#             pickle.dump(gem_standard_country_names, f)
        
    
#     return gem_standard_country_names

# # gem_standard_country_names = get_standard_country_names()



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

# not used but might be useful for pipeline stuff
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
    

def convert_google_to_gdf(df):
    # TODO DOCUMENT HOW EU PIPELINES HY DATA PROCESSED UNTIL HAVE GEOJSON FILE
    df_initial = df.copy()
    # input('check if WKTFormat is there, and also PipelineName')
    df = df[df['WKTFormat'] != '--']
    # print(df[['PipelineName', 'WKTFormat']]) # or name
    df['WKTFormat'].fillna('')
    df = df[df['WKTFormat'] != '']
    # print(df[['PipelineName', 'WKTFormat']])

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


    df = df.drop(to_drop_again) 
    
    df['geometry'] = df['WKTFormat'].apply(lambda x: wkt.loads(x))
    
    # print(len(df))
    df = pd.concat([df, df_to_drop])
    # print(len(df))
    # input('length after of length of df')
    
    # input(f'Check size before and after: now | {len(df)} then | {len(df_initial)}')
    
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    return gdf




def remove_diacritics(name_value):
    
    if pd.isnull(name_value):
        name_value = ''
    elif type(name_value) != float:
        for char in name_value:
            for k, v in diacritic_map.items():
                if char in v:
                    name_value = name_value.replace(char, k)

    return name_value

# TO DO MOVE THIS TO make_map_file or to obj class?
def create_conversion_df(conversion_key, conversion_tab):

    df = gspread_access_file_read_only(conversion_key, conversion_tab)
    # # # printf'this is conversion df: {df}')
    
    df = df[['tracker', 'type', 'original units', 'conversion factor (capacity/production to common energy equivalents, TJ/y)']]
    df = df.rename(columns={'conversion factor (capacity/production to common energy equivalents, TJ/y)': 'conversion_factor', 'original units': 'original_units'})
    df['tracker'] = df['tracker'].apply(lambda x: x.strip())
    
    with open(f'{local_pkl_dir}/conversion_df.pkl', 'wb') as f:
        pickle.dump(df, f)
    print("DataFrames have been saved to conversion_df.pkl")

    return df  

def check_in_range(value, min_val, max_val):
    # doesn't handle na because already was handled
    if min_val <= value <= max_val:

        return value

    else:
        print('value not in range:')
        print(f'value:{value}, min_val:{min_val}, max_val:{max_val}')
        return np.nan


# def find_about_page(tracker,key):
#         # print(f'this is key and tab list in def find_about_page(tracker,key):function:\n{tracker}{key}')

#         gspread_creds = gspread.oauth(
#             scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
#             credentials_filename=client_secret_full_path,
#             # authorized_user_filename=json_token_name,
#         )
#         wait_time = 5
#         time.sleep(wait_time)
#         gsheets = gspread_creds.open_by_key(key)
            
#         # List all sheet names
#         sheet_names = [sheet.title for sheet in gsheets.worksheets()]
#         # print(f"{tracker} Sheet names:", sheet_names)
#         # Access a specific sheet by name
#         first_tab = sheet_names[0]
#         first_sheet = gsheets.worksheet(first_tab)  # Access the first sheet
        
#         last_tab = sheet_names[-1]
#         last_sheet = gsheets.worksheet(last_tab)  # Access the last sheet

#         # print("First sheet name:", sheet.title)
#         if 'About' not in first_sheet.title:
#             # print('Looking for about page in last tab now, first one no.')
#             # handle for goget and ggit, goit who put it in the last tab
#             if 'About' not in last_sheet.title:
#                 if 'Copyright' not in last_sheet.title:
#                     print('Checked first and last tab, no about page found not even for copyright. Pausing.')
#                     input("Press Enter to continue...")
#                 else:
#                     # print(f'Found about page in last tab: {last_tab}')
#                     sheet = last_sheet
#             else:
#                 # print(f'Found about page in last tab: {last_tab}')
#                 sheet = last_sheet
#         else:
#             # print(f'Found about page in first tab: {first_tab}')
#             sheet = first_sheet
        
#         data = pd.DataFrame(sheet.get_all_records(expected_headers=[]))
#         about_df = data.copy()
    
#         return about_df

def wait_n_sec(n):
    print(f"Starting {n} second wait...")

    time.sleep(n)
    print(f"{n}-second wait completed.")
    

def get_key_tabs_prep_file(tracker):
    prep_df = create_prep_file(multi_tracker_log_sheet_key, source_data_tab)

    prep_dict = prep_df.to_dict(orient='index')
    print(prep_dict)
    print(tracker)
    if tracker in non_gsheet_data:
        print('Needs to be local')

    else:
        key = prep_dict[tracker]['gspread_key']
        tabs = prep_dict[tracker]['gspread_tabs']
    return key, tabs

# COMMENTING OUT FOR NOW CAN SHOULD BE ABLE TO REMOVE TESTING THAT THE MAP CLASS ONE IS USED FOR ALL
# Needed for gipt integrated script - keep in for now
# # TODO instances to remove from run_maps.py after tested, then in specifci_temp for asia, and in assign_hy_pci for europe
def create_df(key, tabs=['']):
    # print(tabs)
    dfs = []
    # other logic for goget 
    if trackers_to_update[0] == 'Oil & Gas Extraction':
        for tab in tabs:
            # print(tab)
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
    
    elif trackers_to_update[0] == 'Iron & Steel':
        # keytab = key
        # print(keytab)
        # for k,v in keytab.items(): # dict of tuples the tuple being key and tabs 
        #     # print(f'this is key: {k}')
        #     # print(f'this is v: {v}')
        #     tabtype = k
        #     key = v[0]
        #     tabs = v[1]
        #     # Iron & Steel: plant (unit-level not needed anymore)
        for tab in tabs:
            gsheets = gspread_creds.open_by_key(key)
            spreadsheet = gsheets.worksheet(tab)
            df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            df['tab-type'] = tab
            dfs += [df]

        df = pd.concat(dfs).reset_index(drop=True)
        print(df.info())

    else:
        for tab in tabs:
            gsheets = gspread_creds.open_by_key(key)
            spreadsheet = gsheets.worksheet(tab)
            df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            dfs += [df]
        df = pd.concat(dfs).reset_index(drop=True)

    return df


# TODO can probably remove this once figure out waht specifci_temp.py in asia is used for
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

# TODO look into why this wasn't applied
def add_goit_boedcap_from_baird(gdf):
    # set up fixed goit file pd
    goit_cap_boed = gpd.read_file(goit_cap_updated)
    print(goit_cap_boed.info())
    # goit_cap_boed.drop(columns=['Capacity'], inplace=True) # there is already a capacity that exists

    # goit_cap_boed = goit_cap_boed.rename(columns={'ProjectID':'id', 'CapacityBOEd': 'capacity'})

    # Merge goit_cap_boed with the main gdf on 'id'
    gdf = gdf.merge(goit_cap_boed[['ProjectID', 'CapacityBOEd']], on='ProjectID', how='left', suffixes=('', '_new'))
    
    # Update the 'capacity_boed' column in gdf with the new values where there is a match
    gdf['CapacityBOEd'] = gdf['CapacityBOEd_new'].combine_first(gdf['CapacityBOEd'])
    
    # Drop the temporary 'capacity_boed_new' column
    gdf.drop(columns=['CapacityBOEd_new'], inplace=True)
    print('AFTER')
    
    print(len(gdf))

    # for col in gdf.columns:
    #     print(col)
    print(gdf.info())
    # input('Check the above...')
    return gdf    

# not needed with db data!
def create_goget_wiki_name(df):
    # df['Wiki name'] = df['Unit Name'] + ' Oil and Gas Field ('+ df['Country'] + ')'
    
    # df['Wiki name'] = df.apply(lambda row: f"{row['Unit Name']} Oil and Gas Field ({row['Country/Area']})", axis=1)
    
    df['Wiki name'] = df['Unit Name'] # for simplicity but this whole function can be removed

    # 'Wiki name'
    # print(df[['Country/Area', 'Unit Name', 'Wiki name']].head())
    # input('Check that Wiki name came out alright')
    return df 


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

# Put into db TODO or complete 
def find_most_granular_loc(df):
    '''This will find the most granular location for each row so we can find the best coordinates 
    for the project. For now we will just use the country as the most granular polygon. In the future
    we will make it more robust.'''
    
    # gadm file of all country and province polygon geometries
    # convert all gem data to align with country and province spelling
    
    return df

# TODO on all data in database though
def apply_representative_point(df):
    '''This will apply representative point function to all rows that have missing coordinates'''
    polygon_name_loc = find_most_granular_loc(df)
    
    
    return df

def bold_first_row(writer, sheet_name):
    """Bold all cells in the first row of a sheet after writing with pd.ExcelWriter (openpyxl engine)."""
    worksheet = writer.sheets[sheet_name]
    bold_font = Font(bold=True)
    for cell in worksheet[1]:
        cell.font = bold_font




def clean_about_df(df):
    """Clean about page DataFrame: deduplicate row values (from merged cells), drop blank columns, remove blank first row."""
    df = df.copy()
    # Remove duplicate values in the same row (from unmerged merged cells)
    df = df.apply(lambda row: row.where(~row.duplicated(), ''), axis=1)
    # Drop columns that are entirely blank/empty
    df = df.loc[:, ~(df.fillna('').eq('').all())]
    # Remove first row if blank
    if len(df) > 0 and (df.iloc[0].isnull().all() or (df.iloc[0] == '').all()):
        df = df.drop(df.index[0]).reset_index(drop=True)
    return df


def convert_coords_to_point(df):
    crs = 'EPSG: 4326'
    geometry_col = 'geometry'
    df = df.reset_index(drop=True)
    # df.columns = df.columns.str.lower()
    df['geometry'] = None  # Initialize the geometry column
    if 'Longitude' in df.columns and 'Latitude' in df.columns:
        # do qc on values
        # remove white space
        # convert to numerical coerce
        for col in ['Latitude', 'Longitude']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Remove rows for now, but should save to file or raise... TODO
        df = df.dropna(subset=['Latitude', 'Longitude'])    
        
        df['geometry'] = df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    elif 'longitude' in df.columns and 'latitude' in df.columns:
        df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    
    elif 'lng' in df.columns and 'lat' in df.columns:
        for col in ['lat', 'lng']:
            df[col] = pd.to_numeric(df[col], errors='raise')
        # Remove rows for now, but should save to file or raise... TODO
        df = df.dropna(subset=['lat', 'lng'])
        df['geometry'] = df.apply(lambda row: Point(row['lng'], row['lat']), axis=1)
    
    else:
        print('issues with finding lat lng to convert to gdf!!')
        print(f'{df.columns} \n check columns above')
        input('issues with finding lat lng to convert to gdf!!')
            
            
    gdf = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)
    
    return gdf

# TODO adjust so this is useful in finding new list of countries.json file needed based on involved countries
def rebuild_countriesjs(mapname, newcountriesjs):

        prev_countriesjs = f'{tracker_folder_path}{mapname}/countries.json'
        default = "src/countries.json"
     
        logger.info(prev_countriesjs)
        logger.info('The above is from the existing countries.json file if it exists in the map folder')

        
        # or try except FileNotFoundError 
        if os.path.exists(prev_countriesjs):
            if prev_countriesjs.endswith('.json'):
                with open(prev_countriesjs, 'r') as js_file:
                    prev_countriesjs = js_file.read()
                    logger.info("JSON content:")
                    logger.info(prev_countriesjs)
            else:
                logger.info("The file is not a JSON file.")
        else:
            logger.info(f"File not found. Using default countries.json from {default}")
            with open(default, 'r') as js_file:
                prev_countriesjs = js_file.read()
                logger.info("Default JSON content:")
                logger.info(prev_countriesjs)
        
        # cycle through folder to find new countries.js file and do a comparison
        
        # from map file, create new countries.js based on sorted countries
        missing_countries_areas = set(newcountriesjs) - set(prev_countriesjs)
        
        if len(missing_countries_areas) > 0 and missing_countries_areas != None:
            logger.info(f'paste in this sorted list of new countries into {mapname} countries.js file')
            logger.info(f'These are the net new countries:')
            logger.info(missing_countries_areas)
            # save the sorted file
            cleaned_countriesjs = [country.strip(';') for country in newcountriesjs]
            newcountriesjs = sorted(cleaned_countriesjs)
            logger.info(f'This is the sorted countries file with net new: \n {newcountriesjs}')
            logger.info(newcountriesjs)


def pci_eu_map_read(gdf):
    # take columns PCI5 and pci6 
    # create one column, both, 5, 6, none, all as strings
    # April 14th Made adjustments based on new filter for legend
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


# from GOGPT make, check that its not gogpt specific

def replace_old_date_about_page_reg(df): # TODO augu 28 make this better or delete it
    """ Finds a month and replaces it along with the next five characters (a space and year) with the current release date"""

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    # Convert the entire dataframe to string
    df = df.astype(str)
    
    # find month in about_df string
    # multi_tracker_data is df of main about page for regional dd

    # bold the first row
    # find replace the month and year
    # convert df column to string
    for row in df.index:
        for col_idx in range(len(df.columns)):
            cell_val = str(df.iloc[row, col_idx])
            for month in months:
                sub = month + ' 20'
                year_chars = len(month) + 5
                if sub in cell_val:
                    index = cell_val.find(sub)
                    # Skip if preceded by '(' (e.g. parenthetical dates)
                    if index > 0 and cell_val[index - 1] == '(':
                        continue
                    end = index + year_chars
                    df.iloc[row, col_idx] = cell_val[:index] + new_release_dateinput.replace('_', ' ') + cell_val[end:]

    return df

def rename_cols(df):
    # NEEDED for GIPT
    print(f'Cols before: {df.columns}')

    df = df.copy()
    df = df.rename(columns=str.lower)
    [print(col) for col in df.columns]
    df.columns = df.columns.str.replace(' ', '-')
    df.columns = df.columns.str.replace('.', '')
    if 'gem-wiki-url' in df.columns:
        df = df.rename(columns={'latitude': 'lat', 'longitude':'lng', 'gem-wiki-url': 'url'})
    elif 'wiki-url' in df.columns:
        df = df.rename(columns={'latitude': 'lat', 'longitude':'lng', 'wiki-url': 'url'})
    
    elif 'gemwiki-url' in df.columns:
        df = df.rename(columns={'latitude': 'lat', 'longitude':'lng', 'gemwiki-url': 'url'})

    else:
        print(f'Not sure about wiki url column name.')
        input('check above to adjust rename_cols')
    print(f'Cols after: {df.columns}')
    return df

# TODO explore whether we want this or just a flag in launcher?
def reduce_cols(df):
    print('Finish writing this function to make a lightweight gipt map for homepage!')
    # name, url, capacity, status, type, owner, lat, lng, subnat
    
    
    return df     

def remove_missing_coord_rows(df, tracker):
    df['lng'] = df['lng'].fillna('')
    df['lat'] = df['lat'].fillna('')
    print(len(df))
    issue_df = df[df['lng']== '']
    df = df[df['lng']!= '']
    df = df[df['lat']!= '']
    print(len(df))
    print('This is issues missing coord so removed - good if empty!:')
    print(issue_df)
    if len(issue_df) > 1:
        issue_df.to_csv(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/_scripting/issues/missing_coords_{iso_today_date}_{tracker}.csv')

    return df

def harmonize_countries(df, countries_dict, test_results_folder):
    df = df.copy()

    region_col = set(df['region'].to_list())
    results = []
    for region in region_col:
        df_mask = df[df['region']==region]
        df_mask['country-harmonize-pass'] = df_mask['country/area'].apply(lambda x: 'true' if x in countries_dict[region] else f"false because {x}")
        results_len = df_mask[df_mask['country-harmonize-pass'] == 'false']
        results.append((region, len(results_len)))
        print(f'\nWe want this to be 0: {results}\n')
        results_df = pd.DataFrame(results)
        results_df.to_csv(f'{test_results_folder}results.csv')
        
    # df['areas-subnat-sat-display'] = df.apply(lambda row: f"{row['country']}" if row['state/province'] == '' else f"{row['state/province']}, {row['country']}", axis=1)   

# TODO get this to work so 100 removed
def remove_100(owner):
    if ';' in owner:
        print('owner not relevant')
        print(owner)
    else:
        if '[100%]' in owner:
            print(owner)
            owner = owner.replace(' [100.0%]', '')
            print(owner)
            input('check owner strip 100')
    return owner

# TODO see if just remove this
def remove_100_owner(df):
    # [100%]
    col = ['Owner']
    df[col] = df[col].apply(lambda x: remove_100(x))
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

# TODO apply these
def formatting_checks(df): # gogpt
    df = df.copy()    
    # make sure date is not a float
    df['start-year'] = df['start-year'].replace('not found', np.nan)
    # AND try for capacity too
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


    
def conversion_multiply(row):
    cap = float(row['cleaned_cap'])
    factor = row['conversion_factor']
    # transforming this to 1, it had been purposefully set to n/a for all not regional ones, so should be skipped
    if isinstance(factor, str) and factor.lower() == 'n/a':
        factor = 1        

    else:
        factor = float(factor)
    # print(f'this is factor! {factor}')

    result = float(cap * factor)
    # print(f'this is result! {result}')
    return result

def format_final(df_arg): # TO DO find the other formatting function above
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
        # all_unit_names_statuses = gdf[gdf['name'] == name].apply(lambda x: f"{x['unit_name']} ({x['status']})", axis=1).to_list()
        # all_unit_names_statuses_str = ', '.join(all_unit_names_statuses)
        
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

    
def workaround_table_float_cap(row, cap_col):
    cap = row[cap_col] 
    cap = check_and_convert_float(cap)
    if isinstance(cap, (int, float)):
        cap = float((round(cap, 4))) # handle rounding and converting from string to float to round later 
    else:
        print(f'issue cap should be a float')
        
    return cap
    
def workaround_table_units(row):

    units_of_m = str(row['original_units'])

    return units_of_m
        

def fix_status_inferred(df):
    if 'status' in df.columns:
        inferred_statuses_cancelled = df['status'].str.contains('cancelled - inferred')
        inferred_statuses_shelved = df['status'].str.contains('shelved - inferred')

        df.loc[inferred_statuses_cancelled, 'status'] = 'cancelled'
        df.loc[inferred_statuses_shelved,'status'] = 'shelved'

    elif 'Status' in df.columns:
        print(f"Statuses before: {set(df['Status'].to_list())}")

        inferred_statuses_cancelled = df['Status'].str.contains('cancelled - inferred')
        inferred_statuses_shelved = df['Status'].str.contains('shelved - inferred')

        df.loc[inferred_statuses_cancelled, 'Status'] = 'cancelled'
        df.loc[inferred_statuses_shelved,'Status'] = 'shelved'

        print(f"Statuses before: {set(df['Status'].to_list())}")
        
    return df

def check_rename_keys(renaming_dict_sel, gdf):
    # gdf cols
    
    gdf_cols = gdf.columns.to_list()
    # this has already happned             renaming_dict_sel = renaming_cols_dict[tracker_sel]
    # so it's just the key value pair
    for k, v in renaming_dict_sel.items():
        # print(f"Key: {k}, Value: {v}")
        if k not in gdf_cols:
            print(f'Missing {k} from df columns, and will try to rename on it in a moment')
            logger.info(f'Missing {k} from df columns, and will try to rename on it in a moment')
            print(f'This is all cols in df: \n {gdf_cols} \n')
            logger.info(f'This is all cols in df: \n {gdf_cols} \n')
            input(f'Adjust the all_config.py column name dict to match new file.')
            logger.info(f'Adjust the all_config.py column name dict to match new file.')
    
    logger.info(f'This is all cols in df: \n {gdf_cols} \n')
    
def drop_cols_df_a_rename_value_avoid_dup(renaming_dict_sel, gdf):
    # gdf cols
    cols_to_drop = []
    gdf_cols = gdf.columns.to_list()
    
    for col in gdf_cols:
        # if column lower is in values but not column regular is not in key then drop it
        # example: Capacity for ggit-lng. where we use Capacity MTPA instead but rename to capacity
        if col in renaming_dict_sel.values():
            if col not in renaming_dict_sel.keys():
                print(f'Duplicate df col {col} in renaming dict value so df one will be dropped!')
                input('Check duplicate col')
                logger.info(f'Duplicate df col {col} in renaming dict value so df one will be dropped!')
                cols_to_drop.append(col)
                
    
    logger.info(f'This is all #{len(gdf.columns)} cols in df before drop: \n {gdf_cols} \n')
    print(f'This is all cols in df before drop: \n {gdf_cols} \n')
    gdf.drop(columns=cols_to_drop, inplace=True)
    logger.info(f'This is all #{len(gdf.columns)} cols in df after drop: \n {gdf_cols} \n')
    print(f'This is all cols in df after drop: \n {gdf_cols} \n')
    return gdf

  
def fix_status_space(df):
    # input('check all status options')
    # df['status'] = df['status'].replace('in development', 'in_development')
    # df['status'] = df['status'].replace('shut in','shut_in')
    if 'plant-status' in df.columns:
        df['status_display'] = df['plant-status']
        df['status_display'] = df['status_display'].replace('', 'not found')
        df['status_display'] = df['status_display'].replace('unknown', 'not found')
        df['plant-status'] = df['plant-status'].apply(lambda x: x.replace(' ', '-'))
    else:
        df['status_display'] = df['status']
        df['status_display'] = df['status_display'].replace('', 'not found')
        df['status_display'] = df['status_display'].replace('unknown', 'not found')
        df['status'] = df['status'].apply(lambda x: x.replace(' ', '-'))
        print(set(df['status'].to_list()))
        # input('inspect status with _')
        logging.basicConfig(level=logging.INFO)
        logging.info(set(df['status'].to_list()))
        print(set(df['status_display'].to_list()))
        # input('inspect status_display without _')

    return df

def fix_prod_type_space(df):

    # input('check all status options')
    df['prod-method-tier-display'] = df['prod-method-tier']
    df['prod-method-tier'] = df['prod-method-tier'].apply(lambda x: x.replace(' ', '-'))
    # strip out all punctuation with regex
    df['prod-method-tier'] = df['prod-method-tier'].apply(lambda x: re.sub(r'[^\w\s]', '', x))

    print(set(df['prod-method-tier'].to_list()))
    # input('inspect status with _')
    logging.basicConfig(level=logging.INFO)
    logging.info(set(df['prod-method-tier'].to_list()))
    print(set(df['prod-method-tier-display'].to_list()))
    # input('inspect status_display without _')

    return df
    
def split_coords(df):
    
    if 'Coordinates' in df.columns:
        df['Latitude'] = df['Coordinates'].apply(lambda x: x.split(',')[0])
        df['Longitude'] = df['Coordinates'].apply(lambda x: x.split(',')[1])
    else:
        print(df.columns)
        print('Do you see Coordinates in there above?')

    return df

# TODO add to formatting numerical 
# def make_numerical(df, list_cols):
#     df = df.copy()
#     for col in list_cols:
#         # Replace blank spaces, '>0', and 'unknown' with NaN
#         df[col] = df[col].replace(['', '>0', 'unknown'], np.nan)
        
#         # Fill NaN values with a default 
#         df[col] = df[col].fillna(-100)
        
#         # Convert the column to integers
#         df[col] = df[col].astype(int)

#     print(df[list_cols].info())
#     return df


def make_plant_level_status(unit_status_list, plant_id):
    qa_status_combos_list = []
    # row from plant level cap and status tab
    unit_status_list = unit_status_list.copy()
    set_list = set(unit_status_list)
    # If only 1 status:	That status is assigned to entire plant

    if len(set_list) == 1:
        plant_status = unit_status_list[0]
        # print(f'length of set list should be 1:\n{set_list}')
        # input('check above') # works! 
    # If any of the statuses for the plant ID are "operating"	Entire plant listed as "operating"
    elif 'operating' in unit_status_list:
        plant_status = 'operating'
    # cancelled, operating pre-retirement	operating pre-retirement
    # retired, operating pre-retirement	operating pre-retirement
    elif len(set_list) == 2 and 'operating pre-retirement' in set_list and ('cancelled' in set_list or 'retired' in set_list):
        plant_status = 'operating pre-retirement'

    # announced, cancelled, operating pre-retirement	operating
    # announced, construction, operating pre-retirement	operating
    # announced, construction, retired, operating pre-retirement	operating
    # announced, mothballed, operating pre-retirement	operating
    # announced, operating pre-retirement	operating
    # announced, operating pre-retirement, mothballed pre-retirement	operating
    # announced, retired, operating pre-retirement, mothballed pre-retirement	operating
    # construction, mothballed, operating pre-retirement	operating
    # construction, mothballed, retired, operating pre-retirement	operating
    # construction, operating pre-retirement	operating
    
    elif 'operating pre-retirement' in set_list:
        plant_status = 'operating'
        
    # announced, construction	construction
    # construction, retired	construction
    elif len(set_list) == 2 and 'construction' in set_list:
        plant_status = 'construction'

    # construction, mothballed	mothballed
    # mothballed, retired	mothballed
    # announced, mothballed
    elif len(set_list) == 2 and 'mothballed' in set_list:
        plant_status = 'mothballed'
    # announced, cancelled	announced
    # announced, retired	announced
    elif len(set_list) == 2 and 'announced' in set_list:
        plant_status = 'announced'
    else:
        print('This condition should not happen, check out status set list and logic from PM:')
        print(f'Status set list: \n{set_list}')
        print(f'This is the plant id to check:\n{plant_id}')
        plant_status = ''
        # input('Check above')

    return plant_status

def make_prod_method_tier(mpe, plant_id):
    mpe_list = mpe.split(';')
    mpe_list = [item.strip() for item in mpe_list]
    replace_dict = {'EAF': 'Electric', 'BOF': 'Oxygen', 'BF': 'Ironmaking (BF)', 'DRI': 'Ironmaking (DRI)'}
    steel_list = ['EAF', 'BOF', 'Steel other/unspecified']
    # electric =  EAF
    # Oxygen = BOF
    # ironmaking (BF) = BF
    # ironmaking (DRI) = DRI
    if len(set(mpe_list)) == 1:
        mpe_list = [replace_dict[item] if item in replace_dict else item for item in mpe_list]
        pmt = mpe_list[0]
        # print(pmt)
        # input('Check replace of dict went well') # works
    # electric, oxygen = EAF, BOF
    elif len(set(mpe_list)) == 2 and 'EAF' in mpe_list and 'BOF' in mpe_list:
        pmt = 'Electric, Oxygen'
    # integrated (BF and DRI)= BF + DRI + any steel unit
    elif 'BF' in mpe_list and 'DRI' in mpe_list and any(steel in mpe_list for steel in steel_list):
        pmt = 'Integrated (BF and DRI)'
    # integrated (BF) = BF + any steel unit (EAF, BOF, OHF, other/unspecified)
    elif 'BF' in mpe_list and any(steel in mpe_list for steel in steel_list):
        pmt ='Integrated (BF)'
    # integrated (DRI)= DRI +any steel unit (EAF, BOF, OHF, other/unspecified)
    elif 'DRI' in mpe_list and any(steel in mpe_list for steel in steel_list):
        pmt = 'Integrated (DRI)'
    # integrated (unknown) = any iron unit + any steel unit
    elif 'Iron other/unspecified' in mpe_list and any(steel in mpe_list for steel in steel_list):
        pmt = 'Integrated (unknown)'
        
    # other/ unspecified = other/unspecified steel 
    # example 'EAF', 'Steel other/unspecified' TODO double check this logic with PM
    elif 'Steel other/unspecified' in mpe_list:
        pmt =  'Steel other/unspecified'
    else:
        print(mpe_list)  
        input('Check mpe list unsure what this should be, possibly other unspecified?')     
        
    return pmt

