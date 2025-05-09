import pandas as pd
import geopandas as gpd

# map_xls = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/asia/compilation_output/asia_2024-09-25.xlsx'
map = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/asia/compilation_output/asia_2024-09-25.geojson'

dd = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/asia/compilation_output/2024-09-25/asia-energy-tracker-data-download-with-about August 2024.xlsx'

files = [map, dd]

countries = [
    'China',
    'Hong Kong',
    'Japan',
    'Macao',
    'Mongolia',
    'North Korea',
    'South Korea',
    'Taiwan',
    'Brunei',
    'Cambodia',
    'Indonesia',
    'Laos',
    'Malaysia',
    'Myanmar',
    'Philippines',
    'Singapore',
    'Thailand',
    'Timor-Leste',
    'Vietnam',
    'Afghanistan',
    'Iran',
    'Bangladesh',
    'Bhutan',
    'India',
    'Maldives',
    'Nepal',
    'Pakistan',
    'Sri Lanka'
]

goget_orig_file = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/Global Oil and Gas Extraction Tracker - 2024-03-08_1205 DATA TEAM COPY.xlsx'

def handle_goget_gas_only_workaround(goget_orig_file):
    list_ids = []
    df = pd.read_excel(goget_orig_file, sheet_name='Main data')
    df = df[df['Fuel type']!= 'oil'] # 7101
    print(len(df))
    # goget_gas_only_all_regions_march_2024 = []
    list_ids = df['Unit ID'].to_list()
    return list_ids
    
def create_dfs(files):
    for file in files:
        if 'json' in file:
            map_df = gpd.read_file(file)
        elif 'about' in file:
            dd_df = pd.read_excel(file, sheet_name=None)
        else:
            map_xls_df = pd.read_excel(file, sheet_name=None)
    return map_df, dd_df     

def filter_country(df):
    # map col    
        # if tracker in tracker_mult_countries: # currently no lists like with regions since goit and ggit created countries a list from start and end countries
        #     # if any of the countries in the country column list is in the needed geo list then keep it if none then filter out
        #     for sep in ',;-':
        #         # I want to break up any multiple countries into a list of countries
        #         # then check if any of those are in the needed_geo list
        #         filtered_df['country_to_check'] = filtered_df[col_country_name].str.strip().str.split(sep) 

    # filter the df on the country column to see if any of the countries in that list is in the needed geo
    df['wasia_filter'] = df['areas'].apply(lambda x: x in countries)
    # print(len(df))
    # print(set(df['areas']))

    df[df['wasia_filter']==True]
    # print(len(df))
    # print(df['wasia_filter'])
    
    # need country col for each tab
    return df

def filter_fuel(df):
    # filter out oil only for goget
    # filter out fuel type fossil liquid for gogpt
    list_ids = handle_goget_gas_only_workaround(goget_orig_file)
    print(len(df)) # 3095
    # filter = (df['tracker-acro']=='GOGET') & (df['prod-gas']=='') #2788
    # filter = df['id'] in list_ids #2788
    # df = df[(df['tracker-acro']=='GOGET') & (df['id'] in list_ids)]
    drop_row = []
    for row in df.index:
        if df.loc[row, 'tracker-acro'] == 'GOGET':
            if df.loc[row, 'id'] not in list_ids:
                drop_row.append(row)
                
    # drop all rows from df that are goget and not in the gas list ids 
    df.drop(drop_row, inplace=True)           
    print(len(df)) # 3012 after removing goget
    
    # filter2 = (df['tracker-acro']=='GOGPT') & (df['fuel'].contains('liquid')) #2788
    drop_row = []
    for row in df.index:
        if df.loc[row, 'tracker-acro'] == 'GOGPT': # 1751 from 1966 after filter
            fuel_cat = df.loc[row, 'fuel'].split(':')[0]
            if fuel_cat == 'fossil liquids':
                drop_row.append(row)
                
    # drop all rows from df that are goget and not in the gas list ids 
    df.drop(drop_row, inplace=True)  
    print(len(df)) # should be 2797

    return df


