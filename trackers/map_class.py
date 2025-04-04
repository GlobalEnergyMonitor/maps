

# from pull_down_s3 import get_file_name 
import pandas as pd
import json
import subprocess
import boto3
from trackers.creds import ACCESS_KEY, SECRET_KEY
from .all_config import ggit_geojson, ggit_lng_geojson, new_release_date, gspread_creds, africa_countries, asia_countries, europe_countries, latam_countries, full_country_list
from numpy import absolute
import geopandas as gpd

class MapObject:
    def __init__(self,
                 name="",
                 source="",
                 geo="", 
                 needed_geo=[], # list of countries with get_needed_geo method
                 fuel="",
                 pm="",
                 trackers=[], # TODO april 1st 3:13 Make this become a list of objects not just data but all tracker info like acro
                 aboutkey = "",
                 about=pd.DataFrame(),
                 ):
        self.name = name
        self.source = source.split(", ")
        self.geo = geo
        self.needed_geo = []
        self.fuel = fuel.split(", ")
        self.pm = pm.split("; ")
        self.trackers = trackers
        self.aboutkey = aboutkey
        self.about = about
    
    
    # def getFilteredSourceData(self, prep_dict, geo_mapping):
    #     # using source attribute which is a list of tracker names per map
    #     # go into source tab
    #     # use the tracker name as look up for the acro, key, tabs, release date
    #     # double check release date
    #     # create df 
    #     needed_geo = geo_mapping[self.geo]
    #     df_list = []
        
    #     # for item in self.source:
    #     #     tracker_source_obj = TrackerObject(
    #     #     key = prep_dict[item]['gspread_key']
    #     #     name = prep_dict[item]['official name'] 
    #     #     )
    #     #     print(f'Processing source item: {item}')
    #     #     key = prep_dict[item]['gspread_key']
    #     #     tabs = prep_dict[item]['gspread_tabs']
    #     #     release = prep_dict[item]['latest release']
    #     #     acro = prep_dict[item]['tracker-acro']
    #     #     geocol = prep_dict[item]['geocol']
    #     #     fuelcol =  prep_dict[item]['fuelcol']
    #         # create object or df 
    #     if item == 'Oil Pipelines':
    #         print('handle non_gsheet_data for pulling data from s3 already has coords')
            
    #         # to get the file names in latest
    #         goit_geojson_s3 = get_file_name('goit', '2025-03')
    #         gdf = gpd.read_file(goit_geojson_s3)
            
    #         # # filter by geo optionally
    #         # gdf = create_filtered_geo_df(gdf, geocol, needed_geo)
            
    #         # # filter by fuel optionally
    #         # if map_obj.fuel != ['none']:
    #         #     gdf = create_filtered_fuel_df(gdf, acro)
            
    #         df_list.append(gdf)
    #     elif item == 'Gas Pipelines':
    #         gdf = gpd.read_file(ggit_geojson)
        
    #         # gdf.info()
    #         # gdf = gdf[gdf[geocol].apply(lambda x: check_list(x, needed_geo))]


    #         # # filter by country 
    #         # gdf = create_filtered_geo_df(gdf, geocol, needed_geo)
    #         # # filter by fuel optionally
    #         # if self.fuel != ['none']:
    #         #     gdf = create_filtered_fuel_df(gdf, acro)
                
    #         df_list.append(gdf)
            
    #     elif item == 'LNG Terminals':
    #         gdf = gpd.read_file(ggit_lng_geojson)
    #         # gdf.info()
    #         # gdf = gdf[gdf[geocol].apply(lambda x: check_list(x, needed_geo))]

    #         # # filter by country 
    #         # gdf = create_filtered_geo_df(gdf, geocol, needed_geo)
    #         # # filter by fuel optionally
    #         # if self.fuel != ['none']:
    #         #     gdf = create_filtered_fuel_df(gdf, acro)
                
    #         df_list.append(gdf)
            
    #     elif item == 'Oil & Gas Extraction':
    #         df_tuple = self.create_df_goget(key, tabs)
    #         main = df_tuple[0]
    #         prod = df_tuple[1]
    #         # use ids after filter by country and fuel for dd for two tab dd
    #         print(df_tuple[0].info())
    #         print(df_tuple[1].info())
    #         # gdf = gdf[gdf[geocol].apply(lambda x: check_list(x, needed_geo))]
            
    #         # to_merge = []
    #         # fueldf = 0
    #         # for df in [main,prod]:
    #         #     # filter by country 
    #         #     df = create_filtered_geo_df(df, geocol, needed_geo)
    #         #     # # filter by fuel optionally
    #         #     if self.fuel != ['none']:
    #         #         # get prod filtered then use ID on merge to filter main
    #         #         if fuelcol in df.columns:
    #         #             fueldf = create_filtered_fuel_df(df, acro, fuelcol)
    #         #             to_merge.append(fueldf)
    #         #         else:
    #         #             to_merge.append(df)
    #         #     else:
    #         #         to_merge.append(df) 
    #         # filtered_main = to_merge[0]
    #         # if not fueldf:
    #         #     # no fuel filter needed so we are good to just print the two tabs in dd
    #         #     # and merge them for map later
    #         #     print('no fuel filter needed')
    #         # else:
    #         #     gas_goget_ids = fueldf['Unit ID '].to_list()
    #         #     filtered_main = filtered_main[filtered_main['Unit ID'].isin(gas_goget_ids)]
            
    #         # filtered_prod = to_merge[1]
    #         # filtered_tuple = (filtered_main, filtered_prod)
                
            
    #         # df_list.append(filtered_tuple)
    #         df_list.append(df_tuple)
            

    #     else:
    #         df = self.create_df(key, tabs)

    #         # # filter by country 
    #         # df = create_filtered_geo_df(df, geocol, needed_geo)
    #         # # filter by fuel optionally

    #         # if self.fuel != ['none']:
    #         #     df = create_filtered_fuel_df(df, acro)                    

            
    #         # df = df[df[geocol].apply(lambda x: check_list(x, needed_geo))]
    #         df_list.append(df)

    #     # as a check 
    #     print(f"DataFrames in df_list for {self.name}:")
    #     # This does not work for goit, did work for ggpt though
    #     for i, df in enumerate(df_list):
    #         try:
    #             print(f"DataFrame {i}: {df.shape}")
    #         except AttributeError:
    #             df_tuple_filt = df
    #             main = df_tuple_filt[0]
    #             prod = df_tuple_filt[1]
    #             print(f"DataFrame {i}main: {main.shape}")
    #             print(f"DataFrame {i}prod: {prod.shape}")
    #         except TypeError as e:
    #             print(f'Fix error for {self.name}: \n{e}')
                
                
    #     # then assign the dataframes to the map data attribute
    #     self.data = df_list

         
    
    # def filter_by_fuel(self):
        
    #     # using fuel attribute, which often times will be none, filter out rows in df
    #     if self.fuel == ['none']:
    #         pass
    #     else:
    #         print(f'filter by fuel: {self.fuel}')
    #         # df = create_filtered_fuel_df(df, acro)                    
            
    # def filter_by_geo(self, geocol):
        
    #     # using geo attribute, find country/area column and use gem list 
    #     # to filter out countries not in map's region
    #     if self.geo == 'global':
    #         pass
    #     else:
    #         print(f'filter by geo: {self.geo}')
            
 
    def get_about(self):
        if self.aboutkey != '':
            if self.name in ['africa', 'integrated', 'europe', 'asia', 'latam']:
                # proceed with gspread thing
                gsheets = gspread_creds.open_by_key(self.aboutkey)  
                sheet_names = [sheet.title for sheet in gsheets.worksheets()]
                multi_tracker_about_page = sheet_names[0]  
                multi_tracker_about_page = gsheets.worksheet(multi_tracker_about_page) 
                multi_tracker_about_page = pd.DataFrame(multi_tracker_about_page.get_all_values())
                multi_tracker_about_page = replace_old_date_about_page_reg(multi_tracker_about_page) 
                self.about = multi_tracker_about_page
                print(self.about)
                
            else:
                print('Double check the map tab in the log, did we add global single tracker about pages here?')
                input('Check')
        else:
            stubbdf = pd.DataFrame({"Note": ["Note to PM, please review this data file, report any issues, and then delete this tab"]})
            self.about = stubbdf
            
        # input('Check about page plz') # worked! 
        

    def get_needed_geo(self):
        geo_mapping = {'africa': africa_countries,
                    'asia': asia_countries,
                    'europe': europe_countries,
                    'latam': latam_countries,
                    'global': full_country_list,
                    '': full_country_list
                    }
        geo = self.geo
        self.needed_geo = geo_mapping[geo]
    
    def create_df_goget(self, key, tabs):
        print(self)
        
    def create_df(self, key, tabs):
        print(self)
        
        
    # def create_filtered_fuel_df(self):
    #     print(self)

        
    # def create_filtered_fuel_df(self):
        
    #     if acro == 'GOGET':

    #         drop_row = []
    #         # print(filtered_df.columns)
    #         # input('Check that Fuel type is in there or fuel')
    #         for row in filtered_df.index:
    #             # if df.loc[row, 'tracker-acro'] == 'GOGET':
    #             # if filtered_df.loc[row, 'Unit ID'] not in list_ids:
    #             #     drop_row.append(row)
                
    #             if filtered_df.loc[row, 'Fuel type'] == 'oil':
    #                 drop_row.append(row)
    #         # drop all rows from df that are goget and not in the gas list ids 
    #         print(f'Length of goget before oil drop: {len(filtered_df)}')
    #         filtered_df.drop(drop_row, inplace=True)        
    #         print(f'Length of goget after oil drop: {len(filtered_df)}')
    #         input('Check the above to see if gas only for goget!')

                
    #         # print(len(ndf)) # 3012 after removing goget 
    #     elif acro in ['GGIT-eu', 'GGIT']:
    #         # filter for hydrogen only, but also gas for pci europe uses this instead of other release
    #         drop_row = []
    #         for row in filtered_df.index:
    #             # if df.loc[row, 'tracker-acro'] == 'GOGPT': # 1751 from 1966 after filter
    #             if filtered_df.loc[row, 'Fuel'] == 'Oil':
    #                 drop_row.append(row)
    #             elif filtered_df.loc[row, 'Fuel'] == '':
    #                 drop_row.append(row)

    #         filtered_df.drop(drop_row, inplace=True)  

                
    #     elif acro == 'GOGPT':
    #         # filter2 = (df['tracker-acro']=='GOGPT') & (df['fuel'].contains('liquid')) #2788
    #         drop_row = []
    #         for row in filtered_df.index:
    #             # if df.loc[row, 'tracker-acro'] == 'GOGPT': # 1751 from 1966 after filter
    #             fuel_cat_list = filtered_df.loc[row, 'Fuel'].split(',')
    #             new_fuel_cat_list = []
    #             for fuel in fuel_cat_list:
    #                 fuel = fuel.split(':')[0]
    #                 new_fuel_cat_list.append(fuel)
                
    #             # for Alcudia does not contain gas, or only contains fossil liquids
                
    #             # fossil liquids: diesel, fossil gas: natural ga...      37.5  operating   
    #             if len(new_fuel_cat_list) > 1:
    #                 if new_fuel_cat_list.count('fossil liquids') == len(new_fuel_cat_list):
    #                         drop_row.append(row)

    #             elif new_fuel_cat_list == ['fossil liquids']:
    #                 drop_row.append(row)
                        
    #         # drop all rows from df that are goget and not in the gas list ids 
    #         filtered_df.drop(drop_row, inplace=True)  
    #         # print(len(ndf)) # should be 2797
    #         print(f'len after gas only filter {acro} {len(filtered_df)}') 
    #         input('check the above')
    #         return filtered_df
        
    
    
    # def create_filtered_geo_df(self):
    #     print(self)
        
