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
from config import *
import time

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
    
    
def fix_coords(df, lat='Latitude', lng='Longitude'):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df.dtypes) # more options can be specified also  
        
    print(f'len at beginning: {len(df)}')

    df = df.copy()
    df[lat] = df[lat].apply(lambda x: check_and_convert_float(x))
    df[lng] = df[lng].apply(lambda x: check_and_convert_float(x))
    print("Check which rows will be dropped because nan coords:")
    print(df[df.isna().any(axis=1)])
    nan_df = df[df.isna().any(axis=1)]
    nan_df.to_csv(f'test/{df["tracker"].loc[0]}_nan_coords_{today_date}.csv')

    print(f"This is tracker: {df['tracker'].loc[0]}")
    print(f"This is lat: {lat}")
    print(f"This is lng: {lng}")
    df.dropna(subset = [lat, lng], inplace=True)
    print(f'len at end: {len(df)}')
    return df

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
        print(f"This is tab: {tab}")
        time.sleep(2)  # Sleep for 1 second

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
        # print(tab)
        # print(df['tracker'])
        # fix coords 
        if tab == 'Oil and Gas Reserves':
            
            list_of_dfs.append(df)
            
        elif tab == 'Pipelines':
            # filter out -- geom
            df = df[df['WKTFormat']!= '--']
            df_na = df[df['WKTFormat']== '--']
            df_na.to_csv(f'test/{tab}_nan_coords_{today_date}.csv')
            list_of_dfs.append(df)

        elif tab == 'Plumes':
            latcol = 'Plume Origin Latitude'
            lngcol = 'Plume Origin Longitude'
            df = fix_coords(df, latcol, lngcol) 
            list_of_dfs.append(df)
    
        elif tab == 'Global Coal Mine Tracker (Non-C':
            print(f'Skipping so can handle justs for coal mine merge')
            list_of_dfs = df
        elif tab == 'Countries':
            list_of_dfs = df
        else:
            print(tab)
            df = fix_coords(df, 'Latitude', 'Longitude')   
            list_of_dfs.append(df)

    
    return list_of_dfs

def create_gmet_df(gmet_key, gmet_tabs):

    df = gspread_access_file_read_only(gmet_key, gmet_tabs)
    
    return df

## START OF RE PULL
list_of_dfs = create_gmet_df(gmet_key, gmet_tabs)

# we want to pivot on the plume id nope on the infrastrucrue name UNSURE
# filter by tracker type, and status, then if I can attribution information have that field be on other ones, if match by name
# // # O&G extraction areas and coal mines by status 
# // plumes by "has attribution information"
# // infrastructure emissions estimates


def fill_in_missing_coal_mines(list_of_dfs):
    
    cm_key = '1OJIEYKHR6L9-w1jbSPQr01X3w4Ot0qOWoKaVuZCrEc4'
    cm_tab = ['Global Coal Mine Tracker (Non-C']
    
    cm_df = gspread_access_file_read_only(cm_key, cm_tab)
    # only need ID and country 
    cm_df = cm_df[['GEM Mine ID', 'Country']]
    cm_df = cm_df.rename({'Country': 'areas'}, axis=1)
    print(f"This is cm_df: {cm_df}")
    new_list_of_dfs = [] # to be safe
    for df in list_of_dfs:
        df = df.copy()
        if df['tracker'].loc[0] == 'Coal Mines':
            
            # merge in on MINE ID the country
            methane_cm_df = df.copy()
            print(f"This is Coal Mines / methane_cm_df: {methane_cm_df}")
            
            merged_cm_df = pd.merge(left=methane_cm_df, right=cm_df, on='GEM Mine ID', how='outer')
            
            # filter_ids = (methane_cm_df['GEM Mine ID'].to_list())
            # # cm_ids = (cm_df['GEM Mine ID'].to_list())
            # # new_ids_to_drop = cm_ids - filter_ids
            # # print(f"New ids to drop: {new_ids_to_drop}")
            merged_cm_df['areas'] = merged_cm_df['areas'].fillna('')
            merged_cm_df_drop = merged_cm_df[merged_cm_df['areas']== '']
            merged_cm_df_keep = merged_cm_df[merged_cm_df['areas']!= '']
            print(f"len of merged_cm_df_keep: {len(merged_cm_df_keep)}")
            # merged_cm_df_keep.to_csv(f'coal_mines_with_country_test{today_date}.csv')
            # merged_cm_df_drop.to_csv(f'coal_mines_no_country_drop{today_date}.csv')
            
            # to_drop = merged_cm_df_drop.index.to_list()
            # print(f'this is list of indexs to drop: {to_drop}')
            # # for row in merged_cm_df.index:
            # #     if merged_cm_df.loc[row, '']
            # merged_cm_df = merged_cm_df.drop(index=to_drop)
            
            # print(f"This is merged_cm_df: {merged_cm_df}")
            # print(f"This is cols for merged_cm_df: {merged_cm_df.columns}")
            
            # print(f"This is country of merged: {merged_cm_df['areas']}")
            
            
            # need to merge it back into non cm df 
            new_list_of_dfs.append(merged_cm_df_keep)
        else:
            new_list_of_dfs.append(df)
            print(f'Append but pass')
    
    print(len(new_list_of_dfs))
    for df in new_list_of_dfs:
        print(f"This is tracker: {df['tracker']}")
    return new_list_of_dfs

