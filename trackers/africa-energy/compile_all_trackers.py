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


# # output in geojson

# # so all geometries in the right format


# #### useful general functions ####

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
    
        print(tab)
        wait_time = 1
        time.sleep(wait_time)
        gsheets = gspread_creds.open_by_key(key)
        # Access a specific tab
        spreadsheet = gsheets.worksheet(tab)
        
        # Attempt to fetch data from the sheet
        gsheets = gspread_creds.open_by_key(key)
        # Access a specific tab
        spreadsheet = gsheets.worksheet(tab)
        df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
        df = df.replace('*', pd.NA).replace('Unknown', pd.NA) # TODO maybe deal in another way?
        df = df.dropna()
        list_of_dfs.append(df)

    if len(list_of_dfs) > 1: 
        # df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True).fillna('')
        
        df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True).fillna('')

    else: 
        for i in list_of_dfs:
            df = i.fillna('') # NEW
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
    print(f'length of df at start of cleaned_dfs: {len(df)}')

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
    print(f'length of :{len(non_numeric_rows)}')
    cleaned_df = cleaned_df.drop(non_numeric_rows)
    print("Rows to drop:", non_numeric_rows)
    print("\nCleaned DataFrame:")
    print(cleaned_df)
    
    # Create new DataFrames from the lists
    non_numeric_df = pd.DataFrame(non_numeric_rows)

    print("\nNon-Numeric DataFrame:")
    print(non_numeric_df)
    non_numeric_df.to_csv(f'non_numeric_df_coords_{today_date}.csv')

                
    print(f'length of df at end of cleand_dfs removed lat and long empty which is good because all point data:{len(cleaned_df)}')
    return cleaned_df

def lat_lng_to_Point(df):

    df = clean_dfs(df)
    df = df.fillna('')
    # df = df.drop_duplicates()
    
    # for row in df.index:

    #     if df.loc[row,'geometry'] == '':
    #         # print(df.loc[row,'geometry'])

    #         #             # to rename cols 
    #         # pass
    #         if df.loc[row, 'Latitude'] == '':

    #             # df.loc[row, 'Latitude'] = filler_Angola[0]
    #             # df.loc[row, 'Longitude'] = filler_Angola[1]
    #             df.loc[row,'geometry'] = Point(filler_Angola[0], filler_Angola[1])
    #             print(df.loc[row,'geometry'])
    #             print(f'we had to fill in with filler lat long probably goget mystery')


    #         elif df.loc[row, 'Latitude'] != '':

    #             df.loc[row,'geometry'] = Point(df.loc[row,'Longitude'], df.loc[row,'Latitude'])
    #             print(df.loc[row,'geometry'])
    #             # print(f'we transformed a lat lng pair to a Point!')
    #         else:
    #             print("unsure")
                    

    print('Successfully created a geometry column')
    # print(df['geometry'])
    # else:
    #     # no change needed because already in geojson
    #     print(f'This was a pipelines dataset, heres the columns: {df.columns}')
    
    # print(df.columns)

    return df

def df_to_gdf(df, geometry_col, crs='EPSG:4326'):
    # Ensure the geometry column contains valid geometries
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df[geometry_col]))
    # print(crs)
    gdf = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)
    # gdf.set_crs(epsg=int(crs), inplace=True)  # EPSG:4326  WGS 84
    
    # # Convert the GeoDataFrame to GeoJSON format
    # geojson = gdf.to_json()
    
    # # Save the GeoJSON to a file
    # with open(output_file, 'w') as f:
    #     f.write(geojson)
    
    # gdf.to_file(output_file, driver="GeoJSON")
    
    # print(f"GeoJSON file saved to {output_file}")
    return gdf

def gdf_to_geojson(gdf, output_file):
    gdf.to_file(output_file, driver="GeoJSON")
    
    print(f"GeoJSON file saved to {output_file}")


