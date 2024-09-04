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

################
# ADAPT AET FUNCTIONS FOR ALL MULTI TRACKER MAPS #
################

def what_maps_are_needed(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab):
    needed_map_and_tracker_dict = {} # map: [trackers]
    map_log_df = gspread_access_file_read_only(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab)
    print(f'Trackers with updates to be incorporated: {trackers_to_update}')

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
                print(f'Map {col} needs to be updated with the new data for {tracker}, and existing data for {list_of_trackers_relevant_to_map} minus {tracker}.')

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
#                 map_results = pd.DataFrame(sheet.get_all_records(expected_headers=['release date','map updated','tracker','key','download file link','map file link','project count','unit count','capacity total']))
#                 # filter the dataframe so we only have the first row
#                 most_recent_map_results = map_results.iloc[[0]].reset_index(drop=True).dropna()
#                 print(most_recent_map_results)
#                 # # print(most_recent_map_results['release date'])
#                 # input('Pause to check most recent map results')
#                 # prev_date = most_recent_map_results['release date'] # only if didn't filter like above on index .iloc[0]
#                 # prev_key = sheet.acell('D2').value.to_list() # will always be this if we do most recent first
#                 prev_key = most_recent_map_results.iloc[0, most_recent_map_results.columns.get_loc('key')]
#                 needed_tracker_geo_by_map[mapname].append(most_recent_map_results) # mapname: [trackers, geo, map_log_results_first_row]
#                 print(f'For map {mapname} we found the prev key: {prev_key}.')

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
    prep_df['tracker acro'] = prep_df['acro']

    if slowmo:

        print(f'this is prep df: {prep_df}')

        input('Check prep df')
    
    return prep_df

def pull_gsheet_data(prep_df, needed_tracker_geo_by_map):
    print(f'{needed_tracker_geo_by_map.keys()}') # africa, latam, gipt
    print(f'{needed_tracker_geo_by_map.values()}') # list of trackers, list of those countries and global
    # input('Check map_country_region keys values')
    # list_dfs_by_map[key] = [list_of_filtered_dfs_geo]
    dict_list_dfs_by_map = {} # TODO turn this into a dict for each map {latammap: [filtered_dfsgeo, needed_for, the_map], giptmap: [filtered_dfsgeo, needed_for, the_map], aetmap: [filtered_dfsgeo, needed_for, the_map]}
    dict_list_gdfs_by_map = {} # TODO turn this into a dict for each map {latammap: [filtered_dfsgeo, needed_for, the_map], giptmap: [filtered_dfsgeo, needed_for, the_map], aetmap: [filtered_dfsgeo, needed_for, the_map]}
    prep_dict = prep_df.to_dict(orient='index')
    print(needed_tracker_geo_by_map.keys())
    print('STOP and check all maps are above not just latam')
    # loop through each needed map in dict
    # for that one, create a new dict with a list of all filtered tracker data by geo needed for that map
    for mapname, value in needed_tracker_geo_by_map.items():

        path_for_test_results = gem_path + mapname + '/test_results/'
        os.makedirs(path_for_test_results, exist_ok=True)
        list_dfs_by_map = [] # still use this list to create a list of dfs as we go through all needed trackers
        list_gdfs_by_map = [] # still use this list to create a list of gdfs as we go through all needed trackers
        needed_trackers = value[0] # list of tracker names to include in list of dfs
        needed_geo = value[1] # list of countries or global for gipt to filter each df in the list by
        if local_copy:
            # for key, value in prep_dict.items():
            # local copy
            print(f'Processing local files in {path_for_test_results}.')
            for file in os.listdir(path_for_test_results): # use key for map name
                if file.endswith(".geojson") & (mapname in file) & (iso_today_date in file):
                    gdf = gpd.read_file(f'{path_for_test_results}{file}')
                    list_gdfs_by_map.append(gdf)
                    print(f'Added {file} to list of gdfs for {mapname}')
                elif file.endswith(".xlsx") & (mapname in file) & (iso_today_date in file):
                    df = pd.read_excel(f'{path_for_test_results}{file}', engine='openpyxl')
                    list_dfs_by_map.append(df)
                    print(f'Added {file} to list of dfs for {mapname}')
        else:
            for tracker in needed_trackers:
                print(f'We are on {tracker}')
                
                if tracker in non_gsheet_data:
                    print(f'{tracker} is not in gsheet data so skipping this tracker.')
                    continue
                
                elif tracker == '':
                    print('tracker is nothing')
                    print(f'this is geo, should also be nothing: {needed_geo}')
                    continue
                
                else:
                    df = gspread_access_file_read_only(prep_dict[tracker]['gspread_key'], prep_dict[tracker]['gspread_tabs'])
                    print(f'Shape of df: {df.shape}')
                    df['tracker acro'] = prep_dict[tracker]['tracker acro']
                    df['official_name'] = tracker
                    
                    # insert function to filter on area/country / assign
                    # then can compare filter on country vs region

                    col_reg_name, col_country_name = find_region_country_colname(df)
                    # TODO add in a check to compare filtering by country versus filtering by region column where applicable
                    filtered_geo_df = create_filtered_df_list_by_map(df,col_country_name, col_reg_name, mapname, needed_geo)
                    # filter by needed_geo 
                    filtered_geo_df = filtered_geo_df.fillna('')
                    filtered_geo_df.dropna()
                    df_info(filtered_geo_df, mapname)
                    filtered_geo_df = find_missing_coords(filtered_geo_df)
                    # append df to list of dfs for data download
                    list_dfs_by_map.append(filtered_geo_df)
                    filtered_geo_df.to_excel(f'{path_for_test_results}{mapname}_{tracker}_df_{iso_today_date}.xlsx', index=False)
                    print(f'Added df {tracker} for map {mapname} to list_dfs_by_map for data download and saved to {path_for_test_results}{mapname}_{tracker}_df_{iso_today_date}.xlsx.')
                    gdf = convert_coords_to_point(filtered_geo_df)
                    # append gdf to list of gdfs for map - though now we can have it as a csv for faster AET non tile load
                    list_gdfs_by_map.append(gdf)
                    gdf_to_geojson(gdf, f'{path_for_test_results}{mapname}_{tracker}_gdf_{iso_today_date}.geojson')
                    print(f'Added gdf {tracker} for map {mapname} to list of gdfs for map and saved to {path_for_test_results}{mapname}_{tracker}_gdf_{iso_today_date}.geojson.')
        dict_list_dfs_by_map[mapname] = list_dfs_by_map
        dict_list_gdfs_by_map[mapname] = list_gdfs_by_map
            
    return dict_list_dfs_by_map,dict_list_gdfs_by_map

def incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson, dict_list_dfs_by_map, dict_list_gdfs_by_map):
    
    pipes_gdf = gpd.read_file(goit_geojson)
    pipes_gdf['tracker acro'] = 'GOIT'
    pipes_gdf['official_name'] = 'Oil Pipelines'
    ggit_gdf = gpd.read_file(ggit_geojson)
    ggit_gdf['tracker acro'] = 'GGIT'
    ggit_gdf['official_name'] = 'Gas Pipelines'

    ggit_lng_gdf = gpd.read_file(ggit_lng_geojson)
    ggit_lng_gdf['tracker acro'] = 'GGIT-lng'
    ggit_lng_gdf['official_name'] = 'LNG Terminals'

    
    # filter out by region
    col_reg_name, col_country_name = find_region_country_colname(pipes_gdf)
    pipes_gdf = pipes_gdf[pipes_gdf[col_reg_name] == 'Africa']       
    
    col_reg_name, col_country_name = find_region_country_colname(ggit_gdf)
    ggit_gdf = ggit_gdf[ggit_gdf[col_reg_name] == 'Africa'] 
        
    col_reg_name, col_country_name = find_region_country_colname(ggit_lng_gdf)
    ggit_lng_gdf = ggit_lng_gdf[ggit_lng_gdf[col_reg_name] == 'Africa']   

    pipes_df = pd.DataFrame(pipes_gdf).reset_index(drop=True)
    pipes_df['tracker acro'] = 'GOIT'
    pipes_df['official_name'] = 'Oil Pipelines'
    
    ggit_df = pd.DataFrame(ggit_gdf).reset_index(drop=True)
    ggit_df['tracker acro'] = 'GGIT'
    ggit_df['official_name'] = 'Gas Pipelines'

    ggit_lng_df = pd.DataFrame(ggit_lng_gdf).reset_index(drop=True)
    ggit_lng_df['tracker acro'] = 'GGIT-lng'
    ggit_lng_df['official_name'] = 'LNG Terminals'
    # Just set up all the gdfs and dfs, so now we need to add them 
    incorporated_dict_list_gdfs_by_map = {}
    incorporated_dict_list_dfs_by_map = {}
    
    for mapname, list_of_gdfs in dict_list_gdfs_by_map.items():

        if mapname in gas_only_maps:
            # all but GOIT or pipes since that is for oil
            list_of_gdfs.append(ggit_gdf)
            list_of_gdfs.append(ggit_lng_gdf) 

            incorporated_dict_list_gdfs_by_map[mapname] = list_of_gdfs

        elif mapname == 'GIPT':
            incorporated_dict_list_gdfs_by_map[mapname] = list_of_gdfs
        else:
            # it must be LATAM and Africa Energy which takes them all
            list_of_gdfs.append(pipes_gdf)
            list_of_gdfs.append(ggit_gdf)
            list_of_gdfs.append(ggit_lng_gdf)

            incorporated_dict_list_gdfs_by_map[mapname] = list_of_gdfs
        
    for mapname, list_of_dfs in dict_list_dfs_by_map.items():
        
        if mapname in gas_only_maps:
            # all but GOIT or pipes since that is for oil
            list_of_dfs.append(ggit_df)
            list_of_dfs.append(ggit_lng_df) 
            incorporated_dict_list_dfs_by_map[mapname] = list_of_dfs    

        elif mapname == 'GIPT':
            incorporated_dict_list_dfs_by_map[mapname] = list_of_dfs    

        else:
            # it must be LATAM and Africa Energy which takes them all
            list_of_dfs.append(pipes_df)
            list_of_dfs.append(ggit_df)
            list_of_dfs.append(ggit_lng_df)
            incorporated_dict_list_dfs_by_map[mapname] = list_of_dfs    

    return incorporated_dict_list_gdfs_by_map, incorporated_dict_list_dfs_by_map
    


################
# MAKE MAP FILE #
################

def create_conversion_df(conversion_key, conversion_tab):
    df = gspread_access_file_read_only(conversion_key, conversion_tab)
    # print(f'this is conversion df: {df}')
    
    df = df[['tracker', 'type', 'original units', 'conversion factor (capacity/production to common energy equivalents, TJ/y)']]
    df = df.rename(columns={'conversion factor (capacity/production to common energy equivalents, TJ/y)': 'conversion_factor', 'original units': 'original_units'})
    df['tracker'] = df['tracker'].apply(lambda x: x.strip())

    return df  


