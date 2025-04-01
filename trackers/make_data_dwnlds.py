import pandas as pd
# from all_config import *
from trackers.all_config import *
# from helper_functions import *
from trackers.helper_functions import *

from collections import OrderedDict
from tqdm import tqdm

from .map_class import MapObject
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
    while bufferday <= 7:
        try: 
            # create a variable that is a week from iso_today_date
            buffer_date = (pd.to_datetime(iso_today_date) - pd.Timedelta(days=bufferday)).strftime('%Y-%m-%d')
            print(buffer_date)
            with open(f'trackers/local_pkl/map_objs_list{buffer_date}.pkl', 'rb') as f:
                map_obj_list = pickle.load(f)
                break  # Exit loop if file is successfully loaded

        except:
            bufferday += 1
    
    if not map_obj_list:
        print('Have not created files recently')
    
    if map_obj_list == []:
        map_tab_df = gspread_access_file_read_only(multi_tracker_log_sheet_key, map_tab)
        prep_dict = source_tab_df.to_dict(orient='index')            
        
                    
        for row in map_tab_df.index:
            if tracker in map_tab_df.loc[row, 'source']:
                # create a map object from that row if tracker is in the source col
                map_obj = create_map_objs(map_tab_df, row)
                df_list = []
                print(map_obj.name)
                print(map_obj.geo)
                print(map_obj.fuel)
                print(map_obj.source)
                needed_geo = geo_mapping[map_obj.geo]
                

                for item in map_obj.source:
                    print(f'Processing source item: {item}')
                    key = prep_dict[item]['gspread_key']
                    tabs = prep_dict[item]['gspread_tabs']
                    release = prep_dict[item]['latest release']
                    acro = prep_dict[item]['tracker-acro']
                    geocol = prep_dict[item]['geocol']
                    fuelcol =  prep_dict[item]['fuelcol']

                    # create object or df
                    if item == 'Oil Pipelines':
                        print('handle non_gsheet_data for pulling data from s3 already has coords')
                        
                        gdf = gpd.read_file(goit_geojson)
                        gdf = add_goit_boedcap_from_baird(gdf)

                        # filter by country 
                        gdf = create_filtered_geo_df(gdf, acro, geocol, needed_geo)
                        # filter by fuel optionally
                        if map_obj.fuel != ['none']:
                            gdf = create_filtered_fuel_df(gdf, acro)
                            
                        df_list.append(gdf)
                        
                    elif item == 'Gas Pipelines':
                        gdf = gpd.read_file(ggit_geojson)
                    
                        gdf.info()
                        # gdf = gdf[gdf[geocol].apply(lambda x: check_list(x, needed_geo))]


                        # filter by country 
                        gdf = create_filtered_geo_df(gdf, acro, geocol, needed_geo)
                        # filter by fuel optionally
                        if map_obj.fuel != ['none']:
                            gdf = create_filtered_fuel_df(gdf, acro)
                            
                        df_list.append(gdf)
                        
                    elif item == 'LNG Terminals':
                        gdf = gpd.read_file(ggit_lng_geojson)
                        gdf.info()
                        # gdf = gdf[gdf[geocol].apply(lambda x: check_list(x, needed_geo))]

                        # filter by country 
                        gdf = create_filtered_geo_df(gdf, acro, geocol, needed_geo)
                        # filter by fuel optionally
                        if map_obj.fuel != ['none']:
                            gdf = create_filtered_fuel_df(gdf, acro)
                            
                        df_list.append(gdf)
                        
                    elif item == 'Oil & Gas Extraction':
                        df_tuple = create_df_goget(key, tabs)
                        main = df_tuple[0]
                        prod = df_tuple[1]
                        # use ids after filter by country and fuel for dd for two tab dd
                        print(df_tuple[0].info())
                        print(df_tuple[1].info())
                        # gdf = gdf[gdf[geocol].apply(lambda x: check_list(x, needed_geo))]
                        
                        to_merge = []
                        fueldf = 0
                        for df in [main,prod]:
                            # filter by country 
                            df = create_filtered_geo_df(df, acro, geocol, needed_geo)
                            # # filter by fuel optionally
                            if map_obj.fuel != ['none']:
                                # get prod filtered then use ID on merge to filter main
                                if fuelcol in df.columns:
                                    fueldf = create_filtered_fuel_df(df, acro, fuelcol)
                                    to_merge.append(fueldf)
                                else:
                                    to_merge.append(df)
                            else:
                                to_merge.append(df) 
                        filtered_main = to_merge[0]
                        if not fueldf:
                            # no fuel filter needed so we are good to just print the two tabs in dd
                            # and merge them for map later
                            print('no fuel filter needed')
                        else:
                            gas_goget_ids = fueldf['Unit ID '].to_list()
                            filtered_main = filtered_main[filtered_main['Unit ID'].isin(gas_goget_ids)]
                        
                        filtered_prod = to_merge[1]
                        filtered_tuple = (filtered_main, filtered_prod)
                          
                        
                        df_list.append(filtered_tuple)
                        

                    else:
                        df = create_df(key, tabs)

                        # filter by country 
                        df = create_filtered_geo_df(df, acro, geocol, needed_geo)
                        # filter by fuel optionally

                        if map_obj.fuel != ['none']:
                            df = create_filtered_fuel_df(df, acro)                    
    
                        
                        # df = df[df[geocol].apply(lambda x: check_list(x, needed_geo))]
                        df_list.append(df)


                print(f"DataFrames in df_list for {map_obj.name}:")
                for i, df in enumerate(df_list):
                    try:
                        print(f"DataFrame {i}: {df.shape}")
                    except AttributeError:
                        df_tuple_filt = df
                        main = df_tuple_filt[0]
                        prod = df_tuple_filt[1]
                        print(f"DataFrame {i}main: {main.shape}")
                        print(f"DataFrame {i}prod: {prod.shape}")

                map_obj.data = df_list
                print(f"Updated map_obj.data for {map_obj.name}: {map_obj.data}")
                # print(f'This is df_list: \n{df_list}') # list of dfs
                print(f'Length of data_list for {map_obj.name} {len(map_obj.data)}')
                # for item in map_obj.data:
                #     print(f'length of item: {len(item)}')
                map_obj_list.append(map_obj)
        
        with open(f'trackers/local_pkl/map_objs_list{iso_today_date}.pkl', 'wb') as f:
            print(f'saved to {f}')
            pickle.dump(map_obj_list, f)
    
    else:
        print(f'{len(map_obj_list)} maps to be updated with new {tracker} data!')
    
    for map_obj in map_obj_list:
        
        # add on abouts and then write to files
        map_obj = create_abouts(map_obj, source_tab_df)
        
        path_dwn = gem_path + map_obj.name + '/compilation_output/'
        path_tst = gem_path_tst + f'final/{iso_today_date}/'
        os.makedirs(path_dwn, exist_ok=True)
        os.makedirs(path_tst, exist_ok=True)
        
        xlsfile = f'{path_dwn}{map_obj.name}-data-download_{new_release_date}_{iso_today_date}.xlsx'
        xlsfile_testing = f'{path_tst}{map_obj.name}-data-download_{new_release_date}_{iso_today_date}_test.xlsx'
        for filename in [xlsfile, xlsfile_testing]:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer: 
                df_list = map_obj.data
                # zip up source attribute so have name of tracker data
                source_list = map_obj.source
                abouts_dep_list = map_obj.dep_abouts
                # Ensure the lengths of df_list and source_list match
                if len(df_list) != len(source_list) != len(abouts_dep_list):
                    print(f"Warning: {map_obj.name} Mismatch in lengths - df_list: {len(df_list)}, source_list: {len(source_list)}, dep_abouts: {len(abouts_dep_list)}")
                    input('Check')
                else:
                    print(f"df_list: {len(df_list)}, source_list: {len(source_list)}, dep_abouts: {len(abouts_dep_list)}")
                
                # print out overall about page
                map_obj.about.to_excel(writer, sheet_name=f'About {map_obj.name}', index=False)
                
                # now worry about printing all the data dfs and about dfs
                # Zip the source_list with df_list to pair source names with their corresponding data
                for source_name, df, dep_about_df in zip(source_list, df_list, abouts_dep_list):
                    print(f"Processing source: {source_name}")
                    input('Pause')
                    if isinstance(df, tuple):
                        # Handle tuple case (e.g., main and prod DataFrames)
                        main, prod = df
                        print(f"Main DataFrame shape: {main.shape}")
                        print(f"Prod DataFrame shape: {prod.shape}")
                        main = main.map(remove_illegal_characters)
                        prod = prod.map(remove_illegal_characters)
                        
                        # main = main.drop(columns=['country_to_check'])
                        # prod = prod.drop(columns=['country_to_check'])
                        
                        dep_about_df.to_excel(writer, sheet_name=f'About {source_name}', index=False)
                        main.to_excel(writer, sheet_name=f'{source_name} Main data', index=False)
                        prod.to_excel(writer, sheet_name=f'{source_name} Production & reserves', index=False)
                        print(f'Wrote {source_name} to file {filename} successfully!')

                    else:
                        # Handle single DataFrame case
                        print(f"DataFrame shape: {df.shape}")
                        df = df.map(remove_illegal_characters)
                        
                        dep_about_df.to_excel(writer, sheet_name=f'About {source_name}', index=False)

                        df.to_excel(writer, sheet_name=f'{source_name}', index=False)
                        print(f'Wrote {source_name} to file {filename} successfully!')

    test_make_data_dwnlds()