def geojson_to_gdf(geojson_file):
    """
    convert to gdf
    """
    
    # Load GeoJSON file into a GeoDataFrame
    gdf = gpd.read_file(geojson_file)

    # get crs for final export
    crs = gdf.crs
    # print(crs)

    # print(gdf.columns)
    # print(len(gdf))
    pipes_without_geo = gdf[gdf['geometry']==None]
    # print(len(pipes_without_geo))
    # pipes_without_geo.to_csv('pipes_without_geo_GOIT_2024-05-22.csv')
    # gdf = gdf[gdf['geometry']!= None]
    # print(len(gdf))


    # Convert geometries to WKT
    # gdf['geometry_wkt'] = gdf['geometry'].apply(lambda geom: geom.wkt)

    # # # Convert each geometry to GeoJSON
    # # gdf['geometry_geojson'] = gdf['geometry'].apply(lambda geom: json.loads(geom.to_json()))

    # # Apply the conversion from multistring and linestring geometry to encoded polylines
    # gdf['geometry_polyline'] = gdf['geometry'].apply(geom_to_polyline)

    # Display the updated GeoDataFrame
    # print(gdf[['geometry', 'geometry_wkt', 'geometry_polyline']].head())
    # gdf[['geometry', 'geometry_wkt', 'geometry_polyline']].to_csv('check_geom_formats.csv')


    # If you want to include geometry data as well, you can keep it in the GeoDataFrame or convert it
    # df_with_geometry = pd.DataFrame(gdf)
    return gdf, crs


#### useful data check test functions ####

#### export functions ####

####
# START HERE FOR NEW PULL #
def create_prep_file(key, tab):
    df = gspread_access_file_read_only(key, tab)

    df = df[df['acro'] != '']
    # Convert 'gspread_tabs' and 'sample_cols' to lists
    df['gspread_tabs'] = df['gspread_tabs'].apply(lambda x: x.split(';'))
    # df['sample_cols'] = df['sample_cols'].apply(lambda x: x.split(';'))
    df['gspread_tabs'] = df['gspread_tabs'].apply(lambda lst: [s.strip() for s in lst])
    # df['sample_cols'] = df['sample_cols'].apply(lambda lst: [s.strip() for s in lst])
    df.set_index('acro', inplace=True)
    return df


prep_df = create_prep_file(prep_file_key, prep_file_tab)


def create_conversion_df(key, tab):
    df = gspread_access_file_read_only(key, tab)
    print(f'this is conversion df: {df}')
    
    df = df[['tracker', 'type', 'original units', 'conversion factor (capacity/production to common energy equivalents, TJ/y)']]
    df = df.rename(columns={'conversion factor (capacity/production to common energy equivalents, TJ/y)': 'conversion_factor', 'original units': 'original_units'})
    df['tracker'] = df['tracker'].apply(lambda x: x.strip())

    return df  

conversion_df = create_conversion_df(conversion_key, conversion_tab)  

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
    
def find_missing_coords(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df.dtypes) # more options can be specified also
    
    df['float_col_clean_lat'] = df['Latitude'].apply(lambda x: check_and_convert_float(x))
    
    df['float_col_clean_lng'] = df['Longitude'].apply(lambda x: check_and_convert_float(x))

    print("Check which rows will be dropped because nan coords:")
    print(df[df.isna().any(axis=1)])
    nan_df = df[df.isna().any(axis=1)]
    nan_df.to_csv(f'{df["tracker"].loc[0]}_nan_coords_{today_date}.csv')
    if df['tracker'].loc[0] == 'GOGET':
        print('Matzen')
        print(df[df['Unit ID']=='OG0000001'])
    # TODO 
    df = df.dropna(subset = ['float_col_clean_lat', 'float_col_clean_lng'])
    if df['tracker'].loc[0] == 'GOGET':
        print('Matzen')
        print(df[df['Unit ID']=='OG0000001'])
    
    return df
    