def split_goget_ggit(dict_list_gdfs_by_map):
    custom_dict_list_gdfs_by_map = {}
    # Read the Excel file
    
    for mapname, list_gdfs in dict_list_gdfs_by_map.items():
        custom_list_of_gdfs = []
        print(f'This is length before: {len(list_gdfs)} for {mapname}')
        for gdf in list_gdfs:
            # print(df['tracker'])
            # df = df.fillna('') # df = df.copy().fillna("")
            if gdf['tracker acro'].iloc[0] == 'GOGET':
                # print(gdf.columns)
                # oil
                gdf = gdf.copy()
                # df_goget_missing_units.to_csv('compilation_output/missing_gas_oil_unit_goget.csv')
                # gdf['tracker_custom'] = gdf.apply(lambda row: 'GOGET - gas' if row['Production - Gas (Million m³/y)'] != '' else 'GOGET - oil', axis=1)
                gdf['tracker_custom'] = 'GOGET - oil'
                custom_list_of_gdfs.append(gdf)
                
            elif gdf['tracker acro'].iloc[0] == 'GGIT-lng':
                gdf_ggit_missing_units = gdf[gdf['FacilityType']=='']
                print(f'GGIT LNG missing units: {gdf_ggit_missing_units}')
                # input('Pause to check missing units for GGIT LNG important to know how to calculate capacity factor because differs import and export')
                # gdf_ggit_missing_units.to_csv('compilation_output/missing_ggit_facility.csv')
                gdf = gdf[gdf['FacilityType']!='']
                gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT - import' if row['FacilityType'] == 'Import' else 'GGIT - export', axis=1)
                # print(gdf[['tracker_custom', 'tracker', 'FacilityType']])
                custom_list_of_gdfs.append(gdf)

            else:
                gdf['tracker_custom'] = gdf['tracker acro']
            
                custom_list_of_gdfs.append(gdf)
        custom_dict_list_gdfs_by_map[mapname] = custom_list_of_gdfs
        print(f'This is length after: {len(custom_list_of_gdfs)} for {mapname}')

    return custom_dict_list_gdfs_by_map



def assign_conversion_factors(custom_dict_list_gdfs_by_map, conversion_df):
    # add column for units 
    # add tracker_custom
    # TODO change these because dict not a list now! dict key is map name, value is list of filtered df of gdf
    print(custom_dict_list_gdfs_by_map.keys())
    input('STOP HERE to see if all maps or not')
    custom_dict_list_gdfs_by_map_with_conversion = {}
    for mapname, list_of_gdfs in custom_dict_list_gdfs_by_map.items():
        custom_list_of_gdfs = []
        print(mapname)
        input('check mapname in assign_conversion_factors')
        for gdf in list_of_gdfs:

            gdf = gdf.copy().reset_index()

            print(gdf['tracker acro'].loc[0])
            print(gdf['official_name'].loc[0])

            if gdf['tracker acro'].iloc[0] == 'GOGET': 
                # print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')

                for row in gdf.index:
                    if gdf.loc[row, 'tracker_custom'] == 'GOGET - oil':
                        gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET - oil']['original_units'].values[0]
                        gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET - oil']['conversion_factor'].values[0]
                    # elif gdf.loc[row, 'tracker_custom'] == 'GOGET - gas':  
                    #     gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET - gas']['original_units'].values[0]
                    #     gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET - gas']['conversion_factor'].values[0]
                # gdf['tracker acro'] = 'GOGET' # commenting out not needed
                custom_list_of_gdfs.append(gdf)
                
            elif gdf['tracker acro'].iloc[0] == 'GGIT-lng':
                # print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
                for row in gdf.index:
                    if gdf.loc[row, 'tracker_custom'] == 'GGIT - export':
                        gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT - export']['original_units'].values[0]
                        gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT - export']['conversion_factor'].values[0]
                    elif gdf.loc[row, 'tracker_custom'] == 'GGIT - import':  
                        gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT - import']['original_units'].values[0]
                        gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT - import']['conversion_factor'].values[0]

                custom_list_of_gdfs.append(gdf)

            else:
                # print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
                # This should apply to all rows not just one.
                gdf['tracker_custom'] = gdf["tracker acro"].iloc[0]
                gdf['original_units'] = conversion_df[conversion_df['tracker']==gdf['tracker acro'].iloc[0]]['original_units'].values[0]
                gdf['conversion_factor'] = conversion_df[conversion_df['tracker']==gdf['tracker acro'].iloc[0]]['conversion_factor'].values[0]
                custom_list_of_gdfs.append(gdf)

        custom_dict_list_gdfs_by_map_with_conversion[mapname] = custom_list_of_gdfs
    print(f'This is custom dict: {custom_dict_list_gdfs_by_map_with_conversion}')
    input('Check it, should have all trackers not just pipes!')
    return custom_dict_list_gdfs_by_map_with_conversion


def rename_gdfs(custom_dict_list_gdfs_by_map_with_conversion):

    renamed_one_gdf_by_map = {}
    print(custom_dict_list_gdfs_by_map_with_conversion.keys())
    input('STOP HERE to see if all maps or not')
    for mapname, list_of_gdfs in custom_dict_list_gdfs_by_map_with_conversion.items():
        renamed_gdfs = []
        path_for_test_results = gem_path + mapname + '/test_results/'
        print(mapname)
        print(len(list_of_gdfs))
        [print(gdf['tracker acro']) for gdf in list_of_gdfs]
        input('Check if all trackers are there')
        for gdf in list_of_gdfs:

            # declare which tracker we are at in the list so we can rename columns accordingly
            tracker_sel = gdf['tracker acro'].iloc[0] # GOGPT, GGIT, GGIT-lng, GOGET
            # all_trackers.append(tracker_sel)
            # select the correct renaming dict from config.py based on tracker name
            renaming_dict_sel = renaming_cols_dict[tracker_sel]
            # rename the columns!
            gdf = gdf.rename(columns=renaming_dict_sel) 

            renamed_gdfs.append(gdf)

        # concat all gdfs 
        one_gdf = pd.concat(renamed_gdfs, sort=False).reset_index(drop=True)
        one_gdf = one_gdf.drop_duplicates(subset=['id', 'geometry'])
        # print(f'This is oned_df columns lets see if there are two names: {one_df.columns}')
        print(f'These are the final columns in config.py: {final_cols} in {mapname}')
        print(f'These are the columns in one_gdf: {one_gdf.columns}')
        print(f'These are the cols from gdf that are going to be removed: {set(one_gdf.columns) - set(final_cols)}')
        print(f'These are the cols from final cols that need to be added to our gdf for it to work: {set(final_cols) - set(one_gdf.columns)}')
        cols_to_be_dropped = set(one_gdf.columns) - set(final_cols)
        if slowmo:
            input('Pause to check cols before filtering out all cols in our gdf that are not in final cols, there will be a problem if our gdf does not have a col in final_cols.')
        final_gdf = one_gdf.drop(columns=cols_to_be_dropped)
        # instead of filtering on a preset list, drop the extra columns using cols_to_be_dropped
        # final_gdf = one_gdf[final_cols]
        
        final_gdf.to_csv(f'{path_for_test_results}renamed_one_df_{iso_today_date}.csv',  encoding="utf-8")
        renamed_one_gdf_by_map[mapname] = final_gdf 
        print('Going on to next mapname')
    return renamed_one_gdf_by_map