def filter_country_dd(df):
    print(df.keys())
    country_col = {            
            'Oil & Gas Plants': 'Country/Area',
            'Oil & Gas Extraction': 'Country',
            'Gas Pipelines': 'Countries',
            'LNG Terminals': 'Country'
            }
    for t, ndf in df.items():
        if 'About' not in t:
            print(t)
            # print(value.columns)
            if t in ['Oil & Gas Plants', 'LNG Terminals']:
                print('one country to filter')
                print(ndf[country_col[t]])

            else:
                print('mult countries in there')
                print(ndf[country_col[t]])
                ndf['c_filter'] = ndf[country_col[t]].apply(lambda x: x.split(','))
                ndf['c_filter'] = ndf[country_col[t]].apply(lambda x: x.split('-'))
                print(ndf['c_filter'])
                
    # filter the df on the country column to see if any of the countries in that list is in the needed geo
    df['wasia_filter'] = df['areas'].apply(lambda x: x in countries)
    # print(len(df))
    # print(set(df['areas']))

    df[df['wasia_filter']==True]

    # need country col for each tab
    return df

def filter_fuel_dd(df):
    for t, ndf in df.items():
        if 'About' not in t:
            print(t)
            print(f'len before {len(ndf)}')
            # print(ndf.columns)
            if t == 'Oil & Gas Extraction':
                # filter for goget
                
                list_ids = handle_goget_gas_only_workaround(goget_orig_file)
                # print(len(ndf)) # 3095 will be less because not all trackers
                # filter = (df['tracker-acro']=='GOGET') & (df['prod-gas']=='') #2788
                # filter = df['id'] in list_ids #2788
                # df = df[(df['tracker-acro']=='GOGET') & (df['id'] in list_ids)]
                drop_row = []
                for row in ndf.index:
                    # if df.loc[row, 'tracker-acro'] == 'GOGET':
                    if ndf.loc[row, 'Unit ID'] not in list_ids:
                        drop_row.append(row)
                # drop all rows from df that are goget and not in the gas list ids 
                ndf.drop(drop_row, inplace=True)           
                # print(len(ndf)) # 3012 after removing goget
    
            elif t == 'Oil & Gas Plants':
                # filter2 = (df['tracker-acro']=='GOGPT') & (df['fuel'].contains('liquid')) #2788
                drop_row = []
                for row in ndf.index:
                    # if df.loc[row, 'tracker-acro'] == 'GOGPT': # 1751 from 1966 after filter
                    fuel_cat = ndf.loc[row, 'Fuel'].split(':')[0]
                    if fuel_cat == 'fossil liquids':
                        drop_row.append(row)
                            
                # drop all rows from df that are goget and not in the gas list ids 
                ndf.drop(drop_row, inplace=True)  
                # print(len(ndf)) # should be 2797
            print(f'len after {len(ndf)}')

    return df


# Oil & Gas Plants
# len before 4858
# len after 4346
# Oil & Gas Extraction
# len before 907
# 7101
# len after 660
# Gas Pipelines
# len before 1645
# len after 1645
# LNG Terminals
# len before 481
# len after 481

def filter_map(map_df):
    # map_df = filter_country(map_df) # already done
    map_df = filter_fuel(map_df) 
    return map_df


def filter_dd(dd_df):
    # dd_df = filter_country_dd(dd_df)
    dd_df = filter_fuel_dd(dd_df)

    return dd_df


def to_file(map_df, dd_df):
    
    path = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/asia/compilation_output/'
    map_df.to_file(f'{path}/asia_2024-09-25-gas-only-w-asia.geojson', driver='GeoJSON')
    map_df.to_excel(f'{path}/asia_2024-09-25-gas-only-w-asia.xlsx')
    # dd_df.to_excel(f'{path}/2024-09-25/asia-energy-tracker-data-download-with-about August 2024.xlsx')

# call functions (move this to run_maps file!!)

map_df, dd_df  = create_dfs(files)
# map_df = filter_map(map_df)
dd_df = filter_dd(dd_df)
# to_file(map_df, dd_df)