def find_missing_cap(df):
    
    # GOGET does not have capacity 
    if df['tracker'].loc[0] == 'GOGET':
        pass
    else:
        df['float_col_clean_cap'] = df['capacity'].apply(lambda x: check_and_convert_float(x))
        
        print("Check which rows will be dropped because nan capacity:")
        print(df[df.isna().any(axis=1)])
        nan_df = df[df.isna().any(axis=1)]
        nan_df.to_csv(f'{df["tracker"].loc[0]}_nan_capacity_{today_date}.csv')
        df = df.dropna(subset = ['float_col_clean_cap'])
        
    return df

def convert_coords_to_point(df):
    crs = 'EPSG: 4326'
    geometry_col = 'geometry'
    for row in df.index:
        df.loc[row,'geometry'] = Point(df.loc[row,'Longitude'], df.loc[row,'Latitude'])
    gdf = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)
    
    return gdf

def create_all_dfs(df):
    all_dict = df.to_dict(orient='index')
    print(all_dict)
    list_of_gdfs = []
    
    for key, value in all_dict.items():
        print(f'we are on tracker: {key}')
        if all_dict[key]['gspread_tabs'] == 'n/a':
            pass

        else:
            print(all_dict[key]['gspread_tabs'])
            df = gspread_access_file_read_only(all_dict[key]['gspread_key'], all_dict[key]['gspread_tabs'])
            df['tracker'] = key
            df = df.fillna('')
            df.dropna()
            # clean up missing coords, # do latercapacity, status, country
            df = find_missing_coords(df)
            # handle lat lng into geometry so when concat all gdfs already
            gdf = convert_coords_to_point(df)
            # convert df to gdf
            
            # list_of_dfs.append(df)
            list_of_gdfs.append(gdf)
            print(f'added {key}')

    return list_of_gdfs

list_of_gdfs = create_all_dfs(prep_df)

# add into list of dfs, GGIT and GOIT 

def incorporate_geojson_trackers(GOIT, GGIT, GGIT_lng, list_of_gdfs):
    
    pipes_gdf = gpd.read_file(GOIT)
    pipes_gdf['tracker'] = 'GOIT'
    ggit_gdf = gpd.read_file(GGIT)
    ggit_gdf['tracker'] = 'GGIT'
    ggit_lng_gdf = gpd.read_file(GGIT_lng)
    ggit_lng_gdf['tracker'] = 'GGIT - lng'

    list_of_gdfs.append(pipes_gdf)
    list_of_gdfs.append(ggit_gdf)
    list_of_gdfs.append(ggit_lng_gdf)

        
    return list_of_gdfs


list_of_gdfs = incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson, list_of_gdfs)

def split_goget_ggit(list_of_gdfs):
    custom_list_of_gdfs = []
    print(f'this is length before: {len(list_of_gdfs)}')
    # Read the Excel file

    
    for gdf in list_of_gdfs:
        # print(df['tracker'])
        # df = df.fillna('') # df = df.copy().fillna("")
        if gdf['tracker'].iloc[0] == 'GOGET':
            print(gdf.columns)
            # oil
            gdf = gdf.copy()
            # df_goget_missing_units.to_csv('compilation_output/missing_gas_oil_unit_goget.csv')
            gdf['tracker_custom'] = gdf.apply(lambda row: 'GOGET - gas' if row['Production - Gas (Million m³/y)'] != '' else 'GOGET - oil', axis=1)
            custom_list_of_gdfs.append(gdf)

            # gas 
            
        elif gdf['tracker'].iloc[0] == 'GGIT - lng':
            gdf_ggit_missing_units = gdf[gdf['FacilityType']=='']
            # df_ggit_missing_units.to_csv('compilation_output/missing_ggit_facility.csv')
            gdf = gdf[gdf['FacilityType']!='']
            gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT - import' if row['FacilityType'] == 'Import' else 'GGIT - export', axis=1)
            print(gdf[['tracker_custom', 'tracker', 'FacilityType']])
        
            custom_list_of_gdfs.append(gdf)

        else:
            gdf['tracker_custom'] = gdf['tracker']
        
            custom_list_of_gdfs.append(gdf)
                
    print(f'this is length after: {len(custom_list_of_gdfs)}')
    # for df in custom_list_of_dfs:
    #     if df['tracker'].iloc[0] == 'GOGET':
    #         print(df['tracker_custom'])
    return custom_list_of_gdfs

