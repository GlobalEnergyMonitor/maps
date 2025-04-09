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
from collections import Counter
import time

start_time = time.time()  # Record the start time

################
# ADAPT AET FUNCTIONS FOR ALL MULTI TRACKER MAPS #
################

def what_maps_are_needed(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab):
    needed_map_and_tracker_dict = {} # map: [trackers]
    map_log_df = gspread_access_file_read_only(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab)
    # # printf'Trackers with updates to be incorporated: {trackers_to_update}')

    for tracker in trackers_to_update:
        # filter out the map tracker tab df 
        # so that we only have the row that matches the tracker to be updated
        # and also find the tracker names for the map to be updated beyond the new tracker data but existing tracker data as well
        map_log_df_sel = map_log_df[map_log_df['official release tab name'] == tracker]
        for col in map_log_df_sel.columns:
            if 'yes' in map_log_df_sel[col].values:
                map_log_df_map_sel = map_log_df[map_log_df[col] == 'yes']
                tracker_col_index = map_log_df.columns.get_loc('official release tab name')
                tracker_name_col_map_sel = map_log_df.columns[tracker_col_index]
                list_of_trackers_relevant_to_map = map_log_df_map_sel[tracker_name_col_map_sel].to_list()
                needed_map_and_tracker_dict[col] = list_of_trackers_relevant_to_map
                # # printf'Map {col} needs to be updated with the new data for {tracker}, and existing data for {list_of_trackers_relevant_to_map} minus {tracker}.')

    return needed_map_and_tracker_dict

def what_countries_or_regions_are_needed_per_map(multi_tracker_countries_sheet, needed_map_and_tracker_dict):
    needed_tracker_geo_by_map = {} # {map: [[trackers],[countries]]}
    map_by_region = gspread_creds.open_by_key(multi_tracker_countries_sheet)

    for map, list_needed_trackers in needed_map_and_tracker_dict.items():
        if map == 'GIPT':
            list_needed_geo = '' # global
            needed_tracker_geo_by_map[map] = [list_needed_trackers, list_needed_geo]

        else:
            map = map.lower().split(' ')[0]
            spreadsheet = map_by_region.worksheet(map)
            country_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            list_needed_geo = country_df.iloc[:, 0].to_list()
            needed_tracker_geo_by_map[map] = [list_needed_trackers, list_needed_geo]
 
    return needed_tracker_geo_by_map

# removing for now to simplify!
# def pull_in_prev_key_map(needed_tracker_geo_by_map, multi_tracker_log_sheet_key):
#     # pull in prev key from relevant map results tab
#     map_log_gsheets = gspread_creds.open_by_key(multi_tracker_log_sheet_key)
#     sheet_names = [sheet.title for sheet in map_log_gsheets.worksheets()]


#     for mapname, list_of_geo_trackers in needed_tracker_geo_by_map.items():
#         maphint = mapname.lower().split(' ')[0]
#         # for sheet in gsheets to find results tab and pull prev map results info for about page
#         for sheet_name in sheet_names:
#             if maphint in sheet_name and 'results' in sheet_name:
#                 sheet = map_log_gsheets.worksheet(sheet_name)
#                 map_results = pd.DataFrame(sheet.get_all_records(expected_headers=['release date','map updated','tracker acro','key','download file link','map file link','project count','unit count','capacity total']))
#                 # filter the dataframe so we only have the first row
#                 most_recent_map_results = map_results.iloc[[0]].reset_index(drop=True)
#                 # # printmost_recent_map_results)
#                 # # # # printmost_recent_map_results['release date'])
#                 # # # input('Pause to check most recent map results')
#                 # prev_date = most_recent_map_results['release date'] # only if didn't filter like above on index .iloc[0]
#                 # prev_key = sheet.acell('D2').value.to_list() # will always be this if we do most recent first
#                 prev_key = most_recent_map_results.iloc[0, most_recent_map_results.columns.get_loc('key')]
#                 needed_tracker_geo_by_map[mapname].append(most_recent_map_results) # mapname: [trackers, geo, map_log_results_first_row]
#                 # # printf'For map {mapname} we found the prev key: {prev_key}.')

#     return needed_tracker_geo_by_map


def folder_setup(needed_tracker_geo_by_map):
    
    for mapname, list_of_countries in needed_tracker_geo_by_map.items():
        path_test_results = gem_path + mapname + '/test_results/'
        path_download_and_map_files = gem_path + mapname + '/compilation_output/' + iso_today_date_folder
        os.makedirs(path_download_and_map_files, exist_ok=True)
        os.makedirs(path_test_results, exist_ok=True)

    return None


###########################
###########################
# PULL IN ALL AET DATA #
# SAVE ALL AET DATA AS LOCAL XLSX or GEOJSON #
# FIRST, PULL IN THE DATA FROM THE GOOGLE SHEET
# CONVERT INTO GDF
# THEN, PULL IN THE DATA FROM THE LOCAL GEOJSON

def create_prep_file(multi_tracker_log_sheet_key, prep_file_tab): # needed_map_list
    prep_df = gspread_access_file_read_only(multi_tracker_log_sheet_key, prep_file_tab)
    prep_df = prep_df[prep_df['official release tab name'] != ''] # skips rows at bottom
    # Convert 'gspread_tabs' and 'sample_cols' to lists
    prep_df['gspread_tabs'] = prep_df['gspread_tabs'].apply(lambda x: x.split(';'))
    # df['sample_cols'] = df['sample_cols'].apply(lambda x: x.split(';'))
    prep_df['gspread_tabs'] = prep_df['gspread_tabs'].apply(lambda lst: [s.strip() for s in lst])
    # df['sample_cols'] = df['sample_cols'].apply(lambda lst: [s.strip() for s in lst])
    prep_df['official name'] = prep_df['official release tab name']

    prep_df.set_index('official release tab name', inplace=True) # sets index on offical name
    prep_df['tracker acro'] = prep_df['tracker-acro']

    # # if slowmo:

        # printf'this is prep df: {prep_df}')

        # # input('Check prep df')
    
    return prep_df


def pull_gsheet_data(prep_df, needed_tracker_geo_by_map):

    dict_list_dfs_by_map = {} 
    dict_list_gdfs_by_map = {} 
    prep_dict = prep_df.to_dict(orient='index')
    
    for mapname, value in needed_tracker_geo_by_map.items():

        path_for_test_results = gem_path + mapname + '/test_results/'
        os.makedirs(path_for_test_results, exist_ok=True)
        list_dfs_by_map = [] # still use this list to create a list of dfs as we go through all needed trackers
        list_gdfs_by_map = [] # still use this list to create a list of gdfs as we go through all needed trackers
        needed_trackers = value[0] # list of tracker names to include in list of dfs
        needed_geo = value[1] # list of countries or global for gipt to filter each df in the list by
        if local_copy:

            for file in os.listdir(path_for_test_results): # use key for map name
                if file.endswith(".geojson") & (mapname in file) & (iso_today_date in file): #  & (iso_today_date in file)
                    gdf = gpd.read_file(f'{path_for_test_results}{file}')
                    list_gdfs_by_map.append(gdf)
                    # # printf'Added {file} to list of gdfs for {mapname}')
                elif file.endswith(".xlsx") & (mapname in file) & (iso_today_date in file): # & (iso_today_date in file)
                    df = pd.read_excel(f'{path_for_test_results}{file}', engine='openpyxl')
                    list_dfs_by_map.append(df)
                    # # printf'Added {file} to list of dfs for {mapname}')
        else:
            for tracker in needed_trackers:
                # # printf'We are on {tracker}')
                
                if tracker in non_gsheet_data:
                    # # printf'{tracker} is not in gsheet data so skipping this tracker.')
                    continue
                
                else:
                    df = gspread_access_file_read_only(prep_dict[tracker]['gspread_key'], prep_dict[tracker]['gspread_tabs'])
                    
                    # # printf'Shape of df: {df.shape}')
                    # # # input('check shape')
                    df['tracker acro'] = prep_dict[tracker]['tracker acro']
                    df['official_name'] = tracker
                    df = df.replace('*', pd.NA).replace('Unknown', pd.NA).replace('--', pd.NA)
                    df = df.fillna('')
                    df.to_excel(f'{path_for_test_results}{mapname}_{tracker}_df_{iso_today_date}.xlsx', index=False)

                    col_reg_name, col_country_name = find_region_country_colname(df)
                    # check countries in df against list of official map countries and report issues]

                    # check_countries_official(df, col_country_name, mapname, tracker) # TODO troubleshoot

                    df = create_filtered_df_list_by_map(df,col_country_name, col_reg_name, mapname, needed_geo)

                    list_dfs_by_map.append(df)
                    df.to_excel(f'{path_for_test_results}{mapname}_{tracker}_df_{iso_today_date}.xlsx', index=False)

                    # df_dd has all units even with missing coords
                    # df_map only has units with coords
                    df_map, issues_coords = coordinate_qc(df, col_country_name)  
                    # df.to_excel(f'{path_for_test_results}{mapname}_{tracker}_df-altered-coords_{iso_today_date}.xlsx', index=False)
                    

                    gdf = convert_coords_to_point(df_map) 
                    # append gdf to list of gdfs for map - though now we can have it as a csv for faster AET non tile load
                    list_gdfs_by_map.append(gdf)
                    gdf_to_geojson(gdf, f'{path_for_test_results}{mapname}_{tracker}_gdf_{iso_today_date}.geojson')
                    # # printf'Added gdf {tracker} for map {mapname} to list of gdfs for map and saved to {path_for_test_results}{mapname}_{tracker}_gdf_{iso_today_date}.geojson.')
        dict_list_dfs_by_map[mapname] = list_dfs_by_map
        dict_list_gdfs_by_map[mapname] = list_gdfs_by_map 
        issues_coords_df = pd.DataFrame(issues_coords).to_csv(path_for_test_results + mapname + 'issue_coords_dropped.csv')
            
    return dict_list_dfs_by_map,dict_list_gdfs_by_map

def incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson, dict_list_dfs_by_map, dict_list_gdfs_by_map):
    
    # test that we don't lose existing gdfs

    # TODO ask Hannah to help make this less repetitive
    pipes_gdf = gpd.read_file(goit_geojson)
    pipes_gdf['tracker acro'] = 'GOIT'
    pipes_gdf['official_name'] = 'Oil Pipelines'
    # pipes_gdf = find_missing_geo(pipes_gdf) 
     
    ggit_gdf = gpd.read_file(ggit_geojson)
    ggit_gdf['tracker acro'] = 'GGIT'
    ggit_gdf['official_name'] = 'Gas Pipelines'
    # ggit_gdf = find_missing_geo(ggit_gdf)
    
    ggit_lng_gdf = gpd.read_file(ggit_lng_geojson)
    ggit_lng_gdf['tracker acro'] = 'GGIT-lng'
    ggit_lng_gdf['official_name'] = 'LNG Terminals'
    # ggit_lng_gdf = find_missing_coords(ggit_lng_gdf) # TODO 
##### set up dfs
    pipes_df = pd.DataFrame(pipes_gdf).reset_index(drop=True)
    ggit_df = pd.DataFrame(ggit_gdf).reset_index(drop=True)
    ggit_lng_df = pd.DataFrame(ggit_lng_gdf).reset_index(drop=True)
    
    col_reg_name_pipes, col_country_name_pipes= find_region_country_colname(pipes_gdf)
    col_reg_name_ggit, col_country_name_ggit = find_region_country_colname(ggit_gdf)
    col_reg_name_ggit_lng, col_country_name_ggit_lng = find_region_country_colname(ggit_lng_gdf)
    
    incorporated_dict_list_gdfs_by_map = {}
    incorporated_dict_list_dfs_by_map = {}

    map_by_region = gspread_creds.open_by_key(multi_tracker_countries_sheet)
    result = {}
    result_df = {}
    result_after = {}
    result_after_df = {}    
    for mapname, list_of_gdfs in dict_list_gdfs_by_map.items():
        list_of_gdfs_geojson = []
        # Test first
        # # print'Starting test prior to loop')
        total_gdfs = len(list_of_gdfs)
        tracker_counter = Counter()
        for gdf in list_of_gdfs:
            tracker_counter.update(gdf['tracker acro'])
        result[mapname] = {
            'total_gdfs': total_gdfs,
            'tracker_counts': tracker_counter
        }
        for map_name, stats in result.items():
            print(f"Map: {map_name}")
            print(f"Total number of DataFrames: {stats['total_gdfs']}")
            print(f"Tracker counts: {stats['tracker_counts']}")
            print("-" * 40)
        # input('Check test')
        
        if mapname == 'GIPT':
            incorporated_dict_list_gdfs_by_map[mapname] = list_of_gdfs 
            continue           
        elif mapname in gas_only_maps:   
        # pull needed geo by map type from the gsheet 
            map = mapname.lower().split(' ')[0]
            # # printf'This is map name we use to grab the country tab to filter: {map}')
            geo_spreadsheet = map_by_region.worksheet(map) # europe, asia 
            geo_df = pd.DataFrame(geo_spreadsheet.get_all_records(expected_headers=[]))
            # # printf'This is geo_df {geo_df} for {map}')
            needed_geo = geo_df.iloc[:, 0].to_list()
            # print(needed_geo)

            # all but GOIT or pipes since that is for oil
            ggit_gdf_new = create_filtered_df_list_by_map(ggit_gdf, col_country_name_ggit, col_reg_name_ggit, mapname, needed_geo)  
            ggit_lng_gdf_new = create_filtered_df_list_by_map(ggit_lng_gdf, col_country_name_ggit_lng, col_reg_name_ggit_lng,  mapname, needed_geo)  

            list_of_gdfs_geojson.append(ggit_gdf_new)
            list_of_gdfs_geojson.append(ggit_lng_gdf_new) 

            incorporated_dict_list_gdfs_by_map[mapname] = list_of_gdfs_geojson + list_of_gdfs

        else:
            map = mapname.lower().split(' ')[0]
            # # printf'This is map name we use to grab the country tab to filter: {map}')
            
            geo_spreadsheet = map_by_region.worksheet(map)
            geo_df = pd.DataFrame(geo_spreadsheet.get_all_records(expected_headers=[]))
            # # printf'This is geo_df {geo_df} for {map}')
            needed_geo = geo_df.iloc[:, 0].to_list()
            print(needed_geo)
            # input('check that it is africa or latam')
            # it must be LATAM and Africa Energy which takes them all
            pipes_gdf_new = create_filtered_df_list_by_map(pipes_gdf, col_country_name_pipes, col_reg_name_pipes, mapname, needed_geo)  
            ggit_gdf_new = create_filtered_df_list_by_map(ggit_gdf, col_country_name_ggit, col_reg_name_ggit, mapname, needed_geo)  
            ggit_lng_gdf_new = create_filtered_df_list_by_map(ggit_lng_gdf, col_country_name_ggit_lng, col_reg_name_ggit_lng,  mapname, needed_geo)  

            list_of_gdfs_geojson.append(pipes_gdf_new)
            list_of_gdfs_geojson.append(ggit_gdf_new)
            list_of_gdfs_geojson.append(ggit_lng_gdf_new)

            incorporated_dict_list_gdfs_by_map[mapname] = list_of_gdfs_geojson + list_of_gdfs
        
    for mapname, list_of_dfs in dict_list_dfs_by_map.items():
        list_of_dfs_geojson = []
        total_dfs = len(list_of_dfs)
        tracker_counter = Counter()
        for df in list_of_dfs:
            tracker_counter.update(df['tracker acro'])
        result_df[mapname] = {
            'total_dfs': total_dfs,
            'tracker_counts': tracker_counter
        }
        for map_name, stats in result_df.items():
            print(f"Map: {map_name}")
            print(f"Total number of DataFrames: {stats['total_dfs']}")
            print(f"Tracker counts: {stats['tracker_counts']}")
            print("-" * 40)
        # input('Check test')
        
        if mapname == 'GIPT':
            incorporated_dict_list_dfs_by_map[mapname] = list_of_dfs  
            continue
        elif mapname in gas_only_maps:
            map = mapname.lower().split(' ')[0]

            geo_spreadsheet = map_by_region.worksheet(map)
            geo_df = pd.DataFrame(geo_spreadsheet.get_all_records(expected_headers=[]))
            needed_geo = geo_df.iloc[:, 0].to_list()

            # all but GOIT or pipes since that is for oil
            ggit_df_new = create_filtered_df_list_by_map(ggit_df, col_country_name_ggit, col_reg_name_ggit, mapname, needed_geo)  
            ggit_lng_df_new = create_filtered_df_list_by_map(ggit_lng_df, col_country_name_ggit_lng, col_reg_name_ggit_lng, mapname, needed_geo)  

            list_of_dfs_geojson.append(ggit_df_new)
            list_of_dfs_geojson.append(ggit_lng_df_new) 
            
            incorporated_dict_list_dfs_by_map[mapname] = list_of_dfs_geojson + list_of_dfs   

        else:
            map = mapname.lower().split(' ')[0]

            geo_spreadsheet = map_by_region.worksheet(map)
            geo_df = pd.DataFrame(geo_spreadsheet.get_all_records(expected_headers=[]))
            needed_geo = geo_df.iloc[:, 0].to_list()

            # it must be LATAM and Africa Energy which takes them all
            pipes_df_new = create_filtered_df_list_by_map(pipes_df, col_country_name_pipes, col_reg_name_pipes,  mapname, needed_geo)  
            ggit_df_new = create_filtered_df_list_by_map(ggit_df, col_country_name_ggit,  col_reg_name_ggit,  mapname, needed_geo)  
            ggit_lng_df_new = create_filtered_df_list_by_map(ggit_lng_df, col_country_name_ggit_lng, col_reg_name_ggit_lng,  mapname, needed_geo)  

            list_of_dfs_geojson.append(pipes_df_new)
            list_of_dfs_geojson.append(ggit_df_new)
            list_of_dfs_geojson.append(ggit_lng_df_new)
            incorporated_dict_list_dfs_by_map[mapname] = list_of_dfs_geojson + list_of_dfs   

    ## test after
    for map_name, list_of_gdfs in incorporated_dict_list_gdfs_by_map.items():
        # Test after
        # # print'Starting test after loop')
        total_gdfs = len(incorporated_dict_list_gdfs_by_map)
        tracker_counter = Counter()
        for gdf in list_of_gdfs:
            tracker_counter.update(gdf['tracker acro'])
        result_after[map_name] = {
            'total_gdfs': total_gdfs,
            'tracker_counts': tracker_counter
        }
        for map_name, stats in result_after.items():
            print(f"Map: {map_name}")
            print(f"Total number of DataFrames: {stats['total_gdfs']}")
            print(f"Tracker counts: {stats['tracker_counts']}")

        # input('Check test')
    ## test after
    for map_name, list_of_dfs in incorporated_dict_list_dfs_by_map.items():
        # Test after
        # # print'Starting test after loop')
        total_dfs = len(incorporated_dict_list_dfs_by_map)
        tracker_counter = Counter()
        for df in list_of_dfs:
            tracker_counter.update(df['tracker acro'])
            result_after_df[map_name] = {
            'total_dfs': total_dfs,
            'tracker_counts': tracker_counter
            }
        for map_name, stats in result_after_df.items():
            print(f"Map: {map_name}")
            print(f"Total number of DataFrames: {stats['total_dfs']}")
            print(f"Tracker counts: {stats['tracker_counts']}")
            print("-" * 40)
            
    return incorporated_dict_list_gdfs_by_map, incorporated_dict_list_dfs_by_map
    


