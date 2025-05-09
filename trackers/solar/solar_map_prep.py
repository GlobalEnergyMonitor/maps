# import sqlalchemy as sa
import pandas as pd
import numpy as np
import math
import os
from datetime import date

# Get today's date
today_date = date.today()

# Format the date in ISO format
iso_today_date = today_date.isoformat()

input_file = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/solar/Global-Solar-Power-Tracker-June-2024 DATA TEAM COPY.xlsx'#'all-fields-2024-05-24T162358-solar.csv'
output_file = f'data.csv'

# see which is longer is phase or project

fields_needed = ['Wiki URL', 'Project Name in Local Language / Script', 'Technology-Type', 'Status', 'Capacity (MW)', 'Project Name','Phase Name', 'Owner', 'Operator', 'lat', 'lng','Location accuracy',"Local area (taluk, county)","Major area (prefecture, district)", 'State/Province', 'Country', 'Region', 'Subregion', 'Start year', 'GEM phase ID']

if 'csv' in input_file:
    solar_df = pd.read_csv(input_file)
else:
    dfs = []
    for sheet in ['20 MW+', '1-20 MW']:
        df = pd.read_excel(input_file, sheet_name=sheet)
        dfs.append(df)
    solar_df = pd.concat(dfs)
solar_df = solar_df.fillna('')

print('These are columns:')
for col in solar_df.columns:
    print(col)
input('Check')

print(set(solar_df['Status'].to_list()))
print(set(solar_df['Technology Type'].to_list()))
# print(len(solar_df[solar_df['Phase Name in Local Language / Script'].isna()]))
# print(len(solar_df[solar_df['Project Name in Local Language / Script'].isna()]))
# print(solar_df['Phase Name in Local Language / Script'].head())
# convert Latitude to lat
# filter_deleted_projects = solar_df[solar_df['Project Name'].str.contains('TO BE DELETED')]
# print(filter_deleted_projects)
solar_df_cleaned = solar_df
print(len(solar_df))

print(solar_df_cleaned[solar_df_cleaned['Project Name']=='Zhejiang Anji Meixi China Guoneng Photovoltaic solar farm']['Location accuracy'])
# print(set(solar_df['Owner'].to_list()))
solar_df_cleaned['Owner'] = solar_df_cleaned['Owner'].str.replace(r' \[100%\]$', '', regex=True)
# print(set(solar_df['Owner'].to_list()))

solar_df_cleaned['Start year'] = solar_df_cleaned['Start year'].apply(lambda x: int(x) if isinstance(x, float) else x)
solar_df_cleaned = solar_df_cleaned.rename(columns={'Latitude': 'lat', 'Longitude': 'lng', 'Technology Type': 'Technology-Type'})
# convert Longitude to lng

# consolidate inferred statuses
inferred_statuses = solar_df_cleaned[solar_df_cleaned['Status'].str.contains('inferred')]
print(inferred_statuses)
# solar_df_cleaned.loc[inferred_statuses,'Status'] = solar_df_cleaned.loc[inferred_statuses,'Status'].split(' - inferred')[0]

inferred_statuses_cancelled = solar_df_cleaned['Status'].str.contains('cancelled - inferred')
inferred_statuses_shelved = solar_df_cleaned['Status'].str.contains('shelved - inferred')

solar_df_cleaned.loc[inferred_statuses_cancelled, 'Status'] = 'cancelled'
solar_df_cleaned.loc[inferred_statuses_shelved,'Status'] = 'shelved'
print(set(solar_df_cleaned['Status'].to_list()))

# that one to be deleted 
missed_deletion = solar_df_cleaned['Project Name'].str.contains('TO BE DELETED')
print(solar_df_cleaned[missed_deletion]['Project Name'])
solar_df_cleaned = solar_df_cleaned[~missed_deletion]

solar_df_cleaned = solar_df_cleaned[fields_needed]
print(len(solar_df_cleaned))
# print(set(solar_df_cleaned['Technology-Type'].to_list()))
# print(solar_df_cleaned.columns)
solar_df_cleaned.to_csv(output_file, encoding='utf-16', index=False)
print(f'done {output_file}')

print('Tests:')
df = solar_df_cleaned.copy()
max_cap = df['Capacity (MW)'].max()
print(f'max_cap: {max_cap}')
print(f'total units: {len(df)}')

summ1 = "Solar Farm Capacity by Country/Area (MW)"
summ2 = "Solar Farm Phase Count by Country/Area"
summ3 = "Solar Farm Capacity by Region (MW)"
# df.groupby("Animal", group_keys=True)[['Max Speed']].apply(lambda x: x)
summ1df = df.groupby(['Country', 'Status'])[['Capacity (MW)']].sum()
# print(f'{summ1}: {summ1df}') #Done

summ2df = df.groupby(['Country', 'Status'])[['GEM phase ID']].count()
# print(f'{summ2}: {summ2df}') #Done

summ3df = df.groupby(['Region', 'Subregion', 'Status'])[['Capacity (MW)']].sum()
print(f'{summ3}: {summ3df}') # Done