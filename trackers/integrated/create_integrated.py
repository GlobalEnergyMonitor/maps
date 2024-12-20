# import sqlalchemy as sa
import pandas as pd
import numpy as np
from datetime import date
from datetime import date
from config import countries

# Get today's date
today_date = date.today()
iso_today_date = today_date.isoformat()
iso_today_date_folder = f'{iso_today_date}/'
tracker_folder = 'integrated'

test_results_folder = './test_results/'
testing_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/'
# /Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final
output_folder = './compilation_output/'
input_file_csv = 'compilation_input/Global Integrated Power September 2024 DATA TEAM COPY.xlsx'#'compilation_input/Global Integrated Power August 2024 DATA TEAM COPY.xlsx'

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
    
def set_up_df(input, sheetname):
    df = pd.read_excel(input, sheetname)
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
    # col_info_df.to_csv(f'{test_results_folder}col_df.csv')
    
    print(df.info())
    
    return df

def clean_df(df):
    # clean df
    df['Capacity (MW)'] = df['Capacity (MW)'].apply(lambda x: check_and_convert_float(x))
    df = df.fillna('')
    
    df = df.replace('not found', '')  
    df = df.replace('Not found', '') 
    
    # round all capacity cols to 2 decimal places
    df['Capacity (MW)'] = df['Capacity (MW)'].apply(lambda x: round(x, 4) if x != '' else x)    

    return df

def semicolon_for_mult_countries(df):
    
    cols_to_consider = ['Country/area 1 (hydropower only)',  'Country/area 2 (hydropower only)']
    
    # end goal is we want the hydro cols to fit into country cols
    # only need to do that when there is a second country, in those cases cap2 is not 0
    # the country and cap cols (main) is the first country and combined cap
    # multiple countries separated by ;
    df = df.fillna('')
    for row in df.index:
        if df.loc[row, 'Country/area 2 (hydropower only)'] != '':
            print(f"Country 1: {df.loc[row, 'Country/area 1 (hydropower only)']}")
            df.loc[row,'Country/area'] = f"{df.loc[row, 'Country/area 1 (hydropower only)']}; {df.loc[row, 'Country/area 2 (hydropower only)']};"
            
        else:
            df.loc[row,'Country/area'] = f"{df.loc[row, 'Country/area']};"

    return df

def fix_status_inferred(df):

    print(f"Statuses before: {set(df['Status'].to_list())}")

    inferred_statuses_cancelled = df['Status'].str.contains('cancelled - inferred')
    inferred_statuses_shelved = df['Status'].str.contains('shelved - inferred')

    df.loc[inferred_statuses_cancelled, 'Status'] = 'cancelled'
    df.loc[inferred_statuses_shelved,'Status'] = 'shelved'

    print(f"Statuses before: {set(df['Status'].to_list())}")

    return df

def harmonize_countries(df, countries_dict):
    df = df.copy()
    # for k,v in countries_dict.items():
    #     print(len(v))
    countries_col = set(df['Country/area'].to_list())
    region_col = set(df['Region'].to_list())
    results = []
    for region in region_col:
        
        df_mask = df[df['Region']==region]
        df_mask['country-harmonize-pass'] = df_mask['Country/area'].apply(lambda x: 'true' if x in countries_dict[region] else f"false because {x}")
        results_len = df_mask[df_mask['country-harmonize-pass'] == 'false']
        results.append((region, len(results_len)))
        print(f'\nWe want this to be 0: {results}\n')
        results_df = pd.DataFrame(results)
        results_df.to_csv(f'{test_results_folder}results.csv')
        
    # df['areas-subnat-sat-display'] = df.apply(lambda row: f"{row['Country/area']}" if row['Subnational unit (state, province)'] == '' else f"{row['Subnational unit (state, province)']}, {row['Country/area']}", axis=1)   
    return df