list_of_dfs = fill_in_missing_coal_mines(list_of_dfs)



def rename_dfs(list_of_dfs):
    # rename all non plume emissions to be the same
    renamed_list_of_dfs = []
    for df in list_of_dfs:
        df = df.copy()
        df.reset_index(drop=True, inplace=True)
                
        if df.loc[0,'tracker']=='Plumes':
            df = df.rename(columns={'Emissions (kg/hr)': 'plume_emissions', 'GEM Infrastructure Name (Nearby)': 'infra_name', 'Subnational Unit': 'subnational',
                                'Country/Area': 'areas', 'Plume Origin Latitude': 'lat', 'Plume Origin Longitude': 'lng', 
                                'Observation Date': 'date', 'GEM Wiki': 'url', 'Name': 'name', 'For map only (has attribution information)': 'infra_filter'})
            print("renamed Plumes!")
            renamed_list_of_dfs.append(df) # 'California VISTA and other Government ID Assets (Nearby)': 'cal_gov_assets', 'Government Well ID (Nearby)': 'gov_well','GEM Infrastructure Wiki': 'infra_wiki',

        if df.loc[0,'tracker'] == 'Coal Mines':
            df = df.rename(columns = {'GEM Coal Mine Methane Emissions Estimate (Mt/yr)': 'mtyr-gcmt_emissions','Mine Name': 'name', 'GEM Wiki URLs': 'url', 'Status': 'status', 'Production (Mtpa)': 'capacity_prod', 
                                    'Coal Output (Annual, Mst)': 'capacity_output', 'Owners': 'owner', 'Latitude' : 'lat', 'Longitude': 'lng'})
            
            print("renamed Coal Mines!")
            renamed_list_of_dfs.append(df)

        if df.loc[0,'tracker'] == 'Pipelines':
            df = df.rename(columns = {'Emissions if Operational (tonnes/yr)':'tonnesyr-pipes_emissions','Pipeline Name': 'name', 'GEM Wiki': 'url', 'Status': 'status', 'Length Merged Km': 'pipe_length', 
                                    'Capacity (cubic meters/day)': 'capacity', 'Countries/Areas': 'areas', 'WKTFormat': 'geometry'})
            print("renamed Pipelines!")
            renamed_list_of_dfs.append(df)

        if df.loc[0,'tracker'] == 'Oil and Gas Extraction Areas':
            df = df.rename(columns = {'Climate TRACE Field Emissions (tonnes)':'tonnes-goget_emissions','GEM GOGET ID': 'goget_id','Unit name':'name', 'GEM Wiki': 'url', 'Status': 'status', 'Status year': 'status_year', 'Operator': 'operator',
                                    'ClimateTrace Field (encompasses GEM field)': 'related_cm_field', 'Country/Area': 'areas', 'Latitude':'lat', 'Longitude': 'lng'})
            print("renamed Oil and Gas Extraction Areas!")
            renamed_list_of_dfs.append(df)

        if df.loc[0,'tracker'] == 'Oil and Gas Reserves':
            df = df.rename(columns = {'GEM GOGET ID': 'goget_id', 'Emissions for whole reserves with latest emissions factors (tonnes)': 'tonnes-goget-reserves_emissions', 'Country/Area': 'areas'})
            # print(df.columns)
            print("renamed Oil and Gas Reserves!")
            renamed_list_of_dfs.append(df)


    if len(renamed_list_of_dfs) > 1: 
        df = pd.concat(renamed_list_of_dfs, sort=False).reset_index(drop=True)
    else: 
        for i in renamed_list_of_dfs:
            df = i
    df.to_csv('test/gmet_concatted.csv')
    return df

