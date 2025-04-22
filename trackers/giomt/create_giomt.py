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

pd.options.display.float_format = '{:.0f}'.format
trackers_to_update = 'Iron-Ore'
# Get today's date
today_date = date.today()
# Format the date in ISO format
iso_today_date = today_date.isoformat()

test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/issues'

output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/giomt/output/'

input_file_csv = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/giomt/input/Global Iron Ore Mines Tracker - November 2024 - Standard Copy (V1) DATA TEAM COPY.xlsx'

def set_up_df(input):
    df = pd.read_excel(input, sheet_name = 'Main Data')
    col_info = {}
    # print(df.info())
    for col in df.columns:
        
        print(col)

        if 'ref' in col.lower():
            print('ref found pass')
        else:  

            col_info[col] = {'col_values': set(df[col].to_list()), 'col_type': df[col].dtype}
        
    col_info_df = pd.DataFrame(col_info)
    # print(col_info_df)
    # col_info_df.to_csv(f'{test_results_folder}{trackers_to_update}col_df.csv')
    # print(f'Saved to {test_results_folder}{trackers_to_update}col_df.csv')
    print(df['GEM wiki page URL'])
    print(df.info())

    return df

def filter_cols(df):
    df = df.copy()
    df = df[['Country/Area', 'Asset name (English)', 'Asset name (other language)', 'Design capacity (ttpa)',
    'Operating status', 'Owner', 'Parent', 'Coordinates',
    'Coordinate accuracy', 'Subnational unit', 'Region', 'GEM wiki page URL', 
    'Total reserves (proven and probable, thousand metric tonnes)', 
    'Total resource (inferred, indicated and measured, thousand metric tonnes)',
    'Production 2023 (ttpa)','Production 2022 (ttpa)', 'Start date']]
    
    df = df.fillna('')
    print(df.info())
    
    return df

def fix_coords(df):
    
    df[['lat', 'lng']] = df['Coordinates'].str.split(',', expand=True)
    # change lat lng from string to float
    df[['lat', 'lng']] = df[['lat', 'lng']].apply(lambda x: x.astype(float))
    print(df.info())

    return df

def scaling_cap(df):
    df['scaling_cap'] = df['Design capacity (ttpa)']
    print(df.columns)
    return df

def fix_status_inferred(df):

    print(f"Statuses before: {set(df['Operating status'].to_list())}")
    # Statuses before: {'operating', 'retired', 'mothballed', 'shelved', 'cancelled', 'unknown', 'proposed'}
    
    # inferred_statuses_cancelled = df['Status'].str.contains('cancelled - inferred')
    # inferred_statuses_shelved = df['Status'].str.contains('shelved - inferred')

    # df.loc[inferred_statuses_cancelled, 'Status'] = 'cancelled'
    # df.loc[inferred_statuses_shelved,'Status'] = 'shelved'

    # print(f"Statuses before: {set(df['Status'].to_list())}")

    return df


def rename_cols(df):
    df = df.copy()
    df = df.rename(columns=str.lower)
    df.columns = df.columns.str.split(',').str[0]
    df.columns = df.columns.str.replace(' ', '-')
    df = df.rename(columns={'gem-wiki-page-url': 'url', 'operating-status': 'status', 'asset-name-(english)': 'name-(english)', 'asset-name-(other-language)': 'name-(other-language)',
                            })
    print(df.info())
    
    return df
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
        return '{:.0f}'.format(int(x)) # no decimal
        # return "{:,}".format(int(x))
        # formatted = "{:,}".format(number)
    else:
        return np.nan # 

def remove_decimal_int(x):
    if is_number(x):
        x = int(str(x).replace('.0',''))
        print(x)
        return x

    
def fill_nans(df):
    df = df.copy()
    floats = ['Design capacity (ttpa)',
    'Total reserves (proven and probable, thousand metric tonnes)', 
    'Total resource (inferred, indicated and measured, thousand metric tonnes)']
    
    for col in floats:
        # print(set(df[col].to_list()))
        df[col] = df[col].apply(lambda x: check_and_convert_int(x))
        # df[col] = df[col].apply(lambda x: remove_decimal_int(x))
        # print(df.sort_values(col)[[col, 'Asset name (English)']])
        # df[col] = df[col].replace(np.nan, 'unknown')
        # df[col] = df[col].fillna('unknown')
        # set_col_data = set(df[col].to_list())
        # print(set_col_data)
        # sort max to min each col
        input('check only the unknown is string rest sort correct')
    return df

    
def fix_regions(df):
    df = df.copy()
    
    # {'Eurasia', 'Middle East', 'Africa', 'North America', 'Asia Pacific', 'Europe', 'Central & South America'}
    print(set(df['region'].to_list()))
    region_dict = {'Eurasia': 'Asia', 'Middle East': 'Africa', 'North America': 'Americas', 'Asia Pacific': 'Oceania', 'Central & South America': 'Americas'}
    df['region'] = df['region'].replace(region_dict)
    print(set(df['region'].to_list()))
    
    return df


def harmonize_countries(df, countries_dict):
    df = df.copy()
    # for k,v in countries_dict.items():
    #     print(len(v))

    countries_col = set(df['country/area'].to_list())
    region_col = set(df['region'].to_list())
    # print(region_col)
    # results = []
    # for region in region_col:
        
    #     df_mask = df[df['region']==region]
    #     df_mask['country-harmonize-pass'] = df_mask['country/area'].apply(lambda x: 'true' if x in countries_dict[region] else f"false because {x}")
    #     results_len = df_mask[df_mask['country-harmonize-pass'] == 'false']
    #     results.append((region, len(results_len)))
    #     print(f'\nWe want this to be 0: {results}\n')
    issue_countries = []
    countries_list = []
    for k,v in countries:
        countries_list.append(v)
    print(countries_list)
    
    for country in countries_col:
        if country in countries_list:
            pass
        else:
            print(f'Issue with country: {country}')
            issue_countries.append(country)


        
    df['areas-subnat-sat-display'] = df.apply(lambda row: f"{row['country/area']}" if row['subnational-unit'] == '' else f"{row['subnational-unit']}, {row['country/area']}", axis=1)   
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
df = fix_coords(df)
df = fix_status_inferred(df)
df = scaling_cap(df)
df = fill_nans(df)
df = rename_cols(df)
df = fix_regions(df)
# df = harmonize_countries(df, countries) # find out if they are valid and how to handle regions TODO
print(df.info())

input_to_output(df, f'{output_folder}data-{iso_today_date}.csv')

# def test_stats(df):
#     df = df.copy() 
#     # stats to know for testing:
#     # Total Units: 1,541Total Capacity: 1,405,657.8
#     # Total Operating Units: 419Total Capacity: 396,484
#     # Total Mothballed Units: 27Total Capacity: 22,765
#     # Total Asia Units: 621Total Capacity: 625,830
#     # Total Kenya Units: 2Total Capacity: 4,000

#     return df

# test_stats(df) # 890 total starting 