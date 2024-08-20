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
from helper_functions import *
import pyogrio

################
# ADAPT AET FUNCTIONS FOR ALL MULTI TRACKER MAPS #
################

def what_maps_are_needed(key, tab):
    needed_map_list = []
    map_log_df = gspread_access_file_read_only(key, tab)
    print(f'Trackers with updates to be incorporated: {trackers_to_update}')

    for tracker in trackers_to_update:
        # filter out the map tracker tab df 
        # so that we only have the row that matches the tracker to be updated
        map_log_df_sel = map_log_df[map_log_df['official release tab name'] == tracker]
        for col in map_log_df_sel.columns:
            if 'yes' in map_log_df_sel[col].values:
                needed_map_list.append(tracker)
                print(f'Map {col} needs to be updated with the new data for {tracker}.')

    return needed_map_list

def what_countries_or_regions_are_needed(key, needed_map_list):
    needed_geo_by_map = {} # {map: [countries]}
    # multi_tracker_countries_sheet = gspread_creds.open_by_key(key)
    # country_sheet_names = [sheet.title for sheet in multi_tracker_countries_sheet.worksheets()]
    map_by_region = gspread_access_file_read_only(key, ['key'])
    
    for map in needed_map_list:
        if map == 'LATAM':
            sheet_name = map_by_region[map_by_region['map'] == map]['region'] # I think
            # sheet_data = multi_tracker_countries_sheet.worksheet(sheet)
            # sheet_df = pd.DataFrame(sheet_data.get_all_values())
            country_df = gspread_access_file_read_only(key, f'[{sheet_name}]')
            needed_geo_by_map[map] = country_df
            
        # in future can build this out to check that regions match country list
        elif map == 'GIPT':
            needed_geo_by_map['GIPT'] = 'global'

        else:
            # TODO AttributeError: 'Series' object has no attribute 'strip'
            sheet_name = map_by_region[map_by_region['map'] == map]['region']
            region = sheet_name.strip('-all')[0]
            needed_geo_by_map[map] = region
              
    return needed_geo_by_map

###########################
###########################
# PULL IN ALL AET DATA #
# SAVE ALL AET DATA AS LOCAL XLSX or GEOJSON #
# FIRST, PULL IN THE DATA FROM THE GOOGLE SHEET
# CONVERT INTO GDF
# THEN, PULL IN THE DATA FROM THE LOCAL GEOJSON

def create_prep_file(key, tab): # needed_map_list
    df = gspread_access_file_read_only(key, tab)

    df = df[df['acro'] != '']
    # Convert 'gspread_tabs' and 'sample_cols' to lists
    df['gspread_tabs'] = df['gspread_tabs'].apply(lambda x: x.split(';'))
    # df['sample_cols'] = df['sample_cols'].apply(lambda x: x.split(';'))
    df['gspread_tabs'] = df['gspread_tabs'].apply(lambda lst: [s.strip() for s in lst])
    # df['sample_cols'] = df['sample_cols'].apply(lambda lst: [s.strip() for s in lst])
    df.set_index('acro', inplace=True)
    if slowmo:

        print(f'this is prep df: {df}')

        input('Check prep df')
    
    return df

