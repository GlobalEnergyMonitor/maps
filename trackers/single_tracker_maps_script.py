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
    
    # set up prod method tiers with equipment and logic from summary tables

    plant_df['prod-method-tier'] = plant_df.apply(lambda row: make_prod_method_tier(row['Main production equipment'], row['Plant ID']), axis=1)
    
    
    
    list_unit_cap = [
        'Nominal crude steel capacity (ttpa)',
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
    pd.options.display.float_format = '{:.0f}'.format
    # replace '' with nan for all instances in the list_unit_cap cols
    plant_df[list_unit_cap] = plant_df[list_unit_cap].replace('>0', np.nan)
    plant_df[list_unit_cap] = plant_df[list_unit_cap].replace('N/A', np.nan)
    # make all in list_unit_cap rounded to be without decimal places
    plant_df[list_unit_cap] = plant_df[list_unit_cap].applymap(lambda x: round(x) if pd.notna(x) and isinstance(x, (int, float)) else x)
    

    # I want to pivot or groupby plant ID and sum all the values in the list_unit_cap columns so that I can retain the information but         
    
    # for col in list_unit_cap:
    #     plant_df_grouped_col = plant_df.groupby('Plant ID').agg({col: list}).reset_index()
    #     # print(plant_df_grouped_col)
    #     plant_df_grouped_col = plant_df_grouped_col.rename(columns={col: f'{col}_list'})
    #     # remove all nans from list so can sum entire list of values
    #     plant_df_grouped_col[f'{col}_list'] = plant_df_grouped_col[f'{col}_list'].apply(lambda caplist: [x if pd.notna(x) else 0 for x in caplist if isinstance(x, (int, float)) and not isinstance(x, bool)])
    #     # sum the list and return the value as the actual plant-level value
        
    #     plant_df_grouped_col[f'{col}_plant'] = plant_df_grouped_col[f'{col}_list'].apply(lambda caplist: sum(x for x in caplist))
    #     plant_df = plant_df.merge(plant_df_grouped_col, on='Plant ID', how='left')

    # make new columns with status and prod method capacity
    # rename the columns based on status value and put on same row 
    all_suffixes_check = []
    for row in plant_df.index:
        status_suffix = plant_df.loc[row, 'Status']
        plant_id = plant_df.loc[row, 'Plant ID']
        for col in list_unit_cap:
            if plant_df.loc[row, col] != np.nan:
                all_suffixes_check.append(status_suffix)
                new_col_name = f'{status_suffix.capitalize()} {col}'
                print(new_col_name)
                plant_df.loc[row, new_col_name] = plant_df.loc[row,col]
            else:
                # print(plant_df.loc[row,col])
                print('skip creating new column for this one')
    # print(set(all_suffixes_check)) # passed! 
    print(plant_df[plant_df['Plant ID']=='P100000120823'][['Nominal iron capacity (ttpa)', 'Status']])

    # print(plant_df[plant_df['Plant ID']=='P100000120679'][['Nominal crude steel capacity (ttpa)', 'Status']])
    # print(plant_df[plant_df['Plant ID']=='P100000120620'][['Nominal iron capacity (ttpa)', 'Status']])
    # print(plant_df[plant_df['Plant ID']=='P100000120679'][['Operating Nominal crude steel capacity (ttpa)', 'Nominal crude steel capacity (ttpa)', 'Announced Nominal crude steel capacity (ttpa)']])
    # print(plant_df[plant_df['Plant ID']=='P100000120620'][['Operating Nominal iron capacity (ttpa)', 'Nominal iron capacity (ttpa)', 'Announced Nominal iron capacity (ttpa)', 'Mothballed Nominal iron capacity (ttpa)']])
    input('Check above') # works!  [4000, 2500, 5500] for all three
    print(plant_df.columns)
    input('add cols') #'Main Production Equipment', 'Steel Products',
    # filter out some cols 
    filter_cols = ['tab-type', 'Plant ID', 'Plant name (English)',
       'Plant name (other language)', 'Other plant names (English)',
       'Other plant names (other language)', 'Owner', 'Owner (other language)',
       'Owner GEM ID', 'Parent', 'Parent GEM ID',
       'Steel products', 'Main production equipment',
       'Subnational unit (province/state)', 'Country/Area', 'Coordinates',
       'Coordinate accuracy', 'GEM wiki page', 'Start date','status-list', 'plant-status', 'prod-method-tier', 'scaling-cap', 
       # begins new capacity col by prod type and unit status
       'Operating Nominal crude steel capacity (ttpa)',
       'Operating Nominal EAF steel capacity (ttpa)', 'Operating scaling-cap',
       'Construction Nominal crude steel capacity (ttpa)',
       'Construction Nominal EAF steel capacity (ttpa)',
       'Construction scaling-cap',
       'Operating Nominal BOF steel capacity (ttpa)',
       'Operating Nominal iron capacity (ttpa)',
       'Operating Nominal BF capacity (ttpa)',
       'Announced Nominal crude steel capacity (ttpa)',
       'Announced Nominal EAF steel capacity (ttpa)',
       'Announced Nominal iron capacity (ttpa)',
       'Announced Nominal DRI capacity (ttpa)', 'Announced scaling-cap',
       'Mothballed Nominal iron capacity (ttpa)',
       'Mothballed Nominal BF capacity (ttpa)',
       'Operating Other/unspecified steel capacity (ttpa)',
       'Mothballed Nominal crude steel capacity (ttpa)',
       'Mothballed Nominal EAF steel capacity (ttpa)',
       'Mothballed Nominal DRI capacity (ttpa)', 'Mothballed scaling-cap',
       'Operating Nominal DRI capacity (ttpa)',
       'Announced Other/unspecified steel capacity (ttpa)',
       'Construction Other/unspecified steel capacity (ttpa)',
       'Construction Nominal iron capacity (ttpa)',
       'Construction Nominal DRI capacity (ttpa)',
       'Operating pre-retirement Nominal crude steel capacity (ttpa)',
       'Operating pre-retirement Nominal BOF steel capacity (ttpa)',
       'Operating pre-retirement Nominal iron capacity (ttpa)',
       'Operating pre-retirement Nominal BF capacity (ttpa)',
       'Operating pre-retirement scaling-cap',
       'Announced Nominal BF capacity (ttpa)',
       'Construction Nominal BOF steel capacity (ttpa)',
       'Construction Nominal BF capacity (ttpa)',
       'Announced Nominal BOF steel capacity (ttpa)',
       'Cancelled Nominal crude steel capacity (ttpa)',
       'Cancelled Nominal EAF steel capacity (ttpa)', 'Cancelled scaling-cap',
       'Retired Nominal iron capacity (ttpa)',
       'Retired Nominal BF capacity (ttpa)',
       'Announced Other/unspecified iron capacity (ttpa)',
       'Mothballed Nominal BOF steel capacity (ttpa)',
       'Cancelled Nominal iron capacity (ttpa)',
       'Cancelled Nominal DRI capacity (ttpa)',
       'Retired Nominal crude steel capacity (ttpa)',
       'Retired Nominal BOF steel capacity (ttpa)', 'Retired scaling-cap',
       'Operating pre-retirement Nominal EAF steel capacity (ttpa)',
       'Retired Nominal EAF steel capacity (ttpa)',
       'Cancelled Other/unspecified steel capacity (ttpa)',
       'Cancelled Other/unspecified iron capacity (ttpa)',
       'Retired Nominal OHF steel capacity (ttpa)',
       'Operating Other/unspecified iron capacity (ttpa)',
       'Mothballed Other/unspecified iron capacity (ttpa)',
       'Cancelled Nominal BOF steel capacity (ttpa)',
       'Cancelled Nominal BF capacity (ttpa)',
       'Operating pre-retirement Nominal DRI capacity (ttpa)',
       'Construction Other/unspecified iron capacity (ttpa)',
       'Mothballed Other/unspecified steel capacity (ttpa)',
       'Operating pre-retirement Other/unspecified steel capacity (ttpa)',
       'Mothballed pre-retirement Nominal iron capacity (ttpa)',
       'Mothballed pre-retirement Nominal BF capacity (ttpa)',
       'Operating pre-retirement Other/unspecified iron capacity (ttpa)',
       'Operating Nominal OHF steel capacity (ttpa)',
       'Mothballed Nominal OHF steel capacity (ttpa)']
    plant_df = plant_df[filter_cols]
    plant_df_grouped = plant_df.groupby('Plant ID').agg({
        'tab-type': 'first',
        'Plant name (English)': 'first',
        'Plant name (other language)': 'first',
        'Other plant names (English)': 'first',
        'Other plant names (other language)': 'first',
        'Owner': 'first',
        'Owner (other language)': 'first',
        'Owner GEM ID': 'first',
        'Parent': 'first',
        'Parent GEM ID': 'first',
        'Subnational unit (province/state)': 'first',
        'Country/Area': 'first',
        'Coordinates': 'first',
        'Coordinate accuracy': 'first',
        'GEM wiki page': 'first',
        'Main production equipment': 'first', 
        'Steel products': 'first',
        'Start date': 'first',
        'status-list': 'first',
        'plant-status': 'first',
        'prod-method-tier': 'first',
        'scaling-cap': 'sum',
        'Operating Nominal EAF steel capacity (ttpa)': 'sum',
        'Construction Nominal EAF steel capacity (ttpa)': 'sum',
        'Operating Nominal BOF steel capacity (ttpa)': 'sum',
        'Operating Nominal BF capacity (ttpa)': 'sum',
        'Announced Nominal EAF steel capacity (ttpa)': 'sum',
        'Announced Nominal DRI capacity (ttpa)': 'sum',
        'Mothballed Nominal BF capacity (ttpa)': 'sum',
        'Operating Other/unspecified steel capacity (ttpa)': 'sum',
        'Mothballed Nominal EAF steel capacity (ttpa)': 'sum',
        'Mothballed Nominal DRI capacity (ttpa)': 'sum',
        'Operating Nominal DRI capacity (ttpa)': 'sum',
        'Announced Other/unspecified steel capacity (ttpa)': 'sum',
        'Construction Other/unspecified steel capacity (ttpa)': 'sum',
        'Construction Nominal DRI capacity (ttpa)': 'sum',
        'Operating pre-retirement Nominal BOF steel capacity (ttpa)': 'sum',
        'Operating pre-retirement Nominal BF capacity (ttpa)': 'sum',
        'Announced Nominal BF capacity (ttpa)': 'sum',
        'Construction Nominal BOF steel capacity (ttpa)': 'sum',
        'Construction Nominal BF capacity (ttpa)': 'sum',
        'Announced Nominal BOF steel capacity (ttpa)': 'sum',
        'Cancelled Nominal EAF steel capacity (ttpa)': 'sum',
        'Retired Nominal BF capacity (ttpa)': 'sum',
        'Mothballed Nominal BOF steel capacity (ttpa)': 'sum',
        'Cancelled Nominal DRI capacity (ttpa)': 'sum',
        'Retired Nominal BOF steel capacity (ttpa)': 'sum',
        'Operating pre-retirement Nominal EAF steel capacity (ttpa)': 'sum',
        'Retired Nominal EAF steel capacity (ttpa)': 'sum',
        'Cancelled Other/unspecified steel capacity (ttpa)': 'sum',
        'Retired Nominal OHF steel capacity (ttpa)': 'sum',
        'Cancelled Nominal BOF steel capacity (ttpa)': 'sum',
        'Cancelled Nominal BF capacity (ttpa)': 'sum',
        'Operating pre-retirement Nominal DRI capacity (ttpa)': 'sum',
        'Mothballed Other/unspecified steel capacity (ttpa)': 'sum',
        'Operating pre-retirement Other/unspecified steel capacity (ttpa)': 'sum',
        'Mothballed pre-retirement Nominal BF capacity (ttpa)': 'sum',
        'Operating Nominal OHF steel capacity (ttpa)': 'sum',
        'Mothballed Nominal OHF steel capacity (ttpa)': 'sum'
    }).reset_index()
    

    # print(plant_df_grouped[plant_df_grouped['Plant ID']=='P100000120823']) # worked after removing rouding logic
    # remove decimal point in all capacity values
    for col in plant_df_grouped.columns:
        if 'capacity (ttpa)' in col:
            plant_df_grouped[col] = plant_df_grouped[col].apply(lambda x: str(x).split('.')[0])

    
    print(len(plant_df_grouped))
    plant_df_grouped = plant_df_grouped.drop_duplicates(subset='Plant ID')
    print(len(plant_df_grouped))
    input('pause and check drop worked 1204') # woo worked!
    
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
    
    print(plant_df_grouped.info())
    return plant_df_grouped

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
