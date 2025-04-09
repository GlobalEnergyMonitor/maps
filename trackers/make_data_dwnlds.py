import pandas as pd
# from all_config import *
from .all_config import *
# from helper_functions import *
from .helper_functions import *
from .create_map_objs import create_map_objs
from collections import OrderedDict
from tqdm import tqdm
import subprocess

# from .map_class import MapObject
# from .pull_down_s3 import *
# from .create_map_objs import create_map_objs
# from .tracker_class import TrackerObject
########
# Make data downloads for regional maps with goget change
########
def test_make_data_dwnlds():
    length_source = 0
    length_dd = -1
    if length_source == length_dd:
        print(f'pass! lengths are the same:\n{length_source}={length_dd}')
    else:
        print(f'Faiil :( sry not yet! \n {length_source}!={length_dd}')
        # input('review')

def make_data_dwnlds(tracker):
    print(f'making dd for {tracker}!')
    source_tab_df = create_prep_file(multi_tracker_log_sheet_key, source_data_tab)

    # find which maps need to be updated
    # via map tab in multi_tracker_log_sheet_key
    # make an object called map
    bufferday = 0
    map_obj_list = []  # Initialize map_obj_list outside the loop
    
        ### * FOR SPEEDING IT UP * ####
    # while bufferday <= 7:
    #     try: 
    #         # create a variable that is a week from iso_today_date
    #         buffer_date = (pd.to_datetime(iso_today_date) - pd.Timedelta(days=bufferday)).strftime('%Y-%m-%d')
    #         print(buffer_date)
            
    #         with open(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/local_pkl/map_objs_list{buffer_date}.pkl', 'rb') as f:
    #             map_obj_list = pickle.load(f)
    #             print(map_obj_list)
    #             input('here?')
    #             break  # Exit loop if file is successfully loaded

    #     except:
    #         bufferday += 1

# TODO left off here on april 8th 6:03 pm some sort of issue with oduelnot found error trackers... how i moved around the creds thing for security? :()     
    
    if not map_obj_list:
        print('Have not created files recently')
        map_tab_df = gspread_access_file_read_only(multi_tracker_log_sheet_key, map_tab)
        prep_dict = source_tab_df.to_dict(orient='index')            
  
        for row in map_tab_df.index:
            if tracker in map_tab_df.loc[row, 'source']:
                # create a map object from that row if tracker is in the source col
                
                map_obj = create_map_objs(map_tab_df, row, prep_dict)

                # map_obj.data = df_list
                print(f"Updated map_obj.trackers for {map_obj.name}: {map_obj.source}")
                # print(f'This is df_list: \n{df_list}') # list of dfs
                print(f'Length of tracker list for {map_obj.name} {len(map_obj.trackers)}')
                # for item in map_obj.data:
                #     print(f'length of item: {len(item)}')
                map_obj_list.append(map_obj)
        
        print(iso_today_date)
        with open(f'gem_tracker_maps/local_pkl/map_objs_list{iso_today_date}.pkl', 'wb') as f:
            print(f'saved to {f}')
            pickle.dump(map_obj_list, f)
    
    else:
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        input('Check if the above statement makes sense ^')
    
    for map_obj in map_obj_list:


        # write to xls
        # THEN turn that xls into a df and then parquet for multi-tracker dd to parquet and s3
        path_dwn = gem_path + map_obj.name + '/compilation_output/'
        path_tst = gem_path_tst + f'final/{iso_today_date}/'
        os.makedirs(path_dwn, exist_ok=True)
        os.makedirs(path_tst, exist_ok=True)
        xlsfile = f'{path_dwn}{map_obj.name}-data-download_{new_release_date}_{iso_today_date}.xlsx'
        xlsfile_testing = f'{path_tst}{map_obj.name}-data-download_{new_release_date}_{iso_today_date}_test.xlsx'

        # write to excel files! 
        for filename in [xlsfile, xlsfile_testing]:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer: 
                # df_list = map_obj.data
                # df_list = map_obj.trackers.data # maybe?
                # THIS is where we can remap for the actual tab
                if map_obj.source in trackers_to_update:
                    about_tab_name = map_obj.source
                
                else:
                    
                    about_tab_name = dd_tab_mapping[map_obj.name]
                
                # print(map_obj.about)
                map_obj.about.to_excel(writer, sheet_name=f'About {about_tab_name}', index=False)
                for tracker_obj in map_obj.trackers:
                    print(f"Writing source to filename: {tracker_obj.name}")
                    # df = tracker_obj.data
                    about = tracker_obj.about
                    tracker_name = tracker_obj.name
                    acro = tracker_obj.acro
                    about.to_excel(writer, sheet_name=f'About {tracker_name}', index=False)
                    if isinstance(tracker_obj.data, tuple):
                        tracker_obj.set_data_official() # so have data for map and for datadownload
                        main, prod = tracker_obj.data_official                        
                        print(f"Main DataFrame shape: {main.shape}")
                        print(f"Prod DataFrame shape: {prod.shape}")
                        main = main.map(remove_illegal_characters)
                        prod = prod.map(remove_illegal_characters)
                        main.to_excel(writer, sheet_name=f'{acro} Main data', index=False)
                        prod.to_excel(writer, sheet_name=f'{acro} Production & reserves', index=False)
                        print(f'Wrote {tracker_name} to file {filename} successfully!')
                    
                    else:
                        tracker_obj.set_data_official() # so have data for map and for datadownload
                        df = tracker_obj.data_official
                        df = df.map(remove_illegal_characters)
                        df.to_excel(writer, sheet_name=f'{tracker_name}', index=False)
                        print(f'Wrote {tracker_name} to file {filename} successfully!')
                    

        # read from excel to parquet in DO
        for filename in [xlsfile, xlsfile_testing]:
            df = pd.read_excel(filename)
            # save parquet file locally
            process = save_to_s3(map_obj, df, path_dwn)
            # save parquet file in DO in latest folder
            # Print the output and errors (if any)
            print(process.stdout.decode('utf-8'))
            if process.stderr:
                print(process.stderr.decode('utf-8'))
                
                
        
    test_make_data_dwnlds()
    return map_obj_list

# moved to helper functions cuz need it in make map file too
# def save_to_s3(map_obj, path_dwn, df):
#     parquet = save_as_parquet(df, map_obj.name, path_dwn)
            
          
#     do_command_s3 = (
#                 f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
#                 f'aws s3 cp {parquet} s3://$BUCKETEER_BUCKET_NAME/latest/ '
#                 f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read')

#             # Execute the terminal command to pull down file from digital ocean
#     process = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     return process

