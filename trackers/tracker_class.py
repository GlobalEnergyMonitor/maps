from requests import HTTPError
from .all_config import new_release_date, iso_today_date,trackers_to_update, geo_mapping, releaseiso, gspread_creds, ggit_geojson, ggit_lng_geojson, region_key, region_tab, centroid_key, centroid_tab
from .helper_functions import rename_gdfs, fuel_filter, maturity, clean_about_df, replace_old_date_about_page_reg, convert_google_to_gdf, convert_coords_to_point, check_and_convert_float, check_in_range, check_and_convert_int, get_most_recent_value_and_year_goget, calculate_total_production_goget, get_country_list, get_country_list, create_goget_wiki_name,create_goget_wiki_name, gspread_access_file_read_only
import pandas as pd
from numpy import absolute
import json
import subprocess
import geopandas as gpd
import boto3
from trackers.creds import *
import time
import numpy as np
from shapely import wkt
import pickle


class TrackerObject:
    def __init__(self,
                 name="",
                 off_name="",
                 acro="",
                 key="",
                 tabs=[],
                 release="",
                 geocol = [],
                 fuelcol = "",
                 about_key = "",
                 about = pd.DataFrame(),
                 data = pd.DataFrame(), # will be used for map creation 
                 data_official = pd.DataFrame() # should be for final data downloads removed new columns!
                 ):
        self.name = name
        self.off_name = off_name
        self.acro = acro
        self.key = key
        self.tabs = tabs
        self.release = release
        self.geocol = geocol
        self.fuelcol = fuelcol
        self.about_key = about_key
        self.about = about
        self.data = data
        self.data_official = data_official



    def set_data_official(self):
        # drop country_to_check columns

        internal_cols = ['country_to_check']  # Ensure this is a list
        print(self.name)
        if isinstance(self.data, pd.DataFrame):
            df_official = self.data.copy()
            for col in self.data:
                print(col)
            try:
                df_official.drop(columns=internal_cols, inplace=True)  # Specify columns explicitly
            except KeyError:
                print('key error')


        else:
            # raise TypeError("Expected 'df' to be a DataFrame, but got a tuple or other type.")
            main, prod = self.data
            for df in [main, prod]:
                if internal_cols[0] in df.columns:
                    df.drop(columns=internal_cols, inplace=True)
            df_official = (main, prod)
            # drop internal
            # try:
            # for df in [main, prod]:
                
                
            # except KeyError:
            #     print('key error')
            # finally:
            #     df_official = (main, prod)
        
        self.data_official = df_official
    

    def set_df(self):

        print(f'See if data already exists locally for {self.name}...')
        try: 
            with open(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/local_pkl/trackerdf_for_{self.acro}_on_{iso_today_date}.pkl', 'rb') as f:
                
                print(f'opened from {f}')
                self.data = pickle.load(f)
                input(f'Check the file is up to date or needs to be deleted from local_pk!')
                [print (col) for col in self.data.columns]
                # input(f'Review orig cols in {self.name}')
                
        except:
            
            parquet_file_source_path = 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/'

            # this creates the dataframe for the tracker
            if self.name == 'Oil Pipelines':
                print('handle non_gsheet_data for pulling data from s3 already has coords')
                
                # to get the file names in latest
                parquet_s3 = self.get_file_name(releaseiso)
                print(f'This is file: {parquet_s3}')
                if 'parquet' in parquet_s3:

                    df = pd.read_parquet(f'{parquet_file_source_path}{parquet_s3}') # , engine='pyarrow' NOTE gpd calls a different method "read_table" that requires a file path NOT a URI
                
                    df['geometry'] = df['geometry'].apply(lambda geom: wkt.loads(geom) if geom else None)

                    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
                
                else:
                    gdf = gpd.read_file(f'{parquet_file_source_path}{parquet_s3}')
                
                self.data = gdf
                # gdf = add_goit_boedcap_from_baird(gdf)
                # input('successfully created gdf from s3 file') #worked!
                
            elif self.name == 'Gas Pipelines':
                

                print('handle non_gsheet_data for pulling data from s3 already has coords')

                # to get the file names in latest
                parquet_s3 = self.get_file_name(releaseiso)
                print(f'This is file: {parquet_s3}')

                # self.data = pd.read_parquet(f'{parquet_file_source_path}{parquet_s3}', engine='pyarrow')   # GEM-GGIT-Gas-Pipelines-2024-12_DATA_TEAM_COPY_md_2025-04-16.parquet
                df = pd.read_parquet(f'{parquet_file_source_path}{parquet_s3}')
                df['geometry'] = df['geometry'].apply(lambda geom: wkt.loads(geom) if geom else None)

                gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
                self.data = gdf
                
            elif self.name == 'LNG Terminals':

                print('handle non_gsheet_data for pulling data from s3 already has coords')
                
                # to get the file names in latest
                parquet_s3 = self.get_file_name(releaseiso)
                print(f'This is file: {parquet_s3}')

                df = pd.read_parquet(f'{parquet_file_source_path}{parquet_s3}') 
                # print(df['geometry'])
                # from shapely import wkt
                # Convert geometry to WKT format for saving as Parquet
                # Assuming `df` is the DataFrame loaded from the Parquet file
                df['geometry'] = df['geometry'].apply(lambda geom: wkt.loads(geom) if geom else None)
                # TODO NEED TO TRANSFER geometry back to 
                # TypeError("Input must be valid geometry objects: {0}".format(geom)) 
                # TypeError: Input must be valid geometry objects: POINT (-90.194444 29.105833)
                gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
                self.data = gdf
            
    
            elif self.name == 'Gas Pipelines EU':
                print('handle non_gsheet_data for pulling data from s3 already has coords')
                
                # to get the file names in latest
                parquet_s3 = self.get_file_name(releaseiso)
                
                #assign gdf to data 

                df = pd.read_parquet(f'{parquet_file_source_path}{parquet_s3}') 
                df['geometry'] = df['geometry'].apply(lambda geom: wkt.loads(geom) if geom else None)
    
                gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
                print(len(gdf))
                print(gdf.columns)
                test = gdf[gdf['PipelineName']=='Azerbaijan-Georgia-Romania Interconnector Gas']
                print(test)
                input('its there on s3 download')
                self.data = gdf
                
            elif self.name == 'LNG Terminals EU':
                print('handle non_gsheet_data for pulling data from s3 already has coords')
                
                # to get the file names in latest
                parquet_s3 = self.get_file_name(releaseiso)
                
                #assign gdf to data 

                df = pd.read_parquet(f'{parquet_file_source_path}{parquet_s3}')  
                df['geometry'] = df['geometry'].apply(lambda geom: wkt.loads(geom) if geom else None)
    
                gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
                self.data = gdf                    
                
            elif self.name == 'GOGPT EU':  # TODO issue here april 28th went to else statement when it was gogpt eu

                df_tuple = self.create_df_gogpt_eu() 
                print(type(df_tuple)) 
                self.data = df_tuple
                print('It is a tuple GOGPT EU')
                input('Check')
            
            elif self.name == 'Oil & Gas Extraction':
                df_tuple = self.create_df_goget()
                main = df_tuple[0]
                prod = df_tuple[1]
                # use ids after filter by country and fuel for dd for two tab dd
                # print(df_tuple[0].info())
                # print(df_tuple[1].info())
                
                #assign df tuple to data 
                self.data = df_tuple # not sure how to handle this, concat? 
                # gdf = gdf[gdf[geocol].apply(lambda x: check_list(x, needed_geo))]
            
            else:
                #assign df to data 

                df = self.create_df()
                # input('Check df') # works! didn't call the method correctly..
                
                
                # to get the file names in latest 
                # TODO need to standardize naming saved in s3 first
                # parquet_s3 = self.get_file_name(releaseiso)
                
                # #assign gdf to data 

                # df = pd.read_parquet(f'{parquet_file_source_path}{parquet_s3}') 
                self.data = df


            with open(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/local_pkl/trackerdf_for_{self.acro}_on_{iso_today_date}.pkl', 'wb') as f:
                print(f'saved to {f}')
                pickle.dump(self.data, f)
                try:
                    [print (col) for col in self.data.columns]
                    # input(f'Review orig cols in {self.name}')
                except AttributeError as e:
                    print(f'{e} Should be attribute error for tuple')
                    df_tuple = self.data
                    one = df_tuple[0]
                    two = df_tuple[1]
                    [print (col) for col in one.columns]
                    [print (col) for col in two.columns]
                    


    def get_about(self):
        # this gets the about page for this tracker data
        print(f'Creating about for: {self.name}')
    
        # TODO March 31 yay they are all being written to the file, as expected, at least regionally and gipt
        # But now we need to make sure we pull the about page in its entirety, use the old method but insert into current first last function
        # for example goget about is not complete, only some columns were pulled in 

        # these are the json files like ggit that we need to use its google doc version not geojson version
        if self.about_key != '':
            tracker_key = self.about_key
        
        # this case is for the normies where we'll loop through their final data dwld file and find the about page
        else:
            tracker_key = self.key
            # trying this new function instead of below, messing up for GOGET
        about_df = self.find_about_page(tracker_key)
        
            
        # NEEDS 
        # Copyright © Global Energy Monitor. Global Wind Power Tracker, February 2025 release. Distributed under a Creative Commons Attribution 4.0 International License.
        # Recommended Citation: "Global Energy Monitor, Global Wind Power Tracker, February 2025 release" (See the CC license for attribution requirements if sharing or adapting the data set.)
        
        tracker_official_name = f"{self.off_name}"
        if self.name in trackers_to_update:
            # use new date not old one in map log gsheets
            release_month_year = f"{new_release_date.replace('_', ' ')}" 
        else:
            release_month_year = self.release
        copyright_full = f"Copyright © Global Energy Monitor. Global {tracker_official_name} Tracker, {release_month_year} release. Distributed under a Creative Commons Attribution 4.0 International License."
        citation_full = f'Recommended Citation: "Global Energy Monitor, Global {tracker_official_name} Tracker, {release_month_year} release" (See the CC license for attribution requirements if sharing or adapting the data set.)'
        # if either are not in there fully then insert into the df after first row
        # elif partially in there, delete row and insert
        # else pass
        if copyright_full in about_df.values:
            print(f'Already has full copyright: {copyright_full}')
        elif about_df.apply(lambda row: row.astype(str).str.contains('Copyright © Global Energy Monitor.').any(), axis=1).any():
            print('Partial copyright, delete row and insert full')
            # find row number in df that holds partial
            partial_row_index = about_df.apply(lambda row: row.astype(str).str.contains('Copyright © Global Energy Monitor.').any(), axis=1).idxmax()
            about_df.drop(index=partial_row_index, inplace=True)
            about_df.reset_index(drop=True, inplace=True)
            print(about_df.shape)
            full_copy_row = pd.DataFrame([[copyright_full] * len(about_df.columns)], columns=about_df.columns)
            print(full_copy_row)
            print(full_copy_row.shape)
            about_df = pd.concat([about_df.iloc[:1], full_copy_row, about_df.iloc[1:]]).reset_index(drop=True)

        else:
            print('Inserting full copyright into second row') 
            # insert a new blank row in the second row
            full_copy_row = pd.DataFrame([[copyright_full] * len(about_df.columns)], columns=about_df.columns)
            # split the existing df in two at the second row, concat full copy row like a sandwich in between
            about_df = pd.concat([about_df.iloc[:1], full_copy_row, about_df.iloc[1:]]).reset_index(drop=True)

        about_df.reset_index(drop=True, inplace=True)
        
        
        if citation_full in about_df:
            print(f'Already has full citation: {citation_full}')
        # see if any of the full citation is found in any of the about df rows
        elif about_df.apply(lambda row: row.astype(str).str.contains('Recommended Citation: "Global Energy Monitor,').any(), axis=1).any():
            print('Partial Citations, delete row and insert full via concat sandwich')
            partial_row_index = about_df.apply(lambda row: row.astype(str).str.contains('Recommended Citation: "Global Energy Monitor,').any(), axis=1).idxmax()
            about_df.drop(index=partial_row_index, inplace=True)
            about_df.reset_index(drop=True, inplace=True)
            full_cite_row = pd.DataFrame([[citation_full] * len(about_df.columns)], columns=about_df.columns)
            about_df = pd.concat([about_df.iloc[:2], full_cite_row, about_df.iloc[2:]]).reset_index(drop=True)
            
        else:
            print('Inserting full citation into third row') 
            full_cite_row = pd.DataFrame([[citation_full] * len(about_df.columns)], columns=about_df.columns)
            about_df = pd.concat([about_df.iloc[:2], full_cite_row, about_df.iloc[2:]]).reset_index(drop=True) 
                       

        about_df = clean_about_df(about_df) 

        # print(about_df)
        # input("Check for changes in about_df, full copyright with date and full citation with date.")
            
        self.about = about_df



    def list_all_contents(self, release):
        acro = self.acro.lower() # eu, ggit
        print(acro)
        name = self.name.lower() # pipelines, terminals, gas
        print(name)
        
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
                print(obj['Key']) # this is name of the file in s3
                print(f"Using this {acro} and this {name} to look")
                # it's the current tracker update data so GOIT when it got updated in March
                # if tracker and release in obj['Key']:
                #     list_all_contents.append(obj['Key'])
                
                if acro in obj['Key'].lower() and '-' not in acro:
                    list_all_contents.append(obj['Key'])
                
                elif acro in obj['Key'].lower():
                    # list_all_contents.append(obj['Key'])
                    # weeds out ggit without eu for egt version
                    if name.split(' ')[1].lower() in obj['Key'].lower() and acro.split('-')[-1] == 'eu':
                        list_all_contents.append(obj['Key'])     
                    # weed out ggit without lng for lng 
                    elif name.split(' ')[1].lower() in obj['Key'].lower() and acro.split('-')[-1] == 'lng':
                        list_all_contents.append(obj['Key'])
                    # for the actual ggit when it is ggit, for all EGT ones too
                    elif name.split(' ')[1].lower() in obj['Key'].lower(): # and '-lng' not in acro
                        list_all_contents.append(obj['Key'])    
                    
                    else:
                        print(f'May need to adjust logic in list_all_contents for: {acro}')                    
                    
                else:
                    if name in obj['Key'].lower():
                        list_all_contents.append(obj['Key']) 
                    elif name[:-1] in obj['Key'].lower():
                        list_all_contents.append(obj['Key'])
                    else:
                        print(f'May need to adjust logic in list_all_contents for: {acro}')    
                         
                
        else:
            print("No files found in the specified folder.")
    
        return list_all_contents



    def get_file_name(self, release):
        
        # path_name = self.list_all_contents(release)[0]
        path_name_all = self.list_all_contents(release)
        
        if len(set(path_name_all)) > 1:
            print(path_name_all)
            # input('check it! and adjust logic to pick correct or clean latest folder!') # egt terminals, ggit terminals for ggit lng
            for path in path_name_all:
                if release in path:
                    path_name = f'{path}'
                else:
                    path_name = path_name_all[0]
                    print(f'There are more than 2 so picked first:\n{path_name}')
                
        # if theres more than two and its not EGT then we need to clean latest folder to remove old
        elif len(set(path_name_all)) == 1:
            path_name = f'{path_name_all[0]}'
            print(path_name)
            # input('check it!')
        else:
            input('Might be an issue with path name look into get_file_name plz!')
        # Define the terminal command
        # parquet_file_source_path = 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/latest/'

        # testing_source_path = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/'
        # path_name = 'latest/GEM-GOIT-Oil-NGL-Pipelines-2025-03.geojson' # TODO could rename these month, tracker
        # terminal_cmd = (
        #     f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
        #     f'aws s3 cp s3://$BUCKETEER_BUCKET_NAME/{path_name}/ {testing_source_path} '
        #     f'--endpoint-url https://nyc3.digitaloceanspaces.com --recursive'
        # )

        # # Execute the terminal command to pull down file from digital ocean
        # process = subprocess.run(terminal_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# todo can read file without downloading pd.parquet
# can set up public notebook if can read w/o local access 

        # # Print the output and errors (if any)
        # print(process.stdout.decode('utf-8'))
        # if process.stderr:
        #     print(process.stderr.decode('utf-8'))

        # path_name = path_name.split('latest/')[1] # TODO maybe reinstate this to have latest
        # file = f'{testing_source_path}{path_name}'

        return path_name
    

    

    def create_df(self):
        # print(tabs)
        dfs = []
        
        if self.name == 'Iron & Steel':

            for tab in self.tabs:
                gsheets = gspread_creds.open_by_key(self.key)
                spreadsheet = gsheets.worksheet(tab)
                df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                df['tab-type'] = tab
                dfs += [df]

            df = pd.concat(dfs).reset_index(drop=True)
            print(df.info())

        else:
            for tab in self.tabs:
                gsheets = gspread_creds.open_by_key(self.key)
                spreadsheet = gsheets.worksheet(tab)
                df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                dfs += [df]
            df = pd.concat(dfs).reset_index(drop=True)

            print(df.info())
            # input('Check df info plz')

        df.columns = df.columns.str.strip()
        
        return df
    
    
    def create_df_goget(self):
        if 'Production & reserves' in self.tabs:
            for tab in self.tabs:
                print(tab)
                if tab == 'Main data':
                    gsheets = gspread_creds.open_by_key(self.key)
                    spreadsheet = gsheets.worksheet(tab)
                    main_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    print(main_df.info())
                    main_df.columns = main_df.columns.str.strip()

                elif tab == 'Production & reserves':
                    gsheets = gspread_creds.open_by_key(self.key)
                    spreadsheet = gsheets.worksheet(tab)
                    prod_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    print(prod_df.info())
                    prod_df.columns = prod_df.columns.str.strip()

        return main_df, prod_df            

    def create_df_gogpt_eu(self):
        print(f'This is tabs for GOGPT EU: {self.tabs}')
        # TODO test this, if concatted does not work then keep separate
        if 'H2 Proposals at Oil & Gas Plant' in self.tabs: 
            for tab in self.tabs:
                print(f'This is tab: {tab}')
                if tab == 'Oil & Gas Plants':
                    
                    gsheets = gspread_creds.open_by_key(self.key)
                    spreadsheet = gsheets.worksheet(tab)
                    plants_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    plants_df.columns = plants_df.columns.str.strip()
                    plants_df['tracker-acro'] = 'plants'
                else:
                    gsheets = gspread_creds.open_by_key(self.key)
                    spreadsheet = gsheets.worksheet(tab)
                    plants_hy_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    plants_hy_df.columns = plants_hy_df.columns.str.strip()
                    plants_hy_df['tracker-acro'] = 'plants_hy'
                #     df['tab-type'] = tab
                #     dfs += [df]
                # df = pd.concat(dfs).reset_index(drop=True)
        return plants_df, plants_hy_df
    
    
    def set_fuel_filter_eu(self):
        
        if self.name == 'Oil & Gas Extraction':
            df = self.data
            df['fuel-filter'] = 'methane'
            self.data = df
        elif self.name == 'GOGPT EU':
            plants_df, plants_hy_df  = self.data
            plants_hy_df.columns = plants_hy_df.columns.str.lower()
            plants_hy_df.columns = plants_hy_df.columns.str.replace(' ', '-')
            plants_df.columns = plants_df.columns.str.lower()
            plants_df.columns = plants_df.columns.str.replace(' ', '-')
            # df['tab-type'].iloc[0] == 'H2 Proposals at Oil & Gas Plant':
            # if hydrogen in the fuel column then if H2 usage proposed % to see if it's blend or 100% hydrogen
            # df['fuel-filter'] = np.where(df['fuel'].str.lower().str.contains('hydrogen'), df['h2-usage-proposed-%'], 'methane')
            # find all fuels that have hydrogen and [100] in h2-usage-proposed-%
            for row in plants_hy_df.index:
                # if hydrogen in fuel column
                if 'hydrogen' in plants_hy_df.loc[row, 'fuel'].lower():
                    # print(df.loc[row, 'h2-usage-proposed-%'])
                    if plants_hy_df.loc[row, 'h2-usage-proposed-%'] == 100:
                        plants_hy_df.loc[row, 'fuel-filter'] = 'hy'
                    else:
                        plants_hy_df.loc[row, 'fuel-filter'] = 'blend'

            plants_df['fuel-filter'] = 'methane'
            self.data = plants_df, plants_hy_df
            
        # ISSUE no fuel-filter df['fuel-filter'] = np.where((df['fuel'] != 'lng') & (df['fuel'] != 'oil'), 'hy', df['fuel-filter'])
        elif self.acro == 'EGT-term':
            df = self.data
            df['fuel-filter'] = 'methane'
            df.columns = df.columns.str.lower()
            df.columns = df.columns.str.replace(' ', '-')
            df['fuel'] = df['fuel'].str.lower()
            df['fuel-filter'] = np.where((df['fuel'] != 'lng') & (df['fuel'] != 'oil'), 'hy', df['fuel-filter'])
            self.data = df
        elif self.acro == 'EGT-gas':
            df = self.data
            df['fuel-filter'] = 'methane'
            df.columns = df.columns.str.lower()
            df.columns = df.columns.str.replace(' ', '-')
            df['h2%'].fillna('', inplace=True)
            
            for row in df.index:
                if df.loc[row, 'fuel'].lower().strip() == 'hydrogen':
                    # print(df.loc[row, 'h2%']) # h2 does not exist in json or dd so making them all blend
                    # convert the column to a string after filling na
                    df.loc[row, 'h2%'] = str(df.loc[row, 'h2%'])
                    # print(df.loc[row, 'h2%']) # h2 does not exist in json or dd so making them all blend
                    if df.loc[row, 'h2%'] == '100.00%':
                        df.loc[row, 'fuel-filter'] = 'hy'
                    elif df.loc[row, 'h2%'] == '':
                        df.loc[row, 'fuel-filter'] = 'hy'
                    else:
                        df.loc[row, 'fuel-filter'] = 'blend'
            self.data = df
        
    
    def set_maturity_eu(self):
        # self.data = maturity(self.data)
        # print(set(self.data['maturity'].to_list()))
        # count of maturity equal none by tracker
        # print(self.trackers[self.trackers['maturity']=='none'][['maturity', 'tracker']].groupby('tracker').count())    
        
        if self.name == 'GOGPT EU':
            plants_df, plants_hy_df = self.data
            plants_df['maturity'] = 'none'
            plants_hy_df['maturity'] = 'none'
            plants_hy_df['maturity'] = np.where((plants_hy_df['status'] == 'Construction') | (plants_hy_df['mou-for-h2-supply?'] == 'Y') | (plants_hy_df['contract-for-h2-supply?'] == 'Y') | (plants_hy_df['financing-for-supply-of-h2?'] == 'Y') | (plants_hy_df['co-located-with-electrolyzer/h2-production-facility?'] == 'Y'), 'y','n')


            self.data = plants_hy_df, plants_df
        else:
            
            df = self.data
                
            df['maturity'] = 'none' # starts as none

            for row in df.index:
                if df.loc[row, 'fuel-filter'] == 'methane':
                    df.loc[row, 'maturity'] = 'none'
                else:
                    
                    if self.name == 'LNG Terminals EU':
                        # if df.loc[row, 'fuel-filter'] == 'methane':
                        #     df.loc[row, 'maturity'] = 'none'
                        # else:
                        df['maturity'] = np.where((df['status'] == 'Construction') | (df['fidstatus'] == 'FID') | (df['altfuelprelimagreement'] == 'yes') | (df['altfuelcallmarketinterest'] == 'yes'), 'y','n')

                    elif self.name == 'Gas Pipelines EU':
                        # if df.loc[row, 'fuel-filter'] != 'methane':
                            # df.loc[row, 'maturity'] = 'none'
                            # break out of this for loop and go to the next row
                            df['maturity'] = np.where((df['status'] == 'Construction') | (df['pci5'] == 'yes') | (df['pci6'] == 'yes'), 'y','n')

            # override any where fuel is methane
            # for row in df.index:
            #     if df.loc[row, 'fuel-filter'] == 'methane':
            #         df.loc[row, 'maturity'] = 'none'
            
            self.data = df
        
                
    def deduplicate_gogpt_eu(self):
        # deduplicate and merge into ONE df
        # also lets make tracker-custom GOGPT
        # not clear if we stillneed this or why there would be duplicates but I had it in there 
        # if self.name == 'GOGPT EU':
        #     self.data.drop_duplicates(subset='id', inplace=True, keep='last') # add logic so it defaults to keeping the gogpt-hy ones over the gogpt ones, so if yes in gogpt data remove
        plants_df, plants_hy_df = self.data
        
        plants_df['tracker-acro'] = 'plants'
        plants_hy_df['tracker-acro'] = 'plants_hy'
        
        list_dfs = []
        for df in [plants_df, plants_hy_df]:
            df['custom-tracker'] = 'GOGPT'
             
            df = df.reset_index()
            if 'geometry' not in df.columns:
                df = convert_coords_to_point(df)
            df = rename_gdfs(df) # TODO check that the right acro in all config is here for the tabs
            [print(col) for col in df.columns]
            input('CHECK After renaming in deduplciate_gogpt_eu')
            list_dfs.append(df)
        gogpt_eu_df = pd.concat(list_dfs, sort=False, ignore_index=True)
        gogpt_eu_df.reset_index(drop=True, inplace=True)
        print(len(gogpt_eu_df))
        gogpt_eu_df.drop_duplicates(subset='id', inplace=True, keep='last') # add logic so it defaults to keeping the hy one, last because second df in list
    #     # TODO april 21 this is where you dropped off before picking up Fig
        print(len(gogpt_eu_df))
        [print(col) for col in df.columns]
        input('After concat in deduplciate_gogpt_eu')
        print(f'TYPE of GOGPT EU SHOULD BE DF NOW: {type(gogpt_eu_df)}')
        input('IS IT?!REALLY LOOK')
        [print(col) for col in gogpt_eu_df.columns]
        print('Look at cols in it now to see how to rename in rename_and_concat_gdfs for map GOGPT-eu')
        input('CHECK cols for tracker_obj.name == GOGPT EU')
        self.data = gogpt_eu_df

    def find_about_page(self,key):
            # print(f'this is key and tab list in def find_about_page(tracker,key):function:\n{tracker}{key}')
            tracker = self.name 
            wait_time = 10

            gsheets = gspread_creds.open_by_key(key)
                
            # List all sheet names
            sheet_names = [sheet.title for sheet in gsheets.worksheets()]
            # print(f"{tracker} Sheet names:", sheet_names)
            # Access a specific sheet by name
            first_tab = sheet_names[0]
            first_sheet = gsheets.worksheet(first_tab)  # Access the first sheet
            
            last_tab = sheet_names[-1]
            last_sheet = gsheets.worksheet(last_tab)  # Access the last sheet
            tries = 0
            while tries <= 3:
                time.sleep(wait_time)
                try:
                    # print("First sheet name:", sheet.title)
                    if 'About' not in first_sheet.title:
                        # print('Looking for about page in last tab now, first one no.')
                        # handle for goget and ggit, goit who put it in the last tab
                        if 'About' not in last_sheet.title:
                            if 'Copyright' not in last_sheet.title:
                                print('Checked first and last tab, no about page found not even for copyright. Pausing.')
                                input("Press Enter to continue...")
                            else:
                                # print(f'Found about page in last tab: {last_tab}')
                                sheet = last_sheet
                                
                        else:
                            # print(f'Found about page in last tab: {last_tab}')
                            sheet = last_sheet
                            
                    else:
                        # print(f'Found about page in first tab: {first_tab}')
                        sheet = first_sheet
                        
                    
                    data = pd.DataFrame(sheet.get_all_values(combine_merged_cells=True))
                    
                    # for those situations where tracker to be updated is out of date with about file
                    if self.name in trackers_to_update:
                        data = replace_old_date_about_page_reg(data)

                    about_df = data.copy()
                    break
                except HTTPError as e:
                    print(f'This is error: \n{e}')
                    wait_time += 5
                    tries +=1
        
            return about_df

    def create_filtered_geo_fuel_df(self, geo, fuel):
        needed_geo = geo_mapping[geo]
        print(f'length of self.data: {len(self.data)}')
        if self.acro != 'GOGET' and self.acro != 'GOGPT-eu':
            geocollist = self.geocol.split(';')
            print(f'Getting geo: {geo} from col list: {geocollist}')
            if geo != ['global'] or geo != ['']:
                if len(geocollist) > 1:
                    self.data.columns = self.data.columns.str.strip()
                    # print(geocollist)
                    # input('check what geocol list is')
                    print('do multi-column search')
                    # print(self.data)
                    self.data['country_to_check'] = [[] for _ in range(len(self.data))]
                    for row in self.data.index:
                        for col in geocollist:
                            if col in self.data.columns:
                                self.data.at[row, 'country_to_check'] += [self.data.at[row, col]] # issue
                            # elif col.lower() in self.data.columns:
                            #     self.data.at[row, 'country_to_check'] += [self.data.at[row, col.lower()]] # issue
                            else:
                                print(f'{col} geo col not in df for {self.name}')
                                # print(self.data.columns)
                                # for col in self.data.columns:
                                #     print(col)
                                # input('look into it')
                    filtered_df = self.data[self.data['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                    self.data = filtered_df

                else:
                    self.data['country_to_check'] = self.data[self.geocol].apply(lambda x: split_countries(x) if isinstance(x, str) else [])
                    filtered_df = self.data[self.data['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                    self.data = filtered_df

            if fuel != ['none']:
                filtered_df = create_filtered_fuel_df(filtered_df, self)
                self.data = filtered_df
            
            else:
                print(len(self.data))
                input('Check length of df for normal case!')

        # elif self.acro == 'GOGPT-eu':
        #     plants_hy_df, plants_df = self.data # Unpack the tuple
        #     # TODO not needed 
        
        elif self.acro == 'GOGET':
            main, prod = self.data  # Unpack the tuple
            to_merge = []
            # fueldf = None
            for df in [main, prod]:
                df.columns = df.columns.str.strip()
                df['country_to_check'] = df[self.geocol].apply(lambda x: split_countries(x) if isinstance(x, str) else [])
                
                if geo != ['global'] or geo != ['']:
                    print(f'geo not global or empty so filters via needed geo')
                    df = df[df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                if fuel != ['none']:
                    if self.fuelcol in df.columns:
                        fueldf = create_filtered_fuel_df(df, self)
                        to_merge.append(fueldf)
                    else:
                        to_merge.append(df)
                else:
                    to_merge.append(df)
            
            filtered_main = to_merge[0] # if there is a fuel filter this main would already be filtered since its the one with fuelcol
            filtered_prod = to_merge[1]
            if fuel != ['none']:
                # creates list of unit ids only on correct fuel type
                # then filter
                gas_goget_ids = fueldf['Unit ID'].to_list()
                filtered_prod = to_merge[1] # already filtered by fuel because in this case it IS fueldf
                print(f'Yes {fueldf} == {filtered_main}')
                print(len(filtered_main))
                print(len(fueldf))
                # input('check if length the same for fueldf and filtered main in yes fuel option')
                filtered_prod = filtered_prod[filtered_prod['Unit ID'].isin(gas_goget_ids)]
                # main would already be filtered above because it has fuel col so this is filtering prod
                # filtered_main = filtered_main[filtered_main['Unit ID'].isin(gas_goget_ids)]
            
            else:
                print('no fuel filter needed')


            self.data = (filtered_main, filtered_prod)
        elif self.acro == 'GOGPT-eu':
            print('Pass for gogpt eu')
        else:
            print('Nothing should be printed here, length of df is 1 or 2 if its goget tuple')
            input('Check create_filtered_geo_df')


    def clean_num_data(self):
        # clean df
        # print(f'Length of df at clean num data: {len(self.data)}')
        # input('CHECK ITS NOT EMPTY') #working
        missing_coordinate_row = {} 
        acceptable_range = {
            'lat': {'min': -90, 'max': 90},
            'lng': {'min': -180, 'max': 180}
        }
        if isinstance(self.data, pd.DataFrame):  # Ensure self.data is a DataFrame
            self.data = self.data.replace('*', pd.NA).replace('Unknown', pd.NA).replace('--', pd.NA) # remove the oddities for missing capacity
            
            for col in self.data.columns: # handling for all capacity, production, 
                # if pd.api.types.is_numeric_dtype(self.data[col]): # the problem is we know its not always all numeric unfortunatley
                if any(keyword in col for keyword in ['Capacity (MW)', 'Capacity (Mtpa)', 'CapacityBcm/y', 'CapacityBOEd', 'Capacity (MT)', 'Production - Gas', 'Production - Oil']):                    
                    # print(col)
                    try:
                        self.data.fillna('', inplace=True) # cannot apply to geometry column
                        self.data[col] = self.data[col].apply(lambda x: check_and_convert_float(x))
                        self.data[col].fillna('', inplace=True)
                        # Round all cap/prod columns to 4 decimal places
                        self.data[col] = self.data[col].apply(lambda x: round(x, 4) if x != '' else x)
                        # self.data[col].fillna('', inplace=True) #  why do I fill na with '' because it ends up being a string for the map file? is that true? 
                    except TypeError as e:
                        print(f'{e} error for {col} in {self.name}')
                        # input('Check for QC PM report') # so far problem with StartYearEarliest LNG Terminals geo in there
                        
                
                elif 'Year' in col:
                    print(col)
                    # self.data.fillna('', inplace=True) # cannot apply to geometry column
                    try:
                        self.data[col] = self.data[col].apply(lambda x: check_and_convert_int(x))
                        self.data[col].fillna('', inplace=True)
                        # Round all year columns to 0 decimal places
                        self.data[col] = self.data[col].apply(lambda x: round(x, 0) if x != '' else x)    
                    except TypeError as e:
                        print(f'{e} error for {col} in {self.name}')
                        # input('Check for QC PM report') # so far problem with StartYearEarliest LNG Terminals geo in there
                        # CapacityBcm/y in Gas Pipelines CapacityBOEd in Gas Pipelines
                        # CapacityBOEd in Oil Pipelines
                elif 'Latitude' in col:  
                    print(f'At {col}') 
                    self.data['float_col_clean_lat'] = self.data[col].apply(lambda x: check_and_convert_float(x))
                    # and add to missing_coordinate_row
                    # drop row if the coordinate 

                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lat']): 
                            missing_coordinate_row[self.name] = self.data.loc[row]
                            self.data.drop(index=row, inplace=True)
                    
                    # now check if in appropriate range
                    self.data['float_col_clean_lat'] = self.data['float_col_clean_lat'].apply(
                        lambda x: check_in_range(x, acceptable_range['lat']['min'], acceptable_range['lat']['max'])
                    )
                    
                    # add any coordinates out of range to list to drop
                    # drop row if the coordinate is NaN

                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lat']):
                            # print(self.data.loc[row]) 
                            missing_coordinate_row[self.name] = self.data.loc[row]
                            self.data.drop(index=row, inplace=True)
                        else:
                            self.data.loc[row, 'Latitude'] = self.data.loc[row, 'float_col_clean_lat']

                elif 'Longitude' in col:
                    print(f'At {col}')
                    self.data['float_col_clean_lng'] = self.data[col].apply(lambda x: check_and_convert_float(x))
                    # and add to missing_coordinate_row
                    # drop row if the coordinate is NaN

                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lng']): 
                            print(f'Missing coordinate for {self.name}')
                            missing_coordinate_row[self.name] = self.data.loc[row]
                            self.data.drop(index=row, inplace=True)
                            
                    # now check if in appropriate range
                    self.data['float_col_clean_lng'] = self.data['float_col_clean_lng'].apply(
                        lambda x: check_in_range(x, acceptable_range['lng']['min'], acceptable_range['lng']['max'])
                    )
                    # add any coordinates out of range to list to drop
                    # drop row if the coordinate is NaN
                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lng']): 
                            print(self.data.loc[row])
                            missing_coordinate_row[self.name] = self.data.loc[row]
                            self.data.drop(index=row, inplace=True)  
                            
                        else:
                            self.data.loc[row, 'Longitude'] = self.data.loc[row, 'float_col_clean_lng']           

                    print(F"This is missing_coordinate_row: {missing_coordinate_row}")   
                    input('LOOK INTO IT')          
                else:
                    print(f"Skipping non-numeric column: {col}")
        else:
            print("Error: 'self.data' is not a DataFrame.")

    


    def process_goget_reserve_prod_data(self):
        # output is to return df with scott's code adjustments
        # first run process_goget_reserve_prod_data_dd to save for data download
        # split into two dfs

        main, prod = self.data
        # TODO need to implement the below...
        # lower case and str.replace(' ', '-')
        # main.columns = main.columns.str.lower()
        # prod.columns = prod.columns.str.lower()
        # main.columns = main.columns.str.replace(' ', '-')
        # prod.columns = prod.columns.str.replace(' ', '-')
        
        # Convert 'Data year' to integers in the 'production_reserves_df'
        prod['Data year'] = pd.to_numeric(prod['Data year'], errors='coerce').fillna(-1).astype(int)

        # Update for Production - Oil and its year
        main[["Production - Oil", "Production Year - Oil"]] = main.apply(
            lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million bbl/y", prod)),
            axis=1
        )
        # Update for Production - Gas and its year
        main[["Production - Gas", "Production Year - Gas"]] = main.apply(
            lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million m³/y", prod)),
            axis=1
        )

        # Update for Production - Hydrocarbons (unspecified) and its year
        main[["Production - Hydrocarbons (unspecified)", "Production Year - Hydrocarbons (unspecified)"]] = main.apply(
            lambda x: pd.Series(get_most_recent_value_and_year_goget(x["Unit ID"], "production", "million boe/y", prod)),
            axis=1
        )

        # Calculate total reserves and production
        #filtered_main_data_df['Reserves- Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_reserves, axis=1)
        main['Production - Total (Oil, Gas and Hydrocarbons)'] = main.apply(calculate_total_production_goget, axis=1)


        # Convert Discovery Year to String
        main['Discovery year'] = main['Discovery year'].astype(object)

        # Ensure there are no NaN values in the year columns before conversion to avoid errors
        main['Production Year - Oil'].fillna('', inplace=True)
        main['Production Year - Gas'].fillna('', inplace=True)
        main['Production Year - Hydrocarbons (unspecified)'].fillna('', inplace=True)

        main['Production Year - Oil'] = main['Production Year - Oil'].astype(str)
        main['Production Year - Gas'] = main['Production Year - Gas'].astype(str)
        main['Production Year - Hydrocarbons (unspecified)'] = main['Production Year - Hydrocarbons (unspecified)'].astype(str)

        # remove .0 -1.0
        for col in ['Production Year - Oil', 'Production Year - Gas','Production Year - Hydrocarbons (unspecified)']:
            main[col] = main[col].apply(lambda x: x.replace('.0',''))
            main[col] = main[col].apply(lambda x: x.replace('-1','not stated'))

        # Convert to integer first to remove the trailing zero, then to string
        # filtered_main_data_df['Production Year - Oil'] = filtered_main_data_df['Production Year - Oil'].astype(int).astype(str)
        # filtered_main_data_df['Production Year - Gas'] = filtered_main_data_df['Production Year - Gas'].astype(int).astype(str)
        # filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'] = filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'].astype(int).astype(str)

        # Ensure there are no nan in status, this is before renaming so still uppercase
        main['Status'].fillna('', inplace=True)
        
        # Replace "0" with np.nan or a placeholder if you had NaN values initially
        # filtered_main_data_df.replace('0', np.nan, inplace=True)

        # Check the conversion by printing the dtypes again
        # column_data_types = filtered_main_data_df.dtypes
        # print(column_data_types)
        
        # Apply the function to create a new column 'Country List'
        main['Country List'] = main['Country/Area'].apply(get_country_list)
        # print(filtered_main_data_df[['Country List','Country/Area']]) 
        # print(set(filtered_main_data_df['Country List'].to_list()))
        # print(set(filtered_main_data_df['Country/Area'].to_list()))
        # input('Check country list and country/area after apply')   
        
        dropped_filtered_main_data = main.drop(['Government unit ID',  'Basin', 'Concession / block'], axis=1)
        # average_production_total = filtered_main_data_df["Production - Total (Oil, Gas and Hydrocarbons)"].mean()
        # print("Average Production - Total (Oil, Gas and Hydrocarbons):", average_production_total)
        # input('check avg production total seems right, previous was 6.3041')

        # # Create new column for scaling where there is a fill in value based on average when data is not there.
        # dropped_filtered_main_data["Production for Map Scaling"] = np.where(dropped_filtered_main_data["Production - Total (Oil, Gas and Hydrocarbons)"] != 0,
        #                                                             dropped_filtered_main_data["Production - Total (Oil, Gas and Hydrocarbons)"],
        #                                                             average_production_total)

        dropped_production_Wiki_name = create_goget_wiki_name(dropped_filtered_main_data)
        regions_df = gspread_access_file_read_only(region_key, region_tab)
        # print(set(dropped_production_Wiki_name['Country List'].to_list()))
        # print(set(dropped_production_Wiki_name['Country/Area'].to_list()))
        # input('Check country list and country/area before merge') 
        
        # print(regions_df['GEM Standard Country Name'])
        # input('inspect list of GEM standard names')


        dropped_production_Wiki_name = pd.merge(
            dropped_production_Wiki_name,
            regions_df[['GEM Standard Country Name', 'GEM region']],
            left_on='Country/Area',
            right_on='GEM Standard Country Name',
            how='left'
        )

        
        # After the merge, you might have an extra column 'GEM Standard Country Name' which is a duplicate of 'Country'.
        # You can drop this extra column if it's not needed.
        dropped_production_Wiki_name.drop('GEM Standard Country Name', axis=1, inplace=True)
        # print(dropped_production_Wiki_name.head())
        # input('check that it matches Scotts after dropped_production_Wiki_name')
        # print(dropped_production_Wiki_name.dtypes)
        # input('check thosul be objects for all but prod oil prod gas prod hydrocarbons prod total prod for map scaling, lat and lng')
        # drop superfluous columns
        clean_export = dropped_production_Wiki_name.drop(['Unit type'], axis=1) # Fuel type
        
        # Use not centroid but descriptive point
        # Set up DF of Units without locations
        clean_export[['Longitude', 'Latitude']] = clean_export[['Longitude', 'Latitude']].fillna('')
        missing_location_df = clean_export[clean_export['Latitude']=='']
        # Get unique entries from the 'Country/Area' column
        unique_countries_with_missing_locations = missing_location_df['Country/Area'].unique()

        # Display the unique countries
        unique_countries_df = pd.DataFrame(unique_countries_with_missing_locations, columns=['Country/Area'])
        print(unique_countries_df)
        # input('check unique countries that need descriptive points') # TODO actually save this somewhere
        # normally would use descriptive point
        
        centroid_df = gspread_access_file_read_only(centroid_key, centroid_tab) # TODO update this with descriptive point on subregion
        # print(centroid_df.head())
        # input('check centroid df')
        centroid_df.rename(columns={'Latitude':'Latitude-centroid', 'Longitude':'Longitude-centroid'},inplace=True)
        
        clean_export_center = pd.merge(clean_export, centroid_df, how='left', on='Country/Area')

        # Update 'Location accuracy' for filled-in values
        # print(clean_export_center.columns)
        clean_export_center['Location accuracy'] = clean_export_center.apply(lambda row: 'country level only' if pd.isna(row['Latitude']) or pd.isna(row['Longitude']) else row['Location accuracy'], axis=1)

        # mask to check if merge fills in missing coordinates
        empty_coord_mask = clean_export_center[clean_export_center['Latitude']=='']
        print(f'How many missing coords before?: {len(empty_coord_mask)}')
        
        # Fill in missing latitudes and longitudes if lat lng is '' blank string
        clean_export_center[['Latitude', 'Longitude']] = clean_export_center[['Latitude', 'Longitude']].fillna('')
        
        clean_export_center['Latitude'] = clean_export_center.apply(lambda row: row['Latitude-centroid'] if (row['Latitude'] == '') else row['Latitude'], axis=1)
        clean_export_center['Longitude'] = clean_export_center.apply(lambda row: row['Longitude-centroid'] if (row['Longitude'] == '') else row['Longitude'], axis=1)

        #drop centroid fill in columns
        clean_export_center_clean = clean_export_center.drop(['Latitude-centroid', 'Longitude-centroid'], axis=1)
        
        # mask to check if merge fills in missing coordinates
        empty_coord_mask = clean_export_center_clean[clean_export_center_clean['Latitude']=='']
        # print(f'How many missing coords after?: {len(empty_coord_mask)}')
        # input('Check before and after for empty coord logic!')
        
        # Define a dictionary with old column names as keys and new names with units as values
        column_rename_map = {
            'Production - Oil': 'Production - Oil (Million bbl/y)',
            'Production - Gas': 'Production - Gas (Million m³/y)',
            'Production - Total (Oil, Gas and Hydrocarbons)': 'Production - Total (Oil, Gas and Hydrocarbons) (Million boe/y)',
            # Add other columns you wish to rename similarly here
        }
        
        # Set output order, dropping more columns
        desired_column_order = [
            'Unit ID',
            'Fuel type',
            'Wiki name',
            'Status',
            'Country/Area',
            'Country List',
            'Subnational unit (province, state)',
            'GEM region',
            'Latitude',
            'Longitude',
            'Location accuracy',
            'Discovery year',
            'FID Year',
            'Production start year',
            'Operator',
            'Owner',
            'Parent',
            'Project or complex',
            'Production - Oil (Million bbl/y)',
            'Production Year - Oil',
            'Production - Gas (Million m³/y)',
            'Production Year - Gas',
            'Production - Total (Oil, Gas and Hydrocarbons) (Million boe/y)',
            'Wiki URL',
        ]
    

        # Rename the columns
        clean_export_center_clean_rename = clean_export_center_clean.rename(columns=column_rename_map)
        
        # Reorder the columns
        clean_export_center_clean_reorder_rename = clean_export_center_clean_rename[desired_column_order]

        
        self.data = clean_export_center_clean_reorder_rename
    
        
    def transform_to_gdf(self): # This is dropping all geo rows for pipeline data
        
        if isinstance(self.data, tuple):
            print(self.name)
            input('Why is that a tuple up there? GOGET and GOGPT eu should be consolidated by now...')
        else:
            
            if 'latitude' in self.data.columns.str.lower():
                print('latitude in cols')
                print(f'len of df before convert coords: {len(self.data)}')
                gdf = convert_coords_to_point(self.data) 
                print(f'len of gdf after convert coords: {len(gdf)}')


            elif 'WKTFormat' in self.data.columns:
                # print('Latitude not in cols')
                print(f'Using WKTFormat {self.name}')
                # input('check if eu pipelines eventually come up here - if so check the next inputs that they are not empty until "GeoDataFrames have been saved to"')

                # df_map = insert_incomplete_WKTformat_ggit_eu(df_map)
                # if 'WKTFormat' in df.columns:

                gdf = convert_google_to_gdf(self.data) # this drops all empty WKTformat cols
                
                print(f'len of gdf after convert_google_to_gdf: {len(gdf)}')
                input(self.name)

            else:
                print(F'likely already a gdf: {self.name}')
                input(self.name)
                gdf = self.data

        self.data = gdf
        
    def split_goget_ggit(self):
        gdf = self.data
        if self.acro == 'GOGET':
            gdf['tracker_custom'] = 'GOGET-oil'
        elif self.acro == 'GGIT-lng' or self.acro == 'EGT-term':
            if 'facilitytype' in gdf.columns:
                gdf_ggit_missing_units = gdf[gdf['facilitytype']=='']
                print(gdf_ggit_missing_units)
                # input('for PM QC missing facility type for lng')
                gdf = gdf[gdf['facilitytype']!='']
                gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT-import' if row['facilitytype'] == 'Import' else 'GGIT-export', axis=1)        
            elif 'FacilityType' in gdf.columns:
                gdf_ggit_missing_units = gdf[gdf['FacilityType']=='']
                print(gdf_ggit_missing_units)
                # input('for PM QC missing facility type for lng')
                gdf = gdf[gdf['FacilityType']!='']
                gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT-import' if row['FacilityType'] == 'Import' else 'GGIT-export', axis=1)
            else:
                print(f'Look at cols for {self.acro}:')
                for col in gdf.columns:
                    print(col)   
                input('Checkkk it, issues with Facility Type in split_goget_ggit func')                  
        elif self.acro == 'EGT-gas':
            gdf['tracker_custom'] = 'GGIT'
        
        elif self.acro == 'GOGPT-eu':
            gdf['tracker_custom'] = 'GOGPT'
        else:
            gdf['tracker_custom'] = self.acro

        self.data = gdf


    def assign_conversion_factors(self, conversion_df):
        # add column for units 
        # add tracker_custom
        gdf = self.data
        print(f"This is tracker_custom for gdf:\n{gdf['tracker_custom']}")

        if self.acro == 'GOGET': 
            # # # printf'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GOGET-oil':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['conversion_factor'].values[0]

            gdf = gdf.reset_index(drop=True)

            
        elif self.acro == 'GGIT-lng' or self.acro == 'EGT-term':
            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GGIT-export':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-export']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-export']['conversion_factor'].values[0]
                elif gdf.loc[row, 'tracker_custom'] == 'GGIT-import':  
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-import']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-import']['conversion_factor'].values[0]
            gdf = gdf.reset_index(drop=True)

            
        elif self.acro == 'EGT-gas':
            gdf['tracker_custom'] = 'GGIT'
            gdf['original_units'] = conversion_df[conversion_df['tracker']=='GGIT']['original_units'].values[0]
            gdf['conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT']['conversion_factor'].values[0]
            gdf = gdf.reset_index(drop=True)

        elif self.acro == 'GOGPT-eu':
            gdf['tracker_custom'] = 'GOGPT'
            gdf['original_units'] = conversion_df[conversion_df['tracker']=='GOGPT']['original_units'].values[0]
            gdf['conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGPT']['conversion_factor'].values[0]
            gdf = gdf.reset_index(drop=True)
               
        else:

            if len(gdf) > 0:
                gdf = gdf.reset_index(drop=True)
                conversion_df = conversion_df.reset_index(drop=True)
                # print(f'printing this out to troubleshoot no zero: {gdf}')
                print(f'Setting acro as tracker custom: {self.acro} which is needed to look up conversion factor')
                # gdf['tracker_custom'] = self.acro

                gdf['original_units'] = conversion_df[conversion_df['tracker']==self.acro]['original_units'].values[0]
                gdf['conversion_factor'] = conversion_df[conversion_df['tracker']==self.acro]['conversion_factor'].values[0]
            
            else:
                print("gdf is empty!")
                print('maybe a problem with not having tracker as a col?')
                input(f'Prob not good {self.name}')
            
        self.data = gdf








    # def create_filtered_geo_fuel_df(self, needed_geo, fuel):
    #     print(f'length of self.data: {len(self.data)}')
    #     if self.acro != 'GOGET':
    #         if len(self.geocol) > 1:
    #             print('do multi column search')
    #             self.data['country_to_check'] = [[] for _ in range(len(self.data))]
    #             for row in self.data.index:                    
    #                 # add value to list in column country_to_check
    #                 for col in self.geocol:
    #                     # add value to list in column country_to_check
    #                     self.data.at[row, 'country_to_check'] += [self.data.at[row, col]]
                
    #             filtered_df = self.data[self.data['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                
    #             # # do fuel
                
    #             # self.data = filtered_df                    
    #         else:

    #             self.data['country_to_check'] = self.data.apply(lambda row: split_countries(row[self.geocol]), axis=1)

    #             filtered_df = self.data[self.data['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
                
            
    #         # do fuel
    #         if fuel != ['none']:
    #             filtered_df = create_filtered_fuel_df(filtered_df, self)                

    #         self.data = filtered_df
                
    #     elif self.acro == 'GOGET':
    #         main, prod = self.data
    #         # main = self.data[0]
    #         # prod = self.data[1]

    #         to_merge = []
    #         fueldf = 0
    #         for df in [main,prod]:
    #             df.columns = df.columns.str.strip()
    #             df['country_to_check'] = df.apply(lambda row: split_countries(row[self.geocol]), axis=1) # if isinstance(row[self.geocol],str) else []
    #             df = df[df['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
    #             if fuel != ['none']:
    #                 if self.fuelcol in df.columns:
    #                     fueldf = create_filtered_fuel_df(df, self)
    #                     to_merge.append(fueldf)
    #                 else:
    #                     to_merge.append(df)
                        
    #             else:
    #                 to_merge.append(df)
    #         filtered_main = to_merge[0]
    #         if not fueldf:
    #             print('no fuel filter needed')
    #         else:
    #             gas_goget_ids = fueldf['Unit ID'].to_list()
    #             filtered_main = filtered_main[filtered_main['Unit ID'].isin(gas_goget_ids)]
            
    #         filtered_prod = to_merge[1]
    #         filtered_tuple = (filtered_main, filtered_prod)

    #         self.data = filtered_tuple
    #     else:
    #         print('Nothing should be printed here, length of df is 1 or 2 if its goget tuple')
    #         input('Check create_filtered_geo_df')



# Function to check if any item in the row's list is in needed_geo
def check_list(row_list, needed_geo):
    return any(item in needed_geo for item in row_list)

def split_countries(country_str):

    for sep in [';', '-', ',']:
        if sep in country_str:
            return country_str.strip().split(sep)
        return [country_str]
    


def create_filtered_fuel_df(df, self):
    # self.acro, self.fuelcol
    if self.acro == 'GOGET':
        drop_row = []
        print(f'Length of goget before oil drop: {len(df)}')
        for row in df.index:
            if df.loc[row, 'Fuel type'] == 'oil':
                drop_row.append(row)
            
        df.drop(drop_row, inplace=True)        
        print(f'Length of goget after oil drop: {len(df)}')
        # input('Check the above to see if gas only for goget!')
    
    elif self.acro in ['GGIT-eu', 'GGIT', 'EGT-gas']:
        drop_row = []
        print(f'Length of ggit before oil drop: {len(df)}')
        for row in df.index:
            if df.loc[row, 'Fuel'] == 'Oil':
                drop_row.append(row)
            elif df.loc[row, 'Fuel'] == '':
                drop_row.append(row)
        
        df.drop(drop_row, inplace=True)
        print(f'len after gas only filter {self.acro} {len(df)}')

    
    elif self.acro in ['GOGPT']: # GOGPT-eu # if GOGPT-eu does not need to be run on hydrogen tab, also does not need to be run on 'GOGPT-eu' because it was pre filtered for us
        drop_row = []
        
        print(f'Length of {self.acro} before oil drop: {len(df)}')
        for row in df.index:
            fuel_cat_list = df.loc[row, 'Fuel'].split(',')
            new_fuel_cat_list = []
            for fuel in fuel_cat_list:
                fuel = fuel.split(':')[0]
                new_fuel_cat_list.append(fuel)
            
            if len(new_fuel_cat_list) > 1:
                # if all in list is fossil liquids
                if new_fuel_cat_list.count('fossil liquids') == len(new_fuel_cat_list):
                    drop_row.append(row)
                # if just one in there and it is fossil liquids
            elif new_fuel_cat_list == ['fossil liquids']:
                drop_row.append(row)
        
        df.drop(drop_row, inplace=True)
        print(f'len after gas only filter {self.acro} {len(df)}')
                
    
    return df
    
    
    
    
    
    
    # maybe useful for time outs
    
                        # except HttpError as e:
                        # # Handle rate limit error (HTTP status 429)
                        # if e.resp.status == 429:
                        #     print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                        #     time.sleep(delay)
                        #     delay *= 2  # Exponential backoff
                        # else:
                        #     raise e  # Re-raise other errors