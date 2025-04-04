import pandas as pd
import json
import subprocess
import geopandas as gpd
import boto3
from trackers.creds import ACCESS_KEY, SECRET_KEY


def list_all_contents(tracker, release):
    tracker = tracker.lower()

    list_all_contents = [] # should be one file, if not then we need to remove / update
    # Initialize a session using DigitalOcean Spaces
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY)

    # Define the bucket name and folder prefix
    bucket_name = 'publicgemdata'
    folder_prefix = 'latest/'

    # List objects in the specified folder
    response = client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

    # Check if the 'Contents' key is in the response
    if 'Contents' in response:
        for obj in response['Contents']:
            print(obj['Key'])
            if tracker and release in obj['Key']:
                list_all_contents.append(obj['Key'])
    else:
        print("No files found in the specified folder.")
    
    return list_all_contents


def get_file_name(tracker, release):
    tracker = tracker.lower()
    path_name = list_all_contents(tracker, release)[0]
    if path_name:
        print(path_name)
        input('check it!')
    else:
        input('Might be an issue with path name look into get_file_name plz!')
    # Define the terminal command
    testing_source_path = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/'
    # path_name = 'latest/GEM-GOIT-Oil-NGL-Pipelines-2025-03.geojson' # TODO could rename these month, tracker
    terminal_cmd = f'aws s3 cp s3://$BUCKETEER_BUCKET_NAME/{path_name}/ {testing_source_path} --endpoint-url https://nyc3.digitaloceanspaces.com --recursive'

    # Execute the terminal command to pull down file from digital ocean
    process = subprocess.run(terminal_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Print the output and errors (if any)
    print(process.stdout.decode('utf-8'))
    if process.stderr:
        print(process.stderr.decode('utf-8'))

    path_name = path_name.split('latest/')[1]
    file = f'{testing_source_path}{path_name}'

    return file

# get_file_name('goit', '2025-03')