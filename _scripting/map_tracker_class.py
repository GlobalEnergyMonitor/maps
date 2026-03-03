from requests import HTTPError
from all_config import about_sheets_pkl_path, nostopping, renaming_cols_dict, final_cols, testtracker, testfilekey, force_refresh_flag, about_templates_key, logpath, local_pkl_dir, new_h2_data, logger, new_release_dateinput, iso_today_date,trackers_to_update, geo_mapping, releaseiso, gspread_creds, region_key, region_tab, centroid_key, centroid_tab, rep_point_key, rep_point_tab
from helper_functions import update_col_formatting_config, check_list, split_countries, convert_coords_to_point, wait_n_sec, fix_prod_type_space, fix_status_space, split_coords, make_plant_level_status, make_prod_method_tier, clean_about_df, replace_old_date_about_page_reg, convert_google_to_gdf, check_and_convert_float, check_in_range, check_and_convert_int, get_most_recent_value_and_year_goget, calculate_total_production_goget, get_country_list, get_country_list, create_goget_wiki_name,create_goget_wiki_name, gspread_access_file_read_only
import pandas as pd
from numpy import absolute
import geopandas as gpd
import boto3
from creds import *
import time
import numpy as np
from shapely import wkt
import pickle
from datetime import datetime
import urllib.parse # quote() and quote_plus() for query params
import os
from shapely.geometry import shape, Point, MultiLineString
import geopandas as gpd
import hashlib


class TrackerObject:
    def __init__(self,
                 off_name="",
                 tab_name="",
                 acro="",
                 key="",
                 tabs=[],
                 about_tabs = [],
                 release="",
                 geocol = [],
                 fuelcol = "",
                 about_pipe_key = "",
                 about_pipe_tabs = [],
                 about = pd.DataFrame(),
                 data = pd.DataFrame(), # will be used for map creation 
                 data_official = pd.DataFrame() # should be for final data downloads removed new columns!
                 ):
        self.off_name = off_name
        self.tab_name = tab_name
        self.acro = acro
        self.key = key
        self.tabs = tabs
        self.about_tabs = [tab.strip() for tab in about_tabs.split(';')] if isinstance(about_tabs, str) else about_tabs
        self.release = release
        self.geocol = geocol
        self.fuelcol = fuelcol
        self.about_pipe_key = about_pipe_key
        self.about_pipe_tabs = [tab.strip() for tab in about_pipe_tabs.split(';')] if isinstance(about_pipe_tabs, str) else about_pipe_tabs
        self.about = about
        self.data = data
        self.data_official = data_official

    def set_data_official(self):
        # drop country_to_check columns

        internal_cols = ['country_to_check']  # Ensure this is a list
        if isinstance(self.data, pd.DataFrame):
            df_official = self.data.copy()
            try:
                df_official.drop(columns=internal_cols, inplace=True)  # Specify columns explicitly
            except KeyError:
                logger.warning('key error in set_data_official')


        else:
            # when it's a tuple
            main, prod, dd_dfs = self.data # with new format should have 6 dfs
            for df in [main, prod]:
                if internal_cols[0] in df.columns:
                    df.drop(columns=internal_cols, inplace=True)
            
            if isinstance(dd_dfs, pd.DataFrame) and internal_cols[0] in dd_dfs.columns:
                dd_dfs.drop(columns=internal_cols, inplace=True)
        
            df_official = (main, prod, dd_dfs)

        
        self.data_official = df_official
    
    def set_about_metadata(self):

        # using about tabs in the class and key pull the most up to date about page

        print(self.about_tabs)
        print(self.key)
        
        # Check if cached about pages exist
        about_cache_path = os.path.join(local_pkl_dir, f'about_pages_cache_{iso_today_date}.pkl')
        about_cache = {}
        
        if os.path.exists(about_cache_path):
            try:
                with open(about_cache_path, 'rb') as f:
                    about_cache = pickle.load(f)
                logger.info(f'Loaded about pages cache from {about_cache_path}')
            except Exception as e:
                logger.warning(f'Failed to load about pages cache: {e}. Will fetch fresh.')
                about_cache = {}
        
        # Create a cache key based on tabs and key
        cache_key = f"{self.key}_{'-'.join(self.about_tabs)}_{'-'.join(self.about_pipe_tabs)}"
        
        # Return cached about_df if available
        if cache_key in about_cache:
            logger.info(f'Using cached about page for {self.off_name}')
            about_df = about_cache[cache_key].copy()
        else:
            logger.info(f'Fetching fresh about page for {self.off_name}')
            about_metadata_tabs = []
            
            # handle for geojson ones
            if self.about_tabs == [''] and self.about_pipe_tabs != ['']:
                for tab in self.about_pipe_tabs:
                    gsheets = gspread_creds.open_by_key(self.about_pipe_key)
                    about_spreadsheet = gsheets.worksheet(tab)
                    time.sleep(6)
                    about_df_temp = pd.DataFrame(about_spreadsheet.get_all_values(combine_merged_cells=True))
                    about_metadata_tabs.append(about_df_temp)
            else:
                for about_tab in self.about_tabs:
                    gsheets = gspread_creds.open_by_key(self.key)
                    about_spreadsheet = gsheets.worksheet(about_tab)
                    time.sleep(6)

                    about_df_temp = pd.DataFrame(about_spreadsheet.get_all_values(combine_merged_cells=True))
                    about_metadata_tabs.append(about_df_temp)

            
            about_df = pd.concat(about_metadata_tabs, sort=False).reset_index(drop=True)
            
            # Cache the about_df before processing
            about_cache[cache_key] = about_df.copy()
        
        if self.tab_name in trackers_to_update:
            release_month_year = f"{new_release_dateinput.replace('_', ' ')}" 
        else:
            release_month_year = self.release

        print(f'This is release_month_year for {self.off_name}, make sure gsheet tracker log is updated or input better date:\n{release_month_year}')

        copyright_full = f"Copyright © Global Energy Monitor. Global {self.off_name} Tracker, {release_month_year} release. Distributed under a Creative Commons Attribution 4.0 International License."
        citation_full = f'Recommended Citation: "Global Energy Monitor, Global {self.off_name} Tracker, {release_month_year} release" (See the CC license for attribution requirements if sharing or adapting the data set.)'
                        
        print(f'This is copyright_full for {self.off_name}:\n{copyright_full}')
        print(f'This is citation_full for {self.off_name}:\n{citation_full}')
        
        # Copyright and citation handling
        num_cols = len(about_df.columns)
        if copyright_full in about_df.values:
            logger.info(f'Already has full copyright: {copyright_full}')
        elif about_df.apply(lambda row: row.astype(str).str.contains('Copyright').any(), axis=1).any():
            logger.info('Partial copyright, delete row and insert full')
            copyright_rows = about_df.apply(lambda row: row.astype(str).str.contains('Copyright').any(), axis=1)
            copyright_row_idx = about_df[copyright_rows].index[0]
            about_df.iloc[copyright_row_idx] = [copyright_full] + [''] * (num_cols - 1)
        else:
            logger.info('Inserting full copyright into second row')
            full_copy_row = pd.DataFrame([[copyright_full] + [''] * (num_cols - 1)], columns=about_df.columns)
            about_df = pd.concat([about_df.iloc[:1], full_copy_row, about_df.iloc[1:]]).reset_index(drop=True)

        about_df.reset_index(drop=True, inplace=True)

        if citation_full in about_df.values:
            logger.info(f'Already has full citation: {citation_full}')
        elif about_df.apply(lambda row: row.astype(str).str.contains('Recommended Citation').any(), axis=1).any():
            logger.info('Partial citation, delete row and insert full')
            citation_rows = about_df.apply(lambda row: row.astype(str).str.contains('Recommended Citation').any(), axis=1)
            citation_row_idx = about_df[citation_rows].index[0]
            about_df.iloc[citation_row_idx] = [citation_full] + [''] * (num_cols - 1)
        else:
            logger.info('Inserting full citation_full into second row')
            full_copy_row = pd.DataFrame([[citation_full] + [''] * (num_cols - 1)], columns=about_df.columns)
            about_df = pd.concat([about_df.iloc[:1], full_copy_row, about_df.iloc[1:]]).reset_index(drop=True)

        about_df.reset_index(drop=True, inplace=True)
        about_df = clean_about_df(about_df)

        self.about = about_df
        
        # Save updated cache to pickle file
        try:
            with open(about_cache_path, 'wb') as f:
                pickle.dump(about_cache, f)
            logger.info(f'Saved about pages cache to {about_cache_path}')
        except Exception as e:
            logger.warning(f'Failed to save about pages cache: {e}')

    def set_df(self, final_cols, renaming_cols_dict):
        # DATA LOADING HAPPENS HERE
        f'This is {self.off_name} {self.acro} {self.tab_name}'

        pkl_path = os.path.join(local_pkl_dir, f'trackerdf_for_{self.acro}_on_{iso_today_date}.pkl')

        # Check if local pkl file exists
        if force_refresh_flag or not os.path.exists(pkl_path):


            s3_file_source_path = 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/'

            # this creates the dataframe for the tracker
            if self.tab_name in ['Oil Pipelines']:
                logger.info('handle non_gsheet_data for pulling data from s3 already has coords')
                
                # to get the file names in latest
                geojson_s3 = self.get_file_name(releaseiso)
                logger.info(f'This is file: {geojson_s3}')
                
                # if 'parquet' in geojson_s3:
                # RENAME THIS IT IS NOT A PARQUET ANYMORE
                # geojson_s3 = self.get_file_name(releaseiso)

                
                # #assign gdf to data 

                gdf = gpd.read_file(f'{s3_file_source_path}{geojson_s3}')

                gdf.set_crs("EPSG:4326", inplace=True)

                    # df = pd.read_parquet(f'{s3_file_source_path}{parquet_s3}') # , engine='pyarrow' NOTE gpd calls a different method "read_table" that requires a file path NOT a URI
                
                    # df['geometry'] = df['geometry'].apply(lambda geom: wkt.loads(geom) if geom else None)

                    # gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
                
                # else:
                #     gdf = gpd.read_file(f'{s3_file_source_path}{parquet_s3}')
                
                self.data = gdf
                
            elif self.tab_name in ['Gas Pipelines']:
                

                logger.info('handle non_gsheet_data for pulling data from s3 already has coords')

                # to get the file names in latest
                # RENAME THIS IT IS NOT A PARQUET ANYMORE
                # geojson_s3 = self.get_file_name(releaseiso)

                
                # #assign gdf to data 

                # gdf = gpd.read_file(f'{s3_file_source_path}{geojson_s3}')

                # gdf.set_crs("EPSG:4326", inplace=True)

                geojson_s3 = self.get_file_name(releaseiso)
                logger.info(f'This is file: {geojson_s3}')


                gdf = gpd.read_file(f'{s3_file_source_path}{geojson_s3}') # , engine='pyarrow' NOTE gpd calls a different method "read_table" that requires a file path NOT a URI
                gdf.set_crs("EPSG:4326", inplace=True)
                
                # check all rows that might be empty, not line, multi line or point
                # POLYGON EMPTY
                problematic_geoms = []
                for idx, row in gdf.iterrows():
                    geom = row['geometry']
                    if geom is None or geom.is_empty:
                        problematic_geoms.append(idx)
                
                if problematic_geoms:
                    logger.warning(f"Found {len(problematic_geoms)} rows with empty/problematic geometry in {self.tab_name}")
                    problematic_df = gdf.iloc[problematic_geoms]
                    report_path = f'{logpath}problematic_geometry_{self.tab_name.replace(" ", "_")}_{iso_today_date}.csv'
                    problematic_df.to_csv(report_path, index=False)
                    logger.info(f"Saved problematic geometry report to {report_path}")
                    
                    # Remove problematic rows from gdf
                    gdf = gdf.drop(problematic_geoms)

                
                self.data = gdf


            elif self.tab_name in ['Gas Pipelines EU']:
                logger.info('handle non_gsheet_data for pulling data from s3 already has coords')
                
                # to get the file names in latest
                geojson_s3 = self.get_file_name(releaseiso)

                
                #assign gdf to data 

                gdf = gpd.read_file(f'{s3_file_source_path}{geojson_s3}')

                gdf.set_crs("EPSG:4326", inplace=True)

                self.data = gdf
                

            elif self.tab_name in ['Oil & Gas Extraction']:
                df_tuple = self.create_df_goget() # TODO for new format

                main = df_tuple[0]
                prod = df_tuple[1]
                
                #assign df tuple to data 
                self.data = df_tuple 
                print(len(self.data))

            # NORMAL CASE JUST PULL FROM GSHEETS
            else:
                #assign df to data 
                # print(self.tab_name)
                df = self.create_df(testtracker)
                
                # add in logic to skip this manual input
                if nostopping == True:
                    print('not going into new column add, proceed with assigning the df to the object data attribute self.data')
                else:
                    
                    # only need to deal with this once (not every time with pkl file)                 
                    # deal with seeing what needs to be changed in all_config
                    print(F'***List of all cols in original tracker df for {self.acro}: \n {df.columns}\n')
                    # existing expected columns
                    exp_cols = renaming_cols_dict[self.acro]
                    print(F'***List of all expected columns and their renaming mappings for {self.acro}: \n {exp_cols}\n')
                    net_new_cols = set(exp_cols) - set(df.columns)
                    print(f'***Net new cols for {self.acro}: \n {net_new_cols}\n')
                    # example I paste in ['Plant Age']
                    cols_to_add = input('***Paste in all net new cols you want to add to dictionary as kv pairs and will use keys for final_cols in list of tuple format:\n')
                    
                    cols_to_remove = input(f'Paste in all kv pairs to be removed in list of tuple format:\n')

                    for tp in cols_to_add:
                        # add value to final cols
                        final_cols.append(tp[1])
                        renaming_cols_dict[self.acro][tp[0]] = tp[1]
                        
                    for tp in cols_to_remove:
                        final_cols = final_cols.remove(tp[1])
                        input(f'DEBUG this is final cols: {final_cols}')
                        renaming_cols_dict.pop(tp[0])
                    print(f'***Full list of final cols now after net new for {self.acro} added: \n {final_cols}\n')
                    print(f'***Full dict of renaming_cols_dict now after net new for {self.acro} added and other removed: \n {renaming_cols_dict}\n')

                    # by reading in these variables just updated final_cols, renaming_cols_dict we can make this column mess less tedious

                    update_col_formatting_config(final_cols, renaming_cols_dict) # passing in list and dict
                              
                self.data = df


