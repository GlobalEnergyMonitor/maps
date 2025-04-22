
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
from helper_functions import *
import chardet
from config import countries

# Get today's date
today_date = date.today()
# Format the date in ISO format
iso_today_date = today_date.isoformat()
iso_today_date_folder = f'{iso_today_date}/'
client_secret = "Desktop/GEM_INFO/client_secret.json"

client_secret_full_path = os.path.expanduser("~/") + client_secret
gem_path = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/'

tracker_folder = 'gas-plant'

test_results_folder = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/gas-plant/test_results/'

output_folder = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/gas-plant/compilation_output/'

os.makedirs(test_results_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# input_file_csv = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/nuclear/compilation_input/all-fields-2024-07-11T012203-nuclear.csv'

input_file_key = '19fwJMVF-8fWD4x2Awyebj86mi8lrdv52e7Ww1wXHyrk'

def final_count(df):
    grouped_tracker = df.groupby('project', as_index=False)['id'].count()
    print(print(grouped_tracker))

    # no return

def df_info(df, key):
    # find all col name changes 


    # numerical_cols = ['Capacity (MW)', 'Start year', 'Retired year', 'Planned retire', 'Latitude', 'Longitude']
    numerical_cols = ''
    col_info = {}
    all_cols = df.columns
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
    cols = col_info_df.columns
    print(cols)
    # input('Copy cols for renaming!')
    col_info_df = col_info_df.T # transpose

    col_info_df.to_csv(f'{test_results_folder}/{key}_column_info_{iso_today_date}.csv',  encoding="utf-8")
    print(f'saved col info for  here: "{test_results_folder}/{key}_column_info_{iso_today_date}.csv"')
    
    return cols

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
    
        # print(tab)
        wait_time = 5
        time.sleep(wait_time)
        gsheets = gspread_creds.open_by_key(key)
        # Access a specific tab
        spreadsheet = gsheets.worksheet(tab)
        
        # Attempt to fetch data from the sheet
        gsheets = gspread_creds.open_by_key(key)
        # Access a specific tab
        spreadsheet = gsheets.worksheet(tab)
        df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
        df = df.replace('*', pd.NA).replace('Unknown', pd.NA).replace('--', pd.NA) # TODO maybe deal in another way?
        df = df.fillna('')
        list_of_dfs.append(df)

    if len(list_of_dfs) > 1: 
        # df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True).fillna('')
        
        df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True).fillna('')

    return df

def open_csv_no_error(file):
    # Read the file as binary and detect encoding
    with open(file, 'rb') as f:
        result = chardet.detect(f.read())

    # Read the file using the detected encoding
    df = pd.read_csv(file, encoding=result['encoding'])
    return df

def rename(df):
    renamed_df = df.copy()
    curr_cols =['Wiki URL', 'Country/Area', 'Plant name',
       'Plant Name in Local Language / Script', 'Other Name(s)', 'Unit name',
       'Fuel', 'Capacity (MW)', 'Status', 'Turbine/Engine Technology',
       'Equipment Manufacturer/Model', 'CHP', 'Hydrogen capable?',
       'CCS attachment?', 'Conversion/replacement?',
       'Conversion from/replacement of (fuel)',
       'Conversion from/replacement of (GEM unit ID)', 'Start year',
       'Retired year', 'Planned retire', 'Operator(s)', 'Owner(s)',
       'Parent(s)', 'Latitude', 'Longitude', 'Location accuracy', 'City',
       'Local area (taluk, county)', 'State/Province', 'Subregion', 'Region',
       'Other IDs (location)', 'Other IDs (unit)', 'Captive industry use',
       'Captive industry type', 'Captive non-industry use', 'GEM location ID',
       'GEM unit ID']
    
    # final needed for map
    old_cols = ['fuel_type', 'technology', 'project', 'unit', 'project_loc', 'owner',
       'parent', 'capacity', 'status', 'region', 'country', 'province',
       'start_year', 'url', 'lat', 'lng']
    
    # rename Plant Name in Local Language / Script: project_loc
    # for col in curr_cols:
    #     col = col.split('(')[0]
    #     col = col.lower().replace(' ', '_')
    renaming_dict = {'Fuel':'fuel_type', 'Turbine/Engine Technology': 'technology', 'Plant name' :'project',
                     'Unit name':'unit', 'Plant Name in Local Language / Script':'project_loc', 'Owner(s)':'owner',
                     'Parent(s)':'parent', 'Capacity (MW)':'capacity', 'Status':'status', 'Region':'region',
                     'Country/Area':'country', 'State/Province':'province', 'Start year':'start_year', 'Wiki URL':'url',
                     'Latitude':'lat', 'Longitude':'lng'}
    renamed_df = renamed_df.rename(columns=renaming_dict)
    # filter out cols not needed
    renamed_df = renamed_df[old_cols]
    print(renamed_df.columns)
    input('check cols, filterd by old cols!!')
    return renamed_df