def pull_gsheet_data(prep_df):
    list_dfs = []
    list_gdfs = []
    prep_dict = prep_df.to_dict(orient='index')
    if local_copy:
        for key, value in prep_dict.items():
            print(f'We are on {key}')
                    # local copy
            for file in os.listdir(path_for_test_results):
                if file.endswith(".geojson") & (key in file) & (iso_today_date in file):
                    gdf = gpd.read_file(f'{path_for_test_results}{file}')
                    list_gdfs.append(gdf)
                    print(f'Added {file} to list of gdfs for {key}')
                elif file.endswith(".xlsx") & (key in file) & (iso_today_date in file):
                    df = pd.read_excel(f'{path_for_test_results}{file}')
                    list_dfs.append(df)
                    print(f'Added {file} to list of dfs for {key}')                    
        

    else:
        for key, value in prep_dict.items():
            print(f'We are on {key}')
            df = gspread_access_file_read_only(prep_dict[key]['gspread_key'], prep_dict[key]['gspread_tabs'])
            df['tracker'] = key
            df['official_name'] = prep_dict[key]['official release tab name']
            col_reg_name = find_region_colname(df)
            df = df[df[col_reg_name] == 'Africa'] 
            df = df.fillna('')
            df.dropna()
            df_info(df, key)
            df = find_missing_coords(df)
            # append df to list of dfs for data download
            list_dfs.append(df)
            df.to_excel(f'{path_for_test_results}{key}_df_{iso_today_date}.xlsx', index=False)
            print(f'Added df {key} to list of dfs for data download and saved to {path_for_test_results}{key}_df_{iso_today_date}.xlsx.')
            gdf = convert_coords_to_point(df)
            # append gdf to list of gdfs for map - though now we can have it as a csv for faster AET non tile load
            list_gdfs.append(gdf)
            gdf_to_geojson(gdf, f'{path_for_test_results}{key}_gdf_{iso_today_date}.geojson')
            print(f'Added gdf {key} to list of gdfs for map and saved to {path_for_test_results}{key}_gdf_{iso_today_date}.geojson.')

    return list_dfs,list_gdfs

def incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson, list_dfs, list_gdfs):
    
    pipes_gdf = gpd.read_file(goit_geojson)
    pipes_gdf['tracker'] = 'GOIT'
    pipes_gdf['official_name'] = 'Oil Pipelines'
    ggit_gdf = gpd.read_file(ggit_geojson)
    ggit_gdf['tracker'] = 'GGIT'
    ggit_gdf['official_name'] = 'Gas Pipelines'

    ggit_lng_gdf = gpd.read_file(ggit_lng_geojson)
    ggit_lng_gdf['tracker'] = 'GGIT-lng'
    ggit_lng_gdf['official_name'] = 'LNG Terminals'

    
    # filter out by region

    col_reg_name = find_region_colname(pipes_gdf)
    pipes_gdf = pipes_gdf[pipes_gdf[col_reg_name] == 'Africa']       
    
    col_reg_name = find_region_colname(ggit_gdf)
    ggit_gdf = ggit_gdf[ggit_gdf[col_reg_name] == 'Africa'] 
        
    col_reg_name = find_region_colname(ggit_lng_gdf)
    ggit_lng_gdf = ggit_lng_gdf[ggit_lng_gdf[col_reg_name] == 'Africa']   

    pipes_df = pd.DataFrame(pipes_gdf).reset_index(drop=True)
    pipes_df['tracker'] = 'GOIT'
    pipes_df['official_name'] = 'Oil Pipelines'
    
    ggit_df = pd.DataFrame(ggit_gdf).reset_index(drop=True)
    ggit_df['tracker'] = 'GGIT'
    ggit_df['official_name'] = 'Gas Pipelines'

    ggit_lng_df = pd.DataFrame(ggit_lng_gdf).reset_index(drop=True)
    ggit_lng_df['tracker'] = 'GGIT-lng'
    ggit_lng_df['official_name'] = 'LNG Terminals'
    
    list_dfs.append(pipes_df)
    list_dfs.append(ggit_df)
    list_dfs.append(ggit_lng_df)

    list_gdfs.append(pipes_gdf)
    list_gdfs.append(ggit_gdf)
    list_gdfs.append(ggit_lng_gdf)

    # to do, we need to convert gdf to df so the data download has all the data
    return list_dfs, list_gdfs
    


################
# MAKE MAP FILE #
################

def create_conversion_df(key, tab):
    df = gspread_access_file_read_only(key, tab)
    # print(f'this is conversion df: {df}')
    
    df = df[['tracker', 'type', 'original units', 'conversion factor (capacity/production to common energy equivalents, TJ/y)']]
    df = df.rename(columns={'conversion factor (capacity/production to common energy equivalents, TJ/y)': 'conversion_factor', 'original units': 'original_units'})
    df['tracker'] = df['tracker'].apply(lambda x: x.strip())

    return df  


