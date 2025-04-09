# what id to use

# import sqlalchemy as sa
import pandas as pd
import numpy as np
import geopandas as gpd
import math
import os
from shapely.geometry import Point, LineString
from shapely import wkt
from datetime import date
import csv
import gspread
import time
from datetime import date
import os
from config import countries

# Get today's date
today_date = date.today()
# Format the date in ISO format
iso_today_date = today_date.isoformat()
iso_today_date_folder = f'{iso_today_date}/'

test_results_folder = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/nuclear/test_results/'
tracker_folder = 'nuclear'

output_folder = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/nuclear/compilation_output/'

input_file_csv = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/nuclear/compilation_input/all-fields-2024-07-11T012203-nuclear.csv'

def set_up_df(input):
    df = pd.read_csv(input)
    col_info = {}
    # print(df.info())
    for col in df.columns:
        # print(col)
        
        if 'ref' in col.lower():
            print('ref found pass')
        else:  
            col_types = {}
            col_values = {}
            col_info[col] = {'col_values': set(df[col].to_list()), 'col_type': df[col].dtype}
        
    col_info_df = pd.DataFrame(col_info)
    # print(col_info_df)
    col_info_df.to_csv(f'{test_results_folder}col_df.csv')
    return df

def filter_cols(df):
    df = df.copy()
    df = df[['Country', 'Project Name', 'Unit Name', 'Capacity (MW)',
    'Status', 'Reactor Type', 'Model', 'Owner', 'Operator', 'Latitude',
    'Longitude', 'Location Accuracy', 'State/Province', 'Region', 'Wiki URL']]
    
    df = df.fillna('')
    # print(df.info())
    
    return df

def fix_status_inferred(df):

    print(f"Statuses before: {set(df['Status'].to_list())}")

    inferred_statuses_cancelled = df['Status'].str.contains('cancelled - inferred')
    inferred_statuses_shelved = df['Status'].str.contains('shelved - inferred')

    df.loc[inferred_statuses_cancelled, 'Status'] = 'cancelled'
    df.loc[inferred_statuses_shelved,'Status'] = 'shelved'

    print(f"Statuses before: {set(df['Status'].to_list())}")

    return df

def rename_cols(df):
    df = df.copy()
    df = df.rename(columns=str.lower)
    df.columns = df.columns.str.replace(' ', '-')
    df = df.rename(columns={'latitude': 'lat', 'longitude':'lng', 'wiki-url': 'url'})

    return df

def harmonize_countries(df, countries_dict):
    df = df.copy()
    # for k,v in countries_dict.items():
    #     print(len(v))
    countries_col = set(df['country'].to_list())
    region_col = set(df['region'].to_list())
    results = []
    for region in region_col:
        
        df_mask = df[df['region']==region]
        df_mask['country-harmonize-pass'] = df_mask['country'].apply(lambda x: 'true' if x in countries_dict[region] else f"false because {x}")
        results_len = df_mask[df_mask['country-harmonize-pass'] == 'false']
        results.append((region, len(results_len)))
        print(f'\nWe want this to be 0: {results}\n')
        
    df['areas-subnat-sat-display'] = df.apply(lambda row: f"{row['country']}" if row['state/province'] == '' else f"{row['state/province']}, {row['country']}", axis=1)   
    return df

def input_to_output(df, output_file):

    df = df.copy()
    
    if output_file == None:
        pass
    else:
        df.to_csv(output_file, encoding='utf-8', index=False)
        print(f'done {output_file}')
    return df

df = set_up_df(input_file_csv)
df = filter_cols(df)
df = fix_status_inferred(df)
df = rename_cols(df)
df = harmonize_countries(df, countries)
print(df.info())

input_to_output(df, f'{output_folder}data-{iso_today_date}.csv')

def test_stats(df):
    df = df.copy()
    # stats to know for testing:
    # Total Units: 1,541Total Capacity: 1,405,657.8
    # Total Operating Units: 419Total Capacity: 396,484
    # Total Mothballed Units: 27Total Capacity: 22,765
    # Total Asia Units: 621Total Capacity: 625,830
    # Total Kenya Units: 2Total Capacity: 4,000

    return df

test_stats(df)