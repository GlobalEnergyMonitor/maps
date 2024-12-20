import pandas as pd
from all_config import *
from helper_functions import *

# creates the file for the single map
def get_key_tabs_prep_file(tracker):
    prep_df = create_prep_file(multi_tracker_log_sheet_key, prep_file_tab)

    prep_dict = prep_df.to_dict(orient='index')

    if tracker in non_gsheet_data:
        print('Needs to be local')
    else:
        key = prep_dict[tracker]['gspread_key']
        tabs = prep_dict[tracker]['gspread_tabs']

    return key, tabs


def create_df(key, tabs):
    dfs = []
    for tab in tabs:
        gsheets = gspread_creds.open_by_key(key)
        spreadsheet = gsheets.worksheet(tab)
        df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
        dfs += [df]
    df = pd.concat(dfs).reset_index(drop=True)
    # df = pd.read_excel(input_file_xls, sheet_name=None)
    # print(df)
    print(df.info())
    
    return df


def rename_cols(df):
    df = df.copy()
    df = df.rename(columns=str.lower)
    df.columns = df.columns.str.replace(' ', '-')
    df = df.rename(columns={'latitude': 'lat', 'longitude':'lng', 'wiki-url': 'url'})
    print(df.info())
    return df

def filter_cols(df, final_cols):
    df = df.copy()
    df = df[final_cols]
    
    # df = df.fillna('')
    # print(df.info())
    
    return df

def input_to_output(df, output_file):


    df = df.copy()
    
    if output_file == None:
        pass
    else:
        df.to_csv(output_file, encoding='utf-8', index=False)
        print(f'done {output_file}')
    return df

def input_to_output_all(df_or_dict, output_file):
    # check if being given a dict of dfs
    # print as csv and geojson
    if type(df_or_dict) == dict:
        for key, value in df_or_dict.items():
            print(f'For map type {key} printing to csv and json!')
            df = value.copy()
            
            if output_file == None:
                pass
            else:
                df.to_csv(f'{output_file}{key}.csv', encoding='utf-8', index=False)
                print(f'done {output_file}{key}.csv')
                gdf_to_geojson(df, f'{output_file}.geojson')
    return df

def test_stats(df):
    df = df.copy()
    print(df.info())
    print(df['status'].value_counts())
    # print(df['fuel'].value_counts())
    print(df['type'].value_counts())
    print(df['capacityinbcm/y'].sum())
    # print(df['capacity-(mw)'].sum())
    print(df['areas'].value_counts())
    # print(set(df['project-name'].to_list()))
    # print(set(df['unit-name'].to_list()))
    # # print(len(df['project-name']))
    # print(len(df['unit-name']))
    # stats to know for testing:
    # Total Units: 1,541Total Capacity: 1,405,657.8
    # Total Operating Units: 419Total Capacity: 396,484
    # Total Mothballed Units: 27Total Capacity: 22,765
    # Total Asia Units: 621Total Capacity: 625,830
    # Total Kenya Units: 2Total Capacity: 4,000

    return df
