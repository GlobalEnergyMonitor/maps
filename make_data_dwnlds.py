import pandas as pd
# from all_config import *
from all_config import *
# from helper_functions import *
from helper_functions import *
from make_map_tracker_objs import make_map_tracker_objs
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
    problem_map_objs = []
        ### * FOR SPEEDING IT UP * ####

    # while bufferday <= 7:
    #     try: 
    #         # create a variable that is a week from iso_today_date
    #         buffer_date = (pd.to_datetime(iso_today_date) - pd.Timedelta(days=bufferday)).strftime('%Y-%m-%d')
    #         print(buffer_date)
            
    #         with open(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/local_pkl/map_objs_list{buffer_date}.pkl', 'rb') as f:
    #             map_obj_list = pickle.load(f)
    #             for map_obj in map_obj_list:
    #                 print(map_obj.name)
    #             input('here?')
    #             break  # Exit loop if file is successfully loaded

    #     except:
    #         bufferday += 1

    
    if not map_obj_list:
        print('Have not created files recently')
        map_tab_df = gspread_access_file_read_only(multi_tracker_log_sheet_key, map_tab)
        prep_dict = source_tab_df.to_dict(orient='index')            
  
        for row in map_tab_df.index:
            
            # TO HELP PRIORITIZE AND SPEED UP CODE WHEN DEBUGGING SOMETHING AND NEED TO GET ANOTHER FILE OUT QUICKLY
            if map_tab_df.loc[row, 'mapname'] in priority:
                print(f'Map name is in priority {priority} so making map object')
            elif priority == [''] or None:
                print(f'Nothing is in priority so making map object')
            else:
                print(f"Not making map object for {map_tab_df.loc[row, 'mapname']} moving onto next row in map_tab_df to save time!")
                continue
            
            
            if tracker in map_tab_df.loc[row, 'source']:
                # create a map object from that row if tracker is in the source col
                # TODO THIS pkl file dumping will likely need to be removed before I push
                # just helps to debugging
                try: 
                    with open(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/local_pkl/map_obj_for_{map_tab_df.loc[row, "mapname"]}_on_{iso_today_date}.pkl', 'rb') as f:
                        
                        print(f'opened from {f}')
                        input('CHECK')
                        map_obj = pickle.load(f)
                except:
                    
                    map_obj = make_map_tracker_objs(map_tab_df, row, prep_dict)
                    

                    with open(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/local_pkl/map_obj_for_{map_obj.name}_on_{iso_today_date}.pkl', 'wb') as f:
                        print(f'saved to {f}')
                        pickle.dump(map_obj, f)
                # map_obj.data = df_list
                print(f"Updated map_obj.trackers for {map_obj.name}: {map_obj.source}")
                # print(f'This is df_list: \n{df_list}') # list of dfs
                print(f'Length of tracker list for {map_obj.name} {len(map_obj.trackers)}')
                # for item in map_obj.data:
                #     print(f'length of item: {len(item)}')
                map_obj_list.append(map_obj)
        
        print(iso_today_date) # /Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/local_pkl
        with open(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/local_pkl/map_objs_list{iso_today_date}.pkl', 'wb') as f:
            print(f'saved to {f}')
            pickle.dump(map_obj_list, f)
    
    else:
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        # input('Check if the above statement makes sense ^') # TODO reinstate this when not iterating
    
    for map_obj in map_obj_list:
        problem_map_objs = []
        print(F'This is map name:\n{map_obj.name}')
        print(F'This is list of sources:\n{map_obj.source}')

        # try:
        # write to xls
        # THEN turn that xls into a df and then parquet for multi-tracker dd to parquet and s3
        path_dwn = gem_path + map_obj.name + '/compilation_output/'
        path_tst = gem_path + map_obj.name + '/testing/'
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
                if map_obj.name in dd_tab_mapping.keys():
                    about_tab_name = dd_tab_mapping[map_obj.name]
                else:
                    about_tab_name = map_obj.name
                
                
                # if any(source in trackers_to_update for source in map_obj.source):
                #     about_tab_name = map_obj.source[0]
                
                # elif any(name in priority for name in map_obj.name):
                #     about_tab_name = map_obj.name                  
                # else:

                #     about_tab_name = dd_tab_mapping[map_obj.name]
                
                # print(map_obj.about)
                # # Ensure the column names are not treated as a header row
                # # Use header=False when writing to the xls file
                # df.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
                map_obj.about.to_excel(writer, sheet_name=f'About {about_tab_name}', index=False, header=False) # TODO using header false id not work
                writer = bold_first_row(writer, sheet_name=f'About {about_tab_name}') # TODO this did not work 

                for tracker_obj in map_obj.trackers:
                    print(f"Writing source to filename: {tracker_obj.name}")
                    print(f'Length of tracker df is: {len(tracker_obj.data)}')
                    input('Read that!')
                    # df = tracker_obj.data
                    about = tracker_obj.about
                    tracker_name = tracker_obj.name
                    acro = tracker_obj.acro
                    about.to_excel(writer, sheet_name=f'About {tracker_name}', index=False)
                    writer = bold_first_row(writer, sheet_name=f'About {tracker_name}')
                    if isinstance(tracker_obj.data, tuple):
                        print(tracker_obj.name)
                        input("In tuple part of make data dwnlds, check the name")
                        tracker_obj.set_data_official() # so have data for map and for datadownload

                        if tracker_name == 'Oil & Gas Extraction':
                            print(tracker_obj.data)
                            input('Check if there is anything there before data official')
                            

                            main, prod = tracker_obj.data_official 
                            # check if set data official works
                            for df in [main, prod]: 
                                if 'country_to_check' in df.columns.to_list():
                                    print(f'it is still there')
                                    input('data official not working')                      
                            print(f"Main DataFrame shape: {main.shape}")
                            print(f"Prod DataFrame shape: {prod.shape}")
                            
                            main = main.map(remove_illegal_characters)
                            prod = prod.map(remove_illegal_characters)
                            main.to_excel(writer, sheet_name=f'Extraction Main data', index=False)
                            writer = bold_first_row(writer, sheet_name=f'Extraction Main data')

                            prod.to_excel(writer, sheet_name=f'Extraction Production & reserves', index=False)
                            writer = bold_first_row(writer, sheet_name=f'Extraction Production & reserves')

                            print(f'Wrote {tracker_name} to file {filename} successfully!')
                            
                        elif tracker_name == 'GOGPT EU':
                        
                            print(tracker_obj.data)
                            input('Check if there is anything there before data official')
                            
                            plants, plants_hy = tracker_obj.data_official 
                            # check if set data official works
                            for df in [plants, plants_hy]: 
                                if 'country_to_check' in df.columns.to_list():
                                    print(f'it is still there')
                                    input('data official not working')                      
                            print(f"plants DataFrame shape: {plants.shape}")
                            print(f"plants_hy DataFrame shape: {plants_hy.shape}")
                            
                            plants = plants.map(remove_illegal_characters)
                            plants_hy = plants_hy.map(remove_illegal_characters)
                            
                            plants.to_excel(writer, sheet_name=f'plants', index=False)
                            writer = bold_first_row(writer, sheet_name=f'plants')

                            plants_hy.to_excel(writer, sheet_name=f'plants_hy', index=False)
                            writer = bold_first_row(writer, sheet_name=f'plants_hy')

                            print(f'Wrote {tracker_name} to file {filename} successfully!')
                            
                    else:

                        tracker_obj.set_data_official() # so have data for map and for datadownload
                        df = tracker_obj.data_official

                        # check if set data official works
                        if 'country_to_check' in df.columns.to_list():
                            print(f'it is still there')
                            input('data official not working')
                        df = df.map(remove_illegal_characters)
                        df.to_excel(writer, sheet_name=f'{tracker_name}', index=False)
                        writer = bold_first_row(writer, sheet_name=f'{tracker_name}')

                        print(f'Wrote {tracker_name} to file {filename} successfully!')
                    

        # read from excel to parquet in DO
        for filename in [xlsfile, xlsfile_testing]:
            df = pd.read_excel(filename)
            # save parquet file locally
            process = save_to_s3(map_obj, df, 'datadownload', path_dwn)
            # save parquet file in DO in latest folder
            # Print the output and errors (if any)
            print(process.stdout.decode('utf-8'))
            if process.stderr:
                print(process.stderr.decode('utf-8'))
        
        # except Exception as e:
        #     print(f'Issue with {map_obj.name}, let us skip it, go onto making maps and then come back.')
        #     # remove problem map_obj.name from map_obj_list
        #     map_obj_list.remove(map_obj)
        #     problem_map_objs.append((map_obj, e))
        #     print(e)       
        
    test_make_data_dwnlds()
    return map_obj_list, problem_map_objs

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

