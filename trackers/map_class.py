

# from pull_down_s3 import get_file_name 
import pandas as pd
import json
import subprocess
import boto3
from .helper_functions import save_to_s3, replace_old_date_about_page_reg, check_for_lists, rebuild_countriesjs, pci_eu_map_read, check_and_convert_float, remove_diacritics, check_rename_keys, fix_status_inferred, conversion_multiply, workaround_table_float_cap, workaround_table_units
from .all_config import client_secret_full_path, gem_path, tracker_to_fullname, tracker_to_legendname, iso_today_date, gas_only_maps, final_cols, renaming_cols_dict, ggit_geojson, ggit_lng_geojson, new_release_date, gspread_creds, africa_countries, asia_countries, europe_countries, latam_countries, full_country_list
import geopandas as gpd
import numpy as np
import gspread

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
                 # TODO 4/5/2025 make a data object to store the concatted one gdf but for now using trackers 
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
        

    def set_fuel_goit(self):
        # Oil, NGL should show up under both type options, Oil and NGL
        # LPG should be renamed to NGL 
        if self.name == 'goit':
            # Update all values in the 'Fuel' column from 'LPG' to 'NGL'
            print('Creating fuel legend for goit')
            print(set(self.trackers['Fuel'].to_list()))
            self.trackers['Fuel'] = self.trackers['Fuel'].replace('LPG', 'NGL')  
        else:
            pass
        
        
    
    def capacity_hide_goget_gcmt(self):

        mapname = self.name
        gdf = self.trackers
        if mapname.lower() in ['gipt']:
            pass
            
        else:
            for row in gdf.index:
                tracker = (gdf.loc[row, 'tracker-acro'])
                #if goget then make capacity table and capacity details empty
                if tracker.upper() == 'GOGET':
                    # input('in goget')
                    gdf.loc[row, 'capacity-table'] = np.nan
                    gdf.loc[row, 'capacity-details'] = ''
                    prod_oil = gdf.loc[row, 'prod_oil']
                    prod_gas = gdf.loc[row, 'prod_gas']
                    prod_oil = check_and_convert_float(prod_oil) 
                    prod_gas = check_and_convert_float(prod_gas)

                elif tracker.upper() == 'GCMT':
                    # input('in gcmt')
                    gdf.loc[row, 'capacity-table'] = np.nan
                    gdf.loc[row, 'capacity-details'] = ''
                    prod_coal = gdf.loc[row, 'prod-coal']                    
                else:
                    gdf.loc[row, 'capacity-table'] = gdf.loc[row, 'capacity']
                    gdf.loc[row, 'capacity-details'] = gdf.loc[row, 'capacity']
        # TODO test if this removes BOED from empty goit capacity details 
        gdf['capacity-details'].fillna('',inplace=True)
        self.trackers = gdf


    def create_search_column(self):
        # this can be one string with or without spaces 
        # this creates a new column for project and project in local language
        # in the column it'll be removed of any diacritics 
        # this allows for quick searching
        # for mapname, one_gdf in cleaned_dict_map_by_one_gdf.items():
        one_gdf = self.trackers

        # print('testing create_search_column with no diacritics for first time')
        col_names = ['plant-name', 'parent(s)', 'owner(s)', 'operator(s)', 'name', 'owner', 'parent']
        for col in col_names:
            if col in one_gdf.columns:
                new_col_name = f'{col}_search'
                one_gdf[new_col_name] = one_gdf[col].apply(lambda x: remove_diacritics(x))
        
        self.trackers = one_gdf           


    
    
    def last_min_fixes(self):
        # do filter out oil
        gdf = self.trackers
        
        # print(f'Check all columns:')
        # for col in gdf.columns:
        #     print(col)
        # input('Is prod gas year there?') # fixed
  
        # handle situation where Guinea-Bissau IS official and ok not to be split into separate countries 
        gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) 
        gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Timor,Leste','Timor-Leste')) 

        gdf['name'].fillna('',inplace=True)
        gdf['name'] = gdf['name'].astype(str)

        # row['url'] if row['url'] != '' else 
        # handles for empty url rows and also non wiki cases SHOULD QC FOR THIS BEFOREHAND!! TO QC
        gdf['wiki-from-name'] = gdf.apply(lambda row: f"https://www.gem.wiki/{row['name'].strip().replace(' ', '_')}", axis=1)

        # need to switch to '' not nan so can use not in
        gdf['url'].fillna('',inplace=True)
        gdf['url'] = gdf.apply(lambda row: row['wiki-from-name'] if 'gem.wiki' not in row['url'] else row['url'], axis=1)
        
        # one last check since this'll ruin the filter logic
        gdf.columns = [col.replace('_', '-') for col in gdf.columns] 
        gdf.columns = [col.replace('  ', ' ') for col in gdf.columns] 
        gdf.columns = [col.replace(' ', '-') for col in gdf.columns] 

        print(f'Check all columns:')
        for col in gdf.columns:
            print(col)
        input('Is fuel-filter there?')

        # translate acronyms to full names for legend and table 
        gdf['tracker-display'] = gdf['tracker-custom'].map(tracker_to_fullname)
        gdf['tracker-legend'] = gdf['tracker-custom'].map(tracker_to_legendname)

        # make sure these are removed, though should have already been removed
        gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('--', ''))
        gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('*', ''))

        # make sure all null geo is removed
        gdf.dropna(subset=['geometry'],inplace=True)

        # make sure all of the units of m are removed for goget and gcmt that has no capacity
        for row in gdf.index:
            if gdf.loc[row, 'capacity'] == '':
                gdf.loc[row, 'units-of-m'] = ''
            elif gdf.loc[row, 'capacity-details'] == '':
                gdf.loc[row, 'units-of-m'] = ''
            elif gdf.loc[row, 'capacity-table'] == np.nan:
                gdf.loc[row, 'units-of-m'] = ''

        # remove the decimal in years, and lingering -1 for goget
        year_cols = ['start-year', 'prod-year-gas', 'prod-year-oil']

        for col in year_cols:
            if col in gdf.columns:
                gdf[col] = gdf[col].apply(lambda x: str(x).split('.')[0])
                gdf[col].replace('-1', 'not stated')
            
        if self.name == 'europe':
            print(self.name)
            gdf = pci_eu_map_read(gdf)
            # TODO april 7th 11:23 pm do we want to uncomment the below? or is it in eu script?
            # gdf = assign_eu_hydrogen_legend(gdf)
            # gdf = gdf[gdf['tracker-acro']!='GGIT']
            # gdf = manual_lng_pci_eu_temp_fix(gdf)
            # gdf = swap_gas_methane(gdf)
        
        self.trackers = gdf



    
    def save_file(self):
        print(f'Saving file for map {self.name}')
        print(f'This is len of gdf {len(self.trackers)}')
        path_for_download_and_map_files = gem_path + self.name + '/compilation_output/'
        path_for_download_and_map_files_af = gem_path + f'{self.name}-energy' + '/compilation_output/'

        # #(input('check if prod-coal is there')
        if self.name in gas_only_maps or self.geo == 'global': # will probably end up making all regional maps all energy I would think
            print(f"Yes {self.name} is in gas only maps so skip 'area2', 'subnat2', 'capacity2'")
            gdf = self.trackers.drop(['count-of-semi', 'multi-country', 'original-units', 'conversion-factor', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1) # 'multi-country', 'original-units', 'conversion-factor', 'cleaned-cap', 'wiki-from-name', 'tracker-legend']
        
        else:
            print(f"No {self.name} is not in gas only maps")
            gdf = self.trackers.drop(['count-of-semi','multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1) #  'multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend']

        print(f'Final cols:\n')
        [print(col) for col in gdf.columns]
        input(f'Final cols above! {self.name}')
        
        # save the file to unique path for africa-energy if africa, else save to map name
        # also saving to testing folder 
        # TODO save to map folder in digital ocean

        
        
        if self.name == 'africa':
            

            gdf.to_file(f'{path_for_download_and_map_files_af}{self.name}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
            gdf.to_csv(f'{path_for_download_and_map_files_af}{self.name}_{iso_today_date}.csv', encoding='utf-8')
            gdf.to_file(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{self.name}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
            gdf.to_csv(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{self.name}_{iso_today_date}.csv', encoding='utf-8')
            
            process = save_to_s3(self, gdf, 'map', path_for_download_and_map_files_af)

            print(process.stdout.decode('utf-8'))
            if process.stderr:
                print(process.stderr.decode('utf-8'))
                        

            newcountriesjs = list(set(gdf['areas'].to_list()))
            rebuild_countriesjs(self.name, newcountriesjs)
            

        else:
            # Check if the dataframe is a GeoDataFrame
            if isinstance(gdf, gpd.GeoDataFrame):
                print('Already a GeoDataFrame!')
            else:
                print(f'Converting to GeoDataFrame for {self.name} ...')
                if 'geometry' not in gdf.columns:
                    raise ValueError("The dataframe does not have a 'geometry' column to convert to GeoDataFrame.")
                gdf = gpd.GeoDataFrame(gdf, geometry=gdf['geometry'])
                gdf.set_crs(epsg=4326, inplace=True)  # Set CRS to EPSG:4326 (WGS 84)  
    
                   
            gdf.to_file(f'{path_for_download_and_map_files}{self.name}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
            gdf.to_file(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{self.name}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')


            gdf.to_csv(f'{path_for_download_and_map_files}{self.name}_{iso_today_date}.csv', encoding='utf-8')
            gdf.to_csv(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{self.name}_{iso_today_date}.csv', encoding='utf-8')


            process = save_to_s3(self, gdf, 'map', path_for_download_and_map_files)

            print(process.stdout.decode('utf-8'))
            if process.stderr:
                print(process.stderr.decode('utf-8'))
                
            newcountriesjs = list(set(gdf['areas'].to_list()))
            rebuild_countriesjs(self.name, newcountriesjs)



    
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

    def set_capacity_conversions(self):
    
    # you could multiply all the capacity/production values in each tracker by the values in column C, 
    # "conversion factor (capacity/production to common energy equivalents, TJ/y)."
    # For this to work, we have to be sure we're using values from each tracker that are standardized
    # to the same units that are stated in this sheet (column B, "original units").

        gdf = self.trackers

        if self.name in gas_only_maps:
            print('no need to handle for hydro having two capacities')
            # continue
        else:
            # first let's get GHPT cap added 
            # # printmapname) # africa
            # # printset(gdf_converted['tracker-acro'].to_list())) # only pipeline
            print(len(gdf))
            if 'capacity2' in gdf.columns:
                ghpt_only = gdf[gdf['capacity2'].notna()]
                print(len(ghpt_only))
                # input('check filterd for hydro') # worked! 
                # ghpt_only = gdf[gdf['tracker-acro']=='GHPT'] # for GGPT we need to re run it to get it 
                # ##(input('check')
                gdf_minus_ghpt = gdf[gdf['capacity2'].isna()]
                for col in ghpt_only.columns:
                    print(col)
                # print(ghpt_only['capacity'])
                ghpt_only['capacity'] = ghpt_only.apply(lambda row: row['capacity'] + row['capacity2'], axis=1) 
                
                # concat them back together now that ghpt capacity is in one col
                gdf = pd.concat([gdf_minus_ghpt, ghpt_only],sort=False).reset_index(drop=True)
        
        
        # create cleaned cap for logic below 
        gdf['cleaned_cap'] = pd.to_numeric(gdf['capacity'], errors='coerce')

        total_counts_trackers = []
        avg_trackers = []

        for tracker in set(gdf['tracker-acro'].to_list()):
            print(f'{tracker}')

            # for singular map will only go through one
            total = len(gdf[gdf['tracker-acro'] == tracker])
            sum = gdf[gdf['tracker-acro'] == tracker]['cleaned_cap'].sum()
            avg = sum / total
            total_pair = (tracker, total)
            total_counts_trackers.append(total_pair)
            avg_pair = (tracker, avg)
            avg_trackers.append(avg_pair)
            
        # assign average capacity to rows missing or na capacity
        for row in gdf.index:
            cap_cleaned = gdf.loc[row, 'cleaned_cap']
            tracker = gdf.loc[row, 'tracker-acro']
            if pd.isna(cap_cleaned):
                for pair in avg_trackers:
                    if pair[0] == tracker:
                        gdf.loc[row, 'cleaned_cap'] = pair[1]
            cap_cleaned = gdf.loc[row, 'cleaned_cap']
            if pd.isna(cap_cleaned):
                input('still na')
    

        pd.options.display.float_format = '{:.0f}'.format
        # gdf_converted['ea_scaling_capacity'] = gdf_converted.apply(lambda row: conversion_equal_area(row), axis=1) # square root(4 * capacity / pi)

        gdf['scaling_capacity'] = gdf.apply(lambda row: conversion_multiply(row), axis=1)
        # must be float for table to sort
        gdf['capacity'] = gdf['capacity'].fillna('') # issue if it's natype so filling in
        gdf['capacity-table'] = gdf.apply(lambda row: pd.Series(workaround_table_float_cap(row, 'capacity')), axis=1)
        gdf['units-of-m'] = gdf.apply(lambda row: pd.Series(workaround_table_units(row)), axis=1)
        # TODO april 7th 3:57 come back to the below
        # gdf_converted['units-of-m'] = gdf_converted.apply(lambda row: '' if 'GOGET' in row['tracker-acro'] else row['units-of-m'], axis=1)

        # below doesn't work cap details was empty all the time
        # gdf_converted = workaround_no_sum_cap_project(gdf_converted) # adds capacity-details for singular maps we can just disregard
        # TODO nov 13 test this I think it now adds all cap for a project and applies the original units to it 
        # gdf_converted['capacity-details-unit'] = gdf_converted.apply(lambda row: workaround_display_cap(row, 'capacity-details'), axis=1)
    
        self.trackers = gdf        
        
    def map_ready_statuses_and_countries(self):
        
        gdf = self.trackers

        gdf['status'] = gdf['status'].fillna('Not Found') # ValueError: Cannot mask with non-boolean array containing NA / NaN values
        gdf['status'] = gdf['status'].replace('', 'Not Found') # ValueError: Cannot mask with non-boolean array containing NA / NaN values
        # print(set(gdf['status'].to_list()))
        gdf_map_ready = fix_status_inferred(gdf)
    
        # Create masks for the 'tracker-acro' conditions
        mask_gcmt = gdf_map_ready['tracker-acro'] == 'GCMT'
        mask_goget = gdf_map_ready['tracker-acro'] == 'GOGET'
        # mask_gbpt = gdf_map_ready['tracker-acro'] == 'GBPT'
    
        # Update 'status' to 'Retired' where both masks are True
        gdf_map_ready['status'].fillna('', inplace=True)
        mask_status_empty = gdf_map_ready['status'] == ''
        
        # Update 'status' to 'Not Found' where both masks are True
        gdf_map_ready.loc[mask_status_empty & mask_gcmt, 'status'] = 'retired'
        gdf_map_ready.loc[mask_status_empty & mask_goget, 'status'] = 'not found'
        gdf_map_ready['status_legend'] = gdf_map_ready.copy()['status'].str.lower().replace({
                    # proposed_plus
                    'proposed': 'proposed_plus',
                    'announced': 'proposed_plus',
                    'discovered': 'proposed_plus',
                    # pre-construction_plus
                    'pre-construction': 'pre-construction_plus',
                    'pre-permit': 'pre-construction_plus',
                    'permitted': 'pre-construction_plus',
                    # construction_plus
                    'construction': 'construction_plus',
                    'in development': 'construction_plus',
                    # mothballed
                    'mothballed': 'mothballed_plus',
                    'idle': 'mothballed_plus',
                    'shut in': 'mothballed_plus',
                    # retired
                    'retired': 'retired_plus',
                    'closed': 'retired_plus',
                    'decommissioned': 'retired_plus',
                    'not found': 'not-found'})

            # Create a mask for rows where 'status' is empty

        gdf_map_ready_no_status = gdf_map_ready.loc[mask_status_empty]

        if len(gdf_map_ready_no_status) > 0:
            input(f'check no status df, will be printed to issues as well: {gdf_map_ready_no_status}')
            gdf_map_ready_no_status.to_csv(f'trackers/issues/no-status-{self.name}_{iso_today_date}.csv')
        
        # make sure all statuses align with no space rule
        gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.strip().replace(' ','-')) # TODO why was this commented out?
        gdf_map_ready['status_legend'] = gdf_map_ready['status_legend'].apply(lambda x: x.strip().replace('_','-'))
        gdf_map_ready['status'] = gdf_map_ready['status'].apply(lambda x: x.lower())
        print(set(gdf_map_ready['status'].to_list()))
        # input('check list of statuses after replace space and _') # worked
        
        print(set(gdf_map_ready['areas'].to_list()))


        
        # check that areas isn't empty
        tracker_sel = gdf_map_ready['tracker-acro'].iloc[0]
        print(f'this is tracker_sel {tracker_sel}')
        # input('check above')
        if tracker_sel == 'GOGET':
            print(gdf_map_ready['areas'])
            # input('check goget areas in map ready countries')
        gdf_map_ready['areas'] = gdf_map_ready['areas'].fillna('')

        empty_areas = gdf_map_ready[gdf_map_ready['areas']=='']
        if len(empty_areas) > 0:
            print(f'Check out which rows are empty for countries for map will also be printed in issues: {self.name}')
            print(empty_areas)
            # #(input('Remove above')
            empty_areas.to_csv(f'trackers/issues/empty-areas-{tracker_sel}{iso_today_date}.csv')

        # this formats subnational area for detail maps
        # we would also want to overwrite the subnat and say nothing ""
        gdf_map_ready['count-of-semi'] = gdf_map_ready.apply(lambda row: row['areas'].strip().split(';'), axis=1) # if len of list is more than 2, then split more than once
        gdf_map_ready['count-of-semi'] = gdf_map_ready.apply(lambda row: row['areas'].strip().split('-'), axis=1) # for goget
        gdf_map_ready['count-of-semi'] = gdf_map_ready.apply(lambda row: row['areas'].strip().split(','), axis=1) # just adding in case

        gdf_map_ready['multi-country'] = gdf_map_ready.apply(lambda row: 't' if len(row['count-of-semi']) > 1 else 'f', axis=1)
        # if t then make areas-display 
        for col in gdf_map_ready.columns:
            print(col)
        gdf_map_ready['subnat'].fillna('', inplace=True)
        
        # if only one country and subnat not empty create the string, otherwise it should just be the country 
        # (which means what for multi country?) we use a mask below to fix it for multi countries
        gdf_map_ready['areas-subnat-sat-display'] = gdf_map_ready.apply(lambda row: f"{row['subnat'].strip().strip('')}, {row['areas'].strip().strip('')}" if row['multi-country'] == 'f' and row['subnat'] != '' else row['areas'].strip(), axis=1) # row['areas'].strip()
        # if more than one country replace the '' with mult countries

        maskt = gdf_map_ready['multi-country']=='t'

        gdf_map_ready.loc[maskt, 'areas-subnat-sat-display'] = 'multiple areas/countries'

        # just need to make sure all countries are separated by a comma and have a comma after last country as well
        # GOGET has a hyphen in countries
        # GOIT has comma separated in countries
        # hydropower has two columns country1 and country2
        # GGIT has comma separated in countries

            
        if self.name in gas_only_maps:
            # handle for gas only maps (meaning no two cols for ghpt), the adding of the semicolon for js script
            print('In gas only area of function map ready statuses and countries')
            gdf_map_ready['areas'] = gdf_map_ready['areas'].fillna('')
            gdf_map_ready['areas'] = gdf_map_ready['areas'].apply(lambda x: x.replace(',', ';')) # try this to fix geojson multiple country issue
            gdf_map_ready['areas'] = gdf_map_ready['areas'].apply(lambda x: f"{x.strip()};")
            print(gdf_map_ready['areas'])
            # input('check above has semicolon')
        
        else: 
            
            # print(gdf_map_ready[['areas', 'tracker-acro', 'name']])
            # print(set(gdf_map_ready['areas'].to_list()))
            # print(set(gdf_map_ready['area2'].to_list()))
            if 'area2' in gdf_map_ready.columns:
                gdf_map_ready['area2'] = gdf_map_ready['area2'].fillna('')
                gdf_map_ready['areas'] = gdf_map_ready['areas'].fillna('')
            
            gdf_map_ready['areas'] = gdf_map_ready['areas'].apply(lambda x: x.replace(',', ';')) # try this to fix geojson multiple country issue
            gdf_map_ready['areas'] = gdf_map_ready['areas'].apply(lambda x: f"{x.strip()};")
            # print(gdf_map_ready['areas'])
            # input('check above has semicolon for non gas only maps')
            # print(set(gdf['areas'].to_list()))
            # print(set(gdf['area2'].to_list()))
            # nan_areas = gdf[gdf['areas']=='']
            # print(f'Nan areas: {len(nan_areas)}')
            # # print(nan_areas)
            # input('check nan areas')
            # issues = []
            # tracker_issues = []
            # for row in gdf.index:
            #     if gdf.loc[row, 'areas'] == '':
            #         issues.append(row)
            #         tracker_issues.append(gdf.loc[row, 'tracker-acro'])
            # # if len(issues) >0 :
            # #     print(f'No areas here for these trackers:')
            # #     print(set(tracker_issues))
            # gdf = gdf.drop(issues)
            # issues_df = {'missing_country': issues}
            # issues_df = pd.DataFrame(issues_df)
            # issues_df.to_csv(f'issues/missing_county{mapname}{iso_today_date}.csv')
            # print('Printed issues_df to file and dropped themf rom the df.')
            
            # # ##(input('All area2s in gdf check if any are numbers')
            # if mapname == 'Global':
            #     gdf['areas'] = f"{gdf['areas']};"
                
            # else:
            #     for row in gdf.index:

            #         if gdf.loc[row, 'area2'] != '':
        
            #             gdf.at[row, 'areas'] = f"{gdf.loc[row, 'areas'].strip()};{gdf.loc[row, 'area2'].strip()};"
            #             # print(f"Found a area2! Hydro? {gdf.loc[row, 'areas']} {gdf.loc[row, 'tracker-acro']} {gdf.loc[row, 'name']}")
            #             print(gdf.loc[row,'areas'])
            #             input('check above is ; ; not ,; mult country')
            #         else:
            #             # make it so all areas even just one end with a semincolon 
            #             gdf['areas'] = gdf['areas'].fillna('')
            #             # nan_areas = gdf[gdf['areas']=='']
            #             # print(f'in else: {set(gdf["areas"].to_list())}') # find the rows that are nan or float
            #             ser = gdf['areas']
            #             try:
            #                 ser_str = ser.astype(str)
            #             except:
            #                 for row in ser.index:
            #                     val = ser.iloc[row]
            #                     try:
            #                         val_str = str(val)
            #                     except:
            #                         print("Error!" + f" val couldn't be converted to str: {val}")
                        
            #             gdf.at[row, 'areas'] = f"{gdf.loc[row, 'areas'].strip()};"

        # grouped_tracker_after = gdf.groupby('tracker-acro', as_index=False)['id'].count()

        self.trackers = gdf_map_ready        
        

    def rename_and_concat_gdfs(self):
        # This function takes a dictionary and renames columns for all dataframes within
        # then it concats by map type all the dataframes
        # so you're left with a dictionary by maptype that holds one concatted dataframe filterd on geo and tracker type needed
        
        renamed_gdfs = []     
        for tracker_obj in self.trackers:
            
            gdf = tracker_obj.data
            tracker_sel = tracker_obj.acro # GOGPT, GGIT, GGIT-lng, GOGET
            print(f'tracker_sel is {tracker_sel} equal to tracker-acro...')
            # print('This is tracker-acro:')
            # print(gdf['tracker-acro'])
            if tracker_sel == 'GOGPT-eu':
                print('passing because GOGPT-eu already renamed when concatted hy and plants tabs')
                # gdf['tracker-acro'] = tracker_sel
                # print(f'What is data in this right now: {type(tracker_obj.data)}')
                # use plants and plants_hy to rename or pass it since its already been renamed
                print(set(gdf['tracker-acro'].to_list()))
                input('This should be two, plants and plants_hy!')
                
            else:
                gdf['tracker-acro'] = tracker_sel
                # if tracker_sel == 'GCTT':
                #     print(gdf)
                #     input('GCTT gdf here')
                print(f"renaming on tracker acro: {gdf['tracker-acro'].iloc[0]}")
                # all_trackers.append(tracker_sel)
                # select the correct renaming dict from config.py based on tracker name
                renaming_dict_sel = renaming_cols_dict[tracker_sel]
                # rename the columns!
                # check check_rename_keys(renaming_dict_sel)
                print(f'Check rename keys against cols for {tracker_sel}')
                check_rename_keys(renaming_dict_sel, gdf)
                gdf.columns = gdf.columns.str.strip()
                gdf = gdf.rename(columns=renaming_dict_sel) 
                
                # print(gdf['areas'].value_counts())
                # ##(input('check value counts for area after rename')
                gdf.reset_index(drop=True, inplace=True)  # Reset index in place
            # check why subnat in there
            if 'subnat' in gdf.columns:
                print(f'subnat here for {tracker_obj.name}')
                
            else:
                print(f'subnat not here for {tracker_obj.name}')
                input('check which tracker')
            print(f'Adding {tracker_sel} gdf to renamed_gdfs')
            renamed_gdfs.append(gdf)
            input('Check it adds for gogpt eu')
            
        one_gdf = pd.concat(renamed_gdfs, sort=False, verify_integrity=True, ignore_index=True) 
        # one_gdf = one_gdf.drop_duplicates('id').reset_index(drop=True)
        print(one_gdf.index)

        cols_to_be_dropped = set(one_gdf.columns) - set(final_cols)
        print(f'These cols will be dropped: {cols_to_be_dropped}')
        # # if slowmo:
            # # ##(input('Pause to check cols before filtering out all cols in our gdf that are not in final cols, there will be a problem if our gdf does not have a col in final_cols.')
        final_gdf = one_gdf.drop(columns=cols_to_be_dropped)
        self.trackers = final_gdf
            
 
    def get_about(self):
        if self.aboutkey != '':
            if self.name in ['africa', 'integrated', 'europe', 'asia', 'latam']:
                # proceed with gspread thing
                gspread_creds = gspread.oauth(
                        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
                        credentials_filename=client_secret_full_path,
                        # authorized_user_filename=json_token_name,
                    )
                print(f'Opening about key for map {self.name}')
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


# def create_abouts(map_obj, source_tab_df):
#     # TODO March 31 yay they are all being written to the file, as expected, at least regionally and gipt
#     # But now we need to make sure we pull the about page in its entirety, use the old method but insert into current first last function
#     # for example goget about is not complete, only some columns were pulled in 

#     # not a truly multi tracker dd, like integrated or regional, ggit (with 2) should be handled there 
#     if len(map_obj.source) <= 2:

#         for tracker in map_obj.source:
#             if tracker == 'Gas Pipelines':
#                 tracker_key = about_page_ggit_goit[tracker]
#             elif tracker == 'LNG Terminals':
#                 tracker_key = about_page_ggit_goit[tracker]
#             elif tracker == 'Oil Pipelines':
#                 tracker_key = about_page_ggit_goit[tracker]
#             # using the same as gas pipelines because about page was identical from last release dec 2023

#             else:
#                 tracker_key = source_tab_df[source_tab_df['official name'] == tracker]['gspread_key'].values[0]
#             about_df = find_about_page(tracker, tracker_key)
#             map_obj.about = about_df
#             # nothing for about_deps
#     else:
#         prev_key = prev_key_dict[map_obj.name]

#         gspread_creds = gspread.oauth(
#                 scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
#                 credentials_filename=client_secret_full_path,
#                 # authorized_user_filename=json_token_name,
#             )
#         wait_time = 30
#         time.sleep(wait_time)
#         gsheets = gspread_creds.open_by_key(prev_key)        
#         sheet_names = [sheet.title for sheet in gsheets.worksheets()]
#         multi_tracker_about_page = sheet_names[0]
#         multi_tracker_about_page = gsheets.worksheet(multi_tracker_about_page) 
#         multi_tracker_about_page = pd.DataFrame(multi_tracker_about_page.get_all_values(combine_merged_cells=True))
#         multi_tracker_about_page = replace_old_date_about_page_reg(multi_tracker_about_page)
        
#         map_obj.about = multi_tracker_about_page
        
#         dep_about_list = []
#         for tracker in map_obj.source:
            
#             if tracker == 'Gas Pipelines':
#                 tracker_key = about_page_ggit_goit[tracker]
#             elif tracker == 'LNG Terminals':
#                 tracker_key = about_page_ggit_goit[tracker]
#             elif tracker == 'Oil Pipelines':
#                 tracker_key = about_page_ggit_goit[tracker]
#             # using the same as gas pipelines because about page was identical from last release dec 2023
#             elif tracker == 'Gas Pipelines EU': 
#                 tracker_key = about_page_ggit_goit['Gas Pipelines']
#             elif tracker == 'LNG Terminals EU':
#                 tracker_key = about_page_ggit_goit['LNG Terminals']
#             elif tracker == 'Oil & Gas Plants EU':
#                 tracker_key = source_tab_df[source_tab_df['official name'] == 'Oil & Gas Plants']['gspread_key'].values[0]
                                        
#             else:
#                 tracker_key = source_tab_df[source_tab_df['official name'] == tracker]['gspread_key'].values[0]
#                 # trying this new function instead of below, messing up for GOGET
#             about_df = find_about_page(tracker, tracker_key)
#             dep_about_list.append(about_df)

#         print(f'Length of about dfs: {len(dep_about_list)}')
#         input('Check length matches 14..')
#         map_obj.dep_abouts = dep_about_list

#     return map_obj
    