custom_list_of_gdfs = split_goget_ggit(list_of_gdfs)


def assign_conversion_factors(list_of_gdfs, conversion_df):
    # add column for units 
    # add tracker_custom
    augmented_list_of_gdfs = []
    for gdf in list_of_gdfs:
        gdf = gdf.copy()
        print(gdf['tracker'].loc[0])
        print(gdf['geometry'])
        # print(type(df))
        # print(df.columns.to_list()) # it's saying tracker is equalt to custom_tracker for ggit-lng shouldn't be the case 

        if gdf['tracker'].iloc[0] == 'GOGET': 
            print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')

            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GOGET - oil':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET - oil']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET - oil']['conversion_factor'].values[0]
                elif gdf.loc[row, 'tracker_custom'] == 'GOGET - gas':  
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET - gas']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET - gas']['conversion_factor'].values[0]

            gdf['tracker'] = 'GOGET'
     
            augmented_list_of_gdfs.append(gdf)
        elif gdf['tracker'].iloc[0] == 'GGIT - lng':
            print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GGIT - export':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT - export']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT - export']['conversion_factor'].values[0]
                elif gdf.loc[row, 'tracker_custom'] == 'GGIT - import':  
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT - import']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT - import']['conversion_factor'].values[0]
            # now let's rename GGIT tracker so lng is not needed
            # df['tracker'] = 'GGIT'
            print(gdf['tracker'])
            print(gdf['tracker_custom'])
            augmented_list_of_gdfs.append(gdf)

        else:
            print(f'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
            # This should apply to all rows not just one.
            gdf['tracker_custom'] = gdf["tracker"].iloc[0]
            gdf['original_units'] = conversion_df[conversion_df['tracker']==gdf['tracker'].iloc[0]]['original_units'].values[0]
            gdf['conversion_factor'] = conversion_df[conversion_df['tracker']==gdf['tracker'].iloc[0]]['conversion_factor'].values[0]
      
            augmented_list_of_gdfs.append(gdf)

    return augmented_list_of_gdfs

list_of_gdfs_with_conversion = assign_conversion_factors(custom_list_of_gdfs, conversion_df)




def rename_dfs(list_of_dfs_with_conversion):
    # renaming_cols_dict['GGIT -lng'] = {renaming dict}
    # renaming_dict = {} # GOGPT: {col:newcol, col2:newcol2}
    renamed_dfs = []
    all_trackers = []
    print(f'Length of original gdfs: {len(list_of_dfs_with_conversion)}')
    # print(list_of_gdfs)
    for df in list_of_dfs_with_conversion:
        # print(item.columns)
        # print(item['tracker'])
        # print(item['tracker_custom'])
        tracker_sel = df['tracker'].iloc[0] # GOGPT, GGIT, GGIT - lng, GOGET
        print(tracker_sel)
        # tracker_sel = tracker_sel.split('-')[0]
        all_trackers.append(tracker_sel)
        renaming_dict_sel = renaming_cols_dict[tracker_sel]
        df = df.rename(columns=renaming_dict_sel) 

        # df = find_missing_cap(df) # no need them will fill in average ... still remember for GOGET to differentiate use cap-gas if custom_tracker gas etc

        renamed_dfs.append(df)
    print(f'all tracker names: {all_trackers}')
    print(f'Length of renamed gdfs: {len(renamed_dfs)}')
    
    # drop un needed cols with final_cols  

    # sort 
    # drop duplicate on unit id
    # concat all gdfs 
    one_df = pd.concat(renamed_dfs, sort=False).reset_index(drop=True)
    one_df = one_df.drop_duplicates(subset=['id', 'geometry'])
    # print(one_df.columns)
    df = one_df[final_cols]
    print(df.columns)
    df.to_csv(f'concatted_df{today_date}.csv')
    
    return df

concatted_gdf = rename_dfs(list_of_gdfs_with_conversion)


# END HERE FOR NEW PULL ##

def filter_by_country_all_gdfs(gdf):
    # df = pd.read_csv(file_path) # file_path in config file
    print(f'length of df at start of filter by country: {len(gdf)}')
    
    # df['areas'] = df['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau'))

    # df['areas'] = df['areas'].apply(lambda x: x.split(','))
    # df['areas'] = df[df['tracker']=='GOGET']['areas'].apply(lambda x: x.split('-'))
    
    africa_df1 = gdf[gdf['areas'].isin(africa_countries)]  
    africa_df2 = gdf[gdf['area1'].isin(africa_countries)]
    africa_df3 = gdf[gdf['region']=='Africa']
    africa_df = pd.concat([africa_df1, africa_df2])
    africa_df = pd.concat([africa_df, africa_df3])
    africa_df = africa_df.drop_duplicates(subset='id')
    # africa_df = df['areas'].apply_row(lambda x: row.drop() if x not in africa_countries else row) 
    print(f'filter by country: {len(africa_df)}')

    return africa_df

africa_gdf = filter_by_country_all_gdfs(concatted_gdf)



def remove_null_geo(concatted_gdf):

    # print(set(concatted_gdf['geometry'].to_list()))
    print(f'length of df at start of remove_null_geo: {len(concatted_gdf)}')
    # concatted_gdf = concatted_gdf[concatted_gdf['geometry']!='null']
    good_keywords = ['point', 'line']
    filtered_geo = concatted_gdf[concatted_gdf['geometry'].apply(lambda x: any(keyword in str(x).lower() for keyword in good_keywords))]
    print(f'length of df at after filter for point and line geo: {len(filtered_geo)}')
    dropped_geo = pd.concat([concatted_gdf, filtered_geo], ignore_index=True).drop_duplicates(keep=False)
    print(dropped_geo)
    print(dropped_geo[['tracker','name', 'geometry']])
    
    return filtered_geo

africa_gdf_cleaned = remove_null_geo(africa_gdf)


# def analyze_geojson(filepath):
#     gdf = gpd.read_file(filepath)
#     # print(len(gdf))
#     # print(gdf)
#     # print(gdf.columns)
#     df = pd.DataFrame(gdf)
#     # print(len(df))

#     good_keywords = ['point', 'line']
#     filtered_geo = df[df['geometry'].apply(lambda x: any(keyword in str(x).lower() for keyword in good_keywords))]
#     # print(len(filtered_geo))
#     dropped_geo = pd.concat([df, filtered_geo], ignore_index=True).drop_duplicates(keep=False)
#     # print(dropped_geo)
#     # print(dropped_geo[['name', 'geometry']])
#     return gdf
    
def conversion_multiply(row):
    cap = float(row['cleaned_cap'])
    factor = float(row['conversion_factor'])
    # print(f'this is factor! {factor}')
    result = float(cap * factor)
    # print(f'this is result! {result}')
    return result


def capacity_conversions(gdf): 

# you could multiply all the capacity/production values in each tracker by the values in column C, 
# "conversion factor (capacity/production to common energy equivalents, TJ/y)."
# For this to work, we have to be sure we're using values from each tracker that are standardized
# to the same units that are stated in this sheet (column B, "original units").

# need to get nuances for each tracker, it's just GGIT if point then do lng terminal if line then do pipeline

    gdf_converted = gdf.copy()
    
    # first let's get GHPT cap added 
    print(len(gdf_converted))
    ghpt_only = gdf_converted[gdf_converted['tracker']=='GHPT'] # for GGPT we need to re run it to get it 
    gdf_converted = gdf_converted[gdf_converted['tracker']!='GHPT']
    ghpt_only['capacity'] = ghpt_only.apply(lambda row: row['capacity1'] + row['capacity2'], axis=1)
    gdf_converted = pd.concat([gdf_converted, ghpt_only],sort=False).reset_index(drop=True)
    print(len(gdf_converted))
    
    # second let's handle GOGET -- need to differentiate use cap-gas if custom_tracker gas etc
    goget_oil_only = gdf_converted[gdf_converted['tracker_custom']=='GOGET - oil'] # for GGPT we need to re run it to get it 
    goget_gas_only = gdf_converted[gdf_converted['tracker_custom']=='GOGET - gas'] # for GGPT we need to re run it to get it 

    goget_oil_only['capacity'] = goget_oil_only['capacity_oil']
    goget_gas_only['capacity'] = goget_gas_only['capacity_gas']

    gdf_converted = gdf_converted[gdf_converted['tracker']!='GOGET']
    gdf_converted = pd.concat([gdf_converted, goget_oil_only],sort=False).reset_index(drop=True)
    gdf_converted = pd.concat([gdf_converted, goget_gas_only],sort=False).reset_index(drop=True)

    

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

    print(total_counts_trackers)
    print(avg_trackers)
 
    print(total_counts_trackers)
    print(avg_trackers) 
    
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
    print(f"{gdf_converted['scaling_capacity'].min().round(2)}")
    print(f"{gdf_converted['scaling_capacity'].max().round(2)}")
    print(f"scaling_cap stats: {gdf_converted['scaling_capacity'].describe()}")


    return gdf_converted

africa_df_converted = capacity_conversions(africa_gdf_cleaned)

def fix_status_inferred(df):
    df = df.fillna('')
    print(f"Statuses before: {set(df['status'].to_list())}")
    inferred_statuses_cancelled = df['status'].str.contains('cancelled - inferred')
    inferred_statuses_shelved = df['status'].str.contains('shelved - inferred')
    
    # # print(inferred_statuses_cancelled['status']!=False)
    # # print(len(inferred_statuses_shelved))
    df.loc[inferred_statuses_cancelled, 'status'] = 'cancelled'
    df.loc[inferred_statuses_shelved,'status'] = 'shelved'
    # for row in df.index:
    #     if 'shelved - inferred' in df.loc[row, 'status']:
    #         df.loc[row, 'status'] = 'shelved'
    

    print(f"Statuses after: {set(df['status'].to_list())}")

    return df

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
    gdf_map_ready_no_status.to_csv('no-status-africa-energy.csv')
    gdf_map_ready = gdf_map_ready.fillna('')
    print(set(gdf_map_ready['status'].to_list()))
    gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.lower())
    print(set(gdf_map_ready['status'].to_list()))

    return gdf_map_ready