gmet_df = rename_dfs(list_of_dfs)


def consolidate_statuses(df):
    df = df.copy()
    # find nan status
    df['status'] = df['status'].fillna('unknown') # help with filtering 
    print(set(df['status'].to_list()))
    
    df['status_legend'] = df.copy()['status'].str.lower().replace(status_legend)
    df['status'] = df['status'].apply(lambda x: x.lower())
    print(set(df['status'].to_list()))
    print(set(df['status_legend'].to_list())) 
    
    return df

gmet_df = consolidate_statuses(gmet_df)


# save gmet as csv file 
gmet_df.to_csv(f'{path_for_download_and_map_files_test}{today_date}ready_to_be_manipulated.csv')
print(f'saved the file for {today_date}')

## END OF REPULL

def read_local_csv(file_path):
    df = pd.read_csv(file_path)
    return df


df = read_local_csv(local_file_path)
print(f'Using: {local_file_path} for the df')

# df = gmet_df.copy()

def check_length_start(df):
    
    for tracker in set(df['tracker'].to_list()):
        # print(set(df['tracker'].to_list()))
        print(f"Starting Length for {tracker}: {len(df[df['tracker']==tracker])}")
    print(f"This is the starting shape of {tracker} df: {df.shape}")

check_length_start(df)

def create_scaling_col(df):
    
    df = df.copy()
    # for tracker in set(df['tracker'].to_list()):
    #     print(tracker) # good here
    plume_df = df[df['tracker'] == 'Plumes']
    plume_df.fillna('', inplace=True)
    plume_df = plume_df[plume_df['plume_emissions']!= '']
    plume_df['plume_emissions'] = plume_df['plume_emissions'].apply(lambda x: round(x, 2))
    
    plume_tot_emissions = plume_df['plume_emissions'].astype(float).sum()  
    plume_projects = len(plume_df)
    plume_emissions_avg = plume_tot_emissions / plume_projects
    print(f"Sum of plume emissions: {plume_tot_emissions}")
    print(f"Number of plume projects: {plume_projects}")
    print(f"Average plume emissions: {plume_emissions_avg}")
    
    # if there is no plume emissions then use average otherwise use plume emissions ... 
    non_plume_df = df[df['tracker']!= 'Plumes']
    non_plume_df['scaling_col'] = plume_emissions_avg
    plume_df['scaling_col'] = plume_df['plume_emissions']
    
    # check that plume emissions is only there for plume tracker
    plume_emissions_avg_check = ((plume_df['plume_emissions'].sum()) / (len(plume_df)))
    print(f"Check that plume avg is right: {plume_emissions_avg_check} vs. {plume_emissions_avg}")
    
    # make it round to 2
    plume_df['plume_emissions'] = plume_df['plume_emissions'].astype(float).round(2)
    # make it round to 2
<<<<<<< HEAD
    plume_df['emission_uncertainty'] = plume_df['emission_uncertainty'].astype(float).round(2)
=======
    plume_df['Emissions Uncertainty (kg/hr)'] = plume_df['Emissions Uncertainty (kg/hr)'].astype(float).round(2)

>>>>>>> 81808373619ec7caaa2f0f4b2814984378a66e84
    
    # concat them back 

    df = pd.concat([non_plume_df, plume_df], sort=False).reset_index(drop=True)
    df['scaling_col'] = df['scaling_col'].fillna('')
    
    for row in df.index:
        if df.loc[row, 'scaling_col'] == '':
            df.loc[row, 'scaling_col'] = plume_emissions_avg


    return df

df = create_scaling_col(df)


