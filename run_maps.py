# from trackers.single_tracker_maps_script import *
# from single_tracker_maps_script import *'
from make_data_dwnlds import *
from make_map_file import *
# from make_data_dwnlds import *
# from multi_tracker_maps_script import *
import subprocess
from tqdm import tqdm # can adapt more, special tweaking for dataframe!
# TODO make sure the dependency map makes sense, so it calls both single and multi script depending on new data, try with tests
###
# CALL ALL FUNCTIONS


for tracker in tqdm(trackers_to_update, desc='Running'):
    # print(tracker)
    if tracker == 'Oil & Gas Plants':
        map_obj_list, problem_map_objs = make_data_dwnlds(tracker)  
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        # input('Check if the above statement makes sense ^')
        list_of_map_objs_mapversion = make_map(map_obj_list) # this returns map obj list map version that can be run thru tests
                
        print('Great, now lets run those map objs map version thru tests on source!')
        input('Confirm above')                  
              
    elif tracker == 'Cement and Concrete':
        print('Creating global map for Cement and Concrete then dependent maps and dd')
        # add a comparison between all_config column dictionary and new file
        # make data downloads 
        map_obj_list, problem_map_objs = make_data_dwnlds(tracker)
        # creates single map file
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        # input('Check if the above statement makes sense ^')
        list_of_map_objs_mapversion = make_map(map_obj_list) # this returns map obj list map version that can be run thru tests
        
        print('Great, now lets run those map objs map version thru tests on source!')
        input('Confirm above')          
    
    elif tracker == 'Coal Mines':
        print('Creating global map for Coal Mines then dependent maps and dd')
        # add a comparison between all_config column dictionary and new file
        # make data downloads 
        map_obj_list, problem_map_objs = make_data_dwnlds(tracker)
        # creates single map file
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        # input('Check if the above statement makes sense ^')
        list_of_map_objs_mapversion = make_map(map_obj_list) # this returns map obj list map version that can be run thru tests
        
        print('Great, now lets run those map objs map version thru tests on source!')
        input('Confirm above')                        
        
    
    elif tracker == 'Hydropower':
        # make data downloads 
        map_obj_list, problem_map_objs = make_data_dwnlds(tracker)
        # creates single map file
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        # input('Check if the above statement makes sense ^')
        list_of_map_objs_mapversion = make_map(map_obj_list) # this returns map obj list map version that can be run thru tests
        
        if len(problem_map_objs) > 1:
            print(f'Now that all map and dd files that can work have completed, here are the issue map objs:')
            print(f'Problem Map Name: {problem_map_objs[0]}')
            print(f'Error: {problem_map_objs[1]}')
        
        print('Great, now lets run those map objs map version thru tests on source!')
        input('Confirm above')        
    
    elif tracker == 'Gas Pipelines':
        
        # make data downloads 
        map_obj_list, problem_map_objs = make_data_dwnlds(tracker)
        # creates single map file
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        # input('Check if the above statement makes sense ^')
        list_of_map_objs_mapversion = make_map(map_obj_list) # this returns map obj list map version that can be run thru tests
        
        print(f'Now that all map and dd files that can work have completed, here are the issue map objs:')
        print(f'Problem Map Name: {problem_map_objs[0]}')
        print(f'Error: {problem_map_objs[1]}')
        
        print('Great, now lets run those map objs map version thru tests on source!')
        input('Confirm above')
    
    elif tracker == 'Oil Pipelines':
        # test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/GOIT/test_results/'

        # output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/GOIT/compilation_output/'
        
        # output_file = f'{output_folder}goit-data-{iso_today_date}.csv'
        
        # make data downloads 
        map_obj_list, problem_map_objs = make_data_dwnlds(tracker)
        # creates single map file
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        # input('Check if the above statement makes sense ^')
        list_of_map_objs_mapversion = make_map(map_obj_list) # this returns map obj list map version that can be run thru tests
        
        print(f'Now that all map and dd files that can work have completed, here are the issue map objs:')
        print(f'Problem Map Name: {problem_map_objs[0]}')
        print(f'Error: {problem_map_objs[1]}')
        
        print('Great, now lets run those map objs map version thru tests on source!')
        input('Confirm above')
        

                
    elif tracker == 'Integrated':
        test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/integrated/test_results/'

        output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/integrated/compilation_output/'
        
        output_file = f'{output_folder}gipt-data-{iso_today_date}.csv'

        # creates single map file
        key, tabs = get_key_tabs_prep_file(tracker)

    
        df = create_df(key, tabs)
        ### send to s3 for latest data download
        s3folder = 'latest'
        filetype = 'datadownload'
        parquetpath = f'{output_folder}{tracker}{filetype}{releaseiso}.parquet'
        for col in df.columns:
        # check if mixed dtype
            if df[col].apply(type).nunique() > 1:
                # if so, convert it to string
                df[col] = df[col].fillna('').astype(str)
        
        df.to_parquet(parquetpath, index=False)
        do_command_s3 = (
            f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            f'aws s3 cp {parquetpath} s3://$BUCKETEER_BUCKET_NAME/{s3folder}/ '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
        )            
        process = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
        
        df = clean_capacity(df) 
        df = semicolon_for_mult_countries_gipt(df)
        df = fix_status_inferred(df)        
        # harmonize_countries(df, countries_dict, test_results_folder) # find countries_dict
        df= rename_cols(df)
        df = remove_missing_coord_rows(df)
        
        df.to_csv(output_file, index=False, encoding='utf-8' )

        s3folder = 'mapfiles'                
        filetype = 'map'
        parquetpath_m = f'{output_folder}{tracker}{filetype}{releaseiso}.parquet'
        for col in df.columns:
        # check if mixed dtype
            if df[col].apply(type).nunique() > 1:
                # if so, convert it to string
                df[col] = df[col].fillna('').astype(str)
        df.to_parquet(parquetpath_m, index=False)

        ### do aws command copy to s3 publicgem data
        do_command_s3 = (
            f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            f'aws s3 cp {parquetpath_m} s3://$BUCKETEER_BUCKET_NAME/{s3folder}/ '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
        )            
        process = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        input('Check that ingt was saved to s3')
        capacityfield = 'capacity-(mw)'
        # run csv2json
        do_csv2json = (
            f"csv2geojson --numeric-fields {capacityfield} &&"
            f"'{output_folder}gipt-data-{releaseiso}.csv' > integrated_{releaseiso}.geojson"
        )
        process = subprocess.run(do_csv2json, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # run tippecanoe
        do_tippecanoe = (
            f"tippecanoe -e integrated-{releaseiso}.dir --no-tile-compression -r1 -pk -pf --force -l && "
            f"integrated < integrated_{releaseiso}.geojson"
        )
        process = subprocess.run(do_tippecanoe, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # set aws configue and bucket name  # do aws command copy to s3 mapintegrated 

        do_aws_bucket = (
            f"aws configure set s3.max_concurrent_requests 100 && "
            f"export BUCKETEER_BUCKET_NAME=mapsintegrated && "
            f"aws s3 cp --endpoint-url https://nyc3.digitaloceanspaces.com {output_folder}integrated-{releaseiso}.dir s3://$BUCKETEER_BUCKET_NAME/maps/integrated-{releaseiso} --recursive --acl public-read"
        )
        process = subprocess.run(do_aws_bucket, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                
    elif tracker == 'Integrated-simple':
        test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/integrated/test_results/'

        output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/integrated/compilation_output/'
        
        output_file = f'{output_folder}gipt-data-{iso_today_date}.csv'

        # creates single map file
        key, tabs = get_key_tabs_prep_file(tracker)

    
        df = create_df(key, tabs)
        ### send to s3 for latest data download
        s3folder = 'GIPT-simple'
        filetype = 'dd'
        parquetpath = f'{output_folder}{tracker}{filetype}{releaseiso}.parquet'
        for col in df.columns:
        # check if mixed dtype
            if df[col].apply(type).nunique() > 1:
                # if so, convert it to string
                df[col] = df[col].fillna('').astype(str)
        
        df.to_parquet(parquetpath, index=False)
        do_command_s3 = (
            f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            f'aws s3 cp {parquetpath} s3://$BUCKETEER_BUCKET_NAME/{s3folder}/ '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
        )            
        process = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
        df = clean_capacity(df) 
        df = semicolon_for_mult_countries_gipt(df)
        df = fix_status_inferred(df)        
        # harmonize_countries(df, countries_dict, test_results_folder) # find countries_dict
        df= rename_cols(df)
        df = remove_missing_coord_rows(df)
        df = reduce_cols(df)
        
        
        df.to_csv(output_file, index=False, encoding='utf-8' )

        s3folder = 'GIPT-simple'                
        filetype = 'map'
        parquetpath_m = f'{output_folder}{tracker}{filetype}{releaseiso}.parquet'
        for col in df.columns:
        # check if mixed dtype
            if df[col].apply(type).nunique() > 1:
                # if so, convert it to string
                df[col] = df[col].fillna('').astype(str)
        df.to_parquet(parquetpath_m, index=False)

        ### do aws command copy to s3 publicgem data
        do_command_s3 = (
            f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            f'aws s3 cp {parquetpath_m} s3://$BUCKETEER_BUCKET_NAME/{s3folder}/ '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --acl public-read'
        )            
        process = subprocess.run(do_command_s3, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        input('Check that ingt was saved to s3')
        capacityfield = 'capacity-(mw)'
        # run csv2json
        do_csv2json = (
            f"csv2geojson --numeric-fields '{capacityfield}' {output_folder}gipt-data-{iso_today_date}.csv "
            f"> integrated_{iso_today_date}.geojson"
        )
        process = subprocess.run(do_csv2json, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # run tippecanoe
        do_tippecanoe = (
            f"tippecanoe -e integrated-{iso_today_date}.dir --no-tile-compression -r1 -pk -pf --force -l "
            f"integrated < integrated_{iso_today_date}.geojson"
        )
        process = subprocess.run(do_tippecanoe, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # set aws configue and bucket name  # do aws command copy to s3 mapintegrated 

        do_aws_bucket = (
            f"aws configure set s3.max_concurrent_requests 100 && "
            f"export BUCKETEER_BUCKET_NAME=mapsintegrated && "
            f"aws s3 cp --endpoint-url https://nyc3.digitaloceanspaces.com {output_folder}integrated-{iso_today_date}.dir s3://$BUCKETEER_BUCKET_NAME/maps/integrated-{iso_today_date} --recursive --acl public-read"
        )
        process = subprocess.run(do_aws_bucket, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    elif tracker == 'Geothermal':
        test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/geothermal/test_results/'

        output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/geothermal/compilation_output/'

        map_obj_list, problem_map_objs = make_data_dwnlds(tracker)
        input('check progress on dd') # TODO march 28th getting issue with nonetype for df.info should have filtering done, now focus on GOGET so can be filtered but also two tabs
        # creates single map file
        key, tabs = get_key_tabs_prep_file(tracker)
        
        df = create_df(key, tabs)
        # df = split_coords(df)

        df = rename_cols(df)
        df = fix_status_inferred(df)
        print(df.info())
        df = filter_cols(df,final_cols=['country/area', 'project-name','unit-name', 'project-name-in-local-language-/-script',
                                        'unit-capacity-(mw)', 'status', 'start-year', 'retired-year',
                                        'operator', 'owner', 'lat', 'lng', 'location-accuracy', 'city', 'state/province',
                                        'region', 'gem-unit-id', 'gem-location-id', 'url', 'technology'         
                                        ])
        df = input_to_output(df, f'{output_folder}{tracker}-map-file-{iso_today_date}.csv')
        # creates multi-map files 
        print('DONE MAKING GGPT SINGLE MAP onto MULTI MAPS')
        input('continue?')
        # creates multi-tracker maps
        # if tracker to update is coal terminals then look at sheet and create all regional and of course single
        subprocess.run(["python", "/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/multi_tracker_maps_script.py"])                 
        # update so that instead of running above, we just run each function and move it to helper instead of multi or tracker specific which can be held in tracker folder
        
        
        
    elif tracker == 'Iron & Steel':
        test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/gist/test_results/'
        output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/gist/compilation_output/'
        
        key, tabs = get_key_tabs_prep_file(tracker)
        df = create_df(key, tabs) # steel_df, iron_df, plant_df


        # drop cols don't need # filter_cols
        df = process_steel_iron_parent(df, test_results_folder)
        print(len(df))
        df = split_coords(df)
        # rename_cols
        # print(len(df))

        df = df.rename(columns={'Unit Status':'status', 'GEM Wiki Page': 'url', 'tab-type_x': 'tab-type'})
        # print(len(df))

        df = rename_cols(df)
        # print(len(df))

        # df = make_numerical(df, ['current-capacity-(ttpa)', 'plant-age-(years)'])

        # fix_status_space because filters
        df = fix_status_space(df)
        # print(len(df))

        df = fix_prod_type_space(df) 
        # print(len(df))

        df = input_to_output(df, f'{output_folder}{tracker}-map-file-{iso_today_date}.csv')
        print('DONE MAKING GIST SINGLE MAP') 
        input('Check length 1204')
       
    
    elif tracker == 'Oil & Gas Extraction':
        

        # make data downloads 
        map_obj_list, problem_map_objs = make_data_dwnlds(tracker)
        # creates single map file
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
        # input('Check if the above statement makes sense ^')
        list_of_map_objs_mapversion = make_map(map_obj_list) # this returns map obj list map version that can be run thru tests
        
        print(f'Now that all map and dd files that can work have completed, here are the issue map objs:')

        
        print('Great, now lets run those map objs map version thru tests on source!')
        input('Confirm above')

        # test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/goget/test_results/'

        # output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/goget/compilation_output/'

        # # creates single map file
        # # handle production data
        # key, tabs = get_key_tabs_prep_file(tracker)

        # df_tuple = create_df(key, tabs)
        # main = df_tuple[0]
        # prod = df_tuple[1]
        # # df has df['other'] column to distinguish between main and prod/res
        # # result will be data ready for map, after scott's code
        # df = process_goget_reserve_prod_data(main, prod)
        # df = rename_cols(df) # will need to adjust for goget's columns
        # df = fix_status_space(df)   
        # # df = format_values(df)
        # df = fix_status_inferred(df)         
        # df = filter_cols(df,final_cols=['country/area', 'wiki-name',
        #                                 'status', 'status_display','production-start-year',  
        #                                 'operator', 'owner', 'parent','lat', 'lng', 'location-accuracy', 'subnational-unit-(province,-state)',
        #                                 'gem-region', 'unit-id', 'url', 'country-list', 'discovery-year', 'fid-year', 'production---oil-(million-bbl/y)',
        #                                 'production-year---oil', 'production---gas-(million-m³/y)', 'production-year---gas', 'production---total-(oil,-gas-and-hydrocarbons)-(million-boe/y)'             
        #                                 ])
        
        # # adjust statuses 'operating', 'in_development', 'discovered', 'shut_in', 'decommissioned', 'cancelled', 'abandoned', 'UGS', ""
        
        # df = input_to_output(df, f'{output_folder}{tracker}-map-file-{iso_today_date}.csv')
        # # creates multi-map files 
        # print('DONE MAKING GOGET SINGLE MAP onto MULTI MAPS')
        # input('continue?')
        # # creates multi-tracker maps
        # subprocess.run(["python", "/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/multi_tracker_maps_script.py"])                 
                  
    elif tracker == 'Bioenergy':

        test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/bioenergy/test_results/'

        output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/bioenergy/compilation_output/'

        # creates single map file
        key, tabs = get_key_tabs_prep_file(tracker)

        df = create_df(key, tabs)
        df = rename_cols(df)
        df = fix_status_inferred(df)
        df = filter_cols(df,final_cols=['country/area', 'project-name', 'fuel', 'unit-name', 'project-name-in-local-language-/-script',
                                        'capacity-(mw)', 'status', 'start-year', 'retired-year', 'hydrogen-capable',
                                        'operator(s)', 'owner(s)', 'lat', 'lng', 'location-accuracy', 'city', 'state/province',
                                        'region', 'gem-phase-id', 'url'          
                                        ])
        df = input_to_output(df, f'{output_folder}{tracker}-map-file-{iso_today_date}.csv')
        test_stats(df)
        # creates multi-map files 
        print('DONE MAKING GBPT SINGLE MAP onto MULTI MAPS')
        input('continue?')
        # creates multi-tracker maps
        # if tracker to update is coal terminals then look at sheet and create all regional and of course single
        subprocess.run(["python", "/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/multi_tracker_maps_script.py"])                 
          
        # if test:
        #     check_expected_number(incorporated_dict_list_gdfs_by_map) # TODO HANDLE THIS ONE for dict or use the one thats been concatenated

    elif tracker == 'Oil & Gas Plants':
        # continue for all of them that are in or not in multi tracker maps
        test_results_folder = f'{tracker_folder_path}gas-plant/test_results/'

        output_folder = f'{tracker_folder_path}gas-plant/compilation_output/'

        input_file_path = f'{tracker_folder_path}gas-plant/compilation_input/'
                
        # multi_tracker_log_sheet_key = '15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8'
        # multi_tracker_log_sheet_tab = ['multi_map']
        # prep_file_tab = ['prep_file']
        # key = '1WRRFRuR9mWxZpko-VMYH5xm0LzRX_qM7W73nGGi4Jmg'
        # tabs = ['Data', 'Below Threshold']
        
        # creates single map file
        key, tabs = get_key_tabs_prep_file(tracker)
        df = create_df(key, tabs)
        df = rename_cols(df)
        df = fix_status_inferred(df)
        df = filter_cols(df,final_cols=['gem-location-id','country/area', 'plant-name', 'fuel', 'unit-name', 'plant-name-in-local-language-/-script',
                                        'capacity-(mw)', 'status', 'start-year', 'retired-year', 'parent(s)', 'turbine/engine-technology',
                                        'operator(s)', 'owner(s)', 'lat', 'lng', 'location-accuracy', 'city', 'state/province',
                                        'region', 'url'          
                                        ])
        # make sure 0% and 100% is removed from owners

        df = remove_implied_owner(df)
        df = formatting_checks(df)

        
        df = input_to_output(df, f'{output_folder}{tracker}-map-file-{iso_today_date}.csv')
        # test_stats(df)
        print('DONE MAKING GOGPT SINGLE MAP onto MULTI MAPS')
        input('Continue?')
        # creates multi-tracker maps
        # if tracker to update is coal terminals then look at sheet and create all regional and of course single
        subprocess.run(["python", "/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/multi_tracker_maps_script.py"])                 

    elif tracker == 'Plumes':
        print(f'Starting GMET for release {tracker}')
        # if augmented: # these vars are all set in all_config, this helped adapt AET code to all multi maps
        #     print('Start augmented')
        #     needed_map_and_tracker_dict = what_maps_are_needed(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab)
        #     # map_country_region has the list of needed maps to be created and their countries/regions
        #     needed_tracker_geo_by_map = what_countries_or_regions_are_needed_per_map(multi_tracker_countries_sheet, needed_map_and_tracker_dict)
        #     # print(path_for_download_and_map_files)
        #     folder_setup(needed_tracker_geo_by_map)
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print(f'Ended augmented {elapsed_time}')
            
        # if data_filtering: # this creates gdfs and dfs for all filtered datasets per map, lots of repetition here
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print('Start data filtering')
        #     prep_df = create_prep_file(multi_tracker_log_sheet_key, prep_file_tab) 
        #     conversion_df = create_conversion_df(conversion_key, conversion_tab)

        #     dict_list_dfs_by_map, dict_list_gdfs_by_map = pull_gsheet_data(prep_df, needed_tracker_geo_by_map) # map_country_region
        #     incorporated_dict_list_gdfs_by_map, incorporated_dict_list_dfs_by_map = incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson,dict_list_dfs_by_map, dict_list_gdfs_by_map) 
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print(f'Ended data filtering {elapsed_time}') 
                       
        # if map_create:
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print('Start map file creation')
        #     custom_dict_list_gdfs_by_map = split_goget_ggit(incorporated_dict_list_gdfs_by_map)  #incorporated_dict_list_gdfs_by_map
        #     custom_dict_list_gdfs_by_map_with_conversion = assign_conversion_factors(custom_dict_list_gdfs_by_map, conversion_df)
        #     renamed_one_gdf_by_map = rename_gdfs(custom_dict_list_gdfs_by_map_with_conversion)
        #     # cleaned_dict_map_by_one_gdf = remove_null_geo(renamed_one_gdf_by_map) # doesn't do anything
        #     cleaned_dict_map_by_one_gdf_with_conversions = capacity_conversions(renamed_one_gdf_by_map)
        #     cleaned_dict_by_map_one_gdf_with_better_statuses = map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions)
            
        #     cleaned_dict_by_map_one_gdf_with_better_countries = map_ready_countries(cleaned_dict_by_map_one_gdf_with_better_statuses)
        #     one_gdf_by_maptype = workarounds_eg_interim_goget_gcmt(cleaned_dict_by_map_one_gdf_with_better_countries)
        #     one_gdf_by_maptype_fixed = last_min_fixes(one_gdf_by_maptype) 
        #     final_dict_gdfs = create_map_file(one_gdf_by_maptype_fixed)
        #     final_count(final_dict_gdfs)
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print('End map file creation')
                    
        
    elif tracker == 'LNG Terminals':
        print('Starting on lng terminals')
    #     # if LNG Terminals, then we need to update GGIT, and all regional trackers
    #     # GGIT is unique because as a "singular" tracker it takes two files lng and gas pipelines
    #     # they are both local files
    #     # they need to go through lots for parsing so we'll copy that from the logic we have for regional
    #     # then once that's created we'll create the regional trackers
    #     # for EGT we will include hydrogen pipeline data 
        
    #     # SHOULD I USE incorporate_geojson_trackers
    #     # we can skip finding country col because no filter on singular
    #     # do we need to convert if we can use the bcm/y I don't think so no but let's keep it like the multi
    #     # then we need to rename and concat with rename_gdfs
    #     # then it drops columms based on final_cols paramter set in config
        
        
    #     # local non gspread so 
    #     test_results_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/ggit/test_results/'

    #     output_folder = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/ggit/compilation_output/'

    #     input_file_json = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GGIT-LNG-Terminals-2024-09 DATA TEAM COPY.geojson'
    #     # incorporate gas pipeline data as well
    #     gas_pipeline_json = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GGIT-Gas-Pipelines-2023-12 copy.geojson'                
    #     # creates single map file
    #     ggit_lng_gdf, crs = geojson_to_gdf(input_file_json)
    #     ggit_lng_gdf['tracker-acro'] = 'GGIT-lng'
    #     ggit_gdf, crs = geojson_to_gdf(gas_pipeline_json)
    #     ggit_gdf['tracker-acro'] = 'GGIT'
    #     dict_by_map = {'ggit': [ggit_lng_gdf, ggit_gdf]}
    #     dict_by_map = split_goget_ggit(dict_by_map)
    #     conversion_df = create_conversion_df(conversion_key, conversion_tab)
    #     dict_by_map = assign_conversion_factors(dict_by_map, conversion_df) # feed in conversion_df from multi tracker maps script tho will it be called? 
    #     gdf_by_map = rename_gdfs(dict_by_map) # custom_dict_list_gdfs_by_map_with_conversion
    #     gdf_by_map = capacity_conversions(gdf_by_map)
    #     gdf_by_map = map_ready_statuses(gdf_by_map) # handles for map statuses and inferred
    #     gdf_by_map = map_ready_countries(gdf_by_map) # handles for multiple areas 
    #     gdf_by_map = workarounds_eg_interim_goget_gcmt(gdf_by_map) # mainly handles multiple country sitatuions for details card 
    #     gdf_by_map = last_min_fixes(gdf_by_map) # likely do not need this
        
    #     # can print map file here or can try what we have below with the folders set up above
    #     final_dict_gdfs = create_map_file(gdf_by_map)
    #     # final_count(final_dict_gdfs)

    #     final_dict_gdfs = input_to_output_all(final_dict_gdfs, f'{output_folder}{tracker}-map-file-{iso_today_date}')
    #     # test_stats(gdf) 
    #     # now all maps dependent on LNG
    #     # creates multi-map files 
    #     # input('Main global map done. Do you want to proceed with dependent maps?')
        
    # # if augmented: # these vars are all set in all_config, this helped adapt AET code to all multi maps
    #     print('Start augmented')
    #     map_tracker_dict = what_maps_are_needed(multi_tracker_log_sheet_key, multi_tracker_log_sheet_tab)
    #     # map_country_region has the list of needed maps to be created and their countries/regions
    #     print(map_tracker_dict)
    #     # input('inspect') # this works 
    #     map_tracker_dict = what_countries_or_regions_are_needed_per_map(multi_tracker_countries_sheet, map_tracker_dict)
    #     # print(path_for_download_and_map_files)
    #     # folder_setup(needed_tracker_geo_by_map)
    #     end_time = time.time()  # Record the end time
    #     elapsed_time = end_time - start_time  # Calculate the elapsed time
    #     print(f'Ended augmented {elapsed_time}')
        
    # # if data_filtering: # this creates gdfs and dfs for all filtered datasets per map, lots of repetition here
    #     end_time = time.time()  # Record the end time
    #     elapsed_time = end_time - start_time  # Calculate the elapsed time
    #     print('Start data filtering')
    #     prep_df = create_prep_file(multi_tracker_log_sheet_key, prep_file_tab) 
    #     conversion_df = create_conversion_df(conversion_key, conversion_tab)

    #     map_tracker_dict_dfs, map_tracker_dict_gdfs = pull_gsheet_data(prep_df, map_tracker_dict) # map_country_region
    #     print(f'will this also be empty? {map_tracker_dict_gdfs}')
    #     map_tracker_dict_gdfs, map_tracker_dict_dfs = incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson, map_tracker_dict_dfs, map_tracker_dict_gdfs) 
    #     end_time = time.time()  # Record the end time
    #     elapsed_time = end_time - start_time  # Calculate the elapsed time
    #     print(f'Ended data filtering {elapsed_time}')
        
    # # if map_create:
    #     end_time = time.time()  # Record the end time
    #     elapsed_time = end_time - start_time  # Calculate the elapsed time
    #     print(f'Start map file creation {elapsed_time}')
    #     map_tracker_dict_gdfs = split_goget_ggit(map_tracker_dict_gdfs)  #incorporated_dict_list_gdfs_by_map
    #     print(f'Will this be empty too? {map_tracker_dict_gdfs}')
    #     map_tracker_dict_gdfs = assign_conversion_factors(map_tracker_dict_gdfs, conversion_df)
    #     renamed_one_gdf = rename_gdfs(map_tracker_dict_gdfs)
    #     # cleaned_dict_map_by_one_gdf = remove_null_geo(renamed_one_gdf) # doesn't do anything
    #     renamed_one_gdf = capacity_conversions(renamed_one_gdf)
    #     renamed_one_gdf = map_ready_statuses(renamed_one_gdf)
        
    #     renamed_one_gdf = map_ready_countries(renamed_one_gdf)
    #     renamed_one_gdf = workarounds_eg_interim_goget_gcmt(renamed_one_gdf)
    #     renamed_one_gdf = last_min_fixes(renamed_one_gdf) 
    #     print(f'This is final gdf keys for {tracker}: {one_gdf_by_maptype}')
    #     final_dict_gdfs = create_map_file(renamed_one_gdf)
        
    #     final_dict_gdfs = input_to_output_all(final_dict_gdfs, f'{output_folder}{tracker}-map-file-{iso_today_date}')
    #     final_count(final_dict_gdfs)

    #     end_time = time.time()  # Record the end time
    #     elapsed_time = end_time - start_time  # Calculate the elapsed time
    #     print(f'End map file creation {elapsed_time}')          
    
        ## COMMENTING OUT FOR NOW TIL WE HAVE MAP WORKING

        # if about_create: # this creates and saves a preliminary file with all about pages no adjustments made
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print('Start about creation')
        #     about_df_dict_by_map = gather_all_about_pages(prev_key_dict, prep_df, new_release_date, previous_release_date, needed_tracker_geo_by_map)
        #     create_about_page_file(about_df_dict_by_map)
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print(f'End about creation {elapsed_time}')

        # if dwlnd_create: # this creates and saves the tabular data sheets for the data download from the filtered dfs
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print(f'Start dwlnd creation {elapsed_time}')
        #     create_data_dwnld_file(incorporated_dict_list_dfs_by_map) 
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print(f'End dwlnd creation {elapsed_time}')
            
        # if refine: # this reorders the data download file
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print('Start refining')
        #     if local_copy:
        #         about_df_dict_by_map = ''
        #         incorporated_dict_list_dfs_by_map = ''
        #     reorder_dwld_file_tabs(about_df_dict_by_map, incorporated_dict_list_dfs_by_map) 
        #     end_time = time.time()  # Record the end time
        #     elapsed_time = end_time - start_time  # Calculate the elapsed time
        #     print('End refining')    

    elif tracker == 'Wind':
        # continue for all of them that are in or not in multi tracker maps
        test_results_folder = f'{tracker_folder_path}wind/test_results/'

        output_folder = f'{tracker_folder_path}wind/compilation_output/'

        # input_file_path = f'{tracker_folder_path}coal-terminals/compilation_input/'
        
        os.makedirs(test_results_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)       
             

        # creates single map file
        key, tabs = get_key_tabs_prep_file(tracker)
        df = create_df(key, tabs)
        df = rename_cols(df)
        df = fix_status_inferred(df)
        df = filter_cols(df,final_cols=['gem-location-id', 'gem-phase-id', 'country/area', 'phase-name', 'project-name', 'project-name-in-local-language-/-script',
                                        'other-name(s)', 'capacity-(mw)', 'status', 'start-year', 'retired-year', 'location-accuracy',
                                         'owner', 'lat', 'lng', 'state/province', 'operator', 'installation-type',
                                        'region', 'url', 'owner-name-in-local-language-/-script', 'operator-name-in-local-language-/-script'        
                                        ])
            
        
        df = input_to_output(df, f'{output_folder}{tracker}-map-file-{iso_today_date}.csv')
        # test_stats(df)

        print('DONE MAKING WIND SINGLE MAP onto MULTI MAPS')
        input('continue?')
        # creates multi-tracker maps
        # if tracker to update is coal terminals then look at sheet and create all regional and of course single
        # subprocess.run(["python", "/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/multi_tracker_maps_script.py"])                 


    elif tracker == 'Solar':
        # continue for all of them that are in or not in multi tracker maps
        test_results_folder = f'{tracker_folder_path}solar/test_results/'

        output_folder = f'{tracker_folder_path}solar/compilation_output/'
        
        os.makedirs(test_results_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)       
             

        # creates single map file
        key, tabs = get_key_tabs_prep_file(tracker)
        df = create_df(key, tabs)
        df = rename_cols(df)
        df = fix_status_inferred(df)
        df = filter_cols(df,final_cols=['gem-location-id', 'gem-phase-id', 'country/area', 'phase-name', 'project-name', 'project-name-in-local-language-/-script',
                                        'other-name(s)', 'capacity-(mw)', 'status', 'start-year', 'retired-year', 'location-accuracy',
                                         'owner', 'lat', 'lng', 'state/province', 'operator', 'technology-type',
                                        'region', 'url', 'owner-name-in-local-language-/-script', 'operator-name-in-local-language-/-script'         
                                        ])
                
        
        df = input_to_output(df, f'{output_folder}{tracker}-map-file-{iso_today_date}.csv')
        # test_stats(df)

        print('DONE MAKING SOLAR SINGLE MAP onto MULTI MAPS')
        input('continue?')
        # creates multi-tracker maps
        # if tracker to update is coal terminals then look at sheet and create all regional and of course single
        # subprocess.run(["python", "/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/multi_tracker_maps_script.py"])                 
    
    elif tracker == 'Coal Plants':
        # continue for all of them that are in or not in multi tracker maps
        test_results_folder = f'{tracker_folder_path}coal-plant/test_results/'

        output_folder = f'{tracker_folder_path}coal-plant/compilation_output/'
        
        os.makedirs(test_results_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)       
             

        # creates single map file
        key, tabs = get_key_tabs_prep_file(tracker)
        df = create_df(key, tabs)
        df = rename_cols(df)
        df = fix_status_inferred(df)
        df = filter_cols(df,final_cols=['gem-location-id', 'gem-unit/phase-id', 'country', 'unit-name', 'plant-name', 'plant-name-(other)',
                                        'plant-name-(local)', 'capacity-(mw)', 'status', 'start-year', 'retired-year', 'location-accuracy',
                                         'owner', 'parent','lat', 'lng', 'combustion-technology',
                                        'region', 'url', 'subnational-unit-(province,-state)'        
                                        ])
                
        
        df = input_to_output(df, f'{output_folder}{tracker}-map-file-{iso_today_date}.csv')
        # test_stats(df)

        print('DONE MAKING Coal SINGLE MAP onto MULTI MAPS')
        input('continue?')
    
    # subprocess.run(["python", "/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/multi_tracker_maps_script.py"])                 
    
    
    
# else:
#     # all calls in multi_tracker_maps_script
#     if augmented: # these vars are all set in all_config, this helped adapt AET code to all multi maps
#         print('Start augmented')
#         # print('TESTING what_maps_are_needed_new')
#         # result of new is {'Africa Energy': ['Coal Plants', 'Coal Mines', 'Coal Terminals', 'Oil & Gas Plants', 'Oil & Gas Extraction', 'Gas Pipelines', 'LNG Terminals', 'Oil Pipelines', 'Solar', 'Wind', 'Nuclear', 'Bioenergy', 'Geothermal', 'Hydropower'], 'Asia Gas': ['Oil & Gas Plants', 'Oil & Gas Extraction', 'Gas Pipelines', 'LNG Terminals'], 'Europe Gas': ['Oil & Gas Plants', 'Oil & Gas Extraction', 'Gas Pipelines EU', 'LNG Terminals'], 'LATAM': ['Coal Plants', 'Coal Mines', 'Coal Terminals', 'Oil & Gas Plants', 'Oil & Gas Extraction', 'Gas Pipelines', 'LNG Terminals', 'Oil Pipelines', 'Solar', 'Wind', 'Nuclear', 'Bioenergy', 'Geothermal', 'Hydropower']}
#         # needed_map_and_tracker_dict_new = what_maps_are_needed_new(multi_tracker_log_sheet_key, map_tab) # result is {'Africa Energy': ['Coal Plants', 'Coal Mines', 'Coal Terminals', 'Oil & Gas Plants', 'Oil & Gas Extraction', 'Gas Pipelines', 'LNG Terminals', 'Oil Pipelines', 'Solar', 'Wind', 'Nuclear', 'Bioenergy', 'Geothermal', 'Hydropower'], 'Asia Gas': ['Oil & Gas Plants', 'Oil & Gas Extraction', 'Gas Pipelines', 'LNG Terminals'], 'Europe Gas': ['Oil & Gas Plants', 'Oil & Gas Extraction', 'Gas Pipelines EU', 'LNG Terminals'], 'LATAM': ['Coal Plants', 'Coal Mines', 'Coal Terminals', 'Oil & Gas Plants', 'Oil & Gas Extraction', 'Gas Pipelines', 'LNG Terminals', 'Oil Pipelines', 'Solar', 'Wind', 'Nuclear', 'Bioenergy', 'Geothermal', 'Hydropower']}
#         needed_map_and_tracker_dict = what_maps_are_needed(multi_tracker_log_sheet_key, regional_multi_map_tab) # map_tab
#         # map_country_region has the list of needed maps to be created and their countries/regions
#         print(needed_map_and_tracker_dict)
#         # ##(input('inspect')
#         needed_tracker_geo_by_map = what_countries_or_regions_are_needed_per_map(multi_tracker_countries_sheet, needed_map_and_tracker_dict)
#         # print(path_for_download_and_map_files)
#         folder_setup(needed_tracker_geo_by_map)
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate the elapsed time
#         print(f'Ended augmented {elapsed_time}')
        
#     if data_filtering: # this creates gdfs and dfs for all filtered datasets per map, lots of repetition here
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate the elapsed time
#         print('Start data filtering')
#         prep_df = create_prep_file(multi_tracker_log_sheet_key, source_data_tab)  # so we are using source, so can delete prep file
#         conversion_df = create_conversion_df(conversion_key, conversion_tab)
        
#         to_pass = []
#         if priority != ['']:
#             for key, value in needed_tracker_geo_by_map.items():
#                 if key not in priority:
#                     to_pass.append(key)
#                 else:
#                     print(f'Prioritizing {key}')

            
#             for key in to_pass:
#                 del needed_tracker_geo_by_map[key]
            
        
#         dict_list_dfs_by_map, dict_list_gdfs_by_map = pull_gsheet_data(prep_df, needed_tracker_geo_by_map) # map_country_region
#         incorporated_dict_list_gdfs_by_map, incorporated_dict_list_dfs_by_map = incorporate_geojson_trackers(goit_geojson, ggit_geojson, ggit_lng_geojson, dict_list_dfs_by_map, dict_list_gdfs_by_map) 
#         # print(incorporated_dict_list_gdfs_by_map)
#         # print(len(incorporated_dict_list_gdfs_by_map))
#         # for map in incorporated_dict_list_dfs_by_map.items:
#         #     df = 
#         # (input(f'Check the above, should not be empty! were in filtering. that is the length of local geojson file dfs.')
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate the elapsed time
#         print(f'Ended data filtering {elapsed_time}')  

        
#     if map_create:
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate the elapsed time
#         print(f'Start map file creation {elapsed_time}')
#         custom_dict_list_gdfs_by_map = split_goget_ggit(incorporated_dict_list_gdfs_by_map)  #incorporated_dict_list_gdfs_by_map
#         custom_dict_list_gdfs_by_map_with_conversion = assign_conversion_factors(custom_dict_list_gdfs_by_map, conversion_df)
#         renamed_one_gdf_by_map = rename_gdfs(custom_dict_list_gdfs_by_map_with_conversion)
#         renamed_one_gdf_by_map_with_search = create_search_column(renamed_one_gdf_by_map)
#         input('done with create_search_column')
#         # renamed_one_gdf_by_map = add_boed_routes_from_baird(renamed_one_gdf_by_map)
#         # cleaned_dict_map_by_one_gdf = remove_null_geo(renamed_one_gdf_by_map) # doesn't do anything
        
#         cleaned_dict_map_by_one_gdf_with_conversions = capacity_conversions(renamed_one_gdf_by_map_with_search)
#         cleaned_dict_by_map_one_gdf_with_better_statuses = map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions)
        
#         cleaned_dict_by_map_one_gdf_with_better_countries = map_ready_countries(cleaned_dict_by_map_one_gdf_with_better_statuses)
#         one_gdf_by_maptype = workarounds_eg_interim_goget_gcmt(cleaned_dict_by_map_one_gdf_with_better_countries)
#         one_gdf_by_maptype_fixed = last_min_fixes(one_gdf_by_maptype) 
#         # print(f'This is final gdf keys for: {one_gdf_by_maptype}')
#         final_dict_gdfs = create_map_file(one_gdf_by_maptype_fixed)
        
#         final_count(final_dict_gdfs)

#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate the elapsed time
#         print(f'End map file creation {elapsed_time}')     

#     if dwlnd_create: # this creates and saves the tabular data sheets for the data download from the filtered dfs
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate the elapsed time
#         print(f'Start dwlnd creation {elapsed_time}')
#         create_data_dwnld_file(incorporated_dict_list_dfs_by_map) 
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate the elapsed time
#         print(f'End dwlnd creation {elapsed_time}')
    

#     if about_create: # this creates and saves a preliminary file with all about pages no adjustments made
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time 
#         print('Start about creation')
#         about_df_dict_by_map = gather_all_about_pages(prev_key_dict, prep_df, needed_tracker_geo_by_map)
#         create_about_page_file(about_df_dict_by_map)
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  
#         print(f'End about creation {elapsed_time}')

    
#     if refine: # this reorders the data download file
#         end_time = time.time()  
#         elapsed_time = end_time - start_time  
#         print('Start refining')
#         if local_copy:
#             about_df_dict_by_map = ''
#             incorporated_dict_list_dfs_by_map = ''
#         print(incorporated_dict_list_dfs_by_map)
#         # for map, gdfs in incorporated_dict_list_dfs_by_map.items():
#         #     print(map)
#         #     print(gdfs)
#         #     if map == 'latam':
#         #         input('pause for latam')
#         # for map, aboutdfs in about_df_dict_by_map.items():
#         #     print(map)
#         #     print(aboutdfs)
#         #     if map == 'latam':
#         #         input('pause for latam')


#         reorder_dwld_file_tabs(incorporated_dict_list_dfs_by_map) 
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate the elapsed time
#         print('End refining')  

#     if run_post_tests:
#         # post_tests(final_dict_gdfs)
#         robust_tests_map()
#         # robust_tests_dd()
        
# if tracker in tracker to update is part of a multi tracker map then run that script in addition
# individual script

# individual script should have if else for tracker nuances
# multi map script can be the same as I used for the AET just moved out of africa-energy folder

# so for october should be:
# - bioenergy unique map
# - africa energy
# - latam energy
# - GIPT (wait on James)

# one script for all maps
# print where fails which file which tracker
# output to test file
# output for download file 
# outpuf for map file 

# first bring in gas to africa




# inputs differences for integrated is just the GIPT file from James

# new_tracker_data = 'INSERT TRACKER ACRONYM HERE'
# new_tracker_release_date = 'INSERT RELEASE DATE HERE'