africa_df_status_update = map_ready_statuses(africa_df_converted)

def map_ready_countries(gdf):

    gdf_map_ready = gdf.copy()
    # just need to make sure all countries are separated by a comma and have a comma after last country as well
    # GOGET has a hyphen in countries
    # GOIT has comma separated in countries
    # hydropower has two columns country1 and country2
    # GGIT has comma separated in countries
    print(set(gdf_map_ready['areas'].to_list()))
    test = gdf_map_ready[gdf_map_ready['areas']=='Senegal-Mauritania'] 
    print(test)
    gdf_map_ready['areas'] = gdf_map_ready['areas'].apply(lambda x: x.replace('-', ',')) # for goget

    for row in gdf_map_ready.index:
        # for ggit, goit
        if ',' in gdf_map_ready.loc[row, 'areas']:
            gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas']},"
            print(f"Found a comma! GGIT or GOIT? {gdf_map_ready.loc[row, 'areas']}{gdf_map_ready.loc[row, 'area2']} {gdf_map_ready.loc[row, 'tracker']} {gdf_map_ready.loc[row, 'name']}")

        # for goget
        elif '-' in gdf_map_ready.loc[row, 'areas']:
            gdf_map_ready.loc[row, 'areas'] = gdf_map_ready.loc[row, 'areas'].replace('-', ',')
            gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas']},"
            print(f"Found a hyphen! GOGET? {gdf_map_ready.loc[row, 'areas']} {gdf_map_ready.loc[row, 'tracker']} {gdf_map_ready.loc[row, 'name']}")
            
        elif gdf_map_ready.loc[row, 'area2'] != '':
            gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'area1']},{gdf_map_ready.loc[row, 'area2']},"
            print(f"Found a area2! Hydro? {gdf_map_ready.loc[row, 'areas']}  {gdf_map_ready.loc[row, 'tracker']} {gdf_map_ready.loc[row, 'name']}")

        else:
            # make it so all areas even just one end with a comma 
            gdf_map_ready.loc[row, 'areas'] = f"{gdf_map_ready.loc[row, 'areas']},"

            pass

    return gdf_map_ready