def split_goget_ggit(list_gdfs):
    custom_list_of_gdfs = []
    print(f'This is length before: {len(list_gdfs)}')
    # Read the Excel file

    for gdf in list_gdfs:
        # print(df['tracker'])
        # df = df.fillna('') # df = df.copy().fillna("")
        if gdf['tracker'].iloc[0] == 'GOGET':
            # print(gdf.columns)
            # oil
            gdf = gdf.copy()
            # df_goget_missing_units.to_csv('compilation_output/missing_gas_oil_unit_goget.csv')
            # gdf['tracker_custom'] = gdf.apply(lambda row: 'GOGET - gas' if row['Production - Gas (Million m³/y)'] != '' else 'GOGET - oil', axis=1)
            gdf['tracker_custom'] = 'GOGET - oil'
            custom_list_of_gdfs.append(gdf)
            
        elif gdf['tracker'].iloc[0] == 'GGIT-lng':
            gdf_ggit_missing_units = gdf[gdf['FacilityType']=='']
            # df_ggit_missing_units.to_csv('compilation_output/missing_ggit_facility.csv')
            gdf = gdf[gdf['FacilityType']!='']
            gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT - import' if row['FacilityType'] == 'Import' else 'GGIT - export', axis=1)
            # print(gdf[['tracker_custom', 'tracker', 'FacilityType']])
            custom_list_of_gdfs.append(gdf)

        else:
            gdf['tracker_custom'] = gdf['tracker']
        
            custom_list_of_gdfs.append(gdf)
    print(f'This is length after: {len(custom_list_of_gdfs)}')

    return custom_list_of_gdfs



def assign_conversion_factors(list_gdfs, conversion_df):
    # add column for units 
    # add tracker_custom
    augmented_list_of_gdfs = []
    for gdf in list_gdfs:
        gdf = gdf.copy()
        # print(gdf['tracker'].loc[0])
        # print(gdf['geometry'])
        # print(type(df))
        # print(df.columns.to_list()) # it's saying tracker is equalt to custom_tracker for ggit-lng shouldn't be the case 

        if gdf['tracker'].iloc[0] == 'GOGET': 
            # print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')

            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GOGET - oil':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET - oil']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET - oil']['conversion_factor'].values[0]
                # elif gdf.loc[row, 'tracker_custom'] == 'GOGET - gas':  
                #     gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET - gas']['original_units'].values[0]
                #     gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET - gas']['conversion_factor'].values[0]
            gdf['tracker'] = 'GOGET'
            augmented_list_of_gdfs.append(gdf)
            
        elif gdf['tracker'].iloc[0] == 'GGIT-lng':
            # print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GGIT - export':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT - export']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT - export']['conversion_factor'].values[0]
                elif gdf.loc[row, 'tracker_custom'] == 'GGIT - import':  
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT - import']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT - import']['conversion_factor'].values[0]

            augmented_list_of_gdfs.append(gdf)

        else:
            # print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
            # This should apply to all rows not just one.
            gdf['tracker_custom'] = gdf["tracker"].iloc[0]
            gdf['original_units'] = conversion_df[conversion_df['tracker']==gdf['tracker'].iloc[0]]['original_units'].values[0]
            gdf['conversion_factor'] = conversion_df[conversion_df['tracker']==gdf['tracker'].iloc[0]]['conversion_factor'].values[0]
            augmented_list_of_gdfs.append(gdf)

    return augmented_list_of_gdfs


def rename_gdfs(list_of_gdfs_with_conversion):

    renamed_gdfs = []

    for gdf in list_of_gdfs_with_conversion:

        # declare which tracker we are at in the list so we can rename columns accordingly
        tracker_sel = gdf['tracker'].iloc[0] # GOGPT, GGIT, GGIT-lng, GOGET
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
    print(f'These are the final columns in config.py: {final_cols}')
    print(f'These are the columns in one_gdf: {one_gdf.columns}')
    print(f'These are the cols from gdf that are going to be removed: {set(one_gdf.columns) - set(final_cols)}')
    print(f'These are the cols from final cols that need to be added to our gdf for it to work: {set(final_cols) - set(one_gdf.columns)}')
    if slowmo:
        input('Pause to check cols before filtering out all cols in our gdf that are not in final cols, there will be a problem if our gdf does not have a col in final_cols.')
    gdf = one_gdf[final_cols]
    # gdf = one_gdf.copy()
    # print(df.columns)
    gdf.to_csv(f'{path_for_test_results}concatted_df_{iso_today_date}.csv',  encoding="utf-8")
    
    return gdf