def create_map_objs(map_tab_df,row):
    map_obj = MapObject(
        name=map_tab_df.loc[row, 'mapname'],
        source=map_tab_df.loc[row, 'source'],
        geo=map_tab_df.loc[row, 'geo'],
        fuel=map_tab_df.loc[row, 'fuel'],
        pm=map_tab_df.loc[row, 'PM'], 
        data=[],
        about='',
        dep_abouts = []
    )
    return map_obj

def create_filtered_geo_df(df, acro, geocol, needed_geo):
    df = df.copy()
    # handle for situations that have two separate country columns, like ghpt
    if ';' in geocol:
        df['country_to_check'] = [[] for _ in range(len(df))]
        for row in df.index:
            for col in geocol.split(';'):
                # get a list of countries between all relevant geo columns
                df.at[row,'country_to_check'] += [df.at[row,col]]
        # handle for situations that have more than one country in the col # like goit, ggit
        # filter the df based on whether any of the items in the country to check list are in needed geo
        print(f'len of df before geo filter: {len(df)}')
        df = df[df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
        print(f'len of df after geo filter: {len(df)}')
        # input(f'check filter change for geo \n{needed_geo}')
                
    else:
        # handle for situations that have more than one country in the col # like goit, ggit
        # this split creates a list, we didn't need it above since it's already a list
        df['country_to_check'] = df.apply(lambda row: split_countries(row[geocol]), axis=1)
        print(f'len of df before geo filter: {len(df)}')
        df = df[df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
        print(f'len of df after geo filter: {len(df)}')
        # input(f'check filter change for geo \n{needed_geo}')    

    # drop country_to_check column
    df = df.drop(columns=['country_to_check'])
    
    return df
    
    
def create_filtered_fuel_df(filtered_df, acro, fuelcol=''):
        
    if acro == 'GOGET':

        drop_row = []
        # print(filtered_df.columns)
        # input('Check that Fuel type is in there or fuel')
        for row in filtered_df.index:
            # if df.loc[row, 'tracker-acro'] == 'GOGET':
            # if filtered_df.loc[row, 'Unit ID'] not in list_ids:
            #     drop_row.append(row)
            
            if filtered_df.loc[row, 'Fuel type'] == 'oil':
                drop_row.append(row)
        # drop all rows from df that are goget and not in the gas list ids 
        print(f'Length of goget before oil drop: {len(filtered_df)}')
        filtered_df.drop(drop_row, inplace=True)        
        print(f'Length of goget after oil drop: {len(filtered_df)}')
        input('Check the above to see if gas only for goget!')

            
        # print(len(ndf)) # 3012 after removing goget 
    elif acro in ['GGIT-eu', 'GGIT']:
        # filter for hydrogen only, but also gas for pci europe uses this instead of other release
        drop_row = []
        for row in filtered_df.index:
            # if df.loc[row, 'tracker-acro'] == 'GOGPT': # 1751 from 1966 after filter
            if filtered_df.loc[row, 'Fuel'] == 'Oil':
                drop_row.append(row)
            elif filtered_df.loc[row, 'Fuel'] == '':
                drop_row.append(row)

        filtered_df.drop(drop_row, inplace=True)  

            
    elif acro == 'GOGPT':
        # filter2 = (df['tracker-acro']=='GOGPT') & (df['fuel'].contains('liquid')) #2788
        drop_row = []
        for row in filtered_df.index:
            # if df.loc[row, 'tracker-acro'] == 'GOGPT': # 1751 from 1966 after filter
            fuel_cat_list = filtered_df.loc[row, 'Fuel'].split(',')
            new_fuel_cat_list = []
            for fuel in fuel_cat_list:
                fuel = fuel.split(':')[0]
                new_fuel_cat_list.append(fuel)
            
            # for Alcudia does not contain gas, or only contains fossil liquids
            
            # fossil liquids: diesel, fossil gas: natural ga...      37.5  operating   
            if len(new_fuel_cat_list) > 1:
                if new_fuel_cat_list.count('fossil liquids') == len(new_fuel_cat_list):
                        drop_row.append(row)

            elif new_fuel_cat_list == ['fossil liquids']:
                drop_row.append(row)
                    
        # drop all rows from df that are goget and not in the gas list ids 
        filtered_df.drop(drop_row, inplace=True)  
        # print(len(ndf)) # should be 2797
        print(f'len after gas only filter {acro} {len(filtered_df)}') 
        input('check the above')
        return filtered_df
    
    
def create_abouts(map_obj, source_tab_df):
    # TODO March 31 yay they are all being written to the file, as expected, at least regionally and gipt
    # But now we need to make sure we pull the about page in its entirety, use the old method but insert into current first last function
    # for example goget about is not complete, only some columns were pulled in 

    # not a truly multi tracker dd, like integrated or regional, ggit (with 2) should be handled there 
    if len(map_obj.source) <= 2:

        for tracker in map_obj.source:
            if tracker == 'Gas Pipelines':
                tracker_key = about_page_ggit_goit[tracker]
            elif tracker == 'LNG Terminals':
                tracker_key = about_page_ggit_goit[tracker]
            elif tracker == 'Oil Pipelines':
                tracker_key = about_page_ggit_goit[tracker]
            # using the same as gas pipelines because about page was identical from last release dec 2023

            else:
                tracker_key = source_tab_df[source_tab_df['official name'] == tracker]['gspread_key'].values[0]
            about_df = find_about_page(tracker, tracker_key)
            map_obj.about = about_df
            # nothing for about_deps
    else:
        prev_key = prev_key_dict[map_obj.name]

        gspread_creds = gspread.oauth(
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
                credentials_filename=client_secret_full_path,
                # authorized_user_filename=json_token_name,
            )
        wait_time = 30
        time.sleep(wait_time)
        gsheets = gspread_creds.open_by_key(prev_key)        
        sheet_names = [sheet.title for sheet in gsheets.worksheets()]
        multi_tracker_about_page = sheet_names[0]
        multi_tracker_about_page = gsheets.worksheet(multi_tracker_about_page) 
        multi_tracker_about_page = pd.DataFrame(multi_tracker_about_page.get_all_values())
        multi_tracker_about_page = replace_old_date_about_page_reg(multi_tracker_about_page)
        
        map_obj.about = multi_tracker_about_page
        
        dep_about_list = []
        for tracker in map_obj.source:
            
            if tracker == 'Gas Pipelines':
                tracker_key = about_page_ggit_goit[tracker]
            elif tracker == 'LNG Terminals':
                tracker_key = about_page_ggit_goit[tracker]
            elif tracker == 'Oil Pipelines':
                tracker_key = about_page_ggit_goit[tracker]
            # using the same as gas pipelines because about page was identical from last release dec 2023
            elif tracker == 'Gas Pipelines EU': 
                tracker_key = about_page_ggit_goit['Gas Pipelines']
            elif tracker == 'LNG Terminals EU':
                tracker_key = about_page_ggit_goit['LNG Terminals']
            elif tracker == 'Oil & Gas Plants EU':
                tracker_key = source_tab_df[source_tab_df['official name'] == 'Oil & Gas Plants']['gspread_key'].values[0]
                                        
            else:
                tracker_key = source_tab_df[source_tab_df['official name'] == tracker]['gspread_key'].values[0]
                # trying this new function instead of below, messing up for GOGET
            about_df = find_about_page(tracker, tracker_key)
            dep_about_list.append(about_df)

        print(f'Length of about dfs: {len(dep_about_list)}')
        input('Check length matches 14..')
        map_obj.dep_abouts = dep_about_list

    return map_obj
    