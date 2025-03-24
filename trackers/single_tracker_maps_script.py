import pandas as pd
from all_config import *
from helper_functions import *

# creates the file for the single map
def get_key_tabs_prep_file(tracker):
    prep_df = create_prep_file(multi_tracker_log_sheet_key, source_data_tab)

    prep_dict = prep_df.to_dict(orient='index')

    if tracker in non_gsheet_data:
        print('Needs to be local')
    # elif 'Iron & Steel' == tracker:
    #     keytab = {}
    #     # gist_pages = ['steel', 'iron', 'plant']
    #     for page in gist_pages:
    #         tracker_n = f'{tracker}: {page}'
    #         key = prep_dict[tracker_n]['gspread_key']
    #         key = ''.join(key) # convert string into item in list
    #         tabs = prep_dict[tracker_n]['gspread_tabs'] 
    #         keytab[page] = (key, tabs)
    #         tracker_n = '' 
                 
    #     # print(f'Returning keytab: {keytab} for GIST')
    #     return keytab
     
    else:
        key = prep_dict[tracker]['gspread_key']
        tabs = prep_dict[tracker]['gspread_tabs']
    return key, tabs


def create_df(key, tabs=['']):
    # print(tabs)
    dfs = []
    # other logic for goget 
    if trackers_to_update[0] == 'Oil & Gas Extraction':
        for tab in tabs:
            # print(tab)
            if tab == 'Main data':
                gsheets = gspread_creds.open_by_key(key)
                spreadsheet = gsheets.worksheet(tab)
                main_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                print(main_df.info())
            elif tab == 'Production & reserves':
                gsheets = gspread_creds.open_by_key(key)
                spreadsheet = gsheets.worksheet(tab)
                prod_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                print(prod_df.info())
        return main_df, prod_df
    
    elif trackers_to_update[0] == 'Iron & Steel':
        # keytab = key
        # print(keytab)
        # for k,v in keytab.items(): # dict of tuples the tuple being key and tabs 
        #     # print(f'this is key: {k}')
        #     # print(f'this is v: {v}')
        #     tabtype = k
        #     key = v[0]
        #     tabs = v[1]
        #     # Iron & Steel: plant (unit-level not needed anymore)
        for tab in tabs:
            gsheets = gspread_creds.open_by_key(key)
            spreadsheet = gsheets.worksheet(tab)
            df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
            df['tab-type'] = tab
            dfs += [df]

        df = pd.concat(dfs).reset_index(drop=True)
        print(df.info())

    else:
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