################
# MAKE MAP FILE #
################

def create_conversion_df(conversion_key, conversion_tab):
    df = gspread_access_file_read_only(conversion_key, conversion_tab)
    # # # printf'this is conversion df: {df}')
    
    df = df[['tracker', 'type', 'original units', 'conversion factor (capacity/production to common energy equivalents, TJ/y)']]
    df = df.rename(columns={'conversion factor (capacity/production to common energy equivalents, TJ/y)': 'conversion_factor', 'original units': 'original_units'})
    df['tracker'] = df['tracker'].apply(lambda x: x.strip())

    return df  


def split_goget_ggit(dict_list_gdfs_by_map):
    custom_dict_list_gdfs_by_map = {}
    
    for mapname, list_gdfs in dict_list_gdfs_by_map.items():
        custom_list_of_gdfs = []
        # # printf'This is length before: {len(list_gdfs)} for {mapname}')
        for gdf in list_gdfs:
            # # # printdf['tracker acro'])
            gdf = gdf.reset_index()
            if gdf['tracker acro'].iloc[0] == 'GOGET':
                # # # printgdf.columns)
                # oil
                gdf = gdf.copy()
                # df_goget_missing_units.to_csv('compilation_output/missing_gas_oil_unit_goget.csv')
                # gdf['tracker_custom'] = gdf.apply(lambda row: 'GOGET - gas' if row['Production - Gas (Million m³/y)'] != '' else 'GOGET - oil', axis=1)
                gdf['tracker_custom'] = 'GOGET - oil'
                custom_list_of_gdfs.append(gdf)
                
            elif gdf['tracker acro'].iloc[0] == 'GGIT-lng':
                gdf_ggit_missing_units = gdf[gdf['FacilityType']=='']
                # # printf'GGIT LNG missing units: {gdf_ggit_missing_units}')
                # # # input('Pause to check missing units for GGIT LNG important to know how to calculate capacity factor because differs import and export')
                # gdf_ggit_missing_units.to_csv('compilation_output/missing_ggit_facility.csv')
                gdf = gdf[gdf['FacilityType']!='']
                gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT - import' if row['FacilityType'] == 'Import' else 'GGIT - export', axis=1)
                # # # printgdf[['tracker_custom', 'tracker acro', 'FacilityType']])
                custom_list_of_gdfs.append(gdf)

            else:
                gdf['tracker_custom'] = gdf['tracker acro']
            
                custom_list_of_gdfs.append(gdf)
        custom_dict_list_gdfs_by_map[mapname] = custom_list_of_gdfs
        # # printf'This is length after: {len(custom_list_of_gdfs)} for {mapname}')
    # # printcustom_dict_list_gdfs_by_map.keys())
    # # # input('check that there are enough maps')

    return custom_dict_list_gdfs_by_map



def assign_conversion_factors(custom_dict_list_gdfs_by_map, conversion_df):
    # add column for units 
    # add tracker_custom
    # TODO change these because dict not a list now! dict key is map name, value is list of filtered df of gdf
    # # printcustom_dict_list_gdfs_by_map.keys())
    # # # input('check enough maps')
    # # # input('STOP HERE to see if all maps or not')
    custom_dict_list_gdfs_by_map_with_conversion = {}
    for mapname, list_of_gdfs in custom_dict_list_gdfs_by_map.items():
        custom_list_of_gdfs = []
        # # printmapname)
        # # # input('check mapname in assign_conversion_factors')
        for gdf in list_of_gdfs:

            gdf = gdf.copy()

            # # printgdf['tracker acro'].loc[0])
            # # printgdf['official_name'].loc[0])

            if gdf['tracker acro'].iloc[0] == 'GOGET': 
                # # # printf'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')

                for row in gdf.index:
                    if gdf.loc[row, 'tracker_custom'] == 'GOGET - oil':
                        gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET - oil']['original_units'].values[0]
                        gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET - oil']['conversion_factor'].values[0]
                    # elif gdf.loc[row, 'tracker_custom'] == 'GOGET - gas':  
                    #     gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker acro']=='GOGET - gas']['original_units'].values[0]
                    #     gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker acro']=='GOGET - gas']['conversion_factor'].values[0]
                # gdf['tracker acro'] = 'GOGET' # commenting out not needed
                custom_list_of_gdfs.append(gdf)
                
            elif gdf['tracker acro'].iloc[0] == 'GGIT-lng':
                # # # printf'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
                for row in gdf.index:
                    if gdf.loc[row, 'tracker_custom'] == 'GGIT - export':
                        gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT - export']['original_units'].values[0]
                        gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT - export']['conversion_factor'].values[0]
                    elif gdf.loc[row, 'tracker_custom'] == 'GGIT - import':  
                        gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT - import']['original_units'].values[0]
                        gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT - import']['conversion_factor'].values[0]

                custom_list_of_gdfs.append(gdf)

            else:
                # # # printf'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
                # This should apply to all rows not just one.
                gdf['tracker_custom'] = gdf["tracker acro"].iloc[0]
                gdf['original_units'] = conversion_df[conversion_df['tracker']==gdf['tracker acro'].iloc[0]]['original_units'].values[0]
                gdf['conversion_factor'] = conversion_df[conversion_df['tracker']==gdf['tracker acro'].iloc[0]]['conversion_factor'].values[0]
                custom_list_of_gdfs.append(gdf)

        custom_dict_list_gdfs_by_map_with_conversion[mapname] = custom_list_of_gdfs
    # # printf'This is custom dict: {custom_dict_list_gdfs_by_map_with_conversion}')
    # # # input('Check it, should have all trackers not just pipes!')
    
    # # printcustom_dict_list_gdfs_by_map_with_conversion.keys())
    # # # input('check that there are enough maps')
    return custom_dict_list_gdfs_by_map_with_conversion


def rename_gdfs(custom_dict_list_gdfs_by_map_with_conversion):
    renamed_one_gdf_by_map = {}
    # # printcustom_dict_list_gdfs_by_map_with_conversion.keys())
    # # # input('STOP HERE to see if all maps or not')
    for mapname, list_of_gdfs in custom_dict_list_gdfs_by_map_with_conversion.items():
        
        renamed_gdfs = []
        path_for_test_results = gem_path + mapname + '/test_results/'
        # # printmapname)
        # # printlen(list_of_gdfs))
        # # printgdf['tracker acro']) for gdf in list_of_gdfs]
        # # # input('Check if all trackers are there')
        for gdf in list_of_gdfs:
            print(gdf.columns)
            if 'Countries' in gdf.columns:
                print(gdf['Countries'])
            # declare which tracker we are at in the list so we can rename columns accordingly
            tracker_sel = gdf['tracker acro'].iloc[0] # GOGPT, GGIT, GGIT-lng, GOGET
            print(f'renamed on this {tracker_sel}')
            # all_trackers.append(tracker_sel)
            # select the correct renaming dict from config.py based on tracker name
            renaming_dict_sel = renaming_cols_dict[tracker_sel]
            # rename the columns!
            gdf = gdf.rename(columns=renaming_dict_sel) 
            print(gdf['areas'].value_counts())
            # input('check value counts for area after rename')
            if 'Countries' in gdf.columns:
                print(gdf['Countries'].value_counts())
                input('check value counts for Countries after rename only where applicable')
            renamed_gdfs.append(gdf)

        # concat all gdfs 
        one_gdf = pd.concat(renamed_gdfs, sort=False).reset_index(drop=True)
        # one_gdf = one_gdf.drop_duplicates(subset=['id', 'geometry']) # can I do this for coal mines? STOP DOING THIS, 
        # # # printf'This is oned_df columns lets see if there are two names: {one_df.columns}')
        # # printf'These are the final columns in config.py: {final_cols} in {mapname}')
        # # printf'These are the columns in one_gdf: {one_gdf.columns}')
        # # printf'These are the cols from gdf that are going to be removed: {set(one_gdf.columns) - set(final_cols)}')
        # # printf'These are the cols from final cols that need to be added to our gdf for it to work: {set(final_cols) - set(one_gdf.columns)}')
        cols_to_be_dropped = set(one_gdf.columns) - set(final_cols)
        # # if slowmo:
            # # input('Pause to check cols before filtering out all cols in our gdf that are not in final cols, there will be a problem if our gdf does not have a col in final_cols.')
        final_gdf = one_gdf.drop(columns=cols_to_be_dropped)
        # instead of filtering on a preset list, drop the extra columns using cols_to_be_dropped
        # final_gdf = one_gdf[final_cols]
        
        final_gdf.to_csv(f'{path_for_test_results}renamed_one_df_{iso_today_date}.csv',  encoding="utf-8")
        renamed_one_gdf_by_map[mapname] = final_gdf 
        # # print'Going on to next mapname')
    return renamed_one_gdf_by_map

# REMOVING THIS
# def remove_null_geo(renamed_one_gdf_by_map):
#     cleaned_dict_map_by_one_gdf = {}
#     # # # printset(concatted_gdf['geometry'].to_list()))
#     # # # printf'length of df at start of remove_null_geo: {len(concatted_gdf)}')
#     # concatted_gdf = concatted_gdf[concatted_gdf['geometry']!='null']
#     good_keywords = ['point', 'line']
#     for mapname, final_one_gdf in renamed_one_gdf_by_map.items():
#         # # printfinal_one_gdf.columns)
#         # # # input('Check that geometry is there in the final_one_gdf')
#         filtered_geo = final_one_gdf[final_one_gdf['geometry'].apply(lambda x: any(keyword in str(x).lower() for keyword in good_keywords))]
#         # # # printf'length of df at after filter for point and line geo: {len(filtered_geo)}')
#         # dropped_geo = pd.concat([final_one_gdf, filtered_geo], ignore_index=True).drop_duplicates(keep=False) 
#         # # printlen(dropped_geo))
#         # # printdropped_geo[['tracker acro', 'name', 'geometry']])  # 'lat', 'lng'
#         # # # input('Pause to check dropped geo')
#         cleaned_dict_map_by_one_gdf[mapname] = filtered_geo
    
      
#     # # printcleaned_dict_map_by_one_gdf.keys())
#     # # # input('check that there are enough maps')
#     return cleaned_dict_map_by_one_gdf