# USE LOCAL PKL FILE
        else:
            # Get file creation/modification time
            pkl_timestamp = os.path.getmtime(pkl_path)
            pkl_date = datetime.fromtimestamp(pkl_timestamp).strftime('%Y-%m-%d %H:%M:%S')

            print(f'\nLocal pkl file found for {self.off_name}')
            print(f'File created/modified: {pkl_date}')
            logger.info(msg=f'Local pkl file found for {self.off_name}\nFile created/modified: {pkl_date}')
            # use_local = input(f'Use local pkl file? (y/n, default=y): ').strip().lower()
            # # adjust so can easily press
            # if use_local == 'y' or '':
            try:
                with open(pkl_path, 'rb') as f:
                    logger.info(f'Loading data from local pkl: {pkl_path}')
                    logger.info(f'File timestamp: {pkl_date}')
                    print(f'Loading data from local pkl file...')
                    self.data = pickle.load(f)
                    print(self.data)
                    
                    print(f'Successfully loaded data for {self.off_name}')
                    return  # Exit early if pkl loaded successfully
            except Exception as e:
                logger.error(f'Failed to load pkl file: {e}')
                print(f'Error loading pkl file: {e}')
                print('Proceeding to fetch data from remote source...')



        with open(pkl_path, 'wb') as f:
            logger.info(f'saved to {f}')
            pickle.dump(self.data, f)
            # try:
            if self.acro == 'GOGET':
            # except AttributeError as e:
                # logger.info(f'{e} Should be attribute error for tuple')
                df_tuple = self.data
                main = df_tuple[0]
                prod_res = df_tuple[1]
                # so you just unpack tuple to list out columns in logs ... maybe not necessary.

                [logger.info (col) for col in main.columns]
                [logger.info (col) for col in prod_res.columns]
                
            else:
                [logger.info (col) for col in self.data.columns]

                


    def get_about(self):
        # this gets the about page for this tracker data
        print(f'Creating about for: {self.off_name}')
        if nostopping == True:
            skipabout = False
        else:
            skipabout = input(f'If you want to skip creating an about page click enter! Otherwise press any other key and then enter!')
            # use_local = input(f'Use local pkl file? (y/n, default=y): ').strip().lower()
            # TODO adjust so can easily press
            # if use_local == 'y' or '':
        if skipabout == False:
            # TODO get clarity on whether the about page comes from this logic below or that centralized doc. centralized doc makes it easier to keep formatting. I think centralized doc is only used for the trackers involved in a regional map that don't have new data release (?)
            # these are the json files like ggit that we need to use its google doc version not geojson version - NOTE the about_key is set manually in the map log google sheet. Need to adjust this to include the three tabs used for pipelines and terminals oye
            
            # I think this logic below is ONLY for map wide about not tracker specific about, or the other way around
            if self.about_key != '':
                tracker_key = self.about_key
            
            # this case is for the normies where we'll loop through their final data dwld file and find the about page
            else:
                tracker_key = self.key
                
            about_df = self.find_about_page(tracker_key)
        
            tracker_official_name = f"{self.off_name}"
            
            if self.tab_name in trackers_to_update:
                # use new date not old one in map log gsheets
                release_month_year = f"{new_release_dateinput.replace('_', ' ')}" 
            else:
                # TODO keep the gsheet up to date by automatic or a test at least
                release_month_year = self.release


            # NEEDS 
            # Copyright © Global Energy Monitor. Global Wind Power Tracker, February 2025 release. Distributed under a Creative Commons Attribution 4.0 International License.
            # Recommended Citation: "Global Energy Monitor, Global Wind Power Tracker, February 2025 release" (See the CC license for attribution requirements if sharing or adapting the data set.)
            print(f'This is release_month_year for {self.off_name}, make sure gsheet tracker log is updated or input better date:\n{release_month_year}')

        
            copyright_full = f"Copyright © Global Energy Monitor. Global {tracker_official_name} Tracker, {release_month_year} release. Distributed under a Creative Commons Attribution 4.0 International License."
            citation_full = f'Recommended Citation: "Global Energy Monitor, Global {tracker_official_name} Tracker, {release_month_year} release" (See the CC license for attribution requirements if sharing or adapting the data set.)'
                            
            print(f'This is copyright_full for {self.off_name}:\n{copyright_full}')
            print(f'This is citation_full for {self.off_name}:\n{citation_full}')
            # TEMP
            # TODO redo this because it is so buggy if there are multiple headers or collapsed cells in about pages (re COAL), create about pages like wiki template
            # currently I manually check the about pages to be sure it all looks ok and fix little things
            
            # if either are not in there fully then insert into the df after first row
            # elif partially in there, delete row and insert
            # else pass
            if copyright_full in about_df.values:
                logger.info(f'Already has full copyright: {copyright_full}')
            elif about_df.apply(lambda row: row.astype(str).str.contains('Copyright').any(), axis=1).any():
                logger.info('Partial copyright, delete row and insert full')
                # Find the row index
                copyright_rows = about_df.apply(lambda row: row.astype(str).str.contains('Copyright').any(), axis=1)
                copyright_row_idx = about_df[copyright_rows].index[0]

                # Replace that entire row with the full copyright
                about_df.iloc[copyright_row_idx] = [copyright_full] * len(about_df.columns)


            else:
                logger.info('Inserting full copyright into second row') 
                # insert a new blank row in the second row
                full_copy_row = pd.DataFrame([[copyright_full] * len(about_df.columns)], columns=about_df.columns)
                # split the existing df in two at the second row, concat full copy row like a sandwich in between
                about_df = pd.concat([about_df.iloc[:1], full_copy_row, about_df.iloc[1:]]).reset_index(drop=True)

            about_df.reset_index(drop=True, inplace=True)

            if citation_full in about_df.values:
                logger.info(f'Already has full citation: {citation_full}')
            elif about_df.apply(lambda row: row.astype(str).str.contains('Recommended Citation').any(), axis=1).any():
                logger.info('Partial citation, delete row and insert full')
                # Find the row index
                citation_rows = about_df.apply(lambda row: row.astype(str).str.contains('Recommended Citation').any(), axis=1)
                citation_row_idx = about_df[citation_rows].index[0]

                # Replace that entire row with the full copyright
                about_df.iloc[citation_row_idx] = [citation_full] * len(about_df.columns)

            else:
                logger.info('Inserting full citation_full into second row') 
                # insert a new blank row in the second row
                full_copy_row = pd.DataFrame([[citation_full] * len(about_df.columns)], columns=about_df.columns)
                # split the existing df in two at the second row, concat full copy row like a sandwich in between
                about_df = pd.concat([about_df.iloc[:1], full_copy_row, about_df.iloc[1:]]).reset_index(drop=True)
            
            about_df.reset_index(drop=True, inplace=True)
            

            about_df = clean_about_df(about_df) 

        
            self.about = about_df
            
        else:
            self.about = 'skipped'
            




    def list_all_contents(self, release):
        
        # TODO REDO this based on standardized file names in s3
        # TODO egt change what gets added so it is JUST the file -- LOOK INTO THIS BEFORE GOGPT RELEASE mid Jan
        # not both: ['egt-term/2025-02/', 'egt-term/2025-02/GEM-EGT-Terminals-2025-02 DATA TEAM COPY.geojson']
        acro = self.acro.lower() # eu, ggit
        name = self.tab_name.lower() # pipelines, terminals, gas        
        logger.info(f'DEBUG {acro} {name} {release}')
        found_data_team_copy_file = False
        list_all_contents = [] # should be one file, if not then we need to remove / update
        # Initialize a session using DigitalOcean Spaces
        session = boto3.session.Session()
        client = session.client('s3',
                    region_name='nyc3',
                    endpoint_url='https://nyc3.digitaloceanspaces.com',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY)

        bucket_name = 'publicgemdata'

        # List all folders (prefixes) for this acro
        paginator = client.get_paginator('list_objects_v2')
        prefix = f'{acro}/'
        folders = set()
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter='/'):
            for common_prefix in page.get('CommonPrefixes', []):
                folder = common_prefix['Prefix'].rstrip('/').split('/')[-1]
                folders.add(folder)

        # Try to parse folder names as dates and find the latest
        date_folders = []
        for folder in folders:
            logger.info(f'This is folders that should be dates of release {folder}')

            date_obj = datetime.strptime(folder, '%Y-%m')
            logger.info(f'This is date obj for folders {date_obj}')
 
            date_folders.append((date_obj, folder))

        sorted_dates = sorted(date_folders, key=lambda x: x[0], reverse=True)
        for date_obj, folder in sorted_dates:
            # Try to find the file in this folder
            # If found, break; if not, continue to 
            # if date_folders:
            # Get the folder with the latest date
            # latest_folder = max(date_folders, key=lambda x: x[0])[1]
            folder_prefix = f'{acro.lower()}/{folder}/'

            # List objects in the latest folder
            response = client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

            # Check if the 'Contents' key is in the response
            if 'Contents' in response:
                for obj in response['Contents']:
                    if 'DATA TEAM COPY' in obj['Key']:
                        logger.info(obj['Key']) # this is name of the file in s3
                        logger.info(f"Using this {acro} and this {name} to look")                   
                        list_all_contents.append(obj['Key'])
                        found_data_team_copy_file = True
                        break # break out of inner loop .. so we end the for loop and don't add more than we need to 
                    else:
                        logger.info(f'DATA TEAM COPY not in file name for {acro} so skipped.')
                if found_data_team_copy_file:
                    # break out of outer loop
                    break
            else:
                print("No files found in the specified folder.")
                # doesn't help when there is a file in there just not the right file
                input(f'LOOK INTO THIS list_all_contents for acro: {acro.lower()} and folder_prefix: {folder_prefix}')
            
        if found_data_team_copy_file == False:
            input(f'We looked in all folders starting from most recent and in none of these folders is there a file that can be used here. Look at the digital ocean folder for {acro} {name}')
    
        return list_all_contents



    def get_file_name(self, release):
        
        path_name_all = self.list_all_contents(release) 
        logger.info(f'this is path_name_all: {path_name_all}')
        
        if len(set(path_name_all)) > 1:
            logger.info(path_name_all)
            for path in path_name_all:
                if release in path:
                    path_name = f'{path}'
                else:
                    path_name = path_name_all[0]
                    logger.warning(f'There are more than 2 so picked first:\n{path_name}')
                    print(f'{path_name}')
                    input('There are more than 2 so picked first:\n{path_name} approved? Hit enter')
                
        # if theres more than two and its not EGT then we need to clean latest folder to remove old
        elif len(set(path_name_all)) == 1:
            path_name = f'{path_name_all[0]}'
            logger.info(f'This is path name: {path_name}')
        else:
            input('Might be an issue with path name look into get_file_name plz!')
        
        encoded_path_name = urllib.parse.quote(path_name)
        logger.info(f'Compare path name: {path_name} to encoded path_name: {encoded_path_name}')
        
        return encoded_path_name
    

    

    def create_df(self, testtracker):
        logger.info('in create_df')
        dfs = []
        if testtracker != '':
            print(f'testracker var in all_config IS NOT EMPTY so we are using TEST INPUT DATA held in key testfilekey!')
            print(f'{testfilekey}')
            print(f'{testtracker}')
            yesusetestinputdata = input(f'CONFIRM that is OK by pressing enter! Or override by pressing any other key!')
            logger.info(f'testracker var in all_config IS NOT EMPTY so we are using TEST INPUT DATA held in key testfilekey!\n {testfilekey} {testtracker}')
            if yesusetestinputdata != '': # if didn't press enter then just use actual map tracker log data from https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1875432780#gid=1875432780 source tab
                testtracker = '' # override testtracker variable
        
        elif self.off_name == 'Iron and Steel':
            
            if testtracker.lower() in ['gist']:
                gsheets = gspread_creds.open_by_key(testfilekey)
                spreadsheet = gsheets.worksheet('Sheet1') # always use this when making test input files
                df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                logger.info(df.info())
                logger.info('Check df info plz')                
            else: 

                for tab in self.tabs:
                    gsheets = gspread_creds.open_by_key(self.key)
                    spreadsheet = gsheets.worksheet(tab)
                    df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    df['tab-type'] = tab
                    dfs += [df]

                df = pd.concat(dfs).reset_index(drop=True)

        else:
            # FOR TESTING QUICKLY 
            if testtracker != '':
                if testtracker.lower() in self.acro.lower():
                    gsheets = gspread_creds.open_by_key(testfilekey)
                    spreadsheet = gsheets.worksheet('Sheet1') # always use this when making test input files
                    df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    logger.info(df.info())
                    logger.info('Check df info plz')     
                
            # NORMAL CASE                    
            else: 

                for tab in self.tabs:

                    gsheets = gspread_creds.open_by_key(self.key)
                    spreadsheet = gsheets.worksheet(tab)
                    df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))

                    dfs += [df]

                df = pd.concat(dfs).reset_index(drop=True)

                logger.info(df.info())
                logger.info('Check df info plz')

        df.columns = df.columns.str.strip() # TODO MOVE THIS TO DATA CLEANING FUNCTION? 
        
        return df
    
    # new for new format from db
     
    def create_df_goget(self):
        # March 2026+ format: separate field-level tabs for main, production, and reserves
        # Old format (pre-2026): 'Main data' + 'Production & reserves' combined tab
        gsheets = gspread_creds.open_by_key(self.key)

        # New format tab names
        new_main_tab = 'Field-level main data'
        new_prod_tab = 'Field-level production data'
        new_res_tab = 'Field-level reserves data'

        # new_main_project_tab = 'Project-level main data'
        # new_prod_project_tab = 'Project-level production data'
        # new_res_project_tab = 'Project-level reserves data'
        project_level_tabs = ['Project-level main data', 'Project-level data production', 'Project-level data reserves']

        # Detect which format we're working with
        available_tabs = [ws.title for ws in gsheets.worksheets()]
        is_new_format = new_main_tab in available_tabs

        if is_new_format:
            logger.info('GOGET: Using new March 2026+ format (field-level tabs)')

            spreadsheet = gsheets.worksheet(new_main_tab)
            main_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            print(main_df.info())
            main_df.columns = main_df.columns.str.strip()

            spreadsheet = gsheets.worksheet(new_prod_tab)
            prod_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            print(prod_df.info())
            prod_df.columns = prod_df.columns.str.strip()

            spreadsheet = gsheets.worksheet(new_res_tab)
            res_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            print(res_df.info())
            res_df.columns = res_df.columns.str.strip()

            # Remap new column names to match what downstream code expects
            main_df.rename(columns={
                'Subnational unit': 'Subnational unit (province, state)',
                'Owner(s)': 'Owner',
                'Parent(s)': 'Parent',
                'Block(s)': 'Concession / block',
                'Wiki URL (field)': 'Wiki URL',
            }, inplace=True)

            # New format has separate prod and reserves tabs — recombine into
            # a single prod_res df matching the old 'Production & reserves' schema
            # so downstream functions (get_most_recent_value_and_year_goget) work unchanged.

            # Production tab: already has Quantity (converted) and Units (converted)
            # Just align column names to match old combined schema
            prod_df.rename(columns={
                'Unit Name': 'Unit name',
                'Data Year': 'Data year',
                'Quantity': 'Quantity (original)',
                'Units': 'Units (original)',
            }, inplace=True)
            prod_df['Production/reserves'] = 'production'

            # Reserves tab: align column names to match old combined schema
            # Old schema had 'Quantity (converted)' and 'Units (converted)' — new reserves tab has those too
            # Old schema had 'Reserves classification (original)' — new has 'Reserves classification'
            # old had 'Quantity (original)', and  'Units (original)', rename Quantity and Units to that
            res_df.rename(columns={
                'Unit Name': 'Unit name',
                'Data Year': 'Data year',
                'Quantity': 'Quantity (original)',
                'Units': 'Units (original)',
                'Reserves classification': 'Reserves classification (original)',
            }, inplace=True)
            res_df['Production/reserves'] = 'reserves'

            # Combine into single df matching old schema
            prod_res_df = pd.concat([prod_df, res_df], ignore_index=True, sort=False)
            
            # now pull project level tabs and concat as a df! 
            # can later pull out prod res by that column prod_res
            # TODO OR just keep sepearte and add each as their own df to tuple ... 
            dd_project_tabs = []
            for tab in project_level_tabs:
                
                spreadsheet = gsheets.worksheet(tab)
                df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                df['tabname'] = tab
                print(df.info())
                df.columns = df.columns.str.strip()
                dd_project_tabs.append(df)            
            
            dd_dfs = pd.concat(dd_project_tabs, sort=False).reset_index(drop=True) 
                        

        else:
            # Old format (pre-2026): 'Main data' + 'Production & reserves'
            logger.info('GOGET: Using old pre-2026 format (Main data + Production & reserves)')
            dd_dfs = 'empty n/a for old format'
            for tab in self.tabs:
                if tab == 'Main data':
                    spreadsheet = gsheets.worksheet(tab)
                    main_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    print(main_df.info())
                    main_df.columns = main_df.columns.str.strip()
                elif tab == 'Production & reserves':
                    spreadsheet = gsheets.worksheet(tab)
                    prod_res_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    print(prod_res_df.info())
                    prod_res_df.columns = prod_res_df.columns.str.strip()

        return main_df, prod_res_df, dd_dfs            

    
    def set_fuel_filter_eu_and_maturity(self):
    # NOT NEEDED ANYMORE   
        if self.acro in ['GOGET', 'GOGPT']:
            df = self.data
            df['fuel-filter'] = 'methane'
            df['maturity'] = 'none'
            self.data = df
            
        elif self.acro == 'EGT-term':

            df = self.data
            df['fuel-filter'] = 'methane'
            df['maturity'] = 'none'
            # df.columns = df.columns.str.lower()
            # df.columns = df.columns.str.replace(' ', '-')
            df['fuel'] = df['Fuel'].str.lower()
            df['fuel-filter'] = np.where((df['fuel'] != 'lng') & (df['fuel'] != 'oil'), 'hy', df['fuel-filter'])
            
            # check if hydrogen first then apply maturity logic
            for row in df.index:
                if df.loc[row, 'fuel-filter'] in ['hy']:
                    df.loc[row, 'maturity'] = np.where((df.loc[row, 'Status'] == 'Construction') | (df.loc[row, 'FIDStatus'] == 'FID') | (df.loc[row, 'AltFuelPrelimAgreement'] == 'yes') | (df.loc[row, 'AltFuelCallMarketInterest'] == 'yes'), 'y','n')

            self.data = df
            
        elif self.acro == 'EGT-gas':
            df = self.data
            # set up default
           ## NONE OF THIS IS NEEDED ANYMORE BECUASE NO HYDROGEN RESEARCH, keep lower and replace in case it's used down the line
            
            # df['fuel-filter'] = 'methane'
            # df['maturity'] = 'none'

            df.columns = df.columns.str.lower()
            df.columns = df.columns.str.replace(' ', '-')
            
            # df['h2%'].fillna('', inplace=True)
            
            # for row in df.index:
            #     if df.loc[row, 'fuel'].lower().strip() == 'hydrogen':
            #         # convert the column to a string after filling na
            #         df.loc[row, 'h2%'] = str(df.loc[row, 'h2%'])
            #         if df.loc[row, 'h2%'] == '100.00%':
            #             df.loc[row, 'fuel-filter'] = 'hy'
            #             df.loc[row, 'maturity'] = np.where((df.loc[row,'status'] == 'Construction') | (df.loc[row,'pci5'] == 'yes') | (df.loc[row,'pci6'] == 'yes'), 'y','n')

            #         elif df.loc[row, 'h2%'] == '':
            #             df.loc[row, 'fuel-filter'] = 'hy'
            #             df.loc[row, 'maturity'] = np.where((df.loc[row,'status'] == 'Construction') | (df.loc[row,'pci5'] == 'yes') | (df.loc[row,'pci6'] == 'yes'), 'y','n')

            #         else:
            #             df.loc[row, 'fuel-filter'] = 'blend'
            #             # TODO for gas pipelines update cahnge this so the cols don't lower by this point, so its' in line with rest of projects
            #             df.loc[row, 'maturity'] = np.where((df.loc[row,'status'] == 'Construction') | (df.loc[row,'pci5'] == 'yes') | (df.loc[row,'pci6'] == 'yes'), 'y','n')

            
            
            self.data = df
        
    
    # def set_maturity_eu(self):
    #     # self.data = maturity(self.data)
    #     # print(set(self.data['maturity'].to_list()))
    #     # count of maturity equal none by tracker
    #     # print(self.trackers[self.trackers['maturity']=='none'][['maturity', 'tracker']].groupby('tracker').count())    
        

    #     df = self.data
            
    #     df['maturity'] = 'none' # starts as none

    #     for row in df.index:
    #         if df.loc[row, 'fuel-filter'] == 'methane':
    #             df.loc[row, 'maturity'] = 'none'
    #         else:
                
    #             if self.tab_name == 'LNG Terminals EU': # can we use acro instead? so egt-term? or is that also affected by using global not eu version?
    #                 # check if hydrogen first then apply maturity logic
    #                 for row in df.index:
    #                     if df.loc[row, 'fuel-filter'] in ['hy']:
    #                         df.loc[row, 'maturity'] = np.where((df.loc[row, 'Status'] == 'Construction') | (df.loc[row, 'FIDStatus'] == 'FID') | (df.loc[row, 'AltFuelPrelimAgreement'] == 'yes') | (df.loc[row, 'AltFuelCallMarketInterest'] == 'yes'), 'y','n')
    #                     else:
    #                         df.loc[row, 'maturity'] = 'none'
                        
    #             elif self.tab_name == 'Gas Pipelines EU':
    #                 for row in df.index:
    #                     if df.loc[row, 'fuel-filter'] in ['hy', 'blend']:                        
    #                         # TODO for gas pipelines update cahnge this so the cols don't lower by this point, so its' in line with rest of projects
    #                         df['maturity'] = np.where((df['status'] == 'Construction') | (df['pci5'] == 'yes') | (df['pci6'] == 'yes'), 'y','n')


        
    #     self.data = df
        

    def process_steel_iron_parent(self):
        
        df = self.data
        # split out the two tab data
        plant_cap_df = df[df['tab-type']=='Plant capacities and status']
        plant_cap_df = plant_cap_df[['Plant ID', 'Status', 'Nominal crude steel capacity (ttpa)', 'Nominal BOF steel capacity (ttpa)', 'Nominal EAF steel capacity (ttpa)', 
                                 'Nominal OHF steel capacity (ttpa)', 'Other/unspecified steel capacity (ttpa)', 'Nominal iron capacity (ttpa)', 'Nominal BF capacity (ttpa)',
                                 'Nominal DRI capacity (ttpa)', 'Other/unspecified iron capacity (ttpa)']]         
        
        plant_df = df[df['tab-type']=='Plant data']  
        plant_df = plant_df[['tab-type', 'Plant ID', 'Plant name (English)', 'Plant name (other language)', 'Other plant names (English)',
                            'Other plant names (other language)', 'Owner', 'Owner (other language)', 'Owner GEM ID', 'Parent', 'Parent GEM ID',
                            'Subnational unit (province/state)', 'Country/Area', 'Coordinates', 'Coordinate accuracy', 'GEM wiki page',
                            'Steel products', 'Main production equipment', 'Start date']]        
        
        print(len(plant_df)) # 1204
        plant_df = plant_df.merge(right=plant_cap_df, on='Plant ID', how='outer')       
        print(len(plant_df)) # 1732 looks correct because multiple rows for each unit 
        print('check on len change')
        
        # now that plant level only let's create capacity for scaling using nominal steel when there iron as backfill
        plant_df['capacity'] = plant_df.apply(lambda row: row['Nominal crude steel capacity (ttpa)'] if pd.notna(row['Nominal crude steel capacity (ttpa)']) else row['Nominal iron capacity (ttpa)'], axis=1)
        
        # status is plant level and indivual in plant status capacity tab
        # first group together all rows with same plant id, and get a new column of all status options in a list
        # then apply make plant level status 
        plant_df_grouped = plant_df.groupby('Plant ID').agg({'Status': list}).reset_index(drop=True) 
        plant_df_grouped = plant_df_grouped.rename(columns={'Status': 'status-list'})               
        plant_df = plant_df.merge(plant_df_grouped, on='Plant ID', how='left')
        plant_df['plant-status'] = plant_df.apply(lambda row: make_plant_level_status(row['status-list'], row['Plant ID']),axis=1)

        # set up prod method tiers with equipment and logic from summary tables

        plant_df['prod-method-tier'] = plant_df.apply(lambda row: make_prod_method_tier(row['Main production equipment'], row['Plant ID']), axis=1)

        list_unit_cap = [
            'Nominal crude steel capacity (ttpa)',
            'Nominal BOF steel capacity (ttpa)', 
            'Nominal EAF steel capacity (ttpa)', 
            'Nominal OHF steel capacity (ttpa)', 
            'Other/unspecified steel capacity (ttpa)', 
            'Nominal iron capacity (ttpa)', 
            'Nominal BF capacity (ttpa)', 
            'Nominal DRI capacity (ttpa)', 
            'Other/unspecified iron capacity (ttpa)',
            'capacity'
        ]
        pd.options.display.float_format = '{:.0f}'.format
        # replace '' with nan for all instances in the list_unit_cap cols
        plant_df[list_unit_cap] = plant_df[list_unit_cap].replace('>0', np.nan)
        plant_df[list_unit_cap] = plant_df[list_unit_cap].replace('N/A', np.nan)
        plant_df[list_unit_cap] = plant_df[list_unit_cap].replace('n/a', np.nan)

        # make all in list_unit_cap rounded to be without decimal places
        plant_df[list_unit_cap] = plant_df[list_unit_cap].applymap(lambda x: round(x, 4) if pd.notna(x) and isinstance(x, (int, float)) else x)
                
        # make new columns with status and prod method capacity
        # rename the columns based on status value and put on same row 
        all_suffixes_check = []
        for row in plant_df.index:
            status_suffix = plant_df.loc[row, 'Status']
            plant_id = plant_df.loc[row, 'Plant ID']
            for col in list_unit_cap:
                if plant_df.loc[row, col] != np.nan:
                    all_suffixes_check.append(status_suffix)
                    new_col_name = f'{status_suffix.capitalize()} {col}'
                    logger.info(new_col_name)
                    plant_df.loc[row, new_col_name] = plant_df.loc[row,col]
                else:
                    logger.info('skip creating new column for this one')
        logger.info(plant_df[plant_df['Plant ID']=='P100000120823'][['Nominal iron capacity (ttpa)', 'Status']])


        logger.info(plant_df.columns)
        logger.info('add cols') #'Main Production Equipment', 'Steel Products',
        # filter out some cols 
        filter_cols = ['tab-type', 'Plant ID', 'Plant name (English)',
        'Plant name (other language)', 'Other plant names (English)',
        'Other plant names (other language)', 'Owner', 'Owner (other language)',
        'Owner GEM ID', 'Parent', 'Parent GEM ID',
        'Steel products', 'Main production equipment',
        'Subnational unit (province/state)', 'Country/Area', 'Coordinates',
        'Coordinate accuracy', 'GEM wiki page', 'Start date','status-list', 'plant-status', 'prod-method-tier', 'capacity', 
        # begins new capacity col by prod type and unit status
        'Operating Nominal crude steel capacity (ttpa)',
        'Operating Nominal EAF steel capacity (ttpa)', 'Operating capacity',
        'Construction Nominal crude steel capacity (ttpa)',
        'Construction Nominal EAF steel capacity (ttpa)',
        'Construction capacity',
        'Operating Nominal BOF steel capacity (ttpa)',
        'Operating Nominal iron capacity (ttpa)',
        'Operating Nominal BF capacity (ttpa)',
        'Announced Nominal crude steel capacity (ttpa)',
        'Announced Nominal EAF steel capacity (ttpa)',
        'Announced Nominal iron capacity (ttpa)',
        'Announced Nominal DRI capacity (ttpa)', 'Announced capacity',
        'Mothballed Nominal iron capacity (ttpa)',
        'Mothballed Nominal BF capacity (ttpa)',
        'Operating Other/unspecified steel capacity (ttpa)',
        'Mothballed Nominal crude steel capacity (ttpa)',
        'Mothballed Nominal EAF steel capacity (ttpa)',
        'Mothballed Nominal DRI capacity (ttpa)', 'Mothballed capacity',
        'Operating Nominal DRI capacity (ttpa)',
        'Announced Other/unspecified steel capacity (ttpa)',
        'Construction Other/unspecified steel capacity (ttpa)',
        'Construction Nominal iron capacity (ttpa)',
        'Construction Nominal DRI capacity (ttpa)',
        'Operating pre-retirement Nominal crude steel capacity (ttpa)',
        'Operating pre-retirement Nominal BOF steel capacity (ttpa)',
        'Operating pre-retirement Nominal iron capacity (ttpa)',
        'Operating pre-retirement Nominal BF capacity (ttpa)',
        'Operating pre-retirement capacity',
        'Announced Nominal BF capacity (ttpa)',
        'Construction Nominal BOF steel capacity (ttpa)',
        'Construction Nominal BF capacity (ttpa)',
        'Announced Nominal BOF steel capacity (ttpa)',
        'Cancelled Nominal crude steel capacity (ttpa)',
        'Cancelled Nominal EAF steel capacity (ttpa)', 'Cancelled capacity',
        'Retired Nominal iron capacity (ttpa)',
        'Retired Nominal BF capacity (ttpa)',
        'Announced Other/unspecified iron capacity (ttpa)',
        'Mothballed Nominal BOF steel capacity (ttpa)',
        'Cancelled Nominal iron capacity (ttpa)',
        'Cancelled Nominal DRI capacity (ttpa)',
        'Retired Nominal crude steel capacity (ttpa)',
        'Retired Nominal BOF steel capacity (ttpa)', 'Retired capacity',
        'Operating pre-retirement Nominal EAF steel capacity (ttpa)',
        'Retired Nominal EAF steel capacity (ttpa)',
        'Cancelled Other/unspecified steel capacity (ttpa)',
        'Cancelled Other/unspecified iron capacity (ttpa)',
        'Retired Nominal OHF steel capacity (ttpa)',
        'Operating Other/unspecified iron capacity (ttpa)',
        'Mothballed Other/unspecified iron capacity (ttpa)',
        'Cancelled Nominal BOF steel capacity (ttpa)',
        'Cancelled Nominal BF capacity (ttpa)',
        'Operating pre-retirement Nominal DRI capacity (ttpa)',
        'Construction Other/unspecified iron capacity (ttpa)',
        'Mothballed Other/unspecified steel capacity (ttpa)',
        'Operating pre-retirement Other/unspecified steel capacity (ttpa)',
        'Mothballed pre-retirement Nominal iron capacity (ttpa)',
        'Mothballed pre-retirement Nominal BF capacity (ttpa)',
        'Operating pre-retirement Other/unspecified iron capacity (ttpa)',
        'Operating Nominal OHF steel capacity (ttpa)',
        'Mothballed Nominal OHF steel capacity (ttpa)']
        plant_df = plant_df[filter_cols]
        plant_df_grouped = plant_df.groupby('Plant ID').agg({
            'tab-type': 'first',
            'Plant name (English)': 'first',
            'Plant name (other language)': 'first',
            'Other plant names (English)': 'first',
            'Other plant names (other language)': 'first',
            'Owner': 'first',
            'Owner (other language)': 'first',
            'Owner GEM ID': 'first',
            'Parent': 'first',
            'Parent GEM ID': 'first',
            'Subnational unit (province/state)': 'first',
            'Country/Area': 'first',
            'Coordinates': 'first',
            'Coordinate accuracy': 'first',
            'GEM wiki page': 'first',
            'Main production equipment': 'first', 
            'Steel products': 'first',
            'Start date': 'first',
            'status-list': 'first',
            'plant-status': 'first',
            'prod-method-tier': 'first',
            'capacity': 'sum',
            'Operating Nominal EAF steel capacity (ttpa)': 'sum',
            'Construction Nominal EAF steel capacity (ttpa)': 'sum',
            'Operating Nominal BOF steel capacity (ttpa)': 'sum',
            'Operating Nominal BF capacity (ttpa)': 'sum',
            'Announced Nominal EAF steel capacity (ttpa)': 'sum',
            'Announced Nominal DRI capacity (ttpa)': 'sum',
            'Mothballed Nominal BF capacity (ttpa)': 'sum',
            'Operating Other/unspecified steel capacity (ttpa)': 'sum',
            'Mothballed Nominal EAF steel capacity (ttpa)': 'sum',
            'Mothballed Nominal DRI capacity (ttpa)': 'sum',
            'Operating Nominal DRI capacity (ttpa)': 'sum',
            'Announced Other/unspecified steel capacity (ttpa)': 'sum',
            'Construction Other/unspecified steel capacity (ttpa)': 'sum',
            'Construction Nominal DRI capacity (ttpa)': 'sum',
            'Operating pre-retirement Nominal BOF steel capacity (ttpa)': 'sum',
            'Operating pre-retirement Nominal BF capacity (ttpa)': 'sum',
            'Announced Nominal BF capacity (ttpa)': 'sum',
            'Construction Nominal BOF steel capacity (ttpa)': 'sum',
            'Construction Nominal BF capacity (ttpa)': 'sum',
            'Announced Nominal BOF steel capacity (ttpa)': 'sum',
            'Cancelled Nominal EAF steel capacity (ttpa)': 'sum',
            'Retired Nominal BF capacity (ttpa)': 'sum',
            'Mothballed Nominal BOF steel capacity (ttpa)': 'sum',
            'Cancelled Nominal DRI capacity (ttpa)': 'sum',
            'Retired Nominal BOF steel capacity (ttpa)': 'sum',
            'Operating pre-retirement Nominal EAF steel capacity (ttpa)': 'sum',
            'Retired Nominal EAF steel capacity (ttpa)': 'sum',
            'Cancelled Other/unspecified steel capacity (ttpa)': 'sum',
            'Retired Nominal OHF steel capacity (ttpa)': 'sum',
            'Cancelled Nominal BOF steel capacity (ttpa)': 'sum',
            'Cancelled Nominal BF capacity (ttpa)': 'sum',
            'Operating pre-retirement Nominal DRI capacity (ttpa)': 'sum',
            'Mothballed Other/unspecified steel capacity (ttpa)': 'sum',
            'Operating pre-retirement Other/unspecified steel capacity (ttpa)': 'sum',
            'Mothballed pre-retirement Nominal BF capacity (ttpa)': 'sum',
            'Operating Nominal OHF steel capacity (ttpa)': 'sum',
            'Mothballed Nominal OHF steel capacity (ttpa)': 'sum'
        }).reset_index(drop=True)
        

        # remove decimal point in all capacity values
        for col in plant_df_grouped.columns:
            if 'capacity (ttpa)' in col:
                plant_df_grouped[col] = plant_df_grouped[col].apply(lambda x: str(x).split('.')[0])

        
        logger.info(len(plant_df_grouped))
        plant_df_grouped = plant_df_grouped.drop_duplicates(subset='Plant ID')
        logger.info(len(plant_df_grouped))
        logger.info('pause and check drop worked 1204') # woo worked!        
        
        logger.info(plant_df_grouped.info())
        logger.info('Check on column names in plant_df_grouped for gist lat lng??')

        self.data = plant_df_grouped   
        
    def gist_changes(self):
        df = self.data
        df = split_coords(df)
        # rename in old version ... when does that happen here? happens after all this ... 
        # df = make_numerical(df, ['current-capacity-(ttpa)', 'plant-age-(years)']) # not needed will use clean_num_data later
        df = fix_status_space(df)
        df = fix_prod_type_space(df)
        self.data = df                

    def giomt_changes(self):
        df = self.data
        
        df[['Latitude', 'Longitude']] = df['Coordinates'].str.split(', ', expand=True)
        df[['Latitude', 'Longitude']] = df['Coordinates'].str.split(',', expand=True) # qc test

        self.data = df 

    def gchi_changes(self):
        
        df = self.data
        # filler for now so all assets are sized the same
        df['capacity'] = 30.0
        df['status'] = 'operating'
        df[['Latitude', 'Longitude']] = df['Coordinates'].str.split(', ', expand=True)
        df[['Latitude', 'Longitude']] = df['Coordinates'].str.split(',', expand=True) # qc test

        self.data = df        


    def gmet_changes(self):
        
        df = self.data
        
        # debug the 0 roudning thing for emissions if op for lng terminals 
        # print(set(df['emissions-terminals'].to_list()))
        # input('double check emissions temrinal data not rounding in file')
 
        df['legend-filter'] = df['tab-type']
        df['legend-filter'] = df['legend-filter'].apply(lambda x: x.replace(' ', '-'))
        
        # print(len(df))
        # print(set(df['legend-filter'].to_list()))
        
        # print(df['legend-filter'])
        # input('check legend filter')
      
        # rename
        # ALSO seperate out lng import and export 
        # inportExport
        # filter by import export and set tracker-custom to it
        lenbef = len(df)
        # print(f'all unique of inportexport col: {set(df["inportExport"])}')
        importdf = df[df['inportExport']=='Import'].copy()
        importdf['legend-filter'] = 'lng-import'
        exportdf = df[df['inportExport']=='Export'].copy()
        exportdf['legend-filter'] = 'lng-export'
        na_imex = df[~df['inportExport'].isin(['Import', 'Export'])].copy()

        
        df = pd.concat([importdf, exportdf, na_imex], ignore_index=True)
        lenaf = len(df)
        input(f'Check that length is same before and after: \n before {lenbef}\n after{lenaf}')
        # goget consolidation
        # if tab-type in ['extraction','reserves']:
        # create dfs for each tab
        # on goget id merge
        # deduplicate on goget id
        lenbef = len(df)
        goget_main = df[df['tab-type'] == 'Oil and Gas Extraction Areas'].copy()
        goget_res = df[df['tab-type'] == 'Oil and Gas Reserves'].copy()
        rest = df[df['tab-type'].isin(['Plumes', 'Coal Mines - Non-closed', 'Pipelines', 'LNG Terminals'])].copy()
        print(f'Len goget_main {len(goget_main)} and goget_res {len(goget_res)} is {len(goget_main) + len(goget_res)}')

        # remove columns not needed
        goget_main = goget_main[['legend-filter','tab-type','operator', 'areas', 'status', 'geometry', 'pid','name', 'status_year', 'url']]
        # operator, status, country, lat lng, id  from main
        goget_res = goget_res[['tonnes-goget-reserves_emissions', 'pid']]
        # Emissions for whole reserves with latest emissions factors (tonnes) from reserves from reserves
        
        # on goget id merge - keep only first occurrence of each pid since all are duplicates
        goget_res = goget_res.drop_duplicates(subset=['pid'], keep='first')
        
        # merge reserves data into main on pid
        goget = goget_main.merge(goget_res, on='pid', how='left')
        print(f'Len goget after merge left, should be just same as goget_main {len(goget_main)} above: {len(goget)}')
        # deduplicate on goget id (no need because merged...)       
        # input(f'Check length of goget ok after merging')
        # while goget tabs are separate we add in the infra release date col 

        # hardcode in dates of release direct ask from Sarah due to user confusion with ggit release dates
        # this should not be hardcoded in the future :/  
        goget_date_hardcode = "Data drawn from GEM Global Oil and Gas Extraction Tracker February 2025 release"
        coalmine_date_hardcode = "Data drawn from GEM Global Coal Mine Tracker May 2025 release"
        pipelines_date_hardcode = "Data drawn from GEM Global Gas Infrastructure Tracker December 2024 release"
        lng_date_hardcode = "Data drawn from GEM Global Gas Infrastructure Tracker September 2024 release"
       
        goget['release_date_infra'] = goget_date_hardcode
        # then handle rest
        for row in rest.index:
            if rest.loc[row, 'tab-type'] == 'Coal Mines - Non-closed':
                rest.loc[row, 'release_date_infra'] = coalmine_date_hardcode
            elif rest.loc[row, 'tab-type'] == 'Pipelines':
                rest.loc[row, 'release_date_infra'] = pipelines_date_hardcode
            elif rest.loc[row, 'tab-type'] == 'LNG Terminals':
                rest.loc[row,'release_date_infra'] = lng_date_hardcode

        df = pd.concat([rest, goget])
        

        
        lenaf = len(df)
        
        # input(f'Check that length is same before and after goget: \n before {lenbef}\n after{lenaf}')
    
        # consolidate statuses
                
        # check corresponding infra to show hyperlinked wiki 
        # for plume data only, if infra wiki is not '', then add this line of markup
        # for all plume data, add the carbon mapper liscense
        # just in js make it so it shows up if notempty nah
        # make a new column, string with infra map link and sentence around it markdown
        # add col for all plumes, col called, carbon mapper string   
        df['carbon-mapper-md'] = df.apply(
            lambda row: 'Plume Data © Carbon Mapper. Subject to terms https://carbonmapper.org/terms'
            if row['tab-type'] == 'Plumes'
            else '', 
            axis=1
        )
 
        # change this so that tab-type is not plumes and plume data exists and infrawiki not empty but wouldn't be
        # So for "Kern Front - California Resources Productionoration" goget asset, we'd have the text and link to the infra wiki 
        # https://www.gem.wiki/Kern_Front_-_California_Resources_Productionoration_Oil_and_Gas_Asset_(California,_United_States)
        
        # Only coal mines have the "has associated plume data column" so for the rest 
        # we'd have to use the "GEM Infrastructure Wiki" column (and inverse it) to see which GEM assets have plumes associated with them.

        # I think we should create a new column that is like "plume-associated"
        # if geminfrawiki is not blank 
            # then look up name associated with geminfrawiki value match on gemwiki
            # that is the name that needs this infra-wiki-md data
        lendfbefore = len(df)
        plumesdf = df[df['tab-type']=='Plumes'].copy().reset_index(drop=True)
        coalminesdf = df[df['tab-type']=='Coal Mines - Non-closed'].copy().reset_index(drop=True)
        restdf = df[~df['tab-type'].isin(['Coal Mines - Non-closed', 'Plumes'])].copy().reset_index(drop=True)
        # list of wikis from plumes tab
        infrawithplumeswiki = set(plumesdf[plumesdf['geminfrawiki'].notna() & (plumesdf['geminfrawiki'] != '')]['geminfrawiki'].to_list())
        # print(infrawithplumeswiki) # this is from plumnes column, unfortunately the coal mine wikis are inconsistently in there as mandarin and english. 
        # print(f'len of infrawithplumeswiki: {len(infrawithplumeswiki)}') # 267
        # input('log # of infrawithplumeswiki from plumesdf') 
        # first go through coalmine because special because China coal mines in mandarin
        for row in coalminesdf.index:
            if coalminesdf.loc[row, 'Has associated plume data'] == 'Yes':
                coalminesdf.loc[row, 'plume-associated'] = True
            else:
                coalminesdf.loc[row, 'plume-associated'] = False
        # so now loop through that set in restdf and see if there is a match on the normal wiki col, if so then assign plumeassociated = true
        for row in restdf.index:
            if restdf.loc[row, 'url'] in infrawithplumeswiki:
                restdf.loc[row, 'plume-associated'] = True
            else:
                restdf.loc[row, 'plume-associated'] = False
                
        coalminesdf['plume-associated'] = coalminesdf['plume-associated'].fillna(False)
        restdf['plume-associated'] = restdf['plume-associated'].fillna(False)
        plumesdf['plume-associated'] = False
        df = pd.concat([plumesdf, restdf, coalminesdf], ignore_index=True)
        # then concat back together    
        # print(f'This is length of df: {len(df)}')
        # input(f'check number of df after concat, should be same as {lendfbefore}') # pass 20261
        
        # testplumassociated = df[df['plume-associated']==True]
        # print(f'length of plume associated for test should be 267 {len(testplumassociated)}') # 258 not 267 ok for now
        # input('log # for plume associated')

        df['infra-wiki-md'] = df.apply(
            lambda row: f'This asset has a methane plume associated with it: see the infrastructure wiki for more details\n{row["url"]}'
            if row['plume-associated'] == True
            else '',
            axis=1        
        )
        
        # round emissions and capcaity 
        # replace empty start year with ''
        
        lenbef = len(df)
        # split attribution out for Plumes  For map only (has attribution information)
        attrib = df[df['infra-filter']=='has attribution data'].copy()
        attrib['legend-filter'] = 'plumes-attrib'
        no_attrib = df[df['infra-filter']=='no atttribution data'].copy()
        no_attrib['legend-filter'] = 'plumes-unattrib'
        na_attrib = df[~df['tab-type'].isin(['Plumes'])]

        
        df = pd.concat([attrib, no_attrib, na_attrib])
        lenaf = len(df)
        input(f'Check that length is same before and after: \n before {lenbef}\n after{lenaf}')
        # make id for link field - maybe just with index, just use PID DONE I think
        # handle multiple countries DONE
        # create scaling col for Plume emissions all other same DONE  
        # Deal with scaling / creating fake capacity! DONE
        print(f'this is length of df bf {len(df)}')
        plume_df = df[df['tab-type'] == 'Plumes'].copy()
        print(f'this is length of df af {len(df)}')
        plume_df.fillna('', inplace=True) 
        # print(plume_df.columns)
        # print(plume_df['plume_emissions'])
        # print(set(plume_df['plume_emissions'].to_list()))

        # to get scaling size for plume circles when there is no emissions data getting average of emissions for plume projects 
        tempplume_emissions = plume_df[plume_df['plume_emissions']!= ''].copy()
        tempplume_emissions['plume_emissions'] = tempplume_emissions['plume_emissions'].apply(lambda x: round(x, 2))
        
        plume_tot_emissions = tempplume_emissions['plume_emissions'].astype(float).sum()  
        plume_projects = len(plume_df)
        plume_emissions_avg = plume_tot_emissions / plume_projects
        # print(f"Sum of plume emissions: {plume_tot_emissions}")
        # print(f"Number of plume projects: {plume_projects}")
        # print(f"Average plume emissions: {plume_emissions_avg}")
        
        # if there is no plume emissions then use average otherwise use plume emissions ... 
        non_plume_df = df[df['tab-type'] != 'Plumes'].copy()

        non_plume_df['capacity'] = plume_emissions_avg
        # if no emissions for plume fill in avg for scaling capacity purposes
        plume_df['capacity'] = plume_df['plume_emissions'].fillna('').replace('', plume_emissions_avg)

        # make it round to 2
        plume_df['plume_emissions'] = plume_df['plume_emissions'].apply(lambda x: round(float(x), 2) if x != '' and x != 'nan' else x)
        # make it round to 2
        plume_df['emission_uncertainty'] = plume_df['emission_uncertainty'].apply(lambda x: round(float(x), 2) if x != '' and x != 'nan' else x)
        
        # concat them back 

        df = pd.concat([non_plume_df, plume_df], sort=False).reset_index(drop=True)
        df['capacity'] = df['capacity'].fillna('')
        
        for row in df.index:
            if df.loc[row, 'capacity'] == '':
                df.loc[row, 'capacity'] = plume_emissions_avg      
        
        # print(df['legend-filter'])
        # input('check legend filter')
        
        # carbonmapper asked for the coordinates look up feature, we'll make a new column called coordsearch 
        # this will be just the lat, long in the format Sarah said most users would be pasting them in
        # so example -24.15411438, 149.8027197
        # remove space? 
        # concat lat, lng
        # df['coordssearch'] = df.apply(lambda row: (row['Longitude'], row['Latitude']), axis=1)
        # print(df['coordssearch'])
        # input(f'Check coordssearch temporary solution based on carbonmapper request, should do handling of search input terms.')
        
        self.data = df
    
    def gspt_changes(self):
        df = self.data
        print(df.columns.tolist())
        if 'Technology Type' in df.columns.tolist():
            df['Technology Type-table'] = df['Technology Type']
            df['Technology Type'] = df['Technology Type'].apply(lambda x: str(x).lower().replace(' ', '_'))
        
        else:
            input("technology type uppercase not in df cols for solar TEMP")
        
        self.data = df 
        
    def gwpt_changes(self):
        df = self.data
        if 'Installation Type' in df.columns.tolist():
            df['Installation Type-table'] = df['Installation Type']

            df['Installation Type'] = df['Installation Type'].apply(lambda x: str(x).lower().replace(' ', '_').replace('<na>', 'unknown'))
        else:
            input("installation type uppercase not in df cols for wind TEMP")
        # check statuses for na 
        print(set(df['Installation Type'].tolist()))
        # input(f'The set of statuses for wind at gwpt_changes')
        self.data = df 
        

    def gcct_changes(self):
            # before renaming 
            # before clean_num_data()
            # before transform_to_gdf()
            df = self.data

            # split out coords to be lat, lng 
            # 'Latitude', 'Longitude',
            df[['Latitude', 'Longitude']] = df['Coordinates'].str.split(', ', expand=True)

            df['capacity'] = df['Cement Capacity (millions metric tonnes per annum)']

            # Use Clinker Capacity where Capacity is missing or null
            df['capacity'] = df['capacity'].fillna(df['Clinker Capacity (millions metric tonnes per annum)'])

            # in capacity replace unknown with not found and preserve >0 by copying over to another column
            df['capacity'].replace('unknown', 'not found', inplace=True)

            df['capacity-display'] = df['capacity']

            # adjust capacity so scaling works 
            df['capacity'].replace('not found', '', inplace=True)
            df['capacity'].replace('n/a', '', inplace=True)
            df['capacity'].replace('>0', .008, inplace=True)

            # remove unknown from color, claycal-yn, altf-yn, ccs-yn, prod-type, plant-type
            cols_no_unknown = ['Production type', 'Plant type', 'Cement Color', 'Clay Calcination', 'Alternative Fuel', 'CCS/CCUS', 'Start date', 'Cement Capacity (millions metric tonnes per annum)']
            for col in cols_no_unknown:
                df[col] = df[col].replace('unknown', '')
                logger.info(set(df[col].to_list()))
                logger.info('check no unknown')

            self.data = df 

    def find_about_page(self,key):
            logger.info(f'this is key and tab list in def find_about_page(tracker, key):function:\n{self.off_name} {key}')            
            # tracker = self.acro
            official_name = self.off_name

        
        # TODO decide to only pull from template file if pipelines? or is it ok for regional downloads to create like template
        # OR decide to paste in new about page every release so regional pulls from correct one
        # if we do this then we do not need the citation and copyright check...
        
            # check if the release date should be the current one or pulled from the tracker object / release column in map log
            if official_name in trackers_to_update:
                release = new_release_dateinput
                release_mon = release.split('_')[0]
                release_yr = release.split('_')[1]
            else:
                release = self.release
                release_mon = release.split(' ')[0]
                release_yr = release.split(' ')[1]

            # go to the about sheet template and if the self name has a non empty tab then use that
            # WOOT new better way! Like wiki template
            
            # about_gsheets = gspread_creds.open_by_key(about_templates_key)
            # for sheet in about_gsheets.worksheets():
            #     logger.info(sheet.title)
            #     if self.tab_name in sheet.title:
            #         logger.info(f'Found template for {self.tab_name}!')
            #         data = pd.DataFrame(sheet.get_all_values(combine_merged_cells=True))
            #         if len(data) > 1:
                        
            #             about_df = data.copy()
            #             # find replace  {RELEASE NON NUMERICAL MONTH} {RELEASE YEAR} with release_mon release_yr
            #             about_df = about_df.applymap(lambda x: str(x).replace('{RELEASE NON NUMERICAL MONTH}', release_mon).replace('{RELEASE YEAR}', release_yr).replace('{FULL TRACKER NAME}', self.off_name))
            #             return about_df
            #         else:
            #             input(f'Appears to be empty... so moving on to old way of getting about page for {self.tab_name}')
            #             logger.info('Appears to be empty... so moving on to old way')

            # else go through this search
            
            # wait_time = 10
            # data = None # initialize
            # gsheets = gspread_creds.open_by_key(key)
                
            # # List all sheet names
            # sheet_names = [sheet.title for sheet in gsheets.worksheets()]
            # # Access a specific sheet by name
            # first_tab = sheet_names[0]
            # first_sheet = gsheets.worksheet(first_tab)  # Access the first sheet
            
            # last_tab = sheet_names[-1]
            # last_sheet = gsheets.worksheet(last_tab)  # Access the last sheet
            # tries = 0
            # about_df = None  # Initialize about_df
            # while tries <= 10:
            #     time.sleep(wait_time)
            #     try:
            #         logger.info(f"First sheet name:{first_sheet.title}")
            #         if 'About' not in first_sheet.title:
            #             logger.info('Looking for about page in last tab now, first one no.')
            #             # handle for goget and ggit, goit who put it in the last tab
            #             if 'About' not in last_sheet.title:
            #                 if 'Copyright' not in last_sheet.title:
            #                     logger.info('Checked first and last tab, no about page found not even for copyright. Pausing.')
            #                     logger.info("Press Enter to continue...")
            #                 else:
            #                     logger.info(f'Found about page in last tab: {last_tab}')
            #                     sheet = last_sheet
                                
            #             else:
            #                 logger.info(f'Found about page in last tab: {last_tab}')
            #                 sheet = last_sheet
                            
            #         else:
            #             # print(f'Found about page in first tab: {first_tab}')
            #             sheet = first_sheet
                        
            #         if len(sheet) > 1:
                        
            #             data = pd.DataFrame(sheet.get_all_values(combine_merged_cells=True))
            #         else:
            #             print(f'this is sheet it is empty: {sheet}')
                    

            #         about_df = data.copy()
            #         return about_df
            #     except HTTPError as e:
            #         print(f'This is error: \n{e}')
            #         wait_time += 5
            #         tries +=1
        
            return about_df

    def create_filtered_geo_fuel_df(self, geo, fuel):
        needed_geo = geo_mapping[geo]
        logger.info(f'length of self.data: {len(self.data)}')
        if self.acro != 'GOGET':
            geocollist = self.geocol.split(';')
            logger.info(f'Getting geo: {geo} from col list: {geocollist} for {self.acro}')
               
            if geo != ['global'] or geo != ['']:
                if len(geocollist) > 1:
                    self.data.columns = self.data.columns.str.strip()

                    logger.info('do multi-column search')
                    self.data['country_to_check'] = [[] for _ in range(len(self.data))]
                    for row in self.data.index:
                        for col in geocollist:
                            if col in self.data.columns:
                                self.data.at[row, 'country_to_check'] += [self.data.at[row, col]] # issue

                            else:
                                print(f'{col} geo col not in df for {self.tab_name}')
          
                    filtered_df = self.data[self.data['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                    self.data = filtered_df

                else:
                    if self.geocol in self.data.columns:
                        self.data['country_to_check'] = self.data[self.geocol].apply(lambda x: split_countries(x) if isinstance(x, str) else [])
                    else:
                        print(f"Column '{self.geocol}' not found in data for {self.tab_name}.")
                        [print(col) for col in self.data.columns]
                        input(f"Column '{self.geocol}' not found in data for {self.tab_name}. Update map tracker log gsheet please.")

                    filtered_df = self.data[self.data['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                    self.data = filtered_df

            if fuel != ['none']:
                filtered_df = create_filtered_fuel_df(filtered_df, self)
                self.data = filtered_df
            
            else:

                logger.info(f"Length of df for normal case: {len(self.data)}")

        
        elif self.acro == 'GOGET':
            print(f'This is tuple for goget: {self.data}')
            main, prod, dd_dfs = self.data  # TO DO Unpack the tuple # should we prepare for all 6 tabs? 
            to_merge = []
            # fueldf = None
            for df in [main, prod]:
                df.columns = df.columns.str.strip()
                df['country_to_check'] = df[self.geocol].apply(lambda x: split_countries(x) if isinstance(x, str) else [])
                
                if geo != ['global'] or geo != ['']:
                    print(f'geo not global or empty so filters via needed geo')
                    df = df[df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                if fuel != ['none']:
                    if self.fuelcol in df.columns:
                        fueldf = create_filtered_fuel_df(df, self)
                        to_merge.append(fueldf)
                    else:
                        to_merge.append(df)
                else:
                    to_merge.append(df)
            
            filtered_main = to_merge[0] # if there is a fuel filter this main would already be filtered since its the one with fuelcol
            filtered_prod = to_merge[1]
                                               
            if fuel != ['none']:
                # creates list of unit ids only on correct fuel type
                # then filter
                gas_goget_ids = fueldf['Unit ID'].to_list()
                filtered_prod = to_merge[1] # already filtered by fuel because in this case it IS fueldf
                logger.info(f'Yes {fueldf} == {filtered_main}')
                logger.info(f'length filtered main: {len(filtered_main)}')
                logger.info(f' lenght fueldf {len(fueldf)}')
                logger.info('check if length the same for fueldf and filtered main in yes fuel option')
                filtered_prod = filtered_prod[filtered_prod['Unit ID'].isin(gas_goget_ids)]

            
            else:
                logger.info('no fuel filter needed')
            
            # apply same filtering to rest of dfs.. project level for data downlaods     
            if isinstance(dd_dfs, pd.DataFrame):
                dd_dfs.columns = dd_dfs.columns.str.strip()
                dd_dfs['country_to_check'] = dd_dfs[self.geocol].apply(lambda x: split_countries(x) if isinstance(x, str) else []) 
                filtered_dd_dfs = dd_dfs[dd_dfs['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                if fuel != ['none'] and self.fuelcol in dd_dfs.columns:
                    filtered_dd_dfs = create_filtered_fuel_df(filtered_dd_dfs, self)
            self.data = (filtered_main, filtered_prod, filtered_dd_dfs)
            
        # elif self.acro == 'GOGPT-eu':
        #     logger.info('Pass for gogpt eu')
            
        else:
            logger.info('Nothing should be printed here, length of df is 1 or 2 if its goget tuple')
            logger.info('Check create_filtered_geo_df')

    def clean_cat_data(self):
        """
        Comprehensive cleaning for categorical (non-numeric) data entered by humans.
        Handles whitespace, case issues, null variations, and validates data quality.
        """

        if not isinstance(self.data, pd.DataFrame):
            logger.info("Error: 'self.data' is not a DataFrame. And should be even for GOGET since it has special handling now.")
            
            logger.info(msg=f"Error:'self.data' is {type(self.data).__name__}: {repr(self.data)}")
            input('self.data is not in a dataframe')
            return

        cleaning_issues = []  # Track issues for reporting

        # Define columns to skip (numeric columns handled elsewhere)
        numeric_keywords = ['CapacityInMtpa', 'Capacity (MW)', 'Capacity (Mt)', 'Capacity (Mtpa)',
                          'CapacityBcm/y', 'CapacityBOEd', 'Capacity (MT)', 'Production - Gas',
                          'Production - Oil', 'Production (Mt)', 'Production (Mtpa)', 'Capacity (ttpa)',
                          'Latitude', 'Longitude', 'year']

        # Iterate through each column
        for col in self.data.columns:
            # Skip numeric columns and geometry and helper col like country_to_check
            if col in ['geometry', 'country_to_check'] or any(keyword in col for keyword in numeric_keywords):
                continue

            # Skip if column is not object/string type
            if self.data[col].dtype not in ['object', 'string']:
                continue

            logger.info(f"Cleaning categorical column: {col}")
            original_unique_count = self.data[col].nunique() # unhashable type list uniques = table.unique(values)

            # Convert to string for consistent processing
            self.data[col] = self.data[col].astype(str)

            # 1. Handle null variations BEFORE other operations
            null_variations = ['nan', 'NaN', 'None', 'N/A', 'NA', 'n/a', 'null', 'NULL',
                             '-', '--', '?', 'unknown', 'Unknown', 'UNKNOWN', '*', '']
            self.data[col] = self.data[col].replace(null_variations, np.nan)
            self.data[col] = self.data[col].fillna('')

            # 2. Strip whitespace (leading/trailing/multiple internal spaces)
            self.data[col] = self.data[col].str.strip()
            self.data[col] = self.data[col].str.replace(r'\s+', ' ', regex=True)  # Multiple spaces to single

            # 3. Remove non-printable characters (tabs, newlines, etc.)
            self.data[col] = self.data[col].str.replace(r'[\t\n\r\f\v]', ' ', regex=True)

            # 4. Handle case inconsistencies for likely categorical columns
            # Keep original case for proper nouns (countries, names, etc.)
            # HOLD OFF TO DO HAVE CLASS OBJECT FOR ALL COLUMN RENAMING IS DONE
            # if col in ['Status', 'Fuel', 'Fuel type', 'FacilityType']:
            #     # Standardize case for status-like fields
            #     before_case = self.data[col].copy()
            #     self.data[col] = self.data[col].str.title()
            #     changed = (before_case != self.data[col]) & before_case.notna()
            #     if changed.sum() > 0:
            #         logger.info(f"  Standardized case for {changed.sum()} entries in {col}")

            # 5. Length validation - flag suspiciously short or long entries
            if col not in ['Country/Area', 'Subnational unit (province, state)', 'GEM wiki page', 'Wiki URL']:
                # Check for very short entries (< 2 chars) - might be data entry errors
                short_entries = self.data[self.data[col].str.len() < 2][col]
                if len(short_entries) > 0:
                    cleaning_issues.append({
                        'column': col,
                        'issue_type': 'short_entry',
                        'count': len(short_entries),
                        'examples': short_entries.unique()[:5].tolist()
                    })
                    logger.warning(f"  Found {len(short_entries)} suspiciously short entries in {col}")

                # Check for very long entries (> 200 chars) - might be concatenated data
                long_entries = self.data[self.data[col].str.len() > 200][col]
                if len(long_entries) > 0:
                    cleaning_issues.append({
                        'column': col,
                        'issue_type': 'long_entry',
                        'count': len(long_entries),
                        'examples': [str(x)[:50] + '...' for x in long_entries.unique()[:3].tolist()]
                    })
                    logger.warning(f"  Found {len(long_entries)} suspiciously long entries in {col}")

            # 6. Check for numeric contamination in text fields
            if col not in ['Unit ID', 'Plant ID', 'Owner GEM ID', 'Parent GEM ID']:
                # Check for entries that are purely numeric when they shouldn't be
                numeric_pattern = r'^\d+$'
                numeric_entries = self.data[self.data[col].str.match(numeric_pattern, na=False)][col]
                if len(numeric_entries) > 0:
                    cleaning_issues.append({
                        'column': col,
                        'issue_type': 'unexpected_numeric',
                        'count': len(numeric_entries),
                        'examples': numeric_entries.unique()[:5].tolist()
                    })
                    logger.warning(f"  Found {len(numeric_entries)} purely numeric entries in {col}")

            # 7. Check for entries with only whitespace after cleaning
            whitespace_only = self.data[self.data[col].str.isspace()][col]
            if len(whitespace_only) > 0:
                self.data.loc[self.data[col].str.isspace(), col] = np.nan
                logger.info(f"  Replaced {len(whitespace_only)} whitespace-only entries with NA in {col}")

            # 8. Log significant changes in unique value count
            new_unique_count = self.data[col].nunique()
            if original_unique_count != new_unique_count:
                reduction = original_unique_count - new_unique_count
                logger.info(f"  Reduced unique values in {col} from {original_unique_count} to {new_unique_count} ({reduction} duplicates cleaned)")
                cleaning_issues.append({
                    'column': col,
                    'issue_type': 'duplicates_cleaned',
                    'original_unique': original_unique_count,
                    'new_unique': new_unique_count,
                    'reduction': reduction,
                    
                })

        # Save cleaning issues report
        if cleaning_issues:
            issues_df = pd.DataFrame(cleaning_issues)
            issues_path = f'{logpath}categorical_cleaning_issues_{self.acro}_{releaseiso}_{iso_today_date}.csv'
            issues_df.to_csv(issues_path, index=False)
            logger.info(f"Saved categorical cleaning issues report to {issues_path}")

        logger.info(f"Completed categorical data cleaning for {self.acro}")
        
    
    def clean_num_data(self):
        """
        Clean and validate numerical data in the DataFrame.
        This method processes the DataFrame (self.data) to clean and standardize numerical columns
        including capacity, production, year, and coordinate data. It performs the following operations:
        - Capacity/Production columns: Converts to numeric, replaces common non-numeric placeholders
          with NaN, and rounds to 4 decimal places.
        - Year columns: Converts to numeric (coercing errors to NaN), then converts to integers,
          handling empty strings appropriately.
        - Latitude/Longitude columns: Converts to numeric, validates against acceptable ranges
          (-90 to 90 for latitude, -180 to 180 for longitude), and removes rows with missing or
          out-of-range coordinates.
        Rows with missing coordinates are logged and exported to a CSV file for review.
        Raises:
            TypeError: Caught and logged for problematic columns, with warnings to check QC PM reports.
        Note:
            When pd.to_numeric() is called with errors='coerce', any data point that cannot be
            converted to numeric will be replaced with NaN (Not a Number). This includes invalid
            strings, empty values, and malformed data. Subsequent processing (rounding, range checks,
            etc.) will treat these NaN values according to the logic in those steps, potentially
            resulting in rows being dropped if coordinates are NaN.
        """
        # clean df
        logger.info(f'Length of df at clean num data: {len(self.data)}')
        logger.info('CHECK ITS NOT EMPTY') #working
        missing_coordinate_row = {} 
        acceptable_range = {
            'lat': {'min': -90, 'max': 90},
            'lng': {'min': -180, 'max': 180}
        }
        
        if isinstance(self.data, pd.DataFrame):  # Ensure self.data is a DataFrame
            
            for col in self.data.columns: # handling for all capacity, production, 
                if any(keyword in col for keyword in ['CapacityInMtpa','Capacity (MW)', 'Capacity (Mt)','Capacity (Mtpa)', 'CapacityBcm/y', 'CapacityBOEd', 'Capacity (MT)', 'Production - Gas', 'Production - Oil', 'Production (Mt)', 'Production (Mtpa)', 'Capacity (ttpa)']):                    
                    try:
                        # Clean the column first - strip whitespace and handle common non-numeric values
                        self.data[col] = self.data[col].astype(str).str.strip()
                        self.data[col] = self.data[col].replace(['', 'nan', 'NaN', 'None', 'unknown', 'not found', '--', '*', '<NA>', '-'], np.nan)
                        
                        # Use pandas to_numeric which is more robust than custom function
                        self.data[col] = pd.to_numeric(self.data[col], errors='raise') # raise
                        
                        # # Fill NaN values with empty string after conversion
                        # self.data[col] = self.data[col].fillna('')
                        
                        # Round all cap/prod columns to 4 decimal places
                        self.data[col] = self.data[col].apply(lambda x: round(x, 4))
                    except TypeError as e:
                        logger.warning(f'{e} error for {col} in {self.acro}')
                        logger.warning('Check for QC PM report') # so far problem with StartYearEarliest LNG Terminals geo in there
                        
                # RULESET FLAG
                elif 'year' in col.lower():
                    try:
                        print('in map_tracker_class coercing year to numeric will raise an issue')
                        self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
                        self.data[col] = self.data[col].apply(lambda x: check_and_convert_int(x))
                        self.data[col].fillna('', inplace=True)
                        # Round all year columns to 0 decimal places
                        self.data[col] = self.data[col].apply(lambda x: round(x, 0) if x != '' else x)   
                        self.data[col] = self.data[col].apply(lambda x: int(str(x).replace('.0', '')) if x != '' else x)
                        self.data[col] = self.data[col].fillna('not found')
                    except TypeError as e:
                        logger.warning(f'{e} error for {col} in {self.tab_name}')
                        logger.warning('Check for QC PM report') # so far problem with StartYearEarliest LNG Terminals geo in there
                        # CapacityBcm/y in Gas Pipelines CapacityBOEd in Gas Pipelines
                        # CapacityBOEd in Oil Pipelines
                elif 'latitude' in col.lower():  ## or lat lng
                    
                    self.data[col] = pd.to_numeric(self.data[col], errors='coerce')                    
                    self.data['float_col_clean_lat'] = self.data[col].apply(lambda x: check_and_convert_float(x))
                    # and add to missing_coordinate_row
                    # drop row if the coordinate 

                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lat']): 
                            missing_coordinate_row[self.acro] = self.data.loc[row]
                            self.data.drop(index=row, inplace=True)
                    
                    # now check if in appropriate range
                    self.data['float_col_clean_lat'] = self.data['float_col_clean_lat'].apply(
                        lambda x: check_in_range(x, acceptable_range['lat']['min'], acceptable_range['lat']['max'])
                    )
                    
                    # add any coordinates out of range to list to drop
                    # drop row if the coordinate is NaN

                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lat']):
                            # print(self.data.loc[row]) 
                            missing_coordinate_row[self.acro] = self.data.loc[row]
                            self.data.drop(index=row, inplace=True)
                        else:
                            self.data.loc[row, 'Latitude'] = self.data.loc[row, 'float_col_clean_lat']

                elif 'longitude' in col.lower():
                    self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
                    self.data['float_col_clean_lng'] = self.data[col].apply(lambda x: check_and_convert_float(x))
                    # and add to missing_coordinate_row
                    # drop row if the coordinate is NaN

                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lng']): 
                            print(f'Missing coordinate for {self.acro}')
                            missing_coordinate_row[self.acro] = self.data.loc[row]
                            self.data.drop(index=row, inplace=True)
                            
                    # now check if in appropriate range
                    self.data['float_col_clean_lng'] = self.data['float_col_clean_lng'].apply(
                        lambda x: check_in_range(x, acceptable_range['lng']['min'], acceptable_range['lng']['max'])
                    )
                    # add any coordinates out of range to list to drop
                    # drop row if the coordinate is NaN
                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lng']): 
                            print(self.data.loc[row])
                            missing_coordinate_row[self.acro] = self.data.loc[row]
                            self.data.drop(index=row, inplace=True)  
                            
                        else:
                            self.data.loc[row, 'Longitude'] = self.data.loc[row, 'float_col_clean_lng']           
                    if len(missing_coordinate_row) > 0:
                        logger.info(f"Missing coordinates for {self.acro}:")
                        for key, value in missing_coordinate_row.items():
                            logger.info(f"{key}: {value}")
                        logger.info("\n")
                        logger.warning(f"Missing coordinates logged for {self.acro}.")
                  
                    
                else:
                    logger.info(f"Skipping non-numeric column: {col}")
            #                 # write issues_coords dict to a csv file in gem_tracker_maps
            
        else:
            logger.info("Error: 'self.data' is not a DataFrame. And should be even for GOGET since it is run at a special point for it.")
            logger.info(msg=f"Error:'self.data' is {type(self.data).__name__}: {repr(self.data)}")
            

    

    def check_if_geometry_in_country(self):
        """
        Flags rows where the geometry (Point or MultiLineString) does not fall within the stated country.
        Adds a boolean column 'geometry_in_country' to the DataFrame.
        """

        df = self.data

        # Ensure we have a GeoDataFrame with geometry column
        if not isinstance(df, gpd.GeoDataFrame):
            if 'geometry' in df.columns:
                df = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
            else:
                logger.warning("No geometry column found.")
                self.data = df
                return

        # Load world country polygons from geopandas datasets
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        world = world.to_crs(df.crs)

        # Prepare a mapping from country names to polygons
        country_polys = {row['name']: row['geometry'] for _, row in world.iterrows()}

        def check_geom_in_country(row):
            country = row.get('Country/Area') or row.get('country/area') or row.get('country')
            geom = row['geometry']
            if not country or country not in country_polys or geom is None:
                return False
            country_poly = country_polys[country]
            # For MultiLineString, check if any part intersects
            if isinstance(geom, MultiLineString):
                return geom.intersects(country_poly)
            elif isinstance(geom, Point):
                return country_poly.contains(geom)
            else:
                return False

        df['geometry_in_country'] = df.apply(check_geom_in_country, axis=1)
        self.data = df


    def process_goget_reserve_prod_data(self):
        # output is to return df with scott's code adjustments
        # first run process_goget_reserve_prod_data_dd to save for data download
        # split into two dfs

        main, prod, rest_dfs = self.data # dont need rest_dfs for map but stil in this data so need to unpack it.
        # TODO need to implement the below...
        # lower case and str.replace(' ', '-')
        # main.columns = main.columns.str.lower()
        # prod.columns = prod.columns.str.lower()
        # main.columns = main.columns.str.replace(' ', '-')
        # prod.columns = prod.columns.str.replace(' ', '-')
        
        # Convert 'Data year' to integers in the 'production_reserves_df'
        prod['Data year'] = pd.to_numeric(prod['Data year'], errors='coerce').fillna(-1).astype(int)

        # Update for Production - Oil and its year
        main[["Production - Oil", "Production Year - Oil"]] = main.apply(
            lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million bbl/y", prod)),
            axis=1
        )
        # Update for Production - Gas and its year
        main[["Production - Gas", "Production Year - Gas"]] = main.apply(
            lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million m³/y", prod)),
            axis=1
        )

        # Update for Production - Hydrocarbons (unspecified) and its year
        main[["Production - Hydrocarbons (unspecified)", "Production Year - Hydrocarbons (unspecified)"]] = main.apply(
            lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million boe/y", prod)),
            axis=1
        )

        # Calculate total reserves and production
        #filtered_main_data_df['Reserves- Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_reserves, axis=1)
        main['Production - Total (Oil, Gas and Hydrocarbons)'] = main.apply(calculate_total_production_goget, axis=1)


        # Convert Discovery Year to String
        main['Discovery year'] = main['Discovery year'].astype(object)

        # Ensure there are no NaN values in the year columns before conversion to avoid errors
        main['Production Year - Oil'].fillna('', inplace=True)
        main['Production Year - Gas'].fillna('', inplace=True)
        main['Production Year - Hydrocarbons (unspecified)'].fillna('', inplace=True)

        main['Production Year - Oil'] = main['Production Year - Oil'].astype(str)
        main['Production Year - Gas'] = main['Production Year - Gas'].astype(str)
        main['Production Year - Hydrocarbons (unspecified)'] = main['Production Year - Hydrocarbons (unspecified)'].astype(str)

        # remove .0 -1.0
        for col in ['Production Year - Oil', 'Production Year - Gas','Production Year - Hydrocarbons (unspecified)']:
            main[col] = main[col].apply(lambda x: x.replace('.0',''))
            main[col] = main[col].apply(lambda x: x.replace('-1','not stated'))

        # Convert to integer first to remove the trailing zero, then to string
        # filtered_main_data_df['Production Year - Oil'] = filtered_main_data_df['Production Year - Oil'].astype(int).astype(str)
        # filtered_main_data_df['Production Year - Gas'] = filtered_main_data_df['Production Year - Gas'].astype(int).astype(str)
        # filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'] = filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'].astype(int).astype(str)

        # Ensure there are no nan in status, this is before renaming so still uppercase
        main['Status'].fillna('', inplace=True)
        
        # Replace "0" with np.nan or a placeholder if you had NaN values initially
        # filtered_main_data_df.replace('0', np.nan, inplace=True)

        # Check the conversion by printing the dtypes again
        # column_data_types = filtered_main_data_df.dtypes
        # print(column_data_types)
        
        # Apply the function to create a new column 'Country List'
        main['Country List'] = main['Country/Area'].apply(get_country_list)
        # print(filtered_main_data_df[['Country List','Country/Area']]) 
        # print(set(filtered_main_data_df['Country List'].to_list()))
        # print(set(filtered_main_data_df['Country/Area'].to_list()))
        # input('Check country list and country/area after apply')   
        
        cols_to_drop = [c for c in ['Government unit ID', 'Basin', 'Concession / block'] if c in main.columns]
        dropped_filtered_main_data = main.drop(cols_to_drop, axis=1)
        # average_production_total = filtered_main_data_df["Production - Total (Oil, Gas and Hydrocarbons)"].mean()
        # print("Average Production - Total (Oil, Gas and Hydrocarbons):", average_production_total)
        # input('check avg production total seems right, previous was 6.3041')

        # # Create new column for scaling where there is a fill in value based on average when data is not there.
        # dropped_filtered_main_data["Production for Map Scaling"] = np.where(dropped_filtered_main_data["Production - Total (Oil, Gas and Hydrocarbons)"] != 0,
        #                                                             dropped_filtered_main_data["Production - Total (Oil, Gas and Hydrocarbons)"],
        #                                                             average_production_total)

        dropped_production_Wiki_name = create_goget_wiki_name(dropped_filtered_main_data)
        regions_df = gspread_access_file_read_only(region_key, region_tab)
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
        cols_to_drop_2 = [c for c in ['Unit type'] if c in dropped_production_Wiki_name.columns]
        clean_export = dropped_production_Wiki_name.drop(cols_to_drop_2, axis=1) # Fuel type
        
        # Use not centroid but descriptive point
        # Set up DF of Units without locations
        clean_export[['Longitude', 'Latitude']] = clean_export[['Longitude', 'Latitude']].fillna('')
        missing_location_df = clean_export[clean_export['Latitude']=='']
        # Get unique entries from the 'Country/Area' column
        unique_countries_with_missing_locations = missing_location_df['Country/Area'].unique()

        # Display the unique countries
        unique_countries_df = pd.DataFrame(unique_countries_with_missing_locations, columns=['Country/Area'])
        print(unique_countries_df)
        # input('check unique countries that need descriptive points') # TODO actually save this somewhere
        # normally would use descriptive point
        
        centroid_df = gspread_access_file_read_only(centroid_key, centroid_tab) # TODO update this with descriptive point on subregion
        # centroid_df = gspread_access_file_read_only(rep_point_key, rep_point_tab) # TODO update this with descriptive point on subregion

        # print(centroid_df.head())
        # input('check centroid df')
        centroid_df.rename(columns={'Latitude':'Latitude-centroid', 'Longitude':'Longitude-centroid'},inplace=True)
        
        clean_export_center = pd.merge(clean_export, centroid_df, how='left', on='Country/Area')

        # Update 'Location accuracy' for filled-in values
        # print(clean_export_center.columns)
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
            'Production - Oil': 'Liquids Production (million bbl/y)',
            'Production - Gas': 'Gas Production (million m³/y)', # kep Gas Production (million m³/y) because at asset level million m3/y better
            'Production - Hydrocarbons (unspecified)': 'Unspecified Hydrocarbons Production (million boe/y)',
            'Production - Total (Oil, Gas and Hydrocarbons)': 'Total Production (million boe/y)',
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
            'Liquids Production (million bbl/y)',
            'Production Year - Oil',
            'Gas Production (million m³/y)',
            'Production Year - Gas',
            'Unspecified Hydrocarbons Production (million boe/y)',
            'Production Year - Hydrocarbons (unspecified)',
            'Total Production (million boe/y)',
            'Wiki URL',
        ]
    

        # Rename the columns
        clean_export_center_clean_rename = clean_export_center_clean.rename(columns=column_rename_map)

        # Only keep columns that actually exist (handles old vs new GOGET format differences)
        available_desired = [c for c in desired_column_order if c in clean_export_center_clean_rename.columns]
        missing = [c for c in desired_column_order if c not in clean_export_center_clean_rename.columns]
        if missing:
            logger.info(f'GOGET: desired columns not present (ok for new format): {missing}')
        clean_export_center_clean_reorder_rename = clean_export_center_clean_rename[available_desired]

        print(f'This is clean_export_center_clean_reorder_rename coming at end of process_goget_reserve_prod_data:')
        print(clean_export_center_clean_reorder_rename)
        
        self.data = clean_export_center_clean_reorder_rename
    
        
    def transform_to_gdf(self): # This is dropping all geo rows for pipeline data
    # TODO FIX pipeline issue  
        print(f'length prior to anything in transform_to_gdf: {len(self.data)}')

        if isinstance(self.data, tuple):
            logger.info(self.tab_name)
            logger.info('Why is that a tuple up there? GOGET and GOGPT eu should be consolidated by now...')
            input('There is a tuple in the data but all are consolidated so look into it.')
        else:
            
            if 'latitude' in self.data.columns.str.lower():
                logger.info('latitude in cols')
                logger.info(f'len of df before convert coords: {len(self.data)}')
                gdf = convert_coords_to_point(self.data) 
                logger.info(f'len of gdf after convert coords: {len(gdf)}')


            elif 'WKTFormat' in self.data.columns:
                logger.info(f'Using WKTFormat {self.tab_name}')

                gdf = convert_google_to_gdf(self.data) # this drops all empty WKTformat cols
                
                logger.info(f'len of gdf after convert_google_to_gdf: {len(gdf)}')
                logger.info(self.tab_name)

            else:
                logger.info(f'{self.tab_name} already a gdf MOST LIKELY but if not pipelines or ggit terminals then be worried.')
                gdf = self.data
        print(f'length right before saving in transform_to_gdf: {len(self.data)}')
        # input('check above length')
        
        self.data = gdf
        
    def split_goget_ggit(self):
        gdf = self.data
        if self.acro == 'GOGET':
            gdf['tracker_custom'] = 'GOGET-oil'
        elif self.acro == 'GGIT-lng' or self.acro == 'EGT-term':
            if 'facilitytype' in gdf.columns:
                gdf_ggit_missing_units = gdf[gdf['facilitytype']=='']
                logger.info(gdf_ggit_missing_units)
                gdf = gdf[gdf['facilitytype']!='']
                gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT-import' if row['facilitytype'] == 'import' else 'GGIT-export', axis=1)        
            elif 'FacilityType' in gdf.columns:
                gdf_ggit_missing_units = gdf[gdf['FacilityType']=='']
                logger.info(gdf_ggit_missing_units)
                gdf = gdf[gdf['FacilityType']!='']
                gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT-import' if row['FacilityType'] == 'import' else 'GGIT-export', axis=1)
            else:
                logger.info(f'Look at cols for {self.acro}:')
                for col in gdf.columns:
                    logger.info(col)   
                input('Check logs issue with Facility Type in split_goget_ggit func')
                logger.warning('Checkkk it, issues with Facility Type in split_goget_ggit func')                  
        elif self.acro == 'EGT-gas':
            gdf['tracker_custom'] = 'GGIT'
        
        # elif self.acro == 'GOGPT-eu':
        #     gdf['tracker_custom'] = 'GOGPT'
        else:
            gdf['tracker_custom'] = self.acro

        self.data = gdf


    def assign_conversion_factors(self, conversion_df):
        # add column for units 
        # add tracker_custom
        gdf = self.data
        logger.info(f"This is tracker_custom for gdf:\n{gdf['tracker_custom']}")

        if self.acro == 'GOGET': 
            # # # printf'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GOGET-oil':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['conversion_factor'].values[0]

            gdf = gdf.reset_index(drop=True)

            
        elif self.acro == 'GGIT-lng' or self.acro == 'EGT-term':
            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GGIT-export':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-export']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-export']['conversion_factor'].values[0]
                elif gdf.loc[row, 'tracker_custom'] == 'GGIT-import':  
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-import']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-import']['conversion_factor'].values[0]
            gdf = gdf.reset_index(drop=True)

            
        elif self.acro == 'EGT-gas':
            gdf['tracker_custom'] = 'GGIT'
            gdf['original_units'] = conversion_df[conversion_df['tracker']=='GGIT']['original_units'].values[0]
            gdf['conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT']['conversion_factor'].values[0]
            gdf = gdf.reset_index(drop=True)

        # elif self.acro == 'GOGPT-eu':
        #     gdf['tracker_custom'] = 'GOGPT'
        #     gdf['original_units'] = conversion_df[conversion_df['tracker']=='GOGPT']['original_units'].values[0]
        #     gdf['conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGPT']['conversion_factor'].values[0]
        #     gdf = gdf.reset_index(drop=True)
        
        elif self.acro == 'GMET':
            gdf['tracker_custom'] = 'GMET'
            gdf['original_units'] = 'n/a'
            gdf['conversion_factor'] = 'n/a'
            gdf = gdf.reset_index(drop=True)                   

        elif self.acro == 'GCCT':
            gdf['tracker_custom'] = 'GCCT'
            gdf['original_units'] = 'n/a'
            gdf['conversion_factor'] = 'n/a'
            gdf = gdf.reset_index(drop=True)                   

        elif self.acro == 'GIST':
            gdf['tracker_custom'] = 'GIST'
            gdf['original_units'] = 'n/a'
            gdf['conversion_factor'] = 'n/a'
            gdf = gdf.reset_index(drop=True)  

        elif self.acro == 'GIOMT':
            gdf['tracker_custom'] = 'GIOMT'
            gdf['original_units'] = 'n/a'
            gdf['conversion_factor'] = 'n/a'
            gdf = gdf.reset_index(drop=True) 
        # TODO need to have this get skipped for certain trackers where regional maps don't get created or this kind of measure isn't relevant 
        elif self.acro == 'GChI':
            gdf['tracker_custom'] = 'GChI'
            gdf['original_units'] = 'n/a'
            gdf['conversion_factor'] = 'n/a'
            gdf = gdf.reset_index(drop=True)             
            
            


        else:

            if len(gdf) > 0:
                
                gdf = gdf.reset_index(drop=True)
                conversion_df = conversion_df.reset_index(drop=True)
                logger.info(f'Setting acro as tracker custom: {self.acro} which is needed to look up conversion factor')

                gdf['original_units'] = conversion_df[conversion_df['tracker']==self.acro]['original_units'].values[0]
                gdf['conversion_factor'] = conversion_df[conversion_df['tracker']==self.acro]['conversion_factor'].values[0]
            
            else:
                logger.warning("gdf is empty!")
                logger.warning('maybe a problem with not having tracker as a col?')
                logger.warning(f'Prob not good {self.tab_name}')
            
        self.data = gdf



def create_filtered_fuel_df(df, self): 
    # self.acro, self.fuelcol
    if self.acro == 'GOGET':
        drop_row = []
        logger.info(f'Length of goget before oil drop: {len(df)}')
        for row in df.index:
            if df.loc[row, 'Fuel type'] == 'oil':
                drop_row.append(row)
            
        df.drop(drop_row, inplace=True)        
        logger.info(f'Length of goget after oil drop: {len(df)}')
    
    # all infrastructure ones 
    elif self.acro in ['GGIT-eu', 'GGIT', 'EGT-gas', 'EGT-term', 'GGIT-lng']:
        drop_row = []
        logger.info(f'Length of ggit before oil drop: {len(df)}')
        fuels = set(df['Fuel'].to_list())
        # print(fuels)
        # input(f'TEMP: len before drop {len(df)}') # passed 9 removed
        for row in df.index:
            if df.loc[row, 'Fuel'] == 'Oil':
                drop_row.append(row)
            elif df.loc[row, 'Fuel'] == 'NH3':
                # input('caught lng')
                drop_row.append(row)
            elif df.loc[row, 'Fuel'] == 'LH2': 
                # input('caught lng')
                drop_row.append(row)
            elif df.loc[row, 'Fuel'] == 'eLNG': 
                # input('caught lng')
                drop_row.append(row)
            elif df.loc[row, 'Fuel'] == '':
                drop_row.append(row)
        
        df.drop(drop_row, inplace=True)
        logger.info(f'len after gas only filter {self.acro} {len(df)}')
        # input(f'TEMP: len after drop {len(df)}') # passed 9 removed 
    
    elif self.acro in ['GOGPT']: # removed GOGPT-eu form map form # if GOGPT-eu does not need to be run on hydrogen tab, also does not need to be run on 'GOGPT-eu' because it was pre filtered for us
        drop_row = []
        
        logger.info(f'Length of {self.acro} before oil drop: {len(df)}')
        for row in df.index:
            fuel_cat_list = df.loc[row, 'Fuel'].split(',')
            new_fuel_cat_list = []
            for fuel in fuel_cat_list:
                fuel = fuel.split(':')[0]
                new_fuel_cat_list.append(fuel)
            
            if len(new_fuel_cat_list) > 1:
                # if all in list is fossil liquids
                if new_fuel_cat_list.count('fossil liquids') == len(new_fuel_cat_list):
                    drop_row.append(row)
                # if just one in there and it is fossil liquids
            elif new_fuel_cat_list == ['fossil liquids']:
                drop_row.append(row)
        
        df.drop(drop_row, inplace=True)
        logger.info(f'len after gas only filter {self.acro} {len(df)}')
              
    
    return df
    