def last_min_fixes(africa_gdf_country_update):
    gdf = africa_gdf_country_update.copy()
    
    gdf = gdf.drop(['original_units','conversion_factor', 'area1', 'area2', 'region1', 'region2', 'subnat1', 'subnat2', 'capacity1', 'capacity2', 'Latitude', 'Longitude', 'cleaned_cap'], axis=1)
    # handle countries/areas ? 
    # gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) # reverse this one special case back 
    print(gdf[gdf['areas']=='']) # check if missing!!   
    # handle situation where Guinea-Bissau IS official and ok not to be split into separate countries 
    gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) 
    
    return gdf



africa_gdf_country_update = map_ready_countries(africa_df_status_update)
africa_gdf_country_update = last_min_fixes(africa_gdf_country_update)
# RE RUN with fixed new GOGET OR 

# call all

# prep_df = create_prep_file(prep_file_key, prep_file_tab)

# prep_dict = df_to_dict(prep_df)

# loop_over_dict(prep_dict)

# list_of_dfs = create_all_dfs(prep_dict)

# list_of_renamed_dfs = rename_drop_all_dfs(list_of_dfs, prep_dict)

# one_df = combine_all_dfs(list_of_renamed_dfs)

# africa_df = filter_by_country_all_dfs(one_df)