def remove_null_geo(renamed_one_gdf_by_map):
    cleaned_dict_map_by_one_gdf = {}
    # print(set(concatted_gdf['geometry'].to_list()))
    # print(f'length of df at start of remove_null_geo: {len(concatted_gdf)}')
    # concatted_gdf = concatted_gdf[concatted_gdf['geometry']!='null']
    good_keywords = ['point', 'line']
    for mapname, final_one_gdf in renamed_one_gdf_by_map.items():
        print(final_one_gdf.columns)
        input('Check that geometry is there in the final_one_gdf')
        filtered_geo = final_one_gdf[final_one_gdf['geometry'].apply(lambda x: any(keyword in str(x).lower() for keyword in good_keywords))]
        # print(f'length of df at after filter for point and line geo: {len(filtered_geo)}')
        dropped_geo = pd.concat([final_one_gdf, filtered_geo], ignore_index=True).drop_duplicates(keep=False)
        if slowmo:
            print(dropped_geo)
            print(dropped_geo[['tracker acro', 'name', 'geometry']])
            input('Pause to check dropped geo')
        cleaned_dict_map_by_one_gdf[mapname] = filtered_geo
    return cleaned_dict_map_by_one_gdf


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
            print('no need to handle for hydro having two capacities')
        else:
            # first let's get GHPT cap added 
            
            ghpt_only = gdf_converted[gdf_converted['tracker acro']=='GHPT'] # for GGPT we need to re run it to get it 
            gdf_converted = gdf_converted[gdf_converted['tracker acro']!='GHPT']
            print(len(ghpt_only['capacity']))
            print(len(ghpt_only['capacity1']))
            print(len(ghpt_only['capacity2']))
            input('Check that they are all equal')
            ghpt_only['capacity'] = ghpt_only.apply(lambda row: row['capacity1'] + row['capacity2'], axis=1)
            gdf_converted = pd.concat([gdf_converted, ghpt_only],sort=False).reset_index(drop=True)
            # print(len(gdf_converted))
        
        gdf_converted['cleaned_cap'] = pd.to_numeric(gdf_converted['capacity'], errors='coerce')

        total_counts_trackers = []
        avg_trackers = []

        print(f"this is all trackers: {set(gdf_converted['tracker acro'].to_list())}")
        
        gdf_converted['tracker acro'] = gdf_converted['tracker acro'].fillna('')
        print(f"this is all trackers: {set(gdf_converted['tracker acro'].to_list())}")
        
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
            if pd.isna(cap_cleaned):
                print('still na')
    

        pd.options.display.float_format = '{:.0f}'.format
        gdf_converted['scaling_capacity'] = gdf_converted.apply(lambda row: conversion_multiply(row), axis=1)
        gdf_converted['capacity-table'] = gdf_converted.apply(lambda row: workaround_display_cap(row), axis=1)
        gdf_converted = workaround_no_sum_cap_project(gdf_converted) # adds capacity-details 
        gdf_converted['capacity-details'] = gdf_converted.apply(lambda row: workaround_display_cap_total(row), axis=1)
    
        cleaned_dict_map_by_one_gdf_with_conversions[mapname] = gdf_converted
    return cleaned_dict_map_by_one_gdf_with_conversions


def map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions):
    cleaned_dict_by_map_one_gdf_with_better_statuses = {}
    for mapname, gdf in cleaned_dict_map_by_one_gdf_with_conversions.items():
            
        gdf_map_ready = gdf.copy()
    
        gdf_map_ready = fix_status_inferred(gdf_map_ready)

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
                    'decommissioned': 'retired_plus',})

        # make sure all statuses align with no space rule
        gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.strip().replace(' ','-'))
        gdf_map_ready['status_legend'] = gdf_map_ready['status_legend'].apply(lambda x: x.strip().replace('_','-'))

        print(set(gdf_map_ready['status'].to_list()))
        gdf_map_ready_no_status = gdf_map_ready[gdf_map_ready['status']== '']
        gdf_map_ready= gdf_map_ready[gdf_map_ready['status']!= '']
        # print(len(gdf_map_ready))
        gdf_map_ready_no_status.to_csv(f'{path_for_test_results}no-status-africa-energy.csv')
        gdf_map_ready = gdf_map_ready.fillna('')
        print(set(gdf_map_ready['status'].to_list()))
        gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.lower())
        print(set(gdf_map_ready['status'].to_list()))
        
        cleaned_dict_by_map_one_gdf_with_better_statuses[mapname] = gdf_map_ready
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
        # grouped_tracker_before = gdf.groupby('tracker', as_index=False)['id'].count()
        # print(f'In map ready before adjustment: {grouped_tracker_before}')
        # # no return

        # gdf_map_ready['area2'] = gdf_map_ready['area2'].fillna('')
        if mapname not in gas_only_maps:
            for row in gdf_map_ready.index:

                if gdf_map_ready.loc[row, 'area2'] != '':
                    gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas'].strip()};{gdf_map_ready.loc[row, 'area2'].strip()};"
                    print(f"Found a area2! Hydro? {gdf_map_ready.loc[row, 'areas']} {gdf_map_ready.loc[row, 'tracker acro']} {gdf_map_ready.loc[row, 'name']}")

                else:
                    # make it so all areas even just one end with a semincolon 
                    gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas'].strip()};"
            
        # grouped_tracker_after = gdf.groupby('tracker', as_index=False)['id'].count()

        # print(f'In map ready after adjustment: {grouped_tracker_after}')
        cleaned_dict_by_map_one_gdf_with_better_countries[mapname] = gdf_map_ready  

    return cleaned_dict_by_map_one_gdf_with_better_countries


