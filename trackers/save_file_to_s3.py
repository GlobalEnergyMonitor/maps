import pandas as pd
import geopandas as gpd
import numpy as np
import time
import subprocess
from shapely.geometry import MultiPolygon
import pickle
import os
import argparse
from io import BytesIO
import requests
from datetime import datetime, timedelta
# from helper_functions import *

today_date = datetime.today()
iso_today_date = today_date.isoformat().split('T')[0]

# with this script we can use a google link to push to s3 
# or a list of local filepaths 

def googlelinktoparquet(link=''):

    if link != '':
        # Extract the file ID from the Google Drive link
        try:
            file_id = link.split('/d/')[1].split('/')[0]
            print(file_id)
        except IndexError:
            print("Invalid Google Drive link format.")
            return

        # Construct the export URL for Google Sheets
        export_url = f"https://drive.google.com/uc?id={file_id}&export=download&format=xlsx"
        print(export_url)
        # Download the file
        wait_time = 5
        # tries = 0
        # while tries <= 3:

        try:
            response = requests.get(export_url, headers={"Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
            time.sleep(wait_time)
            # wait for it to download
        except:
            # tries +=1
            # wait_time +=10
            print('did not work')
        

        input(f'response: {response}')
        if response.status_code != 200:
            print(f"Failed to download file. HTTP Status Code: {response.status_code}")
            return
    else:
        print(f'Manually downloading drive files, but now this will run latest download through parquet process!')
        file_id = 'md' # for manually downloaded
        pass

    # Go to the downloads folder and find the most recent Excel file with "DATA TEAM COPY" in the title
    downloads_folder = os.path.expanduser("~/Downloads")
    files = [os.path.join(downloads_folder, f) for f in os.listdir(downloads_folder) if f.endswith(".xlsx")] # and "DATA TEAM COPY" in f
    
    if not files:
        print("No Excel file with 'DATA TEAM COPY' in the title found in the Downloads folder.")
        return
    
    # Find the most recent file
    most_recent_file = max(files, key=os.path.getctime)
    most_recent_file_time = time.ctime(os.path.getctime(most_recent_file))
    print(f"Most recent file's saved date/time: {most_recent_file_time}")
    print(f"Most recent file found: {most_recent_file}")
    
    # Load the file into a pandas DataFrame
    try:

        df = pd.read_excel(most_recent_file, engine='openpyxl', sheet_name=None)
        new_name = most_recent_file.split('/')[-1].split('.xlsx')[0].replace(' ', '').replace('-','').replace('DATATEAMCOPY', 'DTC')
        print(f'new_name: {new_name}')

    except Exception as e:
        print(f"Failed to read the file as an Excel file: {e}")
        return
    

    # Save the DataFrame as a Parquet file
    newfilepath = f"{downloads_folder}/{new_name}_{file_id}_{iso_today_date}.parquet"
    for col in df.columns:
        # check if mixed dtype
        if df[col].apply(type).nunique() > 1:
            # if so, convert it to string
            df[col] = df[col].fillna('').astype(str)
    
    df.to_parquet(newfilepath)
    # save_to_s3(df,'dd_source',newfilepath) # see if this works from helper func so we use the same function! 
    print(f"File saved as {newfilepath}")

    # Optionally upload to S3
    saves3(newfilepath)
    
    

def filetoparquet(filepaths): # should be a list
    
    for filepath in filepaths:
        if 'geojson' in filepath:
            gdf = gpd.read_file(filepath)
            print(gdf.shape)
            # newfilepath = '/'.join(filepath.split('/')[:-1])
            newfilepath = filepath.replace('.geojson', '.parquet').replace(' ', '_')
            print(newfilepath)
            gdf.to_parquet(path = f'{newfilepath}')
        elif 'xlsx' in filepath:
            df = pd.read_excel(filepath)
            print(df.shape)
            # newfilepath = '/'.join(filepath.split('/')[:-1])
            newfilepath = filepath.replace('.xlsx', '.parquet').replace(' ', '_')
            print(newfilepath)
            df.to_parquet(path = f'{newfilepath}')            
        
        else: 
            print(f'Looks like the file is not a json or excel')
            print(filepath)
            input(f'adjust filetoparquet function in save_file_to_s3.py')
        
        # save original and then save parquet version
        saves3(filepath)
        saves3(newfilepath)

def saves3(filepath):
    file = f'{filepath}'

    do_command_s3 = (
                f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
                f'aws s3 cp "{file}" s3://$BUCKETEER_BUCKET_NAME/latest/ '
                f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read')

            # Execute the terminal command to pull down file from digital ocean
    process = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(process.stdout.decode('utf-8'))
    if process.stderr:
        print(process.stderr.decode('utf-8'))


if __name__ == "__main__":

    # parser = argparse.ArgumentParser(description="Save a file to S3.")
    # parser.add_argument("filepath", type=str, help="Path to the file to be uploaded.")
    # args = parser.parse_args()

    # filetoparquet(filepaths=[''])
    # saves3(filepath=args.filepath)
    googlelinktoparquet()
    # googlelinktoparquet('https://docs.google.com/spreadsheets/d/16MoNKcz68GVwv6ztZ6p0vSNlL6EmPd633DZ7V0xG_Ho/')
    
    
    # list_of_links = ['https://docs.google.com/spreadsheets/d/1wI11cMqhqZXTK7MVD2semkZIqlF4DSpfsNTaSPBWWO0/', 'https://drive.google.com/file/d/1X6tpYmgDKUWZzSYGlz0LcCeE-DqGeQcp/', 
    #                 'https://docs.google.com/spreadsheets/d/1aZiKzbHfFXLSEFCeKwstvL1-DV98ErXDhyCx00abRgQ/', 'https://docs.google.com/spreadsheets/d/1dqawuLhgFzYI9GWRU9bwsDY1SQHjzxifZb7u1T8OXqA/',
    #                 'https://docs.google.com/spreadsheets/d/1zUyj7t4FO0M9fc82wpG93fZmisGar0Syq1l5ZGyyxEM/', 'https://docs.google.com/spreadsheets/d/1TxoQ17GUDvRbQ82r90eexbRNHfPfi-50wm9lBih2eYc/',
    #                 'https://docs.google.com/spreadsheets/d/1hB2NuXMMqCJD94muoe6-A9BCi4v-7hquScej44_QWas/', 'https://docs.google.com/spreadsheets/d/1crtLnGzOS6wLYweIb84gLQpMV4A49qD5fty6WBTdLt0/',
    #                 'https://docs.google.com/spreadsheets/d/1jUbsItBq_CVXy0dUxCP7APHfstDL85BaykCXYURagX4/', 'https://docs.google.com/spreadsheets/d/1bUTPRTmIqu7URVECm66NGr_DF7v32UUOzBaBf1dNawk/',
    #                 'https://docs.google.com/spreadsheets/d/1x-IxdiqMJ_v-M_45ASFdg55Gl3Hsx3vb-7wjt8qCq5k/', 'https://docs.google.com/spreadsheets/d/1cy0A7k0GoB2b_b2wesObcAvts0GbXa7go7FVE_bHpBc/',
    #                 'https://docs.google.com/spreadsheets/d/1XxAvcobKZ9XRKvHaSHDb4JbOstqhvrVWkU5Wu8JKhgE/', 'https://docs.google.com/spreadsheets/d/1gOOwjN551r6TllpBpfxtwNqF1yfbLbXdCFwACvKYeI4/',
    #                 'https://docs.google.com/spreadsheets/d/10Clsb8auutXy4iBm6c7HywZjSbNKUiho9NHzZmC2-Bs/', 'https://docs.google.com/spreadsheets/d/1cqLe0xOx7FLpfaGZhtVnV-bhuKgaczHPtXzCRIgy_RQ/',
    #                 'https://docs.google.com/spreadsheets/d/1zCcO9LwVmiQZBOGqlwKGYgZ5lAnBKJ91hjwWcbUw5nQ/', 'https://docs.google.com/spreadsheets/d/1zCcO9LwVmiQZBOGqlwKGYgZ5lAnBKJ91hjwWcbUw5nQ/',
    #                 'https://docs.google.com/spreadsheets/d/16MoNKcz68GVwv6ztZ6p0vSNlL6EmPd633DZ7V0xG_Ho/']


    # for link in list_of_links:
        
    #     googlelinktoparquet(link)