def process_steel_iron_parent(df, test_results_folder):
    # concat steel and iron unit
    # merge with plant for parent
    # steel_df = tuple_gist[0]
    # steel_df = steel_df[['tab-type', 'GEM Plant ID', 'GEM Unit ID', 'Unit Name', 'Unit Status', 'Current Capacity (ttpa)']]
    # iron_df = tuple_gist[1]
    # iron_df = iron_df[['tab-type', 'GEM Plant ID', 'GEM Unit ID', 'Unit Name','Unit Status', 'Current Capacity (ttpa)', 'Most Recent Relining']]
    # plant_df = tuple_gist[2]
    plant_df = df.copy()
    plant_cap_df = plant_df[plant_df['tab-type']=='Plant capacities and status'] # for if I need to deal with the 38 unmatched and if we want to show nominal summed capacity
    plant_cap_df = plant_cap_df[['Plant ID', 'Status', 'Nominal crude steel capacity (ttpa)', 'Nominal BOF steel capacity (ttpa)', 'Nominal EAF steel capacity (ttpa)', 
                                 'Nominal OHF steel capacity (ttpa)', 'Other/unspecified steel capacity (ttpa)', 'Nominal iron capacity (ttpa)', 'Nominal BF capacity (ttpa)',
                                 'Nominal DRI capacity (ttpa)', 'Other/unspecified iron capacity (ttpa)']] # rename Status to unit status 
    
    plant_df = plant_df[plant_df['tab-type']=='Plant data']

    plant_df = plant_df[['tab-type', 'Plant ID', 'Plant name (English)', 'Plant name (other language)', 'Other plant names (English)',
                         'Other plant names (other language)', 'Owner', 'Owner (other language)', 'Owner GEM ID', 'Parent', 'Parent GEM ID',
                         'Subnational unit (province/state)', 'Country/Area', 'Coordinates', 'Coordinate accuracy', 'GEM wiki page',
                          'Steel products', 'Main production equipment', 'Start date']]

    print(len(plant_df)) # 1204
    plant_df = plant_df.merge(right=plant_cap_df, on='Plant ID', how='outer')
    print(len(plant_df)) # 1732 looks correct because multiple rows for each unit 
    
    # unmatched plant prod method is determined by nominal capacity 

    # now that plant level only let's create capacity for scaling using nominal steel when there iron as backfill
    # TODO change column to be prior to rename lowercase
    plant_df['scaling-cap'] = plant_df.apply(lambda row: row['Nominal crude steel capacity (ttpa)'] if pd.notna(row['Nominal crude steel capacity (ttpa)']) else row['Nominal iron capacity (ttpa)'], axis=1)
        
    # status is plant level and indivual in plant status capacity tab
    # first group together all rows with same plant id, and get a new column of all status options in a list
    # then apply make plant level status 
    plant_df_grouped = plant_df.groupby('Plant ID').agg({'Status': list}).reset_index()
    plant_df_grouped = plant_df_grouped.rename(columns={'Status': 'status-list'})
    plant_df = plant_df.merge(plant_df_grouped, on='Plant ID', how='left')
    plant_df['plant-status'] = plant_df.apply(lambda row: make_plant_level_status(row['status-list'], row['Plant ID']),axis=1)

    # qc_list_combos = plant_df[plant_df['plant-status']=='']['status-list']
    
    list_unit_cap = [
        'Nominal BOF steel capacity (ttpa)', 
        'Nominal EAF steel capacity (ttpa)', 
        'Nominal OHF steel capacity (ttpa)', 
        'Other/unspecified steel capacity (ttpa)', 
        'Nominal iron capacity (ttpa)', 
        'Nominal BF capacity (ttpa)', 
        'Nominal DRI capacity (ttpa)', 
        'Other/unspecified iron capacity (ttpa)',
        'scaling-cap'
    ]
    # replace '' with nan for all instances in the list_unit_cap cols
    plant_df[list_unit_cap] = plant_df[list_unit_cap].replace('>0', np.nan)
    # I want to pivot or groupby plant ID and sum all the values in the list_unit_cap columns so that I can retain the information but         
    
    for col in list_unit_cap:
        plant_df_grouped_col = plant_df.groupby('Plant ID').agg({col: list}).reset_index()
        print(plant_df_grouped_col)
        plant_df_grouped_col = plant_df_grouped_col.rename(columns={col: f'{col}_list'})
        # input(f'check grouped by col {col}')
        plant_df = plant_df.merge(plant_df_grouped_col, on='Plant ID', how='left')

    print(plant_df[plant_df['Plant ID']=='P100000120620'][['Nominal iron capacity (ttpa)', 'Nominal iron capacity (ttpa)_list']])
    input('Check above') # works!  [4000, 2500, 5500] for all three
    # plant_df_pivot = plant_df.groupby('Plant ID')[list_unit_cap].apply(lambda x: x.apply(pd.to_numeric, errors='coerce')).sum().reset_index()
    
    # print(plant_df_pivot)
    # input('check pivot results') # TODO FIX this groupby sum so it's only applied on plant level not entire 
    # plant_df = plant_df.drop(columns=list_unit_cap).merge(plant_df_pivot, on='Plant ID', how='left')

    # then deduplicate on Plant ID keep first which is plant_data tab
    print(len(plant_df))
    plant_df = plant_df.drop_duplicates(subset='Plant ID')
    print(len(plant_df))

    
    # set up prod method tiers with equipment and logic from summary tables

    plant_df['prod-method-tier'] = plant_df.apply(lambda row: make_prod_method_tier(row['Main production equipment'], row['Plant ID']), axis=1)
    
    # unit stuff when we did it unit-level
    # unit_df = pd.concat([steel_df, iron_df])

    # df = unit_df.merge(right=plant_df, left_on='GEM Plant ID', right_on='Plant ID', how='inner') # 7783 rows x 27 columns
    # df = df.merge(right=plant_cap_df, on='Plant ID',how='inner') # 14494 when both outer merges and now 14451 with merged those two earlier
    # df = df.drop_duplicates(subset='GEM Unit ID')
    # print(len(df))
    # df = df.dropna(subset='Plant ID')
    # df = df.dropna(how='all')
    # find situation where the unit id is empty
    # unmatched_rows = df[df['Plant ID'].isna() | df['GEM Plant ID'].isna()]
    # # df = df.fillna('')
    # # unmatched = df[df['Plant ID'] == '']
    # print(f"Unmatched rows {len(unmatched_rows)}:")
    # print(unmatched_rows)
    # unmatched_rows.to_csv(f'{test_results_folder}/unmatched_plants_units{iso_today_date}.csv')
    # average_ttpa = 1000
    # unmatched_rows['GEM Unit ID'] = unmatched_rows['Plant ID']
    # unmatched_rows['Current Capacity (ttpa)'] = average_ttpa
    # no status so can't and no production method
    
    print(plant_df.info())
    return plant_df

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
