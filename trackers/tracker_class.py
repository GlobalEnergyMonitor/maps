from requests import HTTPError
from .all_config import releaseiso, gspread_creds, ggit_geojson, ggit_lng_geojson
import pandas as pd
from numpy import absolute
import json
import subprocess
import geopandas as gpd
import boto3
from trackers.creds import ACCESS_KEY, SECRET_KEY
import time

class TrackerObject:
    def __init__(self,
                 name="",
                 acro="",
                 key="",
                 tabs=[],
                 release="",
                 geocol = [],
                 fuelcol = "",
                 about_key = "",
                 about = pd.DataFrame(),
                 data = pd.DataFrame()
                 ):
        self.name = name
        self.acro = acro
        self.key = key
        self.tabs = tabs
        self.release = release
        self.geocol = geocol
        self.fuelcol = fuelcol
        self.about_key = about_key
        self.about = about
        self.data = data

    def set_df(self):
        # this creates the dataframe for the tracker
        if self.name == 'Oil Pipelines':
            print('handle non_gsheet_data for pulling data from s3 already has coords')
            
            # to get the file names in latest
            goit_geojson_s3 = self.get_file_name(releaseiso)
            
            #assign gdf to data 

            self.data = gpd.read_file(goit_geojson_s3)

            # gdf = add_goit_boedcap_from_baird(gdf)
            # input('successfully created gdf from s3 file') #worked!
            
        elif self.name == 'Gas Pipelines':
            
            #assign gdf to data 

            self.data = gpd.read_file(ggit_geojson)

        elif self.name == 'LNG Terminals':
            #assign gdf to data 

            self.data = gpd.read_file(ggit_lng_geojson)
            
        elif self.name == 'Oil & Gas Extraction':
            df_tuple = self.create_df_goget()
            main = df_tuple[0]
            prod = df_tuple[1]
            # use ids after filter by country and fuel for dd for two tab dd
            print(df_tuple[0].info())
            print(df_tuple[1].info())
            
            #assign df tuple to data 
            self.data = df_tuple # not sure how to handle this, concat? 
            # gdf = gdf[gdf[geocol].apply(lambda x: check_list(x, needed_geo))]

        else:
            #assign df to data 

            df = self.create_df()
            print(df)
            # input('Check df') # works! didn't call the method correctly..
            self.data = df


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
        print(about_df)
        
        self.about = about_df



    def list_all_contents(self, release):
        tracker = self.acro.lower()

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


    def get_file_name(self, release):
        
        path_name = self.list_all_contents(release)[0]
        if path_name:
            print(path_name)
            # input('check it!')
        else:
            input('Might be an issue with path name look into get_file_name plz!')
        # Define the terminal command
        testing_source_path = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/'
        # path_name = 'latest/GEM-GOIT-Oil-NGL-Pipelines-2025-03.geojson' # TODO could rename these month, tracker
        terminal_cmd = (
            f'export BUCKETEER_BUCKET_NAME=publicgemdata && '
            f'aws s3 cp s3://$BUCKETEER_BUCKET_NAME/{path_name}/ {testing_source_path} '
            f'--endpoint-url https://nyc3.digitaloceanspaces.com --recursive'
        )

        # Execute the terminal command to pull down file from digital ocean
        process = subprocess.run(terminal_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Print the output and errors (if any)
        print(process.stdout.decode('utf-8'))
        if process.stderr:
            print(process.stderr.decode('utf-8'))

        path_name = path_name.split('latest/')[1]
        file = f'{testing_source_path}{path_name}'

        return file
    



    def create_df(self):
        # print(tabs)
        dfs = []
        # other logic for goget 
        # if trackers_to_update[0] == 'Oil & Gas Extraction':
        #     for tab in tabs:
        #         # print(tab)
        #         if tab == 'Main data':
        #             gsheets = gspread_creds.open_by_key(key)
        #             spreadsheet = gsheets.worksheet(tab)
        #             main_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
        #             print(main_df.info())
        #         elif tab == 'Production & reserves':
        #             gsheets = gspread_creds.open_by_key(key)
        #             spreadsheet = gsheets.worksheet(tab)
        #             prod_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
        #             print(prod_df.info())
        #     return main_df, prod_df
        
        if self.name == 'Iron & Steel':
            # keytab = key
            # print(keytab)
            # for k,v in keytab.items(): # dict of tuples the tuple being key and tabs 
            #     # print(f'this is key: {k}')
            #     # print(f'this is v: {v}')
            #     tabtype = k
            #     key = v[0]
            #     tabs = v[1]
            #     # Iron & Steel: plant (unit-level not needed anymore)
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


        # df = df.replace('*', pd.NA).replace('--', pd.NA)
        # df.columns = df.columns.str.strip()
        
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
                elif tab == 'Production & reserves':
                    gsheets = gspread_creds.open_by_key(self.key)
                    spreadsheet = gsheets.worksheet(tab)
                    prod_df = pd.DataFrame(spreadsheet.get_all_records(expected_headers=[]))
                    print(prod_df.info())
        return main_df, prod_df            


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
                        
                    
                    data = pd.DataFrame(sheet.get_all_records(expected_headers=[]))
                    about_df = data.copy()
                    break
                except HTTPError as e:
                    print(f'This is error: \n{e}')
                    wait_time += 5
                    tries +=1
        
            return about_df

    def create_filtered_geo_fuel_df(self, needed_geo, fuel):
        print(f'length of self.data: {len(self.data)}')
        if self.acro != 'GOGET':
            geocollist = self.geocol.split(';')
            if len(geocollist) > 1:
                self.data.columns = self.data.columns.str.strip()
                print(geocollist)
                input('check what geocol list is')
                print('do multi-column search')
                # print(self.data)
                self.data['country_to_check'] = [[] for _ in range(len(self.data))]
                for row in self.data.index:
                    for col in geocollist:
                        self.data.at[row, 'country_to_check'] += [self.data.at[row, col]] # issue
                filtered_df = self.data[self.data['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
            else:
                self.data['country_to_check'] = self.data[self.geocol].apply(lambda x: split_countries(x) if isinstance(x, str) else [])
                filtered_df = self.data[self.data['country_to_check'].apply(lambda x: check_list(x, needed_geo))]
            
            if fuel != ['none']:
                filtered_df = create_filtered_fuel_df(filtered_df, self)
            self.data = filtered_df

        elif self.acro == 'GOGET':
            main, prod = self.data  # Unpack the tuple
            to_merge = []
            fueldf = 0
            for df in [main, prod]:
                df.columns = df.columns.str.strip()
                df['country_to_check'] = df[self.geocol].apply(lambda x: split_countries(x) if isinstance(x, str) else [])
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
            if not fueldf:
                print('no fuel filter needed')
            else:
                # creates list of unit ids only on correct fuel type
                # then filter
                gas_goget_ids = fueldf['Unit ID'].to_list()
                filtered_prod = to_merge[1] # already filtered by fuel because in this case it IS fueldf
                print(f'Yes {fueldf} == {filtered_main}')
                print(len(filtered_main))
                print(len(fueldf))
                input('check if length the same for fueldf and filtered main in yes fuel option')
                filtered_prod = filtered_prod[filtered_prod['Unit ID'].isin(gas_goget_ids)]
                # main would already be filtered above because it has fuel col so this is filtering prod
                # filtered_main = filtered_main[filtered_main['Unit ID'].isin(gas_goget_ids)]
            
            self.data = (filtered_main, filtered_prod)
        else:
            print('Nothing should be printed here, length of df is 1 or 2 if its goget tuple')
            input('Check create_filtered_geo_df')


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
        for row in df.index:
            if df.loc[row, 'Fuel type'] == 'oil':
                drop_row.append(row)
            print(f'Length of goget before oil drop: {len(df)}')
            df.drop(drop_row, inplace=True)        
            print(f'Length of goget after oil drop: {len(df)}')
            input('Check the above to see if gas only for goget!')
    
    elif self.acro in ['GGIT-eu', 'GGIT']:
        drop_row = []
        for row in df.index:
            if df.loc[row, 'Fuel'] == 'Oil':
                drop_row.append(row)
            elif df.loc[row, 'Fuel'] == '':
                drop_row.append(row)
        
        df.drop(drop_row, inplace=True)
    
    elif self.acro == 'GOGPT':
        drop_row = []
        for row in df.index:
            fuel_cat_list = df.loc[row, 'Fuel'].split(',')
            new_fuel_cat_list = []
            for fuel in fuel_cat_list:
                fuel = fuel.split(':')[0]
                new_fuel_cat_list.append(fuel)
            
            if len(new_fuel_cat_list) > 1:
                if new_fuel_cat_list.count('fossil liquids') == len(new_fuel_cat_list):
                    drop_row.append(row)
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