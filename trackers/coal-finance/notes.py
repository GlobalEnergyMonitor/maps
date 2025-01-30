
import pandas as pd
import geopandas as gpd
import numpy as np
import time
from shapely.geometry import MultiPolygon
from datetime import date
from centroids import centroids
import matplotlib.pyplot as plt
#  coal 
# remove columns uneeded

# df = df[['Fuel','Technology','Plant name','Wiki name','Plant name (local script)','Owner', 'Parent', 'Capacity (MW)', 'Status', 'Region', 'Country', 'Subnational unit (province, state)', 'Start year','Wiki URL','Latitude','Longitude']]

# # rename columns
# df = df.rename(columns={'Technology':'technology','Fuel':'fuel_type','Latitude': 'lat', 'Longitude':'lng', 'Start year': 'start_year', 'Status': 'status',
#                         'Capacity (MW)': 'capacity', 'Parent': 'parent', 'Owner': 'owner',
#                         'Plant name (local script)': 'project_loc', 'Plant name': 'project', 'Wiki name': 'unit',
#                         'Subnational unit (province, state)': 'province', 'Country':'country', 'Wiki URL':'url', 'Region':'region'})

# remove local plant name if country is not china
# df['chinese_name'] = df.apply(lambda row: '' if row['country'] != 'China' else row['chinese_name'], axis=1)

# remove and rename cols or just use the centroid function