# tiles
# for map file we want it to be:  map id link field, geometry, name, scaling col, country, region, statuses, tracker
# def filter_cols_for_tiles(df): # TODO test if this is ok, you may need it in there so can filter
#     df = df.copy()
#     df = df[['GEM location ID', 'Country/area', 'Plant / Project name', 'Capacity (MW)',
#     'Status', 'Latitude', 'Longitude', 'Region', 'GEM.Wiki URL', 'Type', 'Owner', 'Parent',]] # 'Owner', 'Parent', 
    
#     df = df.dropna(subset=['Latitude', 'Longitude', 'Country/area'])
#     df = df.fillna('')
#     # print(df.info())
#     df = rename_cols(df)
#     df = remove_missing_coord_rows(df)

    
#     return df

def filter_cols_for_csv(df):
    df = df.copy()
    df = df[['GEM location ID','Country/area', 'Plant / Project name', 'Unit / Phase name', 'Capacity (MW)',
    'Status', 'Type', 'Owner', 'Parent', 'Latitude', 'Longitude', 'Start year', 'Retired year', 'Fuel', 'Technology',
    'Location accuracy', 'Subnational unit (state, province)', 'Region', 'GEM.Wiki URL']]
    
    df = df.fillna('')
    # print(df.info())
    
    df = rename_cols(df)
    df = remove_missing_coord_rows(df)


    
    return df

def rename_cols(df):
    print(f'Cols before: {df.columns}')

    df = df.copy()
    df = df.rename(columns=str.lower)
    df.columns = df.columns.str.replace(' ', '-')
    df.columns = df.columns.str.replace('.', '')
    df = df.rename(columns={'latitude': 'lat', 'longitude':'lng', 'gem-wiki-url': 'url'})
    print(f'Cols after: {df.columns}')
    return df

def remove_missing_coord_rows(df):
    df['lng'] = df['lng'].fillna('')
    df['lat'] = df['lat'].fillna('')
    print(len(df))
    issue_df = df[df['lng']== '']
    df = df[df['lng']!= '']
    df = df[df['lat']!= '']
    print(len(df))
    print('This is issues missing coord so removed:')
    print(issue_df)
    issue_df.to_csv(f'missing_coords_{iso_today_date}.csv')

    return df

def input_to_output(dftiles, dfcsv):

    df_for_tiles = dftiles.copy()
    df_for_csv = dfcsv.copy()   
    
    
    output_file_tile = f'{output_folder}tile-data-{iso_today_date}.csv'
    print(output_file_tile)
    output_file_csv = f'{output_folder}csv-data-{iso_today_date}.csv'
    print(output_file_csv)
    df_for_tiles.to_csv(output_file_tile, encoding='utf-8', index=False)
    print(f'done {output_file_tile}')

    df_for_csv.to_csv(output_file_csv, encoding='utf-8', index=False)
    print(f'done {output_file_csv}')   
    
    testing_file_tile = f'{testing_folder}tile-data-{iso_today_date}.csv'
    print(testing_file_tile)
    testing_file_csv = f'{testing_folder}csv-data-{iso_today_date}.csv'
    print(testing_file_csv)
    df_for_tiles.to_csv(testing_file_tile, encoding='utf-8', index=False)
    print(f'done {testing_file_tile}')

    df_for_csv.to_csv(testing_file_csv, encoding='utf-8', index=False)
    print(f'done {testing_file_csv}') 
    
    
    return df


print(f'Getting Started on {input_file_csv}, it is {iso_today_date}')

df = set_up_df(input_file_csv, 'Power facilities')
df = semicolon_for_mult_countries(df)
df = fix_status_inferred(df)
df = harmonize_countries(df, countries)

print(df.info())
# df_tiles = filter_cols_for_tiles(df)
df_csv = filter_cols_for_csv(df)
# df = rename_cols(df)

# df = remove_missing_coord_rows(df)


# input_to_output(df_tiles, df_csv)

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