# df_with_point_geom = convert_all_coords(africa_df)
# africa_gdf = create_geojson(df_with_point_geom)
# # africa_gdf = ''

# concatted_gdf = concat_exisiting_geojson(goit_geojson, ggit_geojson, ggit_pipes_geojson, africa_gdf)

# # africa_gdf = analyze_geojson('/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_output/2024-06-20/africa_energy_tracker_2024-06-20.geojson')

# africa_gdf_converted = capacity_conversions(africa_gdf) 

# africa_gdf_status_update = map_ready_statuses(africa_gdf_converted)
# print(set(africa_gdf_status_update['tracker'].to_list()))

# africa_gdf_country_update = map_ready_countries(africa_df_status_update)
# africa_gdf_country_update.to_csv(f'africa_gdf_country_update{today_date}.csv')

# gdf_to_geojson(africa_gdf_converted, f'{path_for_download_and_map_files}africa_gdf_converted.geojson')

gdf_to_geojson(africa_gdf_country_update, f'{path_for_download_and_map_files}{geojson_file_of_all_africa}')


# # df = pd.DataFrame(africa_gdf_country_update)
# # trackers = set(df['tracker'].to_list())
# # for row in df.index:
# #     if pd.isna(df.at[row, 'capacity'])==False:
# #     # remove empty capacity
# #         for tracker in trackers:
# #             print(df[df['tracker']== tracker]['scaling_capacity'])
# # df['capacity'] = df['capacity'].fillna('')
# # print(df.columns)
# # df_africa = df[df['capacity']!='']
# # for tracker in trackers:
# #     print(df_africa[df_africa['tracker']== tracker]['scaling_capacity'])
# #     print(df_africa[df_africa['tracker']== tracker]['capacity'])
# #     print(df_africa[df_africa['tracker']== tracker]['conversion_factor'])
africa_gdf_country_update.to_excel(f'{path_for_download_and_map_files}{geojson_file_of_all_africa.split(".geojson")[0]}.xlsx', index=False)


