
from make_data_dwnlds import *
from make_map_file import *
from make_metadata import *
import subprocess
import geopandas as gpd
from shapely.geometry import Point
import os
from tqdm import tqdm # can adapt more, special tweaking for dataframe!
# TODO make sure the dependency map makes sense, so it calls both single and multi script depending on new data, try with tests
###
# CALL ALL FUNCTIONS



def run_maps():

    for tracker in tqdm(trackers_to_update, desc='Running'):
        # print(tracker)
        trackermapname = official_tracker_name_to_mapname[tracker]
        print(f'Creating new metadata file for the tracker in trackers to update called: trackermeta_{trackermapname}_{releaseiso}_{iso_today_date}.yaml')
        trackerfile = f"trackermeta_{trackermapname}_{releaseiso}_{iso_today_date}"
        # MFILE_ACTUAL = f'{mfile}.yaml'
        metadata = create_or_load_metadata(trackerfile)
        save_metadata(trackerfile, metadata)
        
        if tracker in list_of_all_official:
            
            map_obj_list = make_data_dwnlds(tracker)  
            if dd_only == True:
                print('ALL DONE!')
            else:
                list_of_map_objs_mapversion = make_map(map_obj_list, tracker) # this returns map obj list map version that can be run thru tests
            
                print(f'done making dd and maps for {tracker}')
        
        elif tracker == 'Integrated':

            output_folder = 'trackers/integrated/compilation_output/'
            
            output_file = f'{output_folder}gipt-data-{iso_today_date}.csv'
            output_file2 = f'{output_folder}integrated_{releaseiso}.geojson'


            # creates single map file
            key, tabs = get_key_tabs_prep_file(tracker)

            df = create_df(key, tabs)
            ### send to s3 for latest data download
            # s3folder = 'latest'
            # filetype = 'datadownload'
    
            # parquetpath = f'{output_folder}{tracker}{filetype}{releaseiso}.parquet'
            # for col in df.columns:
            # # check if mixed dtype
            #     if df[col].apply(type).nunique() > 1:
            #         # if so, convert it to string
            #         df[col] = df[col].fillna('').astype(str)
            
            # df.to_parquet(parquetpath, index=False)
            # do_command_s3 = (
            #     f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            #     f'aws s3 cp {parquetpath} s3://$BUCKETEER_BUCKET_NAME/{tracker}/{releaseiso}/ '
            #     f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
            # )            
            
            
            # runresults = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print(runresults.stdout)                    
            
            df = clean_capacity(df) 
            df = semicolon_for_mult_countries_gipt(df)
            df = fix_status_inferred(df)        
            # harmonize_countries(df, countries_dict, test_results_folder) # find countries_dict
            df= rename_cols(df)
            print(f'length before df drops missing coords: {len(df)}')

            df = remove_missing_coord_rows(df, tracker)
            
            print(f'length after df drops missing coords: {len(df)}')
            input('check length difference!')

            # turn into a gdf and save as output_file2
            # Ensure lat/lng are numeric and drop rows with missing values
            print(f'length before gdf conversion drop: {len(df)}')
            df = df.dropna(subset=['lat', 'lng'])
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
            df = df.dropna(subset=['lat', 'lng'])
            print(f'length after gdf conversion drop: {len(df)}')
            logger.info(f'COMPARE THE TWO to see if missing coords row SHOULD BE EQUAL')

            # make sure capacity mw is cast as numeric NOT string, special handling is needed to make sure interpolation works later with tiles
            # df["capacity-(mw)"] = pd.to_numeric(df["capacity-(mw)"], errors="raise") 
            df["capacity-(mw)"] = df["capacity-(mw)"].astype(float) 
            
            df.to_csv(output_file, index=False, encoding='utf-8')

            # save csv to digital ocean            
            # output_file
            save_csv_s3 = (
                f'export aws_access_key_id={ACCESS_KEY} && '
                f'export aws_secret_access_key={SECRET_KEY} && '
                f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
                f'aws s3 cp {output_file} s3://$BUCKETEER_BUCKET_NAME/{tracker}/{releaseiso}/ '
                f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
            )            
            
            runresults = subprocess.run(save_csv_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(runresults.stdout)  
            print(f'saved csv file to s3, update config.js for non tile data {output_file}, now convert df to gdf for tile')           
        
            input('run to here and then check map TEMP')
            # Create geometry column from lng/lat (note: Point(x, y) = Point(lng, lat))
            geometry = [Point(xy) for xy in zip(df['lng'], df['lat'])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
            print(gdf.dtypes)
            input(f'Check dtypes to be sure capacity is float not object')
            gdf.to_file(output_file2, driver='GeoJSON')
            # filetype = 'map'
            # parquetpath_m = f'{output_folder}{tracker}{filetype}{releaseiso}.parquet'
            
            # for col in df.columns:
            # # check if mixed dtype
            #     if df[col].apply(type).nunique() > 1:
            #         # if so, convert it to string
            #         df[col] = df[col].fillna('').astype(str)
            # df.to_parquet(parquetpath_m, index=False)

            ### do aws command copy to s3 publicgem data
            # do_command_s3 = (
            #     f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            #     f'aws s3 cp {parquetpath_m} s3://$BUCKETEER_BUCKET_NAME/{tracker}/{releaseiso}/ '
            #     f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
            # )            
            # runresults = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print(runresults.stdout)
            # logger.info('Check that ingt was saved to s3')
         
            # run tippecanoe to generate pbf files needed for tile
            do_tippecanoe = (
                f"tippecanoe -e {output_folder}integrated-{iso_today_date}.dir --no-tile-compression -r1 -pk -pf --force -l integrated < {output_folder}integrated_{releaseiso}.geojson"
            )
            runresults = subprocess.run(do_tippecanoe, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(runresults.stdout)

            print('Finished running tippecanoe to create pbf files from the json file. Start on aws bucket command.')
            print('This may take about 20 min, check Activity Monitor and search for aws to make sure all is ok.')
            # set aws configue and bucket name  # do aws command copy to s3 mapintegrated 

            # push to maps bucket - note this is different than the public gem data bucket 
            do_aws_bucket = (
                f"aws configure set s3.max_concurrent_requests 100 && "
                f"export BUCKETEER_BUCKET_NAME=mapsintegrated && "
                f"aws s3 cp --endpoint-url https://nyc3.digitaloceanspaces.com {output_folder}integrated-{iso_today_date}.dir s3://$BUCKETEER_BUCKET_NAME/maps/integrated-{releaseiso} --recursive --acl public-read"
            )
            runresults = subprocess.run(do_aws_bucket, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(runresults.stdout)
            

if __name__ == "__main__":
    # main() this log file folder creater i sin all_config for now maybe want to move later!
    run_maps()