def fix_status_inferred(df):

    print(f"Statuses before: {set(df['status'].to_list())}")

    inferred_statuses_cancelled = df['status'].str.contains('cancelled - inferred')
    inferred_statuses_shelved = df['status'].str.contains('shelved - inferred')

    df.loc[inferred_statuses_cancelled, 'status'] = 'cancelled'
    df.loc[inferred_statuses_shelved,'status'] = 'shelved'

    print(f"Statuses before: {set(df['status'].to_list())}")

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
        
    # df['areas-subnat-sat-display'] = df.apply(lambda row: f"{row['country']}" if row['state/province'] == '' else f"{row['state/province']}, {row['country']}", axis=1)   
    return df

def remove_implied_owner(df):
    # filter df where owner or parent contains no semicolon
    # filter furhter where owner parent contains 0 or 100 %
    df = df.copy()
    # mask2 = df['owner'].str.contains('[0%]')
    mask2 = ~df['owner'].str.contains(';')
    mask3 = df['owner'].str.contains('[100%]')
    mask4 = ~df['owner'].str.contains(',')

    maskimplied = mask2 & mask3 & mask4
    df.loc[maskimplied, 'owner'] = df.loc[maskimplied, 'owner'].str.replace('[100%]', '', regex=False)
    
    # oddly not working, but also fine because this is actually not misleading often not at least
    # mask5 = df['parent'].str.contains('[100%]')
    # mask6 = ~df['parent'].str.contains(',')
    # mask7 = ~df['parent'].str.contains(';')

    
    # maskimplied2 = mask5 & mask6 & mask7
    # df.loc[maskimplied2, 'parent'] = df.loc[maskimplied2, 'parent'].str.replace('[100%]', '', regex=False)    
    
    # print(df['owner'])
    # input('check mask 100% owner')
    print(df['parent'])
    input('check mask 100% parent')
    
    # loop through each row of df
    # if the parent or owner value contains no semicolon so is a single value
    # then remove the implied owner of 0 or 100 otherwise keep it
    return df

def formatting_checks(df):
    df = df.copy()    
    # make sure 0% and 100% is removed from owners
    df = remove_implied_owner(df)
    # make sure date is not a float
    df['start_year'] = df['start_year'].replace('not found', np.nan)
    # df['start_year'] = df['start_year'].replace('', np.nan)
    # mask2 = np.isfinite(df['start_year'])
    mask_notna = df['start_year'].notna()
    mask_notstring = ~df['start_year'].apply(lambda x: isinstance(x, str))
    df.loc[mask_notna & mask_notstring, 'start_year'] = df.loc[mask_notna & mask_notstring, 'start_year'].astype(int)
    # round the capacity float
    # replace nans with ''
    df = df.fillna('')
    # transform inferred statuses to real statuses
    df = fix_status_inferred(df)
    # check country and region harmonization
    harmonize_countries(df, countries)
    return df



def input_to_output(df, output_file):

    df = df.copy()
    
    if output_file == None:
        pass
    else:
        df.to_csv(output_file, encoding='utf-8', index=False)
        print(f'done {output_file}')
    return df


### CALL ALL

df = gspread_access_file_read_only(input_file_key, ['Gas & Oil units'])
# old_df = open_csv_no_error('/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/gas-plant/data.csv')
cols = df_info(df, 'gogpt_current')
# cols_old = df_info(old_df, 'gogpt_old')
renamed_df = rename(df)
formatted_df = formatting_checks(renamed_df)
input_to_output(formatted_df, f'{output_folder}data-{iso_today_date}.csv')


def test_stats(df):
    df = df.copy()
    # stats to know for testing:
    # Total Units: 1,541Total Capacity: 1,405,657.8
    # Total Operating Units: 419Total Capacity: 396,484
    # Total Mothballed Units: 27Total Capacity: 22,765
    # Total Asia Units: 621Total Capacity: 625,830
    # Total Kenya Units: 2Total Capacity: 4,000
    # 166 countries

    # 12,436 oil and gas power units

    # 2,108 GW of operating capacity

    # 751 GW of in development capacity
    in_dev_statuses = ['construction', 'pre-construction', 'announced']
    country_count = len(set(df['country'].to_list()))
    total_units = len(df)
    total_operating_capacity = df[df['status'] == 'operating']['capacity'].sum()
    # total_dev_capacity = df[df['status'] in in_dev_statuses]['capacity'].sum()
    country_with_most_units = df['country'].value_counts().idxmax()
    country_with_most_capacity = df.groupby('country')['capacity'].sum().idxmax()
    # Total Dev Unit Capacity: {total_dev_capacity}
    print(f'Total Units: {total_units} Total Operating Unit Capacity: {total_operating_capacity} Country with most units: {country_with_most_units} Country with most capacity: {country_with_most_capacity} Total countries: {country_count}')
    return df

test_stats(formatted_df)