# import sqlalchemy as sa
import pandas as pd
import numpy as np
import math
import os
from datetime import date
import csv

# Get today's date
today_date = date.today()
# Format the date in ISO format
iso_today_date = today_date.isoformat()
iso_today_date_folder = f'{iso_today_date[:7]}/'

geo_map_input_path = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/geothermal/'
file = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/geothermal/data.csv'

# take csv file to df
df = pd.read_csv(file, encoding="utf-16")


def fix_status_inferred(df):

    print(df.columns)
    print(f"statuses before: {set(df['status'].to_list())}")

    inferred_statuses_cancelled = df['status'].str.contains('cancelled - inferred')
    inferred_statuses_shelved = df['status'].str.contains('shelved - inferred')

    df.loc[inferred_statuses_cancelled, 'status'] = 'cancelled'
    df.loc[inferred_statuses_shelved,'status'] = 'shelved'

    print(f"statuses before: {set(df['status'].to_list())}")

    return df

df = fix_status_inferred(df)

df.to_csv(geo_map_input_path + f"data_{iso_today_date}.csv", quoting=csv.QUOTE_ALL)
print(f'done {geo_map_input_path + f"data_{iso_today_date}.csv"}')