def workarounds_eg_interim(cleaned_dict_by_map_one_gdf_with_better_countries):
    one_gdf_by_maptype = {}
    for mapname, gdf in cleaned_dict_by_map_one_gdf_with_better_countries.items():
        gdf = gdf.copy()
        # copy tracker column to be full display name not custom 
        print(f'We are on map: {mapname}')
        input('Check what map we are on')
        # handle more than one country for sat image say intranational project
        # if there is more than one ; you know it's a multiple country situation
        # so we want to say in areas-display "multi country"
        # we would also want to overwrite the subnat and say nothing ""
        gdf['count_of_semi'] = gdf.apply(lambda row: row['areas'].split(';'), axis=1) # if len of list is more than 2, then split more than once
        gdf['multi-country'] = gdf.apply(lambda row: 't' if len(row['count_of_semi']) > 2 else 'f', axis=1)
        print(gdf['multi-country'])
        # if t then make areas-display 
        # TODO add a clause for if subnat is null then only show country/area
        # check out Zambia cases where country is there but not coming through
        # TODO look into region country mix up where not all are being shown as Africa
        
        gdf['areas-subnat-sat-display'] = gdf.apply(lambda row: f"{row['subnat'],row['areas']}" if row['multi-country'] == 'f' else 'Multiple Countries/Areas', axis=1)

        if mapname == 'GIPT':
            # does not have goget
            one_gdf_by_maptype[mapname] = gdf 
            
        else:
            print(gdf.columns)
            input('Check if prod-oil is there in columns')
            for row in gdf.index:

                tracker = (gdf.loc[row, 'tracker acro'])
                #if goget then make capacity table and capacity details empty
                
                if tracker == 'GOGET':
                    gdf.loc[row, 'capacity-table'] = ''
                    gdf.loc[row, 'capacity-details'] = ''
                    prod_oil = gdf.loc[row, 'prod_oil']
                    prod_gas = gdf.loc[row, 'prod_gas']
                    
                    if is_valid_goget(prod_oil):
                        # round it then if either is '' we can remove it later we filter on it before adding to table or details
                        prod_oil = str(float(round(prod_oil, 3)))

                        gdf.loc[row, 'prod-oil-table'] = f'{prod_oil} million bbl/y'
                        gdf.loc[row, 'prod-oil-details'] = f'{prod_oil} (million bbl/y)'
                    else:
                        print('invalid goget')
                        
                    if is_valid_goget(prod_gas):
                        prod_gas = str(float(round(prod_gas, 3)))

                        gdf.loc[row, 'prod-gas-table'] = f'{prod_gas} million m³/y'
                        gdf.loc[row, 'prod-gas-details'] = f'{prod_gas} (million m³/y)'
                        
                    else:
                        print('invalid goget')

                    
        # in that column above make it so all units within a project are summed and it's called total capacityDONE
        

        # here we want to get the total number of units at the project level and put it at each row
        # so however it gets pulled into details it is shown
        # units_per_project = gdf.groupby(['name', 'status'], as_index=False)['geometry'].count()
        # print(len(f'length of units_per_project series from groupby: {units_per_project}'))
        # print(units_per_project.columns)
        # gdf = pd.merge(left=gdf, right=units_per_project, on='name', how='outer')
        
        #### figure out 
        
        # tracker type not clickable! 
        
        #### nice to have
        
        # also create a country multiple or not column for displaying on map's sat picture  
        # escape apostrophe and / 
        one_gdf_by_maptype[mapname] = gdf 
    return one_gdf_by_maptype


def last_min_fixes(one_gdf_by_maptype, needed_geo_for_region_assignment):
    one_gdf_by_maptype_fixed = {}
    print(one_gdf_by_maptype.keys())
    input('check that GIPT is in the above')
    for mapname, gdf in one_gdf_by_maptype.items():
        gdf = gdf.copy()
        print(len(gdf))
        gdf['name'] = gdf['name'].fillna('')
        gdf['url'] = gdf['url'].fillna('')
        print(gdf.columns)
        # TODO for now remove drop to understand why all GOGET empty is now not being filled and also prod doesn't come through
        # gdf = gdf.drop(['original_units','conversion_factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'Latitude', 'Longitude'], axis=1) # 'cleaned_cap'
        # handle countries/areas ? 
        # gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) # reverse this one special case back 
        print(f'Missing areas: {gdf[gdf["areas"]==""]}') # check if missing!!   
        input('Handle missing countries')
        # handle situation where Guinea-Bissau IS official and ok not to be split into separate countries 
        gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) 
        
        # something is happening when we concat, we lose goget's name ... 
        # gdf_empty_name = gdf[gdf['name']=='']
        # print(f"This is cols for gdf: {gdf.columns}")
        gdf['wiki-from-name'] = gdf.apply(lambda row: f"https://www.gem.wiki/{row['name'].strip().replace(' ', '_')}", axis=1)
        # row['url'] if row['url'] != '' else 
        gdf['url'] = gdf.apply(lambda row: row['wiki-from-name'] if row['url'] == '' else row['url'], axis=1)
        
        # gdf['name'] = gdf.apply(lambda row: row['name'] if row['name'] != '' else row['url'].split('www.gem.wiki/')[1].replace('_', ' '))

        gdf_empty_url = gdf[gdf['url'] == '']
        
        # print(gdf_empty_url[['tracker', 'wiki-from-name', 'url']])
        
        # assign Africa to all regions
        # gdf['region'] = 'Africa'
        list_of_needed_geo_countries = needed_geo_for_region_assignment[mapname][1]
        print(list_of_needed_geo_countries)
        input('Check this is a list of countries, otherwise may need to adjust how we access the 2nd value of the dictionary') # if it is then we can assign a region based off of it
        if 'Brazil' in list_of_needed_geo_countries:
            gdf['region'] = 'Americas'
        elif 'China' in list_of_needed_geo_countries:
            gdf['region'] = 'Asia'
        elif 'Mozambique' in list_of_needed_geo_countries:
            gdf['region'] = 'Africa'
        elif 'United Kingdom' in list_of_needed_geo_countries:
            gdf['region'] = 'Europe'
        else:
            gdf['region'] = ''
            print(f'No region found for gdf: {gdf["tracker acro"].iloc[0]} for map: {mapname}')
            
        
        gdf.columns = [col.replace('_', '-') for col in gdf.columns]    
        # let's also look into empty url, by tracker I can assign a filler
        
        # gdf['url'] = gdf['url'].apply(lambda row: row[filler_url] if row['url'] == '' else row['url'])
        
        # gdf['capacity'] = gdf['capacity'].apply(lambda x: x.replace('--', '')) # can't do that ... 
        
        # translate acronyms to full names 
        
        gdf['tracker-display'] = gdf['tracker-custom'].map(tracker_to_fullname)
        gdf['tracker-legend'] = gdf['tracker-custom'].map(tracker_to_legendname)
        # print(set(gdf['tracker-display'].to_list()))
        # print(f'Figure out capacity dtype: {gdf.dtypes}')
        gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('--', ''))
        # gdf['capacity'] = gdf['capacity'].apply(lambda x: x.replace('', pd.NA))
        # gdf['capacity'] = gdf['capacity'].astype(float) # Stuck with concatting like strings for now? ValueError: could not convert string to float: ''
                
        one_gdf_by_maptype_fixed[mapname] = gdf
    return one_gdf_by_maptype_fixed