def inspect_goget(df):
    df = df.copy()
    
    for tracker in set(df['tracker'].to_list()):
        print(tracker)
    
    reserves_df = df[df['tracker'] == 'Oil and Gas Reserves']
    extraction_df = df[df['tracker'] == 'Oil and Gas Extraction Areas']
    # all_other_df = df[(df['tracker'] != 'Oil and Gas Extraction Areas') & (df['tracker'] != 'Oil and Gas Reserves')]
    all_other_df = df[df['tracker'] != 'Oil and Gas Reserves']
    all_other_df = all_other_df[all_other_df['tracker'] != 'Oil and Gas Extraction Areas']    
    
    # print(len(df))
    # print(len(reserves_df))
    # print(len(extraction_df))
    print(f'This is len of all_other_df: {len(all_other_df)}')
        
    # print(f"Cols in Reserves: {reserves_df.columns}")
    # print(f"Cols in Extraction: {extraction_df.columns}")
    # print(len(reserves_df))
    # print(len(extraction_df))
    # only bring in other_emissions
    reserves_df = reserves_df[['goget_id', 'tonnes-goget-reserves_emissions']]
    extraction_df = extraction_df.drop('tonnes-goget-reserves_emissions', axis=1)
    goget_merged_df = pd.merge(left=reserves_df, right=extraction_df, on='goget_id', how='outer')
    print(f"This is len of goget merged: {len(goget_merged_df)}")
    print(goget_merged_df.shape) 
    goget_merged_df = goget_merged_df.drop_duplicates(subset='goget_id')
    goget_merged_df = goget_merged_df.fillna('')
    goget_merged_df = goget_merged_df[goget_merged_df['tracker']!='']
    goget_merged_df.to_csv('test/goget_merged_df.csv')
    print(f"len of all other df: {len(all_other_df)}")
    new_list_to_concat = []
    for tracker in set(all_other_df['tracker'].to_list()):
        print('for tracker in all_other_df')
        print(tracker)
    
    goget_merged_df = goget_merged_df[goget_merged_df['tracker']!='']    
    goget_merged_df.to_csv('test/goget_merged_df_after_drop.csv')

        # now we don't need reserves so drop it
    for tracker in set(goget_merged_df['tracker'].to_list()):
        print('for tracker in goget_merged_df')
        print(tracker)    
    # print(f"Cols in Reserves: {reserves_df.columns}")
    # print(f"Cols in Extraction: {extraction_df.columns}")
    df_new = pd.concat([all_other_df,goget_merged_df], sort=False).reset_index(drop=True)
    print(len(df_new))
    print(f"This is cols after concat: {set(df.columns.to_list())}")
    for tracker in set(df_new['tracker'].to_list()):
        print('for tracker in df_new')
        print(tracker)
    return df_new

df = inspect_goget(df)

def multiple_countries_format(df):
    # apparently I renamed the country fields in a silly fashion...
    # print(df.columns)
    df = df.copy()
    for tracker in set(df['tracker'].to_list()):
        print(tracker)

    list_area_keyword = ['area', 'country', 'countries', 'Country']
    to_rename = []
    for col in df.columns:
        for keyword in list_area_keyword:
            if keyword in col:
                # print(col)
                to_rename.append(col)
                # we're on a area col
    # find all multiple country situations 
    for row in df.index:
        for col in to_rename:
            # if df.loc[row, col] != '':
            if df.loc[row, col].isna():
                df.loc[row,'country_filter'] = df.loc[row, col]
    df['country_filter'] = df['country_filter'].fillna('') 

    print(f"If this isn't empty we have a missing country/area: {df[df['country_filter']==''][['country_filter']]}")
    # print(f"To rename: {to_rename}")
    # df = df.rename({'country': 'area', 'countries': 'area', 'Country': 'area'}, axis=1)
    # how to merge it all?
    # print(df.columns)
    # find multiple
    all_countries = set(df[df['country_filter']!='']['country_filter'].to_list())
    # print(all_countries)
    # print(df[['country_filter']])
    mult_areas = df[df['country_filter'].apply(lambda x: ',' in x)]
    # print(mult_areas[['country_filter']])
    
    pipelines_only = df[df['tracker']=='Pipelines']
    # print(pipelines_only['country_filter'])
    
    # should be goget where there is a hyphen, split on it, take first one and use it for map filter
    # then make countries for list 
    # coal mines with no country ... pull into from coal mine data on GEM Mine ID 
    
    return df

# df = multiple_countries_format(df)

def handle_capacity_prod(df):
    
    df = df.copy()
    mines_df = df[df['tracker']=='Coal Mines']
    # drop cols that are empty? because forget coal mine cols 
    # capacity_output, capacity_prod
    print(mines_df[['capacity_output', 'capacity_prod']])
    # print situations wher both are not nan or check if both are nan is pd.isna()

handle_capacity_prod(df)