def capacity_conversions(cleaned_dict_map_by_one_gdf): 

# you could multiply all the capacity/production values in each tracker by the values in column C, 
# "conversion factor (capacity/production to common energy equivalents, TJ/y)."
# For this to work, we have to be sure we're using values from each tracker that are standardized
# to the same units that are stated in this sheet (column B, "original units").

# need to get nuances for each tracker, it's just GGIT if point then do lng terminal if line then do pipeline
    cleaned_dict_map_by_one_gdf_with_conversions = {}
    for mapname, one_gdf in cleaned_dict_map_by_one_gdf.items():
        gdf_converted = one_gdf.copy()
        if mapname in gas_only_maps:
            # # print'no need to handle for hydro having two capacities')
            continue
        else:
            # first let's get GHPT cap added 
            # # printmapname) # africa
            # # printset(gdf_converted['tracker acro'].to_list())) # only pipeline 
            ghpt_only = gdf_converted[gdf_converted['tracker acro']=='GHPT'] # for GGPT we need to re run it to get it 
            # # printlen(ghpt_only))
            gdf_converted = gdf_converted[gdf_converted['tracker acro']!='GHPT']
            # # printlen(ghpt_only['capacity']))
            # # printlen(ghpt_only['capacity1']))
            # # printlen(ghpt_only['capacity2']))
            # # # input('Check that they are all equal GHPT')
            ghpt_only['capacity'] = ghpt_only.apply(lambda row: row['capacity1'] + row['capacity2'], axis=1)
            gdf_converted = pd.concat([gdf_converted, ghpt_only],sort=False).reset_index(drop=True)
            # # # printlen(gdf_converted))
        
        gdf_converted['cleaned_cap'] = pd.to_numeric(gdf_converted['capacity'], errors='coerce')

        total_counts_trackers = []
        avg_trackers = []

        # # printf"this is all trackers: {set(gdf_converted['tracker acro'].to_list())}")
        
        gdf_converted['tracker acro'] = gdf_converted['tracker acro']
        # # printf"this is all trackers: {set(gdf_converted['tracker acro'].to_list())}")
        
        gdf_converted = gdf_converted[gdf_converted['tracker acro']!=''] # new to filter out nan


        for tracker in set(gdf_converted['tracker acro'].to_list()):
            total = len(gdf_converted[gdf_converted['tracker acro'] == tracker])
            sum = gdf_converted[gdf_converted['tracker acro'] == tracker]['cleaned_cap'].sum()
            avg = sum / total
            total_pair = (tracker, total)
            total_counts_trackers.append(total_pair)
            avg_pair = (tracker, avg)
            avg_trackers.append(avg_pair)
            
        for row in gdf_converted.index:
            cap_cleaned = gdf_converted.loc[row, 'cleaned_cap']
            tracker = gdf_converted.loc[row, 'tracker acro']
            if pd.isna(cap_cleaned):
                for pair in avg_trackers:
                    if pair[0] == tracker:
                        gdf_converted.loc[row, 'cleaned_cap'] = pair[1]
            cap_cleaned = gdf_converted.loc[row, 'cleaned_cap']
            # if pd.isna(cap_cleaned):
                # print'still na')
                # # input('still na')
    

        pd.options.display.float_format = '{:.0f}'.format
        gdf_converted['scaling_capacity'] = gdf_converted.apply(lambda row: conversion_multiply(row), axis=1)
        gdf_converted['capacity-table'] = gdf_converted.apply(lambda row: workaround_display_cap(row), axis=1)
        gdf_converted = workaround_no_sum_cap_project(gdf_converted) # adds capacity-details 
        gdf_converted['capacity-details'] = gdf_converted.apply(lambda row: workaround_display_cap_total(row), axis=1)
    
        cleaned_dict_map_by_one_gdf_with_conversions[mapname] = gdf_converted
    
          
    # # printcleaned_dict_map_by_one_gdf_with_conversions.keys())
    # # # input('check that there are enough maps')
    return cleaned_dict_map_by_one_gdf_with_conversions


def map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions):
    cleaned_dict_by_map_one_gdf_with_better_statuses = {}
    for mapname, gdf in cleaned_dict_map_by_one_gdf_with_conversions.items():
        path_for_test_results = gem_path + mapname + '/test_results/'           
        gdf_map_ready = gdf.copy()
    
        gdf_map_ready = fix_status_inferred(gdf_map_ready)
        
        # Create masks for the 'tracker acro' conditions
        mask_gcmt = gdf_map_ready['tracker acro'] == 'GCMT'
        mask_goget = gdf_map_ready['tracker acro'] == 'GOGET'
        # Update 'status' to 'Retired' where both masks are True
        gdf_map_ready['status'].fillna('', inplace=True)
        mask_status_empty = gdf_map_ready['status'] == ''
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
        # # # input(f'check no status df: {gdf_map_ready_no_status}')

        gdf_map_ready_no_status.to_csv(f'{path_for_test_results}no-status-africa-energy {iso_today_date}.csv')
        # make sure all statuses align with no space rule
        # gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.strip().replace(' ','-'))
        gdf_map_ready['status_legend'] = gdf_map_ready['status_legend'].apply(lambda x: x.strip().replace('_','-'))
        # # printset(gdf_map_ready['status'].to_list()))
        gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.lower())
        # # printset(gdf_map_ready['status'].to_list()))
        
        cleaned_dict_by_map_one_gdf_with_better_statuses[mapname] = gdf_map_ready
    
    # # printcleaned_dict_by_map_one_gdf_with_better_statuses.keys())
    # # # input('check that there are enough maps')
    return cleaned_dict_by_map_one_gdf_with_better_statuses



def map_ready_countries(cleaned_dict_by_map_one_gdf_with_better_statuses):
    cleaned_dict_by_map_one_gdf_with_better_countries = {}
    for mapname, gdf in cleaned_dict_by_map_one_gdf_with_better_statuses.items():
        gdf_map_ready = gdf.copy()
        # just need to make sure all countries are separated by a comma and have a comma after last country as well
        # GOGET has a hyphen in countries
        # GOIT has comma separated in countries
        # hydropower has two columns country1 and country2
        # GGIT has comma separated in countries
        # grouped_tracker_before = gdf.groupby('tracker acro', as_index=False)['id'].count()
        # # # printf'In map ready before adjustment: {grouped_tracker_before}')
        # # no return

        # gdf_map_ready['area2'] = gdf_map_ready['area2'].fillna('')
        if mapname not in gas_only_maps:
            # # printset(gdf_map_ready['area2'].to_list()))
            # # # input('All area2s in gdf check if any are numbers')
            for row in gdf_map_ready.index:

                if gdf_map_ready.loc[row, 'area2'] != '' and pd.notna(gdf_map_ready.loc[row, 'area2']):
                    print(f'in are2 not none {gdf_map_ready["areas"]}') # find the rows that are nan or float
                    ser = gdf_map_ready['areas']
                    try:
                        ser_str = ser.astype(str)
                    except:
                        for row in ser.index:
                            val = ser.at[row]
                            try:
                                val_str = str(val)
                            except:
                                print("Error!" + f" val couldn't be converted to str: {val}")
                    # # printgdf_map_ready.loc[row, 'area2'])
                    gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas'].strip()};{gdf_map_ready.loc[row, 'area2'].strip()};"
                    # # printf"Found a area2! Hydro? {gdf_map_ready.loc[row, 'areas']} {gdf_map_ready.loc[row, 'tracker acro']} {gdf_map_ready.loc[row, 'name']}")

                else:
                    # make it so all areas even just one end with a semincolon 
                    # gdf_map_ready['areas'] = gdf_map_ready['areas'].fillna('')
                    # nan_areas = gdf_map_ready[gdf_map_ready['areas']=='']
                    # print(f'in else: {gdf_map_ready["areas"]}') # find the rows that are nan or float
                    ser = gdf_map_ready['areas']
                    try:
                        ser_str = ser.astype(str)
                    except:
                        for row in ser.index:
                            val = ser.at[row]
                            try:
                                val_str = str(val)
                            except:
                                print("Error!" + f" val couldn't be converted to str: {val}")
                    
                    gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas'].strip()};"
            
        # grouped_tracker_after = gdf.groupby('tracker acro', as_index=False)['id'].count()

        # # # printf'In map ready after adjustment: {grouped_tracker_after}')
        cleaned_dict_by_map_one_gdf_with_better_countries[mapname] = gdf_map_ready  
    # # printcleaned_dict_by_map_one_gdf_with_better_countries.keys())
    # # # input('check that there are enough maps')
    return cleaned_dict_by_map_one_gdf_with_better_countries