# coal finance
# get all centroids of last year's countries
# get all countries unique this year
# /Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/maps/coal-finance-2021-main/data/Global Coal Project Finance Tracker_April 2024 Update_Final_GEM.xlsx
# /Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/maps/coal-finance-2021-main/data/data.csv 
def all_countries_centroid(new_file, centroids_dict):
    # new_df = pd.read_excel(new_file, skiprows=1)
    new_df = pd.read_csv(new_file)    

    # old_c_fin = old_df['Financing Country']
    # print(f'this is cols for new df:{new_df.columns}')
    # new_c_rec = new_df['Country'].to_list()
    new_c_fin = new_df['Financier Country'].to_list()
    # print(set(new_c_rec))
    # print(set(new_c_fin))
    # US UAE
    new_df['Financier Country'] = new_df['Financier Country'].replace('US', 'United States').replace('UAE', 'United Arab Emirates')
    # clean countries, nan, corporate, international, 
    mask_c_fin_1 = new_df['Financier Country'] != 'International'
    mask_c_fin_2 = new_df['Financier Country'] != 'corporate'
    mask_c_fin_3 = new_df['Financier Country'] != 'international'
    mask_domestic_na = (new_df['Domestic/International'] == 'Domestic') & (new_df['Financier Country'].isna())
    # print(new_df[mask_domestic_na][['Country', 'Financier Country']]) # correct 

    # filters out non country values 
    filtered_new_df = new_df[mask_c_fin_1]
    filtered_new_df = filtered_new_df[mask_c_fin_2]
    filtered_new_df = filtered_new_df[mask_c_fin_3]
    # replaces domestic with regular country if Financier Country is na
    filtered_new_df.loc[mask_domestic_na, 'Financier Country'] = filtered_new_df.loc[mask_domestic_na, 'Country']
    # print(filtered_new_df[mask_domestic_na][['Country', 'Financier Country']]) # correct 

    # then replaces all other with arbitrary
    # Latitude: -75.000° Longitude: 71.000°
    all_na_financier_mask = filtered_new_df['Financier Country'].isna()
    # df_na = filtered_new_df[all_na_financier_mask]
    # df_na = df_na.drop_duplicates(subset='GEM unit/phase ID')
    # print((df_na['Capacity (MW)'].sum()))
    # df_na.to_csv('df_na_finance.csv')
    # print(df_na['Financier Country'])
    filtered_new_df.loc[all_na_financier_mask, 'Financier Country'] = 'Unknown'
    # print(filtered_new_df.loc[all_na_financier_mask, 'Financier Country'])
    df_cleaned = filtered_new_df.dropna(subset=['Financier Country'])
    
    df_cleaned_ongoing = df_cleaned[df_cleaned['Financing Status']=='Closed']
    # check that unknown financier country is highest mw
    result = df_cleaned_ongoing.groupby('Financier Country')['Capacity (MW)'].sum().sort_values(ascending=False)
    
    print(f'this is result: {result}')


    # print(len(filtered_new_df))
    # print(len(df_cleaned))
    # print(len(df_cleaned))
    df_cleaned['Financier Country'] = df_cleaned['Financier Country'].str.strip()
    # new_c_fin = df_cleaned['Financier Country'].to_list()
    # print(set(new_c_fin))
    # print(centroids['Australia'][0])
    # make a new column target_lat, target_lng

    for row in df_cleaned.index:
        fin_country = df_cleaned.loc[row, 'Financier Country']
        df_cleaned.loc[row,'source_lat'] = centroids[f'{fin_country}'][0]
        df_cleaned.loc[row,'source_lng'] = centroids[f'{fin_country}'][1]
    
    # print(df_cleaned)
    # print(df_cleaned.columns)
    # clean and rename since we had to save as a csv initially anyway
    # 'All Finance This Plant' convert to int, remove punctuation
    
    df_cleaned = df_cleaned.rename(columns={'GEM unit/phase ID':'tid','Latitude': 'target_lat', 'Longitude':'target_lng', 'Start year': 'start_year', 'Status': 'status',
                        'Capacity (MW)': 'megawatts', 'Parent': 'parent', 'Owner': 'owner',
                        'Plant name (local)': 'project_loc', 'Plant name': 'project_name', 'Unit name': 'unit',
                        'Subnational unit (province, state)': 'subnational', 'Country':'country', 'Wiki URL':'wiki', 'Region':'region', 'Subregion':'subregion', 'Financier': 'financer',
                        'Financier Type': 'financer_type', 'Type of Finance': 'finance_type', 'Close Year': 'close_year', 'EPC Company': 'epc', 'All Finance This Plant': 'dollars',
                        'Financing Status': 'era', 
                        })
    
    # old_c_rec = old_df['sponsor'].dropna() # sponsor
    # print(old_c_rec)
    # # print(new_df['Financing Status'])
    # target is a copy of project_name
    df_cleaned['target'] = df_cleaned['project_name'] 
    # source copy of country 
    df_cleaned['source'] = df_cleaned['Financier Country']
    # get source_iso based on country iso dict 
    df_cleaned['source_iso'] = ''
    # sponsor is just empty so not needed maybe?
    df_cleaned['sponsor'] = ''
    # target_country_lat,target_country_lng,  copy of target_lat, target_lng
    df_cleaned['target_country_lat'] = df_cleaned['target_lat']
    df_cleaned['target_country_lng'] = df_cleaned['target_lng']
    df_cleaned['target_country'] = df_cleaned['country']


    df_cleaned['dollars'] = df_cleaned['dollars'].apply(lambda x: (str(x).replace('$', '').replace(',', '').replace('.00','')))
    df_cleaned['dollars'] = df_cleaned['dollars'].fillna('')
    # make integers 
    # print(type(df_cleaned['megawatts'].iloc[0]))
    # df_cleaned['megawatts'] = df_cleaned['megawatts'].astype(int)
    # print(type(df_cleaned['megawatts'].iloc[0]))
    df_cleaned['unit'] = df_cleaned['project_name'] + ' ' + df_cleaned['unit']  
    # filter out for only needed cols
    list_of_cols_gcbft = [
    'tid', 'country', 'unit', 'target', 'project_name', 'wiki', 'megawatts', 'status',
    'target_lat', 'target_lng', 'source_lat', 'source_lng', 'parent', 'subnational',
    'financer', 'financer_type', 'finance_type', 'close_year', 'epc', 'dollars', 'era',
    'source', 'sponsor', 'source_iso', 'target_country_lat', 'target_country_lng', 'target_country'
    ]
    # 'sponsor', 'source_iso', 'target_country_lat', 'target_country_lng'
    df_cleaned = df_cleaned[list_of_cols_gcbft]
    df_cleaned = df_cleaned.dropna(subset=['source_lat', 'source_lng', 'target_lat', 'target_lng', 'target_country_lat', 'target_country_lng'])

    # df_check_nans = df_cleaned[['source_lat', 'source_lng', 'target_lat', 'target_lng', 'target_country_lat', 'target_country_lng']]
    # print(df_check_nans)
    # # Check for NaN values in the specified columns
    # nan_in_columns = df_cleaned[['source_lat', 'source_lng', 'target_lat', 'target_lng', 'target_country_lat', 'target_country_lng']].isna().any()

    # # Print the columns with NaN values
    # print("Columns with NaN values:")
    # print(nan_in_columns)
    # print(set(df_cleaned['era'].to_list()))
    df_cleaned['era'] = df_cleaned['era'].str.lower()
    df_cleaned['finance_type'] = df_cleaned['finance_type'].str.lower()
    # print(set(df_cleaned['finance_type'].to_list()))
    # df_cleaned['financer_type'] = df_cleaned['financer_type'].str.lower()
    # 'government-owned policy institution' to governmental policy institution
    # filter out financer_type as nan to remove 
    df_cleaned['financer_type'] = df_cleaned['financer_type'].replace('Government-owned policy institution', 'Governmental policy institution').replace('Joint Venture', 'Joint venture')
    df_cleaned['close_year'] = df_cleaned['close_year'].apply(lambda x: ((str(x).replace('.0', ''))))
    # print(set(df_cleaned['era'].to_list()))
    # print(set(df_cleaned['financer_type'].to_list()))

    # print(set(df_cleaned['close_year'].to_list()))
    df_cleaned[['source', 'country', 'target_country']] = df_cleaned[['source', 'country', 'target_country']].applymap(lambda x: x.strip())

    # china_df = df_cleaned[df_cleaned['source'] == 'China']
    # print(len(china_df))
    # print(china_df.columns)
    # print(set(china_df['source'].to_list()))
    # china_df_unique = china_df.drop_duplicates(subset='tid')
    # china_df_unique_name = china_df.drop_duplicates(subset='unit')
    # china_df_unique_financier = china_df.drop_duplicates(subset='financer')
    # print(len(china_df_unique_financier))
    # print(len(china_df_unique))
    # print(len(china_df_unique_name))
    # print(china_df.columns)
    # china_df_closed = china_df_unique[china_df_unique['era'] == 'closed']
    # china_df_closed['cap sum'] = china_df_closed['megawatts'].sum()
    # print(china_df_closed['cap sum'])
    
    # look into why her numbers are slightly off. 
    # df_cleaned_unique = df_cleaned.drop_duplicates(subset=['tid', 'megawatts'])
    # print(df_cleaned_unique[df_cleaned_unique['project_name'] == 'Ketapang Smelter power station'][['tid', 'megawatts', 'era', 'financer', 'source']])

    # capacity total for recipient country for finacning closed all
    df_capacities_diff_unit = df_cleaned.drop_duplicates(['tid', 'megawatts'])
    print(df_capacities_diff_unit['tid'].value_counts(sort=True))
    df_capacities_diff_unit[['tid', 'country', 'source', 'era', 'megawatts']].to_csv('capacities_same_unit_diff_value.csv')




    # df_cleaned_closed = df_cleaned.drop_duplicates('tid')
    df_cleaned_closed = df_cleaned_closed[df_cleaned_closed['era']=='closed'][['megawatts', 'country', 'target_country', 'source', 'tid', 'project_name', 'unit', 'close_year']]
    
    print(df_cleaned_closed['megawatts'].sum())
    
    print(set(df_cleaned_closed['close_year'].to_list()))
    # print(df_cleaned_closed.dtypes)
    valid_close_years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']

    df_cleaned_closed = df_cleaned_closed[df_cleaned_closed['close_year'].isin(valid_close_years)]
    # print(df_cleaned_closed['megawatts'].sum())
    # df_cleaned_closed_groupby = df_cleaned_closed.groupby('country')
    # print(df_cleaned_closed_groupby)
    df_cleaned_closed.to_csv('closed_by_country_recipient_2024_04_25.csv')

    df_cleaned[['source', 'country', 'target_country']] = df_cleaned[['source', 'country', 'target_country']].applymap(lambda x: x.strip())

    df_cleaned.to_csv(output_file, encoding='utf-16', index=False)
    print(f'done {output_file}')
    # return nothing
    return df_cleaned


# df_cleaned = all_countries_centroid(input_file, centroids)


def check_centroids(centroids):
    
    # Convert the dictionary into a DataFrame
    df = pd.DataFrame.from_dict(centroids, orient='index', columns=['Latitude', 'Longitude'])

    # Create a GeoDataFrame from the DataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    # Plot the world map and add the centroids
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Plot
    fig, ax = plt.subplots(figsize=(15, 10))
    world.plot(ax=ax, color='lightgray')
    gdf.plot(ax=ax, color='red', marker='o', markersize=50)

    # Show the plot
    plt.show()

# check_centroids(centroids)