def remove_null_geo(one_gdf):

    # print(set(concatted_gdf['geometry'].to_list()))
    # print(f'length of df at start of remove_null_geo: {len(concatted_gdf)}')
    # concatted_gdf = concatted_gdf[concatted_gdf['geometry']!='null']
    good_keywords = ['point', 'line']
    filtered_geo = one_gdf[one_gdf['geometry'].apply(lambda x: any(keyword in str(x).lower() for keyword in good_keywords))]
    # print(f'length of df at after filter for point and line geo: {len(filtered_geo)}')
    dropped_geo = pd.concat([one_gdf, filtered_geo], ignore_index=True).drop_duplicates(keep=False)
    if slowmo:
        print(dropped_geo)
        print(dropped_geo[['tracker', 'name', 'geometry']])
        input('Pause to check dropped geo')

    return filtered_geo


def capacity_conversions(gdf): 

# you could multiply all the capacity/production values in each tracker by the values in column C, 
# "conversion factor (capacity/production to common energy equivalents, TJ/y)."
# For this to work, we have to be sure we're using values from each tracker that are standardized
# to the same units that are stated in this sheet (column B, "original units").

# need to get nuances for each tracker, it's just GGIT if point then do lng terminal if line then do pipeline

    gdf_converted = gdf.copy()
    
    # first let's get GHPT cap added 
    # print(len(gdf_converted))
    ghpt_only = gdf_converted[gdf_converted['tracker']=='GHPT'] # for GGPT we need to re run it to get it 
    gdf_converted = gdf_converted[gdf_converted['tracker']!='GHPT']
    ghpt_only['capacity'] = ghpt_only.apply(lambda row: row['capacity1'] + row['capacity2'], axis=1)
    gdf_converted = pd.concat([gdf_converted, ghpt_only],sort=False).reset_index(drop=True)
    # print(len(gdf_converted))
    
    # # second let's handle GOGET -- need to differentiate use cap-gas if custom_tracker gas etc
    # goget_oil_only = gdf_converted[gdf_converted['tracker_custom']=='GOGET - oil'] # for GGPT we need to re run it to get it 
    # goget_gas_only = gdf_converted[gdf_converted['tracker_custom']=='GOGET - gas'] # for GGPT we need to re run it to get it 

    # goget_oil_only['capacity'] = goget_oil_only['capacity_oil']
    # goget_gas_only['capacity'] = goget_gas_only['capacity_gas']

    # gdf_converted = gdf_converted[gdf_converted['tracker']!='GOGET']
    # gdf_converted = pd.concat([gdf_converted, goget_oil_only],sort=False).reset_index(drop=True)
    # gdf_converted = pd.concat([gdf_converted, goget_gas_only],sort=False).reset_index(drop=True)

    

    gdf_converted['cleaned_cap'] = pd.to_numeric(gdf_converted['capacity'], errors='coerce')

    total_counts_trackers = []
    avg_trackers = []

    print(f"this is all trackers: {set(gdf_converted['tracker'].to_list())}")
    
    gdf_converted['tracker'] = gdf_converted['tracker'].fillna('')
    print(f"this is all trackers: {set(gdf_converted['tracker'].to_list())}")
    
    gdf_converted = gdf_converted[gdf_converted['tracker']!=''] # new to filter out nan


    for tracker in set(gdf_converted['tracker'].to_list()):
        total = len(gdf_converted[gdf_converted['tracker'] == tracker])
        sum = gdf_converted[gdf_converted['tracker'] == tracker]['cleaned_cap'].sum()
        avg = sum / total
        total_pair = (tracker, total)
        total_counts_trackers.append(total_pair)
        avg_pair = (tracker, avg)
        avg_trackers.append(avg_pair)

    # print(total_counts_trackers)
    # print(avg_trackers)
 
    # print(total_counts_trackers)
    # print(avg_trackers) 
    
    for row in gdf_converted.index:
        cap_cleaned = gdf_converted.loc[row, 'cleaned_cap']
        tracker = gdf_converted.loc[row, 'tracker']
        if pd.isna(cap_cleaned):
            for pair in avg_trackers:
                if pair[0] == tracker:
                    gdf_converted.loc[row, 'cleaned_cap'] = pair[1]
        cap_cleaned = gdf_converted.loc[row, 'cleaned_cap']
        if pd.isna(cap_cleaned):
            print('still na')
 

    pd.options.display.float_format = '{:.0f}'.format
    gdf_converted['scaling_capacity'] = gdf_converted.apply(lambda row: conversion_multiply(row), axis=1)
    # print(f"{gdf_converted['scaling_capacity'].min().round(2)}")
    # print(f"{gdf_converted['scaling_capacity'].max().round(2)}")
    # print(f"scaling_cap stats: {gdf_converted['scaling_capacity'].describe()}")
    gdf_converted['capacity-table'] = gdf_converted.apply(lambda row: workaround_display_cap(row), axis=1)

    gdf_converted = workaround_no_sum_cap_project(gdf_converted) # adds capacity-details 
    
    gdf_converted['capacity-details'] = gdf_converted.apply(lambda row: workaround_display_cap_total(row), axis=1)
    # gdf_converted['capacity-plant-total'] = gdf_converted.apply(lambda row: workaround_no_sum_cap_project(row), axis=1)

    return gdf_converted