def workarounds_eg_interim(cleaned_dict_by_map_one_gdf_with_better_countries):
    one_gdf_by_maptype = {}
    for mapname, gdf in cleaned_dict_by_map_one_gdf_with_better_countries.items():
        gdf = gdf.copy()

        # we would also want to overwrite the subnat and say nothing ""
        gdf['count_of_semi'] = gdf.apply(lambda row: row['areas'].split(';'), axis=1) # if len of list is more than 2, then split more than once
        gdf['count_of_semi'] = gdf.apply(lambda row: row['areas'].split('-'), axis=1) # for goget
        gdf['count_of_semi'] = gdf.apply(lambda row: row['areas'].split(','), axis=1) # just adding in case

        gdf['multi-country'] = gdf.apply(lambda row: 't' if len(row['count_of_semi']) > 1 else 'f', axis=1)
        # # printgdf['multi-country'])
        # if t then make areas-display 
        gdf['subnat'].fillna('', inplace=True)
        # if one country and subnat exists TEST THIS
        gdf['areas-subnat-sat-display'] = gdf.apply(lambda row: f"{row['subnat'].strip().strip(''),row['areas'].strip().strip('')}" if row['multi-country'] == 'f' and row['subnat'] != '' else '', axis=1)
        # if more than one country replace the '' with mult countries
        
        maskt = gdf['mult_country']=='t'
        gdf.loc[maskt, 'areas-subnat-sat-display'] = 'multiple areas/countries'

        print(gdf[gdf['areas-subnat-sat-display']!=''])
        # print(gdf[gdf['id']=='P0539'])
        input('check subnat mult countries test')
        list_invalid_goget = []
        if mapname == 'GIPT':
            # does not have goget
            one_gdf_by_maptype[mapname] = gdf 
            
        else:
            # # # printgdf.columns)
            # # # input('Check if prod-oil is there in columns')
            for row in gdf.index:

                tracker = (gdf.loc[row, 'tracker acro'])
                #if goget then make capacity table and capacity details empty
                

                if tracker == 'GOGET':
                    gdf.loc[row, 'capacity-table'] = ''
                    gdf.loc[row, 'capacity-details'] = ''
                    prod_oil = gdf.loc[row, 'prod_oil']
                    prod_gas = gdf.loc[row, 'prod_gas']
                    # prod_oil = check_and_convert_float(prod_oil) # NEW TO TEST FOR ROUNDING ALL GETTING CAUGH TIN INVALID GOGET
                    # prod_gas = check_and_convert_float(prod_gas)

                    try: # NEW TO DO TEST REMOVING THIS
                        # round it then if either is '' we can remove it later we filter on it before adding to table or details
                        prod_oil = prod_oil.replace(r'[^\d.-]', '', regex=True)
                        prod_oil= prod_oil.replace('', np.nan)
                        prod_oil = prod_oil.astype(float)     
    
                        prod_oil = str(float(round(prod_oil, 2)))

                        gdf.loc[row, 'prod-oil-table'] = f'{prod_oil} million bbl/y'
                        gdf.loc[row, 'prod-oil-details'] = f'{prod_oil} (million bbl/y)'
                    except:
                        list_invalid_goget.append(prod_oil)
                        # # print'invalid goget')
                        # TODO handle these cases and then create a test to confirm it's fixed
                        
                        
                    try:
                        prod_gas = prod_gas.replace(r'[^\d.-]', '', regex=True)
                        prod_gas  = prod_gas .replace('', np.nan)

                        prod_gas = str(float(round(prod_gas, 3)))
                        prod_gas  = prod_gas.astype(float)

                        gdf.loc[row, 'prod-gas-table'] = f'{prod_gas} million m³/y'
                        gdf.loc[row, 'prod-gas-details'] = f'{prod_gas} (million m³/y)'
                        
                    except:
                        list_invalid_goget.append(prod_gas)

                        # # print'invalid goget')
                        # TODO handle these cases and then create a test to confirm it's fixed

                
        one_gdf_by_maptype[mapname] = gdf 
    # # printone_gdf_by_maptype.keys())
    return one_gdf_by_maptype


def last_min_fixes(one_gdf_by_maptype, needed_geo_for_region_assignment):
    one_gdf_by_maptype_fixed = {}
    # # printone_gdf_by_maptype.keys())
    # # # input('check that GIPT is in the above')
    for mapname, gdf in one_gdf_by_maptype.items():
        gdf = gdf.copy()
        # # printlen(gdf))
        # gdf['name'] = gdf['name'].fillna('')
        # gdf['url'] = gdf['url'].fillna('')
        # gdf['geometry'] = gdf['geometry'].fillna('')
        # # printgdf.columns)
        # TODO for now remove drop to understand why all GOGET empty is now not being filled and also prod doesn't come through
        # gdf = gdf.drop(['original_units','conversion_factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'Latitude', 'Longitude'], axis=1) # 'cleaned_cap'
        # handle countries/areas ? 
        # gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) # reverse this one special case back 
        # # printf'Missing areas: {gdf[gdf["areas"]==""]}') # check if missing!!   
        # # # input('Handle missing countries')
        # handle situation where Guinea-Bissau IS official and ok not to be split into separate countries 
        gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) 
        
        # something is happening when we concat, we lose goget's name ... 
        # gdf_empty_name = gdf[gdf['name']=='']
        # # # printf"This is cols for gdf: {gdf.columns}")
        gdf['wiki-from-name'] = gdf.apply(lambda row: f"https://www.gem.wiki/{row['name'].strip().replace(' ', '_')}", axis=1)
        # row['url'] if row['url'] != '' else 
        # handles for empty url rows and also non wiki cases SHOULD QC FOR THIS BEFOREHAND!! TO QC
        # need to switch to '' not nan so can use not in
        gdf['url'].fillna('',inplace=True)
        gdf['url'] = gdf.apply(lambda row: row['wiki-from-name'] if 'gem.wiki' not in row['url'] else row['url'], axis=1)
        
        # gdf['name'] = gdf.apply(lambda row: row['name'] if row['name'] != '' else row['url'].split('www.gem.wiki/')[1].replace('_', ' '))

        gdf_empty_url = gdf[gdf['url'] == '']

        # assign Africa to all regions
        # gdf['region'] = 'Africa'
        # list_of_needed_geo_countries = needed_geo_for_region_assignment[mapname][1]
        # # printlist_of_needed_geo_countries)
        # DO WE WANT THIS FOR SOME REASON? probalby not for the cross-continental ones...
        # # # input('Check this is a list of countries, otherwise may need to adjust how we access the 2nd value of the dictionary') # if it is then we can assign a region based off of it
        # if 'Brazil' in list_of_needed_geo_countries:
        #     gdf['region'] = 'Americas'
        # elif 'China' in list_of_needed_geo_countries:
        #     gdf['region'] = 'Asia'
        # elif 'Mozambique' in list_of_needed_geo_countries:
        #     gdf['region'] = 'Africa'
        # elif 'United Kingdom' in list_of_needed_geo_countries:
        #     gdf['region'] = 'Europe'
        # else:
        #     gdf['region'] = ''
            # # printf'No region found for gdf: {gdf["tracker"].iloc[0]} for map: {mapname}')
            
        
        gdf.columns = [col.replace('_', '-') for col in gdf.columns]    
        # let's also look into empty url, by tracker I can assign a filler
        
        # gdf['url'] = gdf['url'].apply(lambda row: row[filler_url] if row['url'] == '' else row['url'])
        
        # gdf['capacity'] = gdf['capacity'].apply(lambda x: x.replace('--', '')) # can't do that ... 
        
        # translate acronyms to full names 
        
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
        gdf.fillna('', inplace=True)        
        one_gdf_by_maptype_fixed[mapname] = gdf
    # # printone_gdf_by_maptype_fixed.keys())
    return one_gdf_by_maptype_fixed

