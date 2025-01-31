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

input_file = 'all-fields-2024-05-24T162408-wind.csv'
output_file = f'data.csv'


# see which is longer is phase or project

fields_needed = ['Wiki URL', 'Phase Name in Local Language / Script','Project Name in Local Language / Script', 'Installation-Type', 'Status', 'Capacity (MW)', 'Project Name','Phase Name', 'Owner', 'Operator', 'lat', 'lng','Location accuracy',"Local area (taluk, county)","Major area (prefecture, district)", 'State/Province', 'Country', 'Region', 'Subregion', 'Start year']

wind_df = pd.read_csv(input_file)
print(len(wind_df))

filter_deleted_projects = wind_df[wind_df['Project Name'].str.contains('TO BE DELETED')]
print(len(filter_deleted_projects))
# wind_df = wind_df[~filter_deleted_projects]


wind_df = wind_df.fillna('')
print(set(wind_df['Status'].to_list()))
# print(set(wind_df['Installation Type'].to_list()))
# print(set(wind_df['Start year'].to_list()))

# print(len(solar_df[solar_df['Phase Name in Local Language / Script'].isna()]))
# print(len(solar_df[solar_df['Project Name in Local Language / Script'].isna()]))
# print(solar_df['Phase Name in Local Language / Script'].head())
# convert Latitude to lat
# make start year an int
wind_df['Owner'] = wind_df['Owner'].str.replace(r' \[100%\]$', '', regex=True)

wind_df['Start year'] = wind_df['Start year'].apply(lambda x: int(x) if isinstance(x, float) else x)
# wind_df['Status'] = wind_df['Status'].str.capitalize()
# wind_df['Installation Type'] = wind_df['Installation Type'].replace('Offshore floating', 'offshore floating').replace('Offshore hard mount', 'offshore hard mount').replace('Offshore mount unknown', 'offshore mount unknown').replace('Unknown', 'unknown').replace('Onshore', 'onshore')

wind_df = wind_df.rename(columns={'Latitude': 'lat', 'Longitude': 'lng', 'Installation Type': 'Installation-Type'})

# convert Longitude to lng

wind_df = wind_df[fields_needed]
print(set(wind_df['Installation-Type'].to_list()))
print(set(wind_df['Status'].to_list()))

# consolidate inferred statuses
# inferred_statuses = wind_df[wind_df['Status'].str.contains('inferred')]
# print(inferred_statuses['Status'])
# wind_df.loc[inferred_statuses,'Status'] = wind_df.loc[inferred_statuses,'Status'].split(' - inferred')[0]

inferred_statuses_cancelled = wind_df['Status'].str.contains('cancelled - inferred')
inferred_statuses_shelved = wind_df['Status'].str.contains('shelved - inferred')

wind_df.loc[inferred_statuses_cancelled, 'Status'] = 'cancelled'
wind_df.loc[inferred_statuses_shelved,'Status'] = 'shelved'
print(set(wind_df['Status'].to_list()))

# that one to be deleted 
missed_deletion = wind_df['Project Name'].str.contains('TO BE DELETED')
print(wind_df[missed_deletion]['Project Name'])
wind_df = wind_df[~missed_deletion]
print(len(wind_df))
wind_df.to_csv(output_file)