# NAN issue before this for reserves 
def handle_geo_col(df):
    
    # if we do not need pipelines then we can keep lat lng
    
    # if we do want pipelines lets convert to point 
    # and pull in pipelines geojson and filter by list of ids 
    
    # find missing lat lng
    missing_latlnggeo = [] # tracker (row)
    for tracker in set(df['tracker'].to_list()):
        # print(tracker)
        
        print(f"Geo/lat/lng for {tracker}")
        tracker_sel = df[df['tracker']== tracker]
        print(f"Length of tracker: {len(tracker_sel)}")
        for row in tracker_sel.index:
            if tracker == 'Pipelines':
                item = tracker_sel.loc[row,'geometry']
                name = tracker_sel.loc[row,'name']
                if pd.isna(item):
                    missing_latlnggeo.append((tracker, name, 'geo na'))
            else:
                item_lat = tracker_sel.loc[row,'lat']
                item_lng = tracker_sel.loc[row,'lng']
                name = tracker_sel.loc[row,'name']
                if pd.isna(item_lat):
                    missing_latlnggeo.append((tracker, name, 'lat na'))
                if pd.isna(item_lng):
                    missing_latlnggeo.append((tracker, name, 'lng na'))
    # print(f"This is missing_latlnggeo: {missing_latlnggeo}")
    missing_latlnggeo_df = pd.DataFrame(missing_latlnggeo)
    missing_latlnggeo_df.to_csv(f"{path_for_download_and_map_files_test}tracker_name_latlnggeo_missing{today_date}.csv")
    return df

handle_geo_col(df)


# CHECK
# for plumes add link to wiki page of attributed project - get that from P N or O:  California VISTA and other Government ID Assets (Nearby), GEM Infrastructure Wiki, Government Well ID (Nearby)
# CHECK
# no need to bring in capacity? use a average emissions for size for all but plumes, for plumes in another color do the size of emissions 
# CHECK what is the difference between capacity_prod and capacity_output, just keep prod 
# handle two capacity options for GCMT - pull from one or other loop 
# CHECK 
# handle statuses, 
# CHECK
# handle empty plume emissions DONE 
# CHECK
# handle geometry - pipelines and other lat lng # I think I just need to handle na better 
# CHECK
# # handle empty geo
# CHECK seems it should be separate, no conflate on one and keep the emissions info! 
# conflate goget into one ... on id 
# TODO 
# should be goget where there is a hyphen, split on it, take first one and use it for map filter
# then make countries for list 
# coal mines with no country ... pull into from coal mine data on GEM Mine ID 
# NO CHECK There are no multiple countries, but we are missing countries for a lot of rows 11691, all of pipelines 
# handle multiple countries pipelines - pick one country then list out all countries

# get the infra info merged into plume, which name 
# dont' actually need this since we'll just show it

# convert into geojson so can have pipelines! 

def check_corresponding_infra(df):
    df = df.copy()
    df = df.fillna('')
    # for tracker in set(df['tracker'].to_list()):
    #     print(tracker) # good here 
    infra_list = []
    plume_only = df[df['tracker']=='Plumes']
    for row in plume_only.index:
        tracker = plume_only.loc[row, 'tracker']
        infra_filter = plume_only.loc[row, 'infra_filter']
        # Government Well ID (Nearby)
        p_col = plume_only.loc[row, 'California VISTA and other Government ID Assets (Nearby)']
        n_col = plume_only.loc[row, 'GEM Infrastructure Wiki']
        o_col = plume_only.loc[row, 'Government Well ID (Nearby)']
        if infra_filter == 'Y':
            # check that p n or o is not null
            if (len(str(p_col)) + len(str(n_col)) + len(str(o_col)) == 3):

                plume_only.loc[row,'has_info'] = 'no info'
            else:
                plume_only.loc[row,'has_info'] = 'info'

        else:
            plume_only.loc[row,'has_info'] = 'skip'
        
check_corresponding_infra(df)

# def merge_infra_info(df):
#     df = df.copy()
#     # only way is the wiki column
#     # GEM Infrastructure Wiki
#     # url
 
#     return df

# df = merge_infra_info(df)