def create_map_file(one_gdf_by_maptype_fixed):
    final_dict_gdfs = {}
    print(one_gdf_by_maptype_fixed.keys())
    input('STOP HERE - why only one map being printed??')

    for mapname, gdf in one_gdf_by_maptype_fixed.items():
        path_for_download_and_map_files = gem_path + mapname + '/compilation_output/'

        print(f'We are on map: {mapname} there are {len(one_gdf_by_maptype_fixed)} total maps')
        print(f"This is cols for gdf: {gdf.columns}")
        input('STOP HERE')
        # drop columns we don't need
        if mapname in gas_only_maps: # will probably end up making all regional maps all energy I would think
            gdf = gdf.drop(['count-of-semi', 'multi-country', 'original-units', 'conversion-factor', 'region2', 'subnat2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1)
        
        else:
            gdf = gdf.drop(['count-of-semi', 'multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1)

        print(gdf.info())
        check_for_lists(gdf)
        if slowmo:
            input('Check what is a list')
        gdf.to_file(f'{path_for_download_and_map_files}{mapname}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
        # gdf_to_geojson(gdf, f'{path_for_download_and_map_files}{geojson_file_of_all_africa}')
        print(f'Saved map geojson file to {path_for_download_and_map_files}{mapname}_{iso_today_date}.geojson')

        gdf.to_excel(f'{path_for_download_and_map_files}{mapname}_{iso_today_date}.xlsx', index=False)
        print(f'Saved xlsx version just in case to {path_for_download_and_map_files}{mapname}_{iso_today_date}.xlsx')
        final_dict_gdfs[mapname] = gdf
    
    return final_dict_gdfs

###############
# MAKE DOWNLOAD FILE #
###############
def create_data_dwnld_file(dict_list_dfs_by_map):
    for mapname, list_dfs in dict_list_dfs_by_map.items():
        print(f'Creating data download file for {mapname}')
        path_for_download_and_map_files = gem_path + mapname + '/compilation_output/'
        os.makedirs(path_for_download_and_map_files, exist_ok=True)
        
        xlsfile = f'{path_for_download_and_map_files}{mapname}-data-download {new_release_date}.xlsx'
        with pd.ExcelWriter(xlsfile, engine='openpyxl') as writer:    
            for df in list_dfs:
                # TODO getting the at least one sheet must be visible issue again
                df = df.reset_index(drop=True)
                tracker_curr = df['official_name'].loc[0]
                print(f'Adding this tracker to dt dwnld: {tracker_curr}')
                print(df.columns)
                
                if slowmo:
                    input('Check cols')
                columns_to_drop = ['tracker acro', 'float_col_clean_lat', 'float_col_clean_lng']
                existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
                # Drop the existing columns
                if existing_columns_to_drop:
                    df = df.drop(columns=existing_columns_to_drop)
                df.to_excel(writer, sheet_name=f'{tracker_curr}', index=False)
                print(f"DataFrame {tracker_curr} written to {xlsfile}")
        
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
        list_of_tuples_holding_about_page_name_df = []
        # TODO make a list in config of all previous releases to gather about page for multi tracker
        # most_recent_map_results = list_of_dfs_trackers_geo_prev_info[2] # it is the third item in the list, this may not be true anymore
        # prev_key = most_recent_map_results.iloc[0, most_recent_map_results.columns.get_loc('key')]
        prev_key = prev_key_dict[mapname]

        print(f'Creating about page file for map: {mapname} with prev key {prev_key}') # Africa Energy, Asia Gas, Europe Gas, LATAM SKIP #  GIPT FOR NOW        
        
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
        print(f"Sheet names previous release:", sheet_names)
        # TODO TAYLOR START HERE adjust for all maps not just Africa Energy Tracker
        # TODO TAYLOR USE needed_tracker_geo_by_map and you can remove a lot of hte other paramters excpet mayhbe prep_df
        # adjust About Africa Energy Tracker tab with new release date
        multi_tracker_about_page = sheet_names[0]
        multi_tracker_about_page = gsheets.worksheet(multi_tracker_about_page) 
        multi_tracker_data = pd.DataFrame(multi_tracker_about_page.get_all_values())
        # aet_data = pd.DataFrame(aet_about.get_all_values())
        # TODO get this from the gsheet map log that holds last time we updated the multi map
        cell_list_prev_release_date = multi_tracker_about_page.findall(previous_release_date)
        print(f"Found {len(cell_list_prev_release_date)} cells with {previous_release_date}")
        print(multi_tracker_data.info())
        if slowmo:
            input('check if prev date is there otherwise manually edit!')
        multi_tracker_data_updated = multi_tracker_data.replace(previous_release_date, new_release_date)
        # print(multi_tracker_data_updated)
        cell_list_prev_release_date = multi_tracker_about_page.findall(previous_release_date)
        print(f"Found {len(cell_list_prev_release_date)} cells with {previous_release_date}")
        if slowmo:
            input('check if prev date is STILL there')
        # list_about_dfs.append(aet_data)
        list_of_tuples_holding_about_page_name_df.append((f'About {mapname}', multi_tracker_data_updated))
        # go throguh all sheets in prev release and add to list unless it is in the trackers_to_update
        # for those I will pull their keys and get the new about page
        for sheet in sheet_names[1:]:
            if 'About' in sheet:
                tracker = sheet.split('About ')[1]
                print(f"Tracker: {tracker}")
                if slowmo:
                    input('Check tracker')
                if tracker in trackers_to_update:
                    continue
                else:
                    about_sheet = gsheets.worksheet(sheet)
                    # about_data_dict = pd.DataFrame(about_sheet.get_all_records(expected_headers=[]))
                    about_data_list = pd.DataFrame(about_sheet.get_all_values())
                    # print(about_data_dict)
                    # print(about_data_list)
                    # input('Compare get all records vs values')
                    # list_about_dfs.append(about_data)
                    
                    # about_df_dict[f'About {tracker} 1'] = about_data_dict
                    list_of_tuples_holding_about_page_name_df.append((f'About {mapname}', about_data_list))

        for new_tracker in trackers_to_update:
            if slowmo:
                print(prep_df.columns)
                print(prep_df['official name'])
                input('check cols')
            new_tracker_key = prep_df[prep_df['official name'] == new_tracker]['gspread_key'].values[0]
            # print(new_tracker_key)
            # input('check key')

            gsheets = gspread_creds.open_by_key(new_tracker_key)
            sheet_names = [sheet.title for sheet in gsheets.worksheets()]
            for sheet in sheet_names:
                if 'About' in sheet:
                    about_sheet = gsheets.worksheet(sheet)
                    about_data = pd.DataFrame(about_sheet.get_all_values())
                    list_of_tuples_holding_about_page_name_df.append((f'About {new_tracker}', about_data))

                    # about_df_dict_by_map[mapname] = (f'About {new_tracker}', about_data)
                    print(f'Found About page for {new_tracker}')
                    # input('check about page')
                    break
                elif 'Copyright' in sheet:
                    about_sheet = gsheets.worksheet(sheet)
                    about_data = pd.DataFrame(about_sheet.get_all_values())
                    # about_df_dict_by_map[mapname] = (f'About {new_tracker}', about_data)
                    list_of_tuples_holding_about_page_name_df.append((f'About {new_tracker}', about_data))
    
                    print(f'Found About page for {new_tracker} in Copyright.')
                    # input('check about page')
                    break

                else:
                    print(f'No about page for {new_tracker} found. Check the gsheet tabs {new_tracker_key}')
                    # input('check about page')

        about_df_dict_by_map[mapname] = list_of_tuples_holding_about_page_name_df
        print(f'About page data pulled for {len(about_df_dict_by_map.keys)} maps.')
        
        # input('check total number is 15')
        
        # updated_aet_data.to_excel(f'{path_for_test_results}aet_about_page{iso_today_date}.xlsx')
        # print(f'Pause to check test results folder for updated AET about page data.')
        # input("Press Enter to continue...")
        
    return about_df_dict_by_map

    
def create_about_page_file(about_df_dict_by_map):

        # I should update this so that we can have the full data download
        
    for mapname, list_of_tuples_holding_aboutpagetabname_aboutpagedata in about_df_dict_by_map.items():
        path_for_download_and_map_files = gem_path + mapname + '/compilation_output/'

        about_output = f'{path_for_download_and_map_files}{mapname}_about_pages_{iso_today_date}.xlsx'
           
        # pull out previous overall about page - done in dict
        with pd.ExcelWriter(about_output, engine='xlsxwriter') as writer:
            for about_tab_name_about_data_tuple in list_of_tuples_holding_aboutpagetabname_aboutpagedata:
                about_tab_name = about_tab_name_about_data_tuple[0]
                about_data = about_tab_name_about_data_tuple[1]
                
                print(f'About page for {about_tab_name} has {len(about_data)} rows.')
                if slowmo:
                    input('Check about page')
                about_data.to_excel(writer, sheet_name=f'{about_tab_name}', index=False)

            print(f'Saved about page sheets to {about_output} for {len(list_of_tuples_holding_aboutpagetabname_aboutpagedata)} trackers including the multi-tracker one.')
            
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
            print(f'this is df cols: {df.cols}') # yep it was reset issue, just needs consistnet column names no Country
            tracker = df['tracker'].loc[0]
            print(f'Creating summary files for {tracker}')
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

def reorder_dwld_file_tabs(about_page_dict, incorporated_dict_list_dfs_by_map):
    # use this file as order for tabs /Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_output/2024-08-15/africa_energy_tracker_2024-08-15.xlsx 
    output = f'{path_for_download_and_map_files}africa-energy-data-download.xlsx'        

    first_about_page = next(iter(about_page_dict.items()))

    final_order = {'Africa Energy Tracker': (first_about_page[1])} # tab name: (df of about data, df of tracker/tabular data)
    # go through each item in the dict and list of dfs, pair up the tracker info, then put them in order based on prev key
    for about_sheetname, about_df in about_page_dict.items():
        print(f'This is about sheetname: {about_sheetname}')
        # sheetname holds the tracker name official 
        # df holds the about page info
        # input('check item')
        trackername = about_sheetname.split('About ')[1].strip()
        print(f'This is tracker name from sheet name about: {trackername}')
        
        for mapname, list_of_dfs in incorporated_dict_list_dfs_by_map.items():
            for tabular_df in list_of_dfs:
                tabular_df = tabular_df.reset_index(drop=True)
                print(tabular_df.columns)
                print(len(tabular_df))
            
                print(f'This is official name from tabular df: {tabular_df["official_name"]}')
                tracker = tabular_df['official_name'].loc[0]
                if tracker == trackername:
                    print(f'Found {trackername} in list of dfs.')
                    final_order[trackername] = (about_df, tabular_df) # 
                    break
    print(final_order)
    input('check final order')
            
    # pull out previous overall about page - done in dict
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

        for trackername, about_tabular_tuple in final_order.items():
            print(f'About page for {trackername} has {len(about_tabular_tuple[0])} rows.')
            if slowmo:
                input('Check about page')
            about_tabular_tuple[0].to_excel(writer, sheet_name=f'About {trackername}', index=False)   
            
            if trackername == 'Africa Energy Tracker':
                continue
            else:
                print(f'Tabular data for {trackername} has {len(about_tabular_tuple[1])} rows.')
                if slowmo:
                    input('Check tabular data')                 
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
    if slowmo:
        print(df.info())
        input('Check df info')

    # numerical_cols = ['Capacity (MW)', 'Start year', 'Retired year', 'Planned retire', 'Latitude', 'Longitude']
    numerical_cols = ''
    col_info = {}
    
    for col in df.columns:                
        if 'ref' in col.lower():
            print('ref found pass')
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
    if slowmo:

        print(col_info_df)

        input(f'Check col info for {key}')
    col_info_df.to_csv(f'test_results/{key}_column_info_{iso_today_date}.csv',  encoding="utf-8")
    print(f'saved col info for {key} here: "test_results/{key}_column_info_{iso_today_date}.csv"')

def final_count(final_dict_gdfs):
    for mapname, gdf in final_dict_gdfs.items():
        grouped_tracker = gdf.groupby('tracker acro', as_index=False)['id'].count()
        print(print(grouped_tracker))

    # no return
    
def compare_prev_current(prev_geojson, curr_geojson):
    
    gdf1 = gpd.read_file(prev_geojson)
    gdf2 = gpd.read_file(curr_geojson)
    # Find all differences between gdf1 and gdf2
    symmetric_difference_gdf = gpd.GeoDataFrame(pd.concat([gdf1, gdf2]).drop_duplicates(keep=False))
    print(symmetric_difference_gdf)
    input('Check symmetric difference')


def check_expected_number(list_dfs):
    # TODO figure out tracker_folder for multiple maps 
    curr_geojson = f'{path_for_download_and_map_files}{tracker_folder}_{iso_today_date}.geojson'
    curr_gdf = gpd.read_file(curr_geojson)
    print(f'Current number of rows in geojson: {len(curr_gdf)}')
    grouped_tracker = curr_gdf.groupby('tracker', as_index=False)['id'].count()
    print(print(grouped_tracker))
    input('Check current number of rows')
    
    summed_from_dfs = 0
    for df in list_dfs:
        print(f"{len(df)} {df['tracker'].loc[0]}")
        summed_from_dfs += len(df)
    
    print(f'Sum of all dfs: {summed_from_dfs}')
    return 

################

### CALL ALL FUNCTIONS ###
if augmented:
    needed_map_and_tracker_dict = what_maps_are_needed(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab)
    # map_country_region has the list of needed maps to be created and their countries/regions
    needed_tracker_geo_by_map = what_countries_or_regions_are_needed_per_map(multi_tracker_countries_sheet, needed_map_and_tracker_dict)
    # TODO for about generation maybe add in the prev_key for each map's results
    # needed_tracker_geo_by_map = pull_in_prev_key_map(needed_tracker_geo_by_map, multi_tracker_log_sheet_key)
    folder_setup(needed_tracker_geo_by_map)

prep_df = create_prep_file(multi_tracker_log_sheet_key, ['prep_file']) 
conversion_df = create_conversion_df(conversion_key, conversion_tab)

dict_list_dfs_by_map, dict_list_gdfs_by_map = pull_gsheet_data(prep_df, needed_tracker_geo_by_map) # map_country_region
incorporated_dict_list_gdfs_by_map, incorporated_dict_list_dfs_by_map = incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson,dict_list_dfs_by_map, dict_list_gdfs_by_map) 

if summary_create: # WAIT til it's been concatenated
    create_summary_files(incorporated_dict_list_dfs_by_map) # TODO HANDLE THIS ONE for dict
    print('need to update prep_df with website for each trackers summary tables')
    input('Pause here')
    pull_existing_summary_files(prep_df) 

if about_create: 
    about_df_dict_by_map = gather_all_about_pages(prev_key_dict, prep_df, new_release_date, previous_release_date, needed_tracker_geo_by_map)
    create_about_page_file(about_df_dict_by_map)

if dwlnd_create:
    create_data_dwnld_file(incorporated_dict_list_dfs_by_map) 

if map_create:
    custom_dict_list_gdfs_by_map = split_goget_ggit(incorporated_dict_list_gdfs_by_map) 
    custom_dict_list_gdfs_by_map_with_conversion = assign_conversion_factors(custom_dict_list_gdfs_by_map, conversion_df)
    renamed_one_gdf_by_map = rename_gdfs(custom_dict_list_gdfs_by_map_with_conversion)
    cleaned_dict_map_by_one_gdf = remove_null_geo(renamed_one_gdf_by_map)
    cleaned_dict_map_by_one_gdf_with_conversions = capacity_conversions(cleaned_dict_map_by_one_gdf)
    cleaned_dict_by_map_one_gdf_with_better_statuses = map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions)
    
    cleaned_dict_by_map_one_gdf_with_better_countries = map_ready_countries(cleaned_dict_by_map_one_gdf_with_better_statuses)
    one_gdf_by_maptype = workarounds_eg_interim(cleaned_dict_by_map_one_gdf_with_better_countries)
    one_gdf_by_maptype_fixed = last_min_fixes(one_gdf_by_maptype, needed_tracker_geo_by_map) 
    final_dict_gdfs = create_map_file(one_gdf_by_maptype_fixed)
    final_count(final_dict_gdfs)

if refine:
    reorder_dwld_file_tabs(about_df_dict_by_map, incorporated_dict_list_dfs_by_map) # TODO HANDLE THIS ONE for dict
    
if test:
    check_expected_number(incorporated_dict_list_gdfs_by_map) # TODO HANDLE THIS ONE for dict or use the one thats been concatenated