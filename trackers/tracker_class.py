from requests import HTTPError
from .all_config import trackers_to_update, geo_mapping, releaseiso, gspread_creds, ggit_geojson, ggit_lng_geojson, region_key, region_tab, centroid_key, centroid_tab
from .helper_functions import replace_old_date_about_page_reg, convert_google_to_gdf, convert_coords_to_point, check_and_convert_float, check_in_range, check_and_convert_int, get_most_recent_value_and_year_goget, calculate_total_production_goget, get_country_list, get_country_list, create_goget_wiki_name,create_goget_wiki_name, gspread_access_file_read_only
import pandas as pd
from numpy import absolute
import json
import subprocess
import geopandas as gpd
import boto3
from trackers.creds import *
import time
import numpy as np

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
                 data = pd.DataFrame(), # will be used for map creation 
                 data_official = pd.DataFrame() # should be for final data downloads removed new columns!
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
        self.data_official = data_official



    def set_data_official(self):
        
  
        if isinstance(self.data, pd.DataFrame):
            df_official = self.data.copy()
        else:
            # raise TypeError("Expected 'df' to be a DataFrame, but got a tuple or other type.")
            main, prod = self.data
            # drop do what ever
            main_official, prod_official = main.copy(), prod.copy()
            df_official = (main_official, prod_official)
        # drop country_to_check columns
        # come back to this TODO saying this column is not in there
        # internal_cols = 'country_to_check'
        # df_official.drop(internal_cols, inplace=True)
        
        self.data_official = df_official
    

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

# todo can read file without downloading pd.parquet
# can set up public notebook if can read w/o local access 

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
        if self.acro != 'GOGET':
            geocollist = self.geocol.split(';')
            if geo != ['global'] or geo != ['']:
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
                
                if geo != ['global'] or geo != ['']:
                    print('Skipping geo filter for internal map')
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


    def clean_num_data(self):
        # clean df
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
                    self.data['float_col_clean_lng'] = self.data[col].apply(lambda x: check_and_convert_float(x))
                    # and add to missing_coordinate_row
                    # drop row if the coordinate is NaN

                    for row in self.data.index:
                        if pd.isna(self.data.loc[row, 'float_col_clean_lng']): 
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

                                     
                else:
                    print(f"Skipping non-numeric column: {col}")

            print("Error: 'self.data' is not a DataFrame.")

    


    def process_goget_reserve_prod_data(self):
        # output is to return df with scott's code adjustments
        # first run process_goget_reserve_prod_data_dd to save for data download
        # split into two dfs

        main, prod = self.data
        
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
    
        
    def transform_to_gdf(self):
            
        if 'Latitude' in self.data.columns:
            print('latitude in cols')
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
        else:
            print(F'likely already a gdf: {self.name}')
            gdf = self.data

        self.data = gdf
        
    def split_goget_ggit(self):
        gdf = self.data
        if self.acro == 'GOGET':
            gdf['tracker_custom'] = 'GOGET-oil'
        elif self.acro == 'GGIT-lng':
  
            gdf_ggit_missing_units = gdf[gdf['FacilityType']=='']
            print(gdf_ggit_missing_units)
            # input('for PM QC missing facility type for lng')
            gdf = gdf[gdf['FacilityType']!='']
            gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT-import' if row['FacilityType'] == 'Import' else 'GGIT-export', axis=1)        
        else:
            gdf['tracker_custom'] = self.acro

        self.data = gdf


    def assign_conversion_factors(self, conversion_df):
        # add column for units 
        # add tracker_custom
        gdf = self.data

        if self.acro == 'GOGET': 
            # # # printf'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GOGET-oil':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['conversion_factor'].values[0]

            gdf = gdf.reset_index(drop=True)

            
        elif self.acro == 'GGIT-lng':
            for row in gdf.index:
                if gdf.loc[row, 'tracker_custom'] == 'GGIT-export':
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-export']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-export']['conversion_factor'].values[0]
                elif gdf.loc[row, 'tracker_custom'] == 'GGIT-import':  
                    gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-import']['original_units'].values[0]
                    gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-import']['conversion_factor'].values[0]
            gdf = gdf.reset_index(drop=True)

            
        elif self.acro == 'GGIT-eu':
            gdf.loc[row, 'tracker_custom'] = 'GGIT'
            gdf['original_units'] = conversion_df[conversion_df['tracker']=='GGIT']['original_units'].values[0]
            gdf['conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT']['conversion_factor'].values[0]
            gdf = gdf.reset_index(drop=True)

            
        else:

            if len(gdf) > 0:
                gdf = gdf.reset_index(drop=True)
                conversion_df = conversion_df.reset_index(drop=True)
                # print(f'printing this out to troubleshoot no zero: {gdf}')
                gdf['tracker_custom'] = self.acro

                gdf['original_units'] = conversion_df[conversion_df['tracker']==self.acro]['original_units'].values[0]
                gdf['conversion_factor'] = conversion_df[conversion_df['tracker']==self.acro]['conversion_factor'].values[0]
            
            else:
                print("gdf is empty!")
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