def last_min_fixes(df):
    
    # status legend needs to have no underscores
    
    print(f"Set of Status Legend before: {set(df['status_legend'].to_list())}")
    df['status_legend'] = df['status_legend'].fillna('unknown-plus') # why is this empty? 
    df['status_legend'] = df['status_legend'].apply(lambda x: x.replace('_', '-'))
    print(f"Set of Status Legend after CHECK config.js: {set(df['status_legend'].to_list())}")
        # remove any NAN areas
    print(len(df))
    df['areas'] = df['areas'].fillna('')
    df_final = df[df['areas']!='']
    print(len(df_final))
    print(df_final.columns)

    
    # clean out cols
    # lat lng 
    coord_cols = ['lat', 'lng', 'Latitude', 'Longitude']
    # fillna
    for col in coord_cols:
        df_final[col] = df_final[col].fillna('')

    row_to_drop = []
    for row in df_final.index:  
            # if the value for that col is empty fill with another 
            if df_final.loc[row, 'lat'] == '':
                if df_final.loc[row, 'Latitude'] == '':
                    # drop it
                    row_to_drop.append(row)
                else:
                    # otherwise use the Latitude value for lat
                    df_final.loc[row, 'lat'] = df_final.loc[row, 'Latitude']
                    
            if df_final.loc[row, 'lng'] == '':
                if df_final.loc[row, 'Longitude'] == '':
                    # drop it
                    row_to_drop.append(row)
                else:
                    # otherwise use the Longitude value for lat
                    df_final.loc[row, 'lng'] = df_final.loc[row, 'Longitude'] 
                    
    print(f'this is row to drop: {row_to_drop}')
    print(len(row_to_drop)) 
                 
    df_finaler = df_final.drop('Longitude', axis = 1)
    df_finaler = df_finaler.drop('Latitude', axis = 1)
    
    # fill in plume data with avg DONE
    # use filler wiki page https://globalenergymonitor.org/projects/global-methane-emitters-tracker/
    # or "no page yet"
    df_finaler['url'].fillna(filler_wiki_url)
    df_finaler['url'] = df_finaler['url'].apply(lambda x: filler_wiki_url if x == '' else x)
    # df_finaler['url'] = df_finaler['url'].apply(lambda x: filler_wiki_url if pd.isna(x) else x)


    # replace scaling cap at 0 with .01
    # df_finaler['scaling_col'] = df_finaler['scaling_col'].apply(lambda x: (x).replace('0', '0.1'))
    
    return df_finaler

df = last_min_fixes(df)

def clean_col_names(df):
    
    # delete first two columns
    cols_tobedropped = ['Quantity (conveted)', 'Units (converted)', 'Reserves Classification (Original)','GEM Mine ID','Unnamed: 0','Climate TRACE Field Estimate Year', 'Climate TRACE Field Emissions Factor (T CH4 per T of product produced)','Fuel description',
    'Upstream methane intensity (kg/boe)','Reserves Data Year','Quantity (boe)', 'GEM Methane Plume ID', 
    'Satellite Data Provider', 'Provider ID', 'Satellite Data Provider Ref', 'Infrastructure Notes']
    
    tbrenamed = {'status_legend':'status-legend','infra_filter':'infra-filter','Instrument': 'instrument','Emissions Uncertainty (kg/hr)': 'emission_uncertainty','Type of Infrastructure': 'infra_type',  'GEM Infrastructure Wiki': 'infra_url', 'Government Well ID (Nearby)': 'well_id', 'California VISTA and other Government ID Assets (Nearby)': 'gov_assets'}
    df = df.rename(tbrenamed, axis=1)
    df = df.drop(labels=cols_tobedropped, axis=1)
    cols = df.columns.to_list() 
    print(cols)
    
    # make trackers have no spaces or underscroes
    df['tracker'] = df['tracker'].apply(lambda x: x.lower().replace(' ', '-'))

    return df

df = clean_col_names(df)


def make_id_for_link_field(df):
    df = df.copy()
    df = df.reset_index()
    df['map_id'] = df.index
    print(len(df))
    df = df.drop_duplicates(subset = 'map_id')
    print(len(df))

    return df

df = make_id_for_link_field(df)


def split_plumes_out_attrib(df):
    
    df = df.copy()
    
    # df['tracker'] = df.apply(lambda row: row['tracker']=='plumes' and row['infra-filter']== 'Y' then plumes-attrib)
    # df['tracker'] = df.apply(lambda row: row['tracker']=='plumes' and row['infra-filter']== 'N' then plumes-unattrib)
    df['tracker'] = df.apply(lambda row: 'plumes-attrib' if row['tracker'] == 'plumes' and row['infra-filter'] == 'Y' else ('plumes-unattrib' if row['tracker'] == 'plumes' and row['infra-filter'] == 'N' else row['tracker']), axis=1)    
    print(df[['tracker','infra-filter']])
    df['infra-filter'] = df['infra-filter'].fillna('')
    return df

