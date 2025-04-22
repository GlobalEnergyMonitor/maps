# what id to use

# import sqlalchemy as sa
import pandas as pd
import numpy as np
import geopandas as gpd
import math
import os
from shapely.geometry import Point, LineString
from shapely import wkt
import polyline
from datetime import date
import csv
import gspread
import time
from datetime import date
import os

# Get today's date
today_date = date.today()
# Format the date in ISO format
iso_today_date = today_date.isoformat()
iso_today_date_folder = f'{iso_today_date}/'

test_results_folder = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/coal-plant/test_results/'
tracker_folder = 'coal-plant'

output_folder = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/coal-plant/compilation_output/'

input_file_csv = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/coal-plant/compilation_input/Global-Coal-Plant-Tracker-July-2024 DATA TEAM COPY.xlsx'

def set_up_df(input, sheetname):
    # df = pd.read_csv(input)
    df = pd.read_excel(input, sheet_name=sheetname)
    col_info = {}
    # print(df.info())
    for col in df.columns:
        # print(col)
        
        if 'ref' in col.lower():
            print('ref found pass')
        else:  
            col_info[col] = {'col_values': set(df[col].to_list()), 'col_type': df[col].dtype}
        
    col_info_df = pd.DataFrame(col_info)
    # print(col_info_df)
    col_info_df.to_csv(f'{test_results_folder}col_df.csv')
    return df

def filter_cols(df):
    df = df.copy()
    df = df[['Country/Area', 'GEM location ID','Plant name','Plant name (local)', 'Unit name', 'Capacity (MW)',
    'Status', 'Owner', 'Parent', 'Latitude', 'Start year', 'Retired year',
    'Longitude', 'Location accuracy', 'Subnational unit (province, state)', 'Region', 'Wiki URL']]
    
    df = df.fillna('')
    # print(df.info())
    
    return df

def remove_float_year(df):
    print(f"s years before: {set(df['Start year'].to_list())}")
    print(f"r years before: {set(df['Retired year'].to_list())}")
    
    year_cols = ['Start year', 'Retired year']
    
    for col in year_cols:
        df[col] = df[col].apply(lambda x: str(x).split('.')[0])
    
    
    print(f"s years after: {set(df['Start year'].to_list())}")
    print(f"r years after: {set(df['Retired year'].to_list())}")
    return df

def fix_status_inferred(df):

    print(f"Statuses before: {set(df['Status'].to_list())}")

    inferred_statuses_cancelled = df['Status'].str.contains('cancelled - inferred')
    inferred_statuses_shelved = df['Status'].str.contains('shelved - inferred')

    df.loc[inferred_statuses_cancelled, 'Status'] = 'cancelled'
    df.loc[inferred_statuses_shelved,'Status'] = 'shelved'

    print(f"Statuses after: {set(df['Status'].to_list())}")

    return df

def rename_cols(df):
    df = df.copy()
    df = df.rename(columns=str.lower)
    df.columns = df.columns.str.replace(' ', '-')
    df = df.rename(columns={'capacity-(mw)': 'capacity','latitude': 'lat', 'longitude':'lng', 'wiki-url': 'url', 'subnational-unit-(province,-state)': 'subnational'})

    return df

def input_to_output(df, output_file):

    df = df.copy()
    
    if output_file == None:
        pass
    else:
        df.to_csv(output_file, encoding='utf-8', index=False)
        print(f'done {output_file}')
    return df

df = set_up_df(input_file_csv, 'Units')
df = filter_cols(df)
df = remove_float_year(df)
df = fix_status_inferred(df)
df = rename_cols(df)
print(df.info())

input_to_output(df, f'{output_folder}data-{iso_today_date}.csv')

def test_stats(df):
    df = df.copy()
    # stats to know for testing:
    # Total Units: 14,012Total Capacity: 5,159,634.4
    # Total Operating Units: 6,528Total Capacity: 2,128,527.1
    # Total Mothballed Units: 166Total Capacity: 32,695.9
    # Total Asia Units: 10,233Total Capacity: 4,075,208.4
    # Total India Units: 1,934Total Capacity: 948,884.3

    return df

test_stats(df)