def map_ready_statuses(gdf):
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

    return gdf_map_ready



def map_ready_countries(gdf):

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
    for row in gdf_map_ready.index:

        if gdf_map_ready.loc[row, 'area2'] != '':
            gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas'].strip()};{gdf_map_ready.loc[row, 'area2'].strip()};"
            print(f"Found a area2! Hydro? {gdf_map_ready.loc[row, 'areas']} {gdf_map_ready.loc[row, 'tracker']} {gdf_map_ready.loc[row, 'name']}")

        else:
            # make it so all areas even just one end with a comma 
            gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas'].strip()};"
    
    # grouped_tracker_after = gdf.groupby('tracker', as_index=False)['id'].count()

    # print(f'In map ready after adjustment: {grouped_tracker_after}')
    

    return gdf_map_ready


def workarounds_eg_interim(gdf):
    # copy tracker column to be full display name not custom 
    gdf = gdf.copy()
    # create column that has capacity with appended units 
    
    # for items with no capacity remove capacity
    # goget, and GCMT need to not have anything in capacity
    
    # make capacity == ''
    # production_mask = gdf[gdf['tracker']=='GOGET' or 'GCMT'] 
    for row in gdf.index:
        prod_oil = gdf.loc[row, 'prod_oil']
        prod_gas = gdf.loc[row, 'prod_gas']
        cap = gdf.loc[row, 'capacity']
        tracker = (gdf.loc[row, 'tracker'])
        #if goget then make capacity table and capacity details empty
        
        if tracker == 'GOGET':
            gdf.loc[row, 'capacity-table'] = ''
            gdf.loc[row, 'capacity-details'] = ''
            
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
    
    return gdf


def last_min_fixes(gdf):
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
    gdf['region'] = 'Africa'
    
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
    
    # REMOVE TODO not found!! 
    
     
    return gdf