df = split_plumes_out_attrib(df)

def get_standard_country_names():
    
    df = gspread_access_file_read_only(
        '1mtlwSJfWy1gbIwXVgpP3d6CcUEWo2OM0IvPD6yztGXI', 
        ['Countries'],
    )

    gem_standard_country_names = df['GEM Standard Country Name'].tolist()
    
    return gem_standard_country_names

gem_standard_country_names = get_standard_country_names()

def fix_countries(df):
    df = df.copy()
    # add ; and split on - or , 
    # account for exceptions
    country_col = 'areas'
    hyphenated_countries = ['Timor-Leste', 'Guinea-Bissau']
    comma_countries = ['Bonaire, Sint Eustatius, and Saba']
    # for row in df.index:
    #         if df.at[row, country_col] in comma_countries:
    #             continue
    #         elif pd.isna(df.at[row, country_col])==False:    
    #             try:
        
    #                 countries_list = gdf.at[row, country_col].split(', ') 
    #                 countries_list = [x.split('-') for x in countries_list if x not in hyphenated_countries]
                    
    #             except:
    #                 # print("Error!" + f" Exception for row {row}, country_col: {df.at[row, country_col]}")
    #                 countries_list = df.at[row, country_col]
                    
    #             # flatten list
    #             countries_list = [
    #                 country
    #                 for group in countries_list
    #                 for country in group
    #             ]
    #             # clean up
    #             countries_list = [x.strip() for x in countries_list]
            
    #             # check that countries are standardized
    #             for country in countries_list:
    #                 if country not in gem_standard_country_names:
    #                     print(f"For row {row}, non-standard country name after trying to standardize: {country}")
    #         else:
    #             continue
    # fix mult countries
    # kuwait-iran to kuwait, iran and main being kuwait
    df['country'] = df['areas']
    for row in df.index:
        if df.at[row, 'country'] in hyphenated_countries or df.at[row, 'country'] in comma_countries:
            continue
        else:
            df.at[row,'country'] = df.at[row,'country'].replace('-',';')
            df.at[row,'country'] = df.at[row,'country'].replace(',',';')
    
    # country is the column holding the fixed areas data with ; and handling multiple countries
    df['country'] = df['country'].apply(lambda x: f"{x};")

    # df['country'].to_csv('countries_check.csv')

    return df

df = fix_countries(df)


<<<<<<< HEAD
# TODO fix start year if not stated replace with ''
def round_cap_emissions(df):
    print(df.columns)
    print('TODO round the emissions and cap columns')
=======
# TODO fix status year if not stated replace with '' DONE
# TODO replace null subnational FIX MULT COUNTRY DONE
# TODO if search field is empty undefined fix search DONE
# TODO find out why some goget still not coming through, likely status 

def is_valid(x):
    return isinstance(x, (int, float)) and not pd.isna(x) and x != '' and x != 0 and x != 0.0
def is_valid_str(x):
    return isinstance(x, (str)) and not pd.isna(x)


def last_min_data_fixes(df):
    for col in ['infra_type', 'gov_assets', 'operator']: # ['infra_type']
        df[col] = df[col].apply(lambda x: x.strip().lower() if is_valid_str(x) else '')

    print(set(df['status'].to_list()))
    print(set(df['tracker'].to_list()))

    # make all search values have something
    print(set(df['infra_type'].to_list()))
    df['infra_type'].fillna('', inplace = True)
    print(set(df['infra_type'].to_list()))
    
    # well_id
    df['well_id'].fillna('', inplace = True)

    # gov_assets
    df['gov_assets'].fillna('', inplace = True)

    # status_year
    df['status_year'].fillna('', inplace = True)
    

    # fix null subnat
    # print(df.columns)
    # print(df.head())

    df['count_of_semi'] = df.apply(lambda row: len(row['country'].split(';')) - 1, axis=1) # if len of list is more than 2, then split more than once
    df['multi-country'] = df.apply(lambda row: 't' if row['count_of_semi'] > 1 else 'f', axis=1)
    # if t then make areas-display 
    df['areas-subnat-sat-display'] = df.apply(lambda row: f"{row['country']}" if row['multi-country'] == 'f' else 'Multiple Countries/Areas', axis=1)

    # infra_url make it a hyperlink html!!
    
    

    return df