def replace_old_date_about_page_reg(df):
    """ Finds a month and replaces it along with the next five characters (a space and year) with the current release date"""

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    # Convert the entire dataframe to string
    df = df.astype(str)
    
    # find month in about_df string
    # multi_tracker_data is df of main about page for regional dd
    # print(f'INFO: {df.info()}')
    # print(f'COLS: {df.columns}')
    # input('Check out what this about page df is')
    # bold the first row
    # find replace the month and year
    # convert df column to string
    for row in df.index:
        for month in months:
            sub = str(month + ' 20')
            year_chars = len(month) + 5
            if sub in df.iloc[row,0]:
                print(f'Row is: {df.iloc[row,0]}')
                # replace the substring in the value (row string)
                index = df.iloc[row,0].find(sub)
                print(index)
                print(df.iloc[row,0][index-1])
                check = df.iloc[row,0][index-1]
                # input('Check if it has ( before')
                if check == '(':
                    pass
                else:
                    end = index + year_chars
                    # input(f'Found a month! at index: {index}')
                    startbit = df.iloc[row,0][:(index)]
                    endbit = df.iloc[row,0][end:]
                    df.iloc[row,0] = startbit + new_release_date.replace('_', ' ') + endbit
                    # df.iloc[row,0] = df.iloc[row,0].replace(sub, new_release_date)
                    print(df.iloc[row,0])
                    # input('Check find replace did the right thing')
                        
    return df






    
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
    