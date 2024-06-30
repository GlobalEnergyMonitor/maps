# import sqlalchemy as sa
import pandas as pd
import numpy as np
import math
import os
from datetime import date
import csv
import gspread
from config import *

# def create_folder_if_no(folder_path):
#     if not os.path.exists(folder_path):
#         try:
#             # Create the folder if it doesn't exist
#             os.makedirs(folder_path)
#             print(f"Folder '{folder_path}' created successfully.")
#         except OSError as e:
#             print(f"Error creating folder '{folder_path}': {e}")
#     else:
#         print(f"Folder '{folder_path}' already exists.")


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

    for tab in tab_list:
        print(tab)
        gsheets = gspread_creds.open_by_key(key)
        # Access a specific tab
        spreadsheet = gsheets.worksheet(tab)
        # expected_header option provided following: https://github.com/burnash/gspread/issues/1007
        # Getting All Values From a Worksheet as a List of Dictionaries
        # if key in [list of pipelines sheets]
        # df = pd.DataFrame(spreadsheet.get_all_records[2:](expected_headers=[]))
        # Attempt to fetch data from the sheet
        gsheets = gspread_creds.open_by_key(key)
        # Access a specific tab
        spreadsheet = gsheets.worksheet(tab)
        df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
        df = df.replace('*', pd.NA).replace('Unknown', pd.NA)
        df = df.dropna()
        df['tracker'] = tab

        list_of_dfs.append(df)

    # if len(list_of_dfs) > 1: 
    #     df = pd.concat(list_of_dfs, sort=False).reset_index(drop=True).fillna('')
    # else: 
    #     for i in list_of_dfs:
    #         df = i
    return list_of_dfs

def create_gmet_df(gmet_key, gmet_tabs):

    df = gspread_access_file_read_only(gmet_key, gmet_tabs)
    
    return df


list_of_dfs = create_gmet_df(gmet_key, gmet_tabs)

# df = pd.read_csv('/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/gmet/test/check.csv')
# print(df.columns)

# df.to_csv(f'{path_for_download_and_map_files_test}check.csv')

# we want to pivot on the plume id nope on the infrastrucrue name UNSURE
# filter by tracker type, and status, then if I can attribution information have that field be on other ones, if match by name
# // # O&G extraction areas and coal mines by status 
# // plumes by "has attribution information"
# // infrastructure emissions estimates

# rename all non plume emissions to be the same
renamed_list_of_dfs = []
for df in list_of_dfs:
    print(df.loc[0,'tracker'])
    est_emissions_cols = ['GEM Coal Mine Methane Emissions Estimate (Mt/yr)', 'Emissions if Operational (tonnes/yr)', 'Climate TRACE Field Emissions (tonnes)', 'Emissions for whole reserves with latest emissions factors (tonnes)']
    for col_name in est_emissions_cols:
        if col_name in df.columns:
            df = df.rename(columns={col_name: 'est_emissions'})
            print("renamed estimated emissions!")
    
    if df.loc[0,'tracker']=='Plumes':
        df = df.rename(columns={'Emissions (kg/hr)': 'plume_emissions', 'GEM Infrastructure Name': 'infra_name', 'Subnational Unit': 'subnational',
                            'Country/Area': 'area', 'Plume Origin Latitude': 'lat', 'Plume Origin Longitude': 'lng', 
                            'Observation Date': 'date', 'GEM Wiki': 'url', 'Name': 'name', 'For map only (has attribution information)': 'plume_filter'})
        print("renamed Plumes!")
        renamed_list_of_dfs.append(df)

    if df.loc[0,'tracker'] == 'Coal Mines':
        df = df.rename(columns = {'Mine Name': 'name', 'GEM Wiki URLs': 'url', 'Status': 'status', 'Production (Mtpa)': 'capacity_prod', 
                                  'Coal Output (Annual, Mst)': 'capacity_output', 'Owners': 'owners', 'Latitude':'lat', 'Latitude': 'lng'})
        
        print("renamed Coal Mines!")
        renamed_list_of_dfs.append(df)

    if df.loc[0,'tracker'] == 'Pipelines':
        df = df.rename(columns = {'Pipeline Name': 'name', 'GEM Wiki': 'url', 'Status': 'status', 'Length Merged Km': 'length', 
                                  'Capacity (cubic meters/day)': 'capacity', 'Countries': 'countries', 'WKTFormat': 'geometry'})
        print("renamed Pipelines!")
        renamed_list_of_dfs.append(df)

    if df.loc[0,'tracker'] == 'Oil and Gas Extraction Areas':
        df = df.rename(columns = {'GEM GOGET ID': 'goget_id','Unit name':'name', 'GEM Wiki': 'url', 'Status': 'status', 'Status Year': 'status_year', 'Operator': 'operator',
                                  'ClimateTrace Field': 'subnational', 'Country': 'country', 'Latitude':'lat', 'Latitude': 'lng'})
        print("renamed Oil and Gas Extraction Areas!")
        renamed_list_of_dfs.append(df)

    if df.loc[0,'tracker'] == 'Oil and Gas Reserves':
        df = df.rename(columns = {'GEM GOGET ID': 'goget_id'})
    
        print("renamed Oil and Gas Reserves!")
        renamed_list_of_dfs.append(df)


if len(renamed_list_of_dfs) > 1: 
    df = pd.concat(renamed_list_of_dfs, sort=False).reset_index(drop=True).fillna('')
else: 
    for i in renamed_list_of_dfs:
        df = i


# for plumes add link to wiki page of attributed project - get that from P N or O:  California VISTA and other Government ID Assets (Nearby), GEM Infrastructure Wiki, Government Well ID (Nearby)

# no need to bring in capacity? use a average emissions for size for all but plumes, for plumes in another color do the size of emissions 

# conflate goget into one ... on id 

# handle multiple countries pipelines - pick one country then list out all countries

# handle two capacity options for GCMT - pull from one or other loop 

# handle geometry - pipelines and other lat lng 

# handle statuses, and empty geo or empty plume emissions 


# df.to_csv(f'{path_for_download_and_map_files_test}renamed.csv')