df = last_min_data_fixes(df)
# Define a function to check for valid values

    
def round_cap_emissions(df):
    print(df.columns)
    print('TODO round the emissions and cap columns!')
    # emission_uncertainty, plume_emissions, mtyr-gcmt_emissions, capacity_output, capacity_prod, tonnesyr-pipes_emissions, capacity, tonnes-goget_emissions, tonnes-goget-reserves_emissions
    for col in ['emission_uncertainty', 'plume_emissions', 'mtyr-gcmt_emissions', 'capacity_output', 'capacity_prod', 'tonnes-goget_emissions', 'tonnes-goget-reserves_emissions']:
        
        
        df[col] = df[col].apply(lambda x: round(x, 2) if is_valid(x) else '')
>>>>>>> 81808373619ec7caaa2f0f4b2814984378a66e84
    return df

df = round_cap_emissions(df)

<<<<<<< HEAD
=======

# def make_table_wiki_url(df):
#     df = df.copy()
#     df['table_infra_url'] = df.apply(lambda row: f"<a href={infra_url} target='_blank'></a>" if row['infra_url'] != "" else row['infra_url'], axis=1)
#     return df
# df = make_table_wiki_url(df)

def investigate_goget_missing(df):
    
    df = df.copy()
    
    df_mask = df[(df['status-legend']==pd.NA) & (df['tracker']=="oil-and-gas-extraction-areas")]
    df_mask.to_csv('goget_investigate.csv')
    df['status-legend'] = df['status-legend'].mask(df['status-legend']=='', other='unknown-plus')
    df['status-legend'] = df['status-legend'].mask(df['status-legend']==pd.NA, other='unknown-plus')
    df['status'] = df['status'].mask(df['status']=='', other='not found')
    df['status'] = df['status'].mask(df['status']==pd.NA, other='not found')
    
    
    # print(set(df['tracker'].to_list()))
    # df_test = df[df['tracker']=='oil-and-gas-extraction-areas']
    df_mask = df[(df['status-legend']=='') & (df['tracker']=="oil-and-gas-extraction-areas")]
    df_mask.to_csv('goget_investigate.csv')
    # # df_test = df_test['country', 'areas', 'goget_id', 'status', 'status-legend', 'scaling_col', 'map_id', 'infra-filter', 'name', 'lat', 'lng']
    
    # df_test.to_csv('goget_investigate.csv')
    # return nothing 
    return df
df = investigate_goget_missing(df)

# TODO fix start year if not stated replace with ''
def round_cap_emissions(df):
    print(df.columns)
    print('TODO round the emissions and cap columns')
    return df

df = round_cap_emissions(df)

>>>>>>> 81808373619ec7caaa2f0f4b2814984378a66e84
def create_geo(df):
# def convert_coords_to_point(df): from compile all trackers for AET
    crs = 'EPSG: 4326'
    geometry_col = 'geometry'
    for row in df.index:
        df.loc[row,'geometry'] = Point(df.loc[row,'lng'], df.loc[row,'lat'])
    gdf = gpd.GeoDataFrame(df, geometry=geometry_col, crs=crs)
    
    return gdf

gdf = create_geo(df)



def check_length_and_other_end(df):
    
    for tracker in set(df['tracker'].to_list()):
        print(f"Ending Length for {tracker}: {len(df[df['tracker']==tracker])}")
    
    print(f"This is ending cols: {df.columns}")
    print(f"This is the ending shape of df: {df.shape}")
    
    ####
    
    # print(set(df['scaling_col'].to_list()))

check_length_and_other_end(df)

def gdf_to_geojson(gdf, output_file):
    gdf.to_file(output_file, driver="GeoJSON")
    
    print(f"GeoJSON file saved to {output_file}")

gdf_to_geojson(gdf, f"{path_for_download_and_map_files}data.geojson")

df.to_excel(f"{path_for_download_and_map_files}data.xlsx",index=False) 

df.to_csv(f"{path_for_download_and_map_files}data.csv") 

# issue with plume data... missign emissions and missing lat long


# TODO replace 	gas or oil plant with extraction
# why when filter goes down to 2066? 