def create_map_file(one_gdf_by_maptype_fixed):
    final_dict_gdfs = {}
    # # printone_gdf_by_maptype_fixed.keys())
    # # # input('STOP HERE - why only one map being printed??')

    for mapname, gdf in one_gdf_by_maptype_fixed.items():
        path_for_download_and_map_files = gem_path + mapname + '/compilation_output/'

        # # printf'We are on map: {mapname} there are {len(one_gdf_by_maptype_fixed)} total maps')
        # # printf"This is cols for gdf: {gdf.columns}")
        # # # input('STOP HERE')
        # drop columns we don't need
        if mapname in gas_only_maps: # will probably end up making all regional maps all energy I would think
            gdf = gdf.drop(['count-of-semi', 'multi-country', 'original-units', 'conversion-factor', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1)
        
        else:
            gdf = gdf.drop(['count-of-semi', 'multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1)

        # # # printgdf.info())
        check_for_lists(gdf)
        # # if slowmo:
            # # input('Check what is a list')
        gdf.to_file(f'{path_for_download_and_map_files}{mapname}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
        gdf.to_file(f'/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{mapname}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')

        # gdf_to_geojson(gdf, f'{path_for_download_and_map_files}{geojson_file_of_all_africa}')
        # # printf'Saved map geojson file to {path_for_download_and_map_files}{mapname}_{iso_today_date}.geojson')

        gdf.to_excel(f'{path_for_download_and_map_files}{mapname}_{iso_today_date}.xlsx', index=False)
        gdf.to_excel(f'/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{mapname}_{iso_today_date}.xlsx', index=False)

        # # printf'Saved xlsx version just in case to {path_for_download_and_map_files}{mapname}_{iso_today_date}.xlsx')
        final_dict_gdfs[mapname] = gdf
    # # printfinal_dict_gdfs.keys())
    return final_dict_gdfs

###############
# MAKE DOWNLOAD FILE #
###############
def create_data_dwnld_file(dict_list_dfs_by_map):
    result = {}
    for mapname, list_dfs in dict_list_dfs_by_map.items():
        # reorder list_dfs to be in final format order_datadownload
        # pull in about pages to go along side them 
        # starting first with the multi tracker about page
        # Test first
        # # print'Starting test prior to loop')
        total_dfs = len(list_dfs)
        tracker_counter = Counter()
        for df in list_dfs:
            tracker_counter.update(df['tracker acro'])
        result[mapname] = {
            'total_dfs': total_dfs,
            'tracker_counts': tracker_counter
        }
        # for map_name, stats in result.items():
            # printf"Map: {map_name}")
            # printf"Total number of DataFrames: {stats['total_dfs']}")
            # printf"Tracker counts: {stats['tracker_counts']}")
            # print"-" * 40)
        # # # input('Check test')        
        
        
        # # printf'Creating data download file for {mapname}')
        path_for_download_and_map_files = gem_path + mapname + '/compilation_output/'
        os.makedirs(path_for_download_and_map_files, exist_ok=True)
        
        xlsfile = f'{path_for_download_and_map_files}{mapname}-data-download {new_release_date}.xlsx'
        xlsfile_testing = f'/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{mapname}-data-download {new_release_date}.xlsx'
        for file_name in [xlsfile, xlsfile_testing]:
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:    
                for df in list_dfs:
                    df = df.reset_index(drop=True)
                    tracker_curr = df['official_name'].loc[0]
                    # # printf'Adding this tracker to dt dwnld: {tracker_curr}')
                    # # printf'About page data pulled for {(about_df_dict_by_map.keys)} maps.')                
                    # if slowmo:
                        # # input('Check cols')
                    columns_to_drop = ['tracker acro', 'float_col_clean_lat', 'float_col_clean_lng', 'official_name']
                    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
                    # Drop the existing columns
                    if existing_columns_to_drop:
                        df = df.drop(columns=existing_columns_to_drop)
                    df.to_excel(writer, sheet_name=f'{tracker_curr}', index=False)
                    # printf"DataFrame {tracker_curr} written to {file_name}")
        

    # # printdict_list_dfs_by_map.keys())
    return writer



###############
# MAKE ABOUT FILE #
###############

def gather_all_about_pages(prev_key_dict, prep_df, new_release_date, previous_release_date, needed_tracker_geo_by_map):
    # first iterate by map key in dict needed_tracker_geo_by_map
    # make it so that with mapname and dict of about is return
    # official name for sheet: {about page df}
    about_df_dict_by_map = {} # map name: list of tuples with the about page name and about page dfs for each tracker as well as overarching one
    for mapname, list_of_dfs_trackers_geo_prev_info in needed_tracker_geo_by_map.items():
        # needed_trackers = value[0] # list of tracker names to include in list of dfs
        # needed_geo = value[1] # list of countries or global for gipt to filter each df in the list by
        list_of_tuples_holding_about_page_name_df = []
        # TODO make a list in config of all previous releases to gather about page for multi tracker
        # most_recent_map_results = list_of_dfs_trackers_geo_prev_info[2] # it is the third item in the list, this may not be true anymore
        # prev_key = most_recent_map_results.iloc[0, most_recent_map_results.columns.get_loc('key')]
        prev_key = prev_key_dict[mapname]

        # # printf'Creating about page file for map: {mapname} with prev key {prev_key}') # Africa Energy, Asia Gas, Europe Gas, LATAM SKIP #  GIPT FOR NOW        
        
        # about_df_dict = {} # official name for sheet: {about page df}
        gspread_creds = gspread.oauth(
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
                credentials_filename=client_secret_full_path,
                # authorized_user_filename=json_token_name,
            )
        wait_time = 5
        time.sleep(wait_time)
        gsheets = gspread_creds.open_by_key(prev_key) # this is the last release for this map
            # List all sheet names
        sheet_names = [sheet.title for sheet in gsheets.worksheets()]
        # # printf"Sheet names previous release:", sheet_names)

        multi_tracker_about_page = sheet_names[0]
        multi_tracker_about_page = gsheets.worksheet(multi_tracker_about_page) 
        multi_tracker_data = pd.DataFrame(multi_tracker_about_page.get_all_values())
 
        list_of_tuples_holding_about_page_name_df.append((f'About {mapname}', multi_tracker_data))
    
        needed_trackers = list_of_dfs_trackers_geo_prev_info[0] # list of tracker names to include in list of dfs

        for tracker in needed_trackers:
            # # printtracker)
            if tracker == 'Oil & Gas Extraction':
                # currently Scott makes a special file for releases for maps 
                # this is the actual release file
                tracker_key = '1fdXqNS40NZuIVJreNZKkz1qZd5LB7avQuBQfhOByvgc'
            # these are separate from geojson data so not in prepdf, in config
            elif tracker == 'Gas Pipelines':
                tracker_key = about_page_ggit_goit[tracker]
            elif tracker == 'LNG Terminals':
                tracker_key = about_page_ggit_goit[tracker]
            elif tracker == 'Oil Pipelines':
                 tracker_key = about_page_ggit_goit[tracker]
                
            else:
                tracker_key = prep_df[prep_df['official name'] == tracker]['gspread_key'].values[0]

            gsheets = gspread_creds.open_by_key(tracker_key)
            sheet_names = [sheet.title for sheet in gsheets.worksheets()]
            # # printsheet_names)
            # # # input('Check tracker, key and sheet names')
            for sheet in sheet_names:
                # # printsheet)
                if 'About' in sheet:
                    about_sheet = gsheets.worksheet(sheet)
                    about_data = pd.DataFrame(about_sheet.get_all_values())
                    list_of_tuples_holding_about_page_name_df.append((f'About {tracker}', about_data))

                    # about_df_dict_by_map[mapname] = (f'About {new_tracker}', about_data)
                    # # printf'Found About page for {tracker}')
                    # # # input('check about page')
                    # # # printlist_of_tuples_holding_about_page_name_df)
                    break
                elif 'Copyright' in sheet:
                    about_sheet = gsheets.worksheet(sheet)
                    about_data = pd.DataFrame(about_sheet.get_all_values())
                    # about_df_dict_by_map[mapname] = (f'About {new_tracker}', about_data)
                    list_of_tuples_holding_about_page_name_df.append((f'About {tracker}', about_data))

                    # # printf'Found About page for {tracker} in Copyright.')
                    # # # input('check about page')
                    break

                else:
                    # printf'No about page for {tracker} found. Check the gsheet tabs')
                    # # # input('check about page')
                    continue

        about_df_dict_by_map[mapname] = list_of_tuples_holding_about_page_name_df

    return about_df_dict_by_map

    
def create_about_page_file(about_df_dict_by_map):

    for mapname, about_tab_df_tuple in about_df_dict_by_map.items():
        path_for_download_and_map_files = gem_path + mapname + '/compilation_output/' 

        about_output = f'{path_for_download_and_map_files}{mapname}_about_pages_{new_release_date}.xlsx'  
        # # printabout_output)    
        # # input('Check')     
        # pull out previous overall about page - done in dict
        with pd.ExcelWriter(about_output, engine='xlsxwriter') as writer:
            for about_tuple in about_tab_df_tuple:
                about_tab_name = about_tuple[0]
                about_data = about_tuple[1]
                
                # # printf'About page for {about_tab_name} has {len(about_data)} rows.')
                # if slowmo:
                    # input('Check about page')
                about_data.to_excel(writer, sheet_name=f'{about_tab_name}', index=False)

            # # printf'Saved about page sheets to {about_output} for {len(list_of_tuples_holding_aboutpagetabname_aboutpagedata)} trackers including the multi-tracker one.')
            
        return None

#########################
### SUMMARY FILES ###
#########################

# TODO maybe do this once it is one_gdf so we have consistent column names
def create_summary_files(dict_list_dfs): # map name: list of filtered dfs for map
    # go through each df
    types_of_pivots = {'all': ['Country', 'Owner', 'Start year', 'Province']} # come back to this, can be {tracker name: [list of specific pivot types]}
    cols_to_organize = ['Status', 'Start year']
    cols_to_sum = ['Capacity', 'Kilometers']
    cols_to_count = ['Project Name']
    status_filter = ['operating', 'prospective']
    country_filter = ['China']
    
    dict_of_summary_dfs = {} # {mapname: [list of summary dfs]}
    list_of_summary_dfs = []
    for mapname, list_dfs in dict_list_dfs.items():
        for df in list_dfs:
            # have a list of all files needed
            # do a groupby to create the df for each file
            df = df.reset_index(drop=True)
            # # printf'this is df cols: {df.cols}') # yep it was reset issue, just needs consistnet column names no Country
            tracker = df['tracker acro'].loc[0]
            # # printf'Creating summary files for {tracker}')
            for pivot_type in types_of_pivots['all']:
                pivot = df.groupby([pivot_type, 'Status'])['Capacity'].sum().reset_index() 
                list_of_summary_dfs.append(pivot)
    dict_of_summary_dfs[mapname] = list_of_summary_dfs
    # TODO save each df to a gsheet and or excel
    df = pd.DataFrame(dict_of_summary_dfs)
    sheet = gspread_creds.open("https://docs.google.com/spreadsheets/d/18zyOMB7S_bAnvFDOPqC1emPA_AT1OMO26CXzTjpwN7o/edit?gid=0#gid=0").sheet1  # Use .worksheet("Sheet Name") to specify a sheet
    set_with_dataframe(sheet, df)
    
    return None

def pull_existing_summary_files(prep_df):
    # in prep_df get the URL for each tracker's summary tables
    # using scrapy or bs go to the site and find each summary table by the div
    # pull the google link 
    # read the google link into df with gspread
    # pull the title
    # compare title to the needed ones for AET
    # if in their pull it and filter for Africa so we can compare to the new one
    # we can compare manually for now
    return None


#### Oil and Gas Plants https://globalenergymonitor.org/projects/global-oil-gas-plant-tracker/summary-tables/
# Oil and Gas Plants by Country/Area (MW)
# Oil and Gas Plants by Country/Area (Power Stations)
# Oil and Gas Plants by Country/Area (Units)
# Oil and Gas Plants by Region (MW)
# Ownership of Oil and Gas Plants in Africa (MW)
# Oil and Gas Plants by Technology by Country/Area (MW)
###### Coal Plants https://globalenergymonitor.org/projects/global-coal-plant-tracker/summary-tables/
# Coal Plants by Country/Area (MW)
# Coal Plants by Country/Area (Power Stations)
# Coal Plants by Country/Area (Units)
# Coal Plants by Region (MW)
###### Geothermal https://globalenergymonitor.org/projects/global-geothermal-power-tracker/summary-tables/
# Geothermal Power Capacity by Country/Area (MW)
# Geothermal Unit Count by Country/Area
# Geothermal Power Capacity by Installation Type and Region (MW)
# Geothermal Operational Capacity Installed by Country/Area and Year (MW)
# Geothermal Prospective Capacity by Country/Area and Year (MW)
###### Bioenergy https://globalenergymonitor.org/projects/global-bioenergy-power-tracker/summary-tables/
# Bioenergy Capacity by Country/Area (MW)
# Bioenergy Unit Count by Country/Area
# Bioenergy Fuel Types by Country/Area
# Bioenergy Capacity by Region (MW)
# Bioenergy Unit Count by Region
# Bioenergy Fuel Types by Region
# Bioenergy Operational Capacity Added by Country/Area and Year (MW)
###### Wind https://globalenergymonitor.org/projects/global-wind-power-tracker/summary-tables/
# Wind Farm Capacity by Country/Area (MW)
# Wind Farm Phase Count by Country/Area
# Wind Farm Capacity by Region (MW)
# Wind Farm Phase Count by Region
# Wind Farm Capacity by Installation Type and Region (MW)
# Wind Farm Operational Capacity by Country/Area and Year (MW)
# Wind Farm Prospective Capacity by Country/Area and Year (MW)
####### Solar https://globalenergymonitor.org/projects/global-solar-power-tracker/summary-tables/
# Solar Farm Capacity by Country/Area (MW)
# Solar Farm Phase Count by Country/Area
# Solar Farm Capacity by Region (MW)
# Solar Farm Phase Count by Region
# Solar Farm Operational Capacity by Country/Area and Year (MW)
# Solar Farm Prospective Capacity by Country/Area and Year (MW)
####### Hydropower https://globalenergymonitor.org/projects/global-hydropower-tracker/summary-tables/
# Hydropower Capacity by Country/Area (MW)
# Hydropower Project Count by Country/Area
# Hydropower Capacity by Region and Subregion (MW)
# Hydropower Project Count by Region and Subregion
# Hydropower Capacity by Region and Type (MW)
###### Nuclear https://globalenergymonitor.org/projects/global-nuclear-power-tracker/summary-tables/
# Nuclear Power Capacity by Country/Area (MW)
# Nuclear power Unit Count by Country/Area
# Nuclear Power Capacity by Region and Subregion (MW)
# Nuclear Power Unit Count by Region and Subregion
# Nuclear Power Capacity by Reactor Type and Region (MW)
###### Oil & Gas Pipelines https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/summary-tables/ ; https://globalenergymonitor.org/projects/global-oil-infrastructure-tracker/summary-tables/
# Gas Pipeline Length by Country/Area (km)
# Gas Pipeline Length by Region (km)
# Oil Pipeline Length by Country/Area (km)
# Oil Pipeline Length by Region (km)
####### LNG Terminals https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/summary-tables/
# LNG Export Projects by Region
# LNG Export Projects by Country/Area
# LNG Import Projects by Region
# LNG Import Projects by Country/Area
# LNG Export Capacity by Region (mtpa)
# LNG Export Capacity by Country/Area (mtpa)
# LNG Import Capacity by Region (mtpa)
# LNG Import Capacity by Country/Area (mtpa)
# LNG Terminals by Start Year
# LNG Capacity by Start Year (mtpa)
######## Coal Terminals https://globalenergymonitor.org/projects/global-coal-terminals-tracker/summary-tables/
# Number of Coal Terminals by Country/Area
# Coal Terminal Capacity by Country/Area
# Coal Terminal Capacity by Region
# Coal Terminal Capacity by Type (Import/Export)
######### Oil & Gas Extraction https://globalenergymonitor.org/projects/global-oil-gas-extraction-tracker/summary-tables/
# Oil & Gas Extraction Sites by Region
# Oil & Gas Extraction Sites by Country/Area
# Oil Production by Sub Region
# Oil Production by Country/Area
# Gas Production by Region
# Gas Production by Country/Area
########## Coal Mines https://globalenergymonitor.org/projects/global-coal-mine-tracker/summary-tables/
# Number of Coal Mines by Country/Area
# groupby count on country/area filtered for Africa
#####################

#######################
### FORMAT & EXECUTION #####
#######################

def reorder_dwld_file_tabs(about_df_dict_by_map, incorporated_dict_list_dfs_by_map):
    # use this file as order for tabs /Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/africa-energy/compilation_output/2024-08-15/africa_energy_tracker_2024-08-15.xlsx 
    # about page dict jhold all tracker about page data
    # incorporated dict list dfs holds tabular data as well as overarching map about page
    # about_df_dict_by_map {mapname: {tab_name: tab_data_df}, mapname2: {tab_name: tab_data_df}}
    # incorporated_dict_list_dfs_by_map {mapname: [list_d,fs_filt,ered_for_ma,p], mapname2: [list_dfs,filter,ed_for,_map]}
    
    # pull from local files, per map, about and data download 
    print(final_order_datadownload) # print ones that are relevant to map
    # TODO apply format_final() on a df at some point
    priority = ['africa']
    if local_copy:
        for mapname in ['africa', 'asia', 'europe', 'latam']:
            if mapname in priority:
                path_for_download_and_map_files = gem_path + mapname + '/compilation_output/'

                for file in os.listdir(path_for_download_and_map_files): # use key for map name
                    if file.endswith(".xlsx") & (new_release_date in file) & ('download' in file): 
                        print(f'{path_for_download_and_map_files}{file}')
                        dd_df_dict = pd.read_excel(f'{path_for_download_and_map_files}{file}') # TODO rework so it pulls all tabs
                        
                    elif file.endswith(".xlsx") & (new_release_date in file) & ('about' in file): 
                        print(f'{path_for_download_and_map_files}{file}')
                        about_df_dict = pd.read_excel(f'{path_for_download_and_map_files}{file}')  # TODO rework so it pulls all tabs
                          
                print(f'Length of {mapname} dd: {len(dd_df_dict)}')    
                print(f'Length of {mapname} about: {len(about_df_dict)}')
                print(dd_df_dict.keys()) # TODO handle this 
                print(about_df_dict.keys())  
                input()
                output = f'{path_for_download_and_map_files}{mapname}-energy-tracker-data-download-with-about {new_release_date}.xlsx'        
                final_order = {}
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # TODO handle getting the overall tracker about page
                    # for tab, df in about_df_dict.items():
                        
                    #         final_order = {f'About {mapname.title()} Energy Tracker': df} 
                    #         df.to_excel(writer, sheet_name=f'About {mapname.title()} Energy Tracker', index=False)    
                    #            first_about_page = next(iter(about_df_dict[mapname].items()))   # TEST this it should work if about_df_dict is dict of excel of all about pages   
   
                    for tracker_official in final_order_datadownload:
                        final_order[f'About {tracker_official}'] = about_df_dict[f'About {tracker_official}']
                        final_order[tracker_official] = dd_df_dict[tracker_official]

                        about_df_dict[f'About {tracker_official}'].to_excel(writer, sheet_name=f'About {tracker_official}', index=False)
                        dd_df_dict[tracker_official].to_excel(writer, sheet_name=f'{tracker_official}', index=False)         
         
            else:
                continue
    else:  # TODO SIMPLIFY THIS WHOLE PIECE We want to go ghrough tabular df and about df and one final order use that to print to final ecel          
        for mapname, map_df_dict in incorporated_dict_list_dfs_by_map.items():
            
            path_for_download_and_map_files = gem_path + mapname + '/compilation_output/'

            output = f'{path_for_download_and_map_files}{mapname}-energy-tracker-data-download-with-about {new_release_date}.xlsx'        

            # first_about_page = next(iter(about_page_dict.items()))
            first_about_page = next(iter(about_df_dict_by_map[mapname].items()))

            # final_order = {'Africa Energy Tracker': (first_about_page[1])} # tab name: (df of about data, df of tracker/tabular data)
            # go through each item in the dict and list of dfs, pair up the tracker info, then put them in order based on prev key
            final_order = {first_about_page[0]: (first_about_page[1])} 

            for tracker_official in final_order_datadownload:
                    
                for about_sheetname, about_df in about_df_dict_by_map[mapname].items():
                    # # printf'This is about sheetname: {about_sheetname}')
                    # sheetname holds the tracker name official 
                    # df holds the about page info
                    # # # input('check item')
                    trackername = about_sheetname.split('About ')[1].strip()
                    # # printf'This is tracker name from sheet name about: {trackername}')
                    if trackername == tracker_official:
                        # for tabular_df in map_df_dict[trackername]: # TEST TODO I think this is wrong so commenting out
                            tabular_df = map_df_dict[trackername].reset_index(drop=True)
                            # # printtabular_df.columns)
                            # # printlen(tabular_df))
                        
                            # # printf'This is official name from tabular df: {tabular_df["official_name"]}')
                            # tracker = tabular_df['official_name'].loc[0] # trakce should already eqult trackername ... so this should be redundant
                            # if tracker == tracker_official:
                            # # printf'Found {trackername} in list of dfs.')
                            final_order[trackername] = (about_df, tabular_df) 
                            break # break out of loop in the about df, go to next in outer loop of final order datadownlaod
        # printfinal_order)
        # input('check final order')
            
        # pull out previous overall about page - done in dict
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

            for trackername, about_tabular_tuple in final_order.items():
                # # printf'About page for {trackername} has {len(about_tabular_tuple[0])} rows.')
                # if slowmo:
                    # input('Check about page')
                about_tabular_tuple[0].to_excel(writer, sheet_name=f'About {trackername}', index=False)   
                
                # if trackername == 'Africa Energy Tracker':
                #     continue
                # else:
                # # printf'Tabular data for {trackername} has {len(about_tabular_tuple[1])} rows.')
                # if slowmo:
                    # input('Check tabular data')                 
                about_tabular_tuple[1].to_excel(writer, sheet_name=f'{trackername}', index=False)   

    return final_order


### email google sheet of final download file and summary pages #####


#########################
#### RUN TEST OF FILE ###
# def col_differences(df):
    # todo pull over what you have in the other script for release notes to help highlight code changes
    # needed based on column name changes 

def df_info(df, key):
    # find all col name changes 
    # if slowmo:
        # printdf.info())
        # # input('Check df info')

    # numerical_cols = ['Capacity (MW)', 'Start year', 'Retired year', 'Planned retire', 'Latitude', 'Longitude']
    numerical_cols = ''
    col_info = {}
    
    for col in df.columns:                
        if 'ref' in col.lower():
            # # print'ref found pass')
            continue
        else:  
            col_values = set(df[col].to_list()) # len can be a lot, cap at 30
            col_dtype = df[col].dtype # len = 1
            if col in numerical_cols:
                col_range = [df[col].min(), df[col].max()] # len = 2
                col_mid = df[col].mean() # len = 1
                col_sum = df[col].sum()   # len = 1
            else:
                col_range = ''
                col_mid = ''
                col_sum = ''
            # cap for readability 
            if len(col_values) > 5:
                col_sample = list(col_values)[:5]
            else:
                col_sample = list(col_values)
            col_info[col] = {'col_len': len(col_values), 'col_dtype': col_dtype, 'col_sample': col_sample,'col_range': col_range, 'col_mid': col_mid, 'col_sum': col_sum}
        
    col_info_df = pd.DataFrame(col_info)
    col_info_df = col_info_df.T # transpose
    # if slowmo:

        # printcol_info_df)

        # # input(f'Check col info for {key}')
    col_info_df.to_csv(f'test_results/{key}_column_info_{iso_today_date}.csv',  encoding="utf-8")
    # # printf'saved col info for {key} here: "test_results/{key}_column_info_{iso_today_date}.csv"')

def final_count(final_dict_gdfs):
    # # printfinal_dict_gdfs.keys())
    # # # input('check that there are enough maps')
    for mapname, gdf in final_dict_gdfs.items():
        grouped_tracker = gdf.groupby('tracker acro', as_index=False)['id'].count()
        # # printmapname)
        # # print# # printgrouped_tracker))
        # # # input('Review above')

    # no return
    
def compare_prev_current(prev_geojson, curr_geojson):
    
    gdf1 = gpd.read_file(prev_geojson)
    gdf2 = gpd.read_file(curr_geojson)
    # Find all differences between gdf1 and gdf2
    symmetric_difference_gdf = gpd.GeoDataFrame(pd.concat([gdf1, gdf2]).drop_duplicates(keep=False))
    # # printsymmetric_difference_gdf)
    # # input('Check symmetric difference')


def check_expected_number(list_dfs):

    curr_geojson = f'{path_for_download_and_map_files}{tracker_folder}_{iso_today_date}.geojson'
    curr_gdf = gpd.read_file(curr_geojson)
    # # printf'Current number of rows in geojson: {len(curr_gdf)}')
    grouped_tracker = curr_gdf.groupby('tracker acro', as_index=False)['id'].count()
    # # print# # printgrouped_tracker))
    # # input('Check current number of rows')
    
    summed_from_dfs = 0
    for df in list_dfs:
        # # printf"{len(df)} {df['tracker acro'].loc[0]}")
        summed_from_dfs += len(df)
    
    # # printf'Sum of all dfs: {summed_from_dfs}')
    
    # number in map by region and tracker compared to source tracker data filtered by that region
    # GCPT 433 africa
    # GCMT 186 africa
    # GCTT 22 africa
    # GOGPT 714 africa
    # GOGET 578 africa (there are ones missing for country, need to use region, whereas latam needs countries, unless you take the first from the country if there's a hyphen)
    # Solar 844 africa
    # Wind 315 africa (region gives 3 more)
    # Nuclear 14 africa
    # Bioenergy 44 africa
    # Geothermal 39 africa
    # Hydro 218 africa
    
    return 

################

### CALL ALL FUNCTIONS ###
# REFACTOR where it goes through on a map by map basis, runs through and saves the files so can move along with testing it
# currently it filters it all, creates all downloads for all maps 
if augmented:
    print('Start augmented')
    needed_map_and_tracker_dict = what_maps_are_needed(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab)
    # map_country_region has the list of needed maps to be created and their countries/regions
    needed_tracker_geo_by_map = what_countries_or_regions_are_needed_per_map(multi_tracker_countries_sheet, needed_map_and_tracker_dict)
    # TODO for about generation maybe add in the prev_key for each map's results
    # needed_tracker_geo_by_map = pull_in_prev_key_map(needed_tracker_geo_by_map, multi_tracker_log_sheet_key)
    folder_setup(needed_tracker_geo_by_map)
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('Ended augmented')
if data_filtering:
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('Start data filtering')
    prep_df = create_prep_file(multi_tracker_log_sheet_key, prep_file_tab) 
    conversion_df = create_conversion_df(conversion_key, conversion_tab)

    dict_list_dfs_by_map, dict_list_gdfs_by_map = pull_gsheet_data(prep_df, needed_tracker_geo_by_map) # map_country_region
    incorporated_dict_list_gdfs_by_map, incorporated_dict_list_dfs_by_map = incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson,dict_list_dfs_by_map, dict_list_gdfs_by_map) 
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('Ended data filtering')


if summary_create: # rename then concat the dfs for this, then reverse rename and split up again for actual summary tables, check numbers align with original 
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('Start summary creation')
    one_df = rename_concat(incorporated_dict_list_dfs_by_map) # TO CREATE
    pull_existing_summary_files(prep_df) # why do we need this? 
    create_summary_files(one_df) # TODO HANDLE THIS ONE for dict
    push_summary_files(one_df) # TO CREATE
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('End summary creation')
    
if about_create: 
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('Start about creation')
    about_df_dict_by_map = gather_all_about_pages(prev_key_dict, prep_df, new_release_date, previous_release_date, needed_tracker_geo_by_map)
    create_about_page_file(about_df_dict_by_map)
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print(f'End about creation {elapsed_time}')

if dwlnd_create:
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print(f'Start dwlnd creation {elapsed_time}')
    create_data_dwnld_file(incorporated_dict_list_dfs_by_map) 
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print(f'End dwlnd creation {elapsed_time}')
    
if refine:
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('Start refining')
    if local_copy:
        about_df_dict_by_map = ''
        incorporated_dict_list_dfs_by_map = ''
    reorder_dwld_file_tabs(about_df_dict_by_map, incorporated_dict_list_dfs_by_map) 
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('End refining')    

    
if map_create:
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('Start map file creation')
    custom_dict_list_gdfs_by_map = split_goget_ggit(incorporated_dict_list_gdfs_by_map)  #incorporated_dict_list_gdfs_by_map
    custom_dict_list_gdfs_by_map_with_conversion = assign_conversion_factors(custom_dict_list_gdfs_by_map, conversion_df)
    renamed_one_gdf_by_map = rename_gdfs(custom_dict_list_gdfs_by_map_with_conversion)
    # cleaned_dict_map_by_one_gdf = remove_null_geo(renamed_one_gdf_by_map) # doesn't do anything
    cleaned_dict_map_by_one_gdf_with_conversions = capacity_conversions(renamed_one_gdf_by_map)
    cleaned_dict_by_map_one_gdf_with_better_statuses = map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions)
    
    cleaned_dict_by_map_one_gdf_with_better_countries = map_ready_countries(cleaned_dict_by_map_one_gdf_with_better_statuses)
    one_gdf_by_maptype = workarounds_eg_interim(cleaned_dict_by_map_one_gdf_with_better_countries)
    one_gdf_by_maptype_fixed = last_min_fixes(one_gdf_by_maptype, needed_tracker_geo_by_map) 
    final_dict_gdfs = create_map_file(one_gdf_by_maptype_fixed)
    final_count(final_dict_gdfs)
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print('End map file creation')
    
if test:
    check_expected_number(incorporated_dict_list_gdfs_by_map) # TODO HANDLE THIS ONE for dict or use the one thats been concatenated

end_time = time.time()  # Record the end time
elapsed_time = end_time - start_time  # Calculate the elapsed time

# printf"Elapsed time: {elapsed_time:.4f} seconds")

# Starting test after loop
# Map: africa
# Total number of DataFrames: 4
# Tracker counts: Counter({'GSPT': 844, 'GOGPT': 714, 'GOGET': 578, 'GCPT': 433, 'GWPT': 315, 'GHPT': 218, 'GCMT': 186, 'GGIT': 117, 'GOIT': 104, 'GGIT-lng': 97, 'GBPT': 44, 'GGPT': 39, 'GCTT': 22, 'GNPT': 14})
# ----------------------------------------
# Map: latam
# Total number of DataFrames: 4
# Tracker counts: Counter({'GSPT': 4906, 'GWPT': 2173, 'GOGET': 922, 'GOGPT': 778, 'GHPT': 447, 'GBPT': 339, 'GCPT': 176, 'GGIT': 144, 'GOIT': 139, 'GGIT-lng': 88, 'GGPT': 38, 'GCMT': 31, 'GCTT': 27, 'GNPT': 10})
# ----------------------------------------
# Map: asia
# Total number of DataFrames: 4
# Tracker counts: Counter({'GOGPT': 4852, 'GGIT': 1616, 'GOGET': 905, 'GGIT-lng': 480})
# ----------------------------------------
# Map: europe
# Total number of DataFrames: 4
# Tracker counts: Counter({'GOGPT': 2675, 'GOGET': 1204, 'GGIT': 1041, 'GGIT-lng': 168})
# ----------------------------------------

# maybe change it all so iterates over prep df, but goes through to the end of creating all files so will have for all 