def create_map_file(gdf):
    print(f"This is cols for gdf: {gdf.columns}")

    # drop columns we don't need
    
    gdf = gdf.drop(['count-of-semi', 'multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1)

    print(gdf.info())
    check_for_lists(gdf)
    if slowmo:
        input('Check what is a list')
    gdf.to_file(f'{path_for_download_and_map_files}{geojson_file_of_all_africa}', driver='GeoJSON', encoding='utf-8')
    # gdf_to_geojson(gdf, f'{path_for_download_and_map_files}{geojson_file_of_all_africa}')
    print(f'Saved map geojson file to {path_for_download_and_map_files}{geojson_file_of_all_africa}')

    gdf.to_excel(f'{path_for_download_and_map_files}{geojson_file_of_all_africa.split(".geojson")[0]}.xlsx', index=False)
    print(f'Saved xlsx version just in case to {path_for_download_and_map_files}{geojson_file_of_all_africa.split(".geojson")[0]}.xlsx')

    return gdf

###############
# MAKE DOWNLOAD FILE #
###############
def create_data_dwnld_file(list_dfs):
    xlsfile = f'{path_for_download_and_map_files}africa-energy-tracker-data-download {new_release_date}.xlsx'
    with pd.ExcelWriter(xlsfile, engine='openpyxl') as writer:    
        for df in list_dfs:
            tracker_curr = df['tracker'].loc[0]
            print(f'Adding this tracker to dt dwnld: {tracker_curr}')
            print(df.columns)
            if slowmo:
                input('Check cols')
            columns_to_drop = ['tracker', 'float_col_clean_lat', 'float_col_clean_lng']
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

def gather_all_about_pages(prev_key, prep_df, new_release_date, previous_release_date):
    about_df_dict = {} # official name for sheet: {about page df}
    gspread_creds = gspread.oauth(
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
            credentials_filename=client_secret_full_path,
            # authorized_user_filename=json_token_name,
        )
    wait_time = 5
    time.sleep(wait_time)
    gsheets = gspread_creds.open_by_key(prev_key)
        # List all sheet names
    sheet_names = [sheet.title for sheet in gsheets.worksheets()]
    print(f"Sheet names previous release:", sheet_names)
    # adjust About Africa Energy Tracker tab with new release date
    aet_about = sheet_names[0]
    aet_about = gsheets.worksheet(aet_about) 

    aet_data = pd.DataFrame(aet_about.get_all_values())
    # aet_data = pd.DataFrame(aet_about.get_all_values())
    cell_list_prev_release_date = aet_about.findall(previous_release_date)
    print(f"Found {len(cell_list_prev_release_date)} cells with {previous_release_date}")
    print(aet_data.info())
    if slowmo:
        input('check if July is there')
    updated_aet_data = aet_data.replace(previous_release_date, new_release_date)
    print(updated_aet_data)
    cell_list_prev_release_date = aet_about.findall(previous_release_date)
    print(f"Found {len(cell_list_prev_release_date)} cells with {previous_release_date}")
    if slowmo:
        input('check if July is STILL there')
    # list_about_dfs.append(aet_data)
    about_df_dict['About Africa Energy Tracker'] = updated_aet_data
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
                print(about_data_list)
                # input('Compare get all records vs values')
                # list_about_dfs.append(about_data)
                
                # about_df_dict[f'About {tracker} 1'] = about_data_dict
                about_df_dict[f'About {tracker}'] = about_data_list
    
    for new_tracker in trackers_to_update:
        if slowmo:
            print(prep_df.columns)
            print(prep_df['official release tab name'])
            input('check cols')
        new_tracker_key = prep_df[prep_df['official release tab name'] == new_tracker]['gspread_key'].values[0]
        # print(new_tracker_key)
        # input('check key')

        gsheets = gspread_creds.open_by_key(new_tracker_key)
        sheet_names = [sheet.title for sheet in gsheets.worksheets()]
        for sheet in sheet_names:
            if 'About' in sheet:
                about_sheet = gsheets.worksheet(sheet)
                about_data = pd.DataFrame(about_sheet.get_all_values())
                about_df_dict[f'About {new_tracker}'] = about_data
                print(f'Found About page for {new_tracker}')
                # input('check about page')
                break
            elif 'Copyright' in sheet:
                about_sheet = gsheets.worksheet(sheet)
                about_data = pd.DataFrame(about_sheet.get_all_values())
                about_df_dict[f'About {new_tracker}'] = about_data
                print(f'Found About page for {new_tracker} in Copyright.')
                # input('check about page')
                break

            else:
                print(f'No about page for {new_tracker} found. Check the gsheet tabs {new_tracker_key}')
                # input('check about page')

    
    print(f'About page data pulled for {len(about_df_dict)} trackers.')
    # input('check total number is 15')
    
    # updated_aet_data.to_excel(f'{path_for_test_results}aet_about_page{iso_today_date}.xlsx')
    # print(f'Pause to check test results folder for updated AET about page data.')
    # input("Press Enter to continue...")
    
    return about_df_dict

    
def create_about_page_file(about_page_df_dict):

        # I should update this so that we can have the full data download
        about_output = f'{path_for_download_and_map_files}about_pages.xlsx'        
        # pull out previous overall about page - done in dict
        with pd.ExcelWriter(about_output, engine='xlsxwriter') as writer:

            for sheetname, df in about_page_df_dict.items():
                print(f'About page for {sheetname} has {len(df)} rows.')
                if slowmo:
                    input('Check about page')
                df.to_excel(writer, sheet_name=f'{sheetname}', index=False)

        print(f'Saved about page sheets to {about_output} for {len(about_page_df_dict)} trackers.')
            
        return about_output

#########################
### SUMMARY FILES ###
#########################

# TODO 
def create_summary_files(list_dfs):
    # go through each df
    dict_of_summary_dfs = {} # tracker name: [list of summary dfs]
    for df in list_dfs:
        # have a list of all files needed
        # do a groupby to create the df for each file
        tracker = df['tracker'].loc[0]
        dict_of_summary_dfs[tracker] = []
        print(f'Creating summary files for {tracker}')
    
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

def reorder_dwld_file_tabs(about_page_dict, list_dfs):
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
        for tabular_df in list_dfs:
            tabular_df = tabular_df.reset_index(drop=True)
            print(tabular_df.columns)
            print(len(tabular_df))
           
            print(f'This is official name from tabular df: {tabular_df["official_name"]}')
            print(0 in tabular_df.index)
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

def final_count(gdf):
    grouped_tracker = gdf.groupby('tracker', as_index=False)['id'].count()
    print(print(grouped_tracker))

    # no return
    
def compare_prev_current(prev_geojson, curr_geojson):
    
    gdf1 = gpd.read_file(prev_geojson)
    gdf2 = gpd.read_file(curr_geojson)
    # Find all differences between gdf1 and gdf2
    symmetric_difference_gdf = gpd.GeoDataFrame(pd.concat([gdf1, gdf2]).drop_duplicates(keep=False))
    print(symmetric_difference_gdf)
    input('Check symmetric difference')


def check_expected_number(list_dfs, one_gdf):
    
    return None

################

### CALL ALL FUNCTIONS ###
if augmented:
    map_name_list = what_maps_are_needed(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab)
    # map_country_region has the list of needed maps to be created and their countries/regions
    map_country_region = what_countries_or_regions_are_needed(multi_tracker_countries_sheet, map_name_list)

# TODO set up folders based on needed maps 

prep_df = create_prep_file(prep_file_key, prep_file_tab) # map_country_region
conversion_df = create_conversion_df(conversion_key, conversion_tab)  
list_dfs, list_gdfs = pull_gsheet_data(prep_df) # map_country_region
list_dfs, list_of_gdfs = incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson, list_dfs, list_gdfs) # map_country_region

if summary_create: 
    create_summary_files(list_dfs)
    # TODO
    print('need to update prep_df with website for each trackers summary tables')
    pull_existing_summary_files(prep_df) 

if about_create:
    about_page_dict = gather_all_about_pages(prev_key, prep_df, new_release_date, previous_release_date)
    create_about_page_file(about_page_dict)

if dwlnd_create:
    create_data_dwnld_file(list_dfs)

if map_create:
    custom_list_of_gdfs = split_goget_ggit(list_gdfs)
    augmented_list_of_gdfs = assign_conversion_factors(custom_list_of_gdfs, conversion_df)
    one_gdf = rename_gdfs(augmented_list_of_gdfs)
    one_gdf = remove_null_geo(one_gdf)
    one_gdf = capacity_conversions(one_gdf)
    one_gdf = map_ready_statuses(one_gdf)
    one_gdf = map_ready_countries(one_gdf)
    one_gdf = workarounds_eg_interim(one_gdf)
    one_gdf = last_min_fixes(one_gdf) # map_country_region
    one_gdf = create_map_file(one_gdf)
    final_count(one_gdf)


if refine:
    reorder_dwld_file_tabs(about_page_dict, list_dfs)
    check_expected_number(list_dfs)