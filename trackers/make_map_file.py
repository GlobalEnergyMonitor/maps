import pandas as pd
# from all_config import *
from .all_config import *
# from helper_functions import *
from .helper_functions import *
from .create_map_objs import create_map_objs
from collections import OrderedDict
from tqdm import tqdm
import subprocess


def make_map(list_of_map_objs):
    """
    Processes a list of map objects by iterating through their trackers, 
    cleaning and preparing data as needed, and returns a modified list of map objects.

    Args:
        list_of_map_objs (list): A list of map objects, each containing trackers with data to process.

    Returns:
        list: A list of processed map objects with updated tracker data.
    """
    list_of_map_objs_mapversion = []
    conversion_df = create_conversion_df(conversion_key, conversion_tab)
    for map_obj in list_of_map_objs:
        
        for tracker_obj in map_obj.trackers:
            # this gets to each df within each map
            # first I should combine goget so we can stop filtering by tuple
            if isinstance(tracker_obj.data, tuple):
                # print(tracker_obj.name)
                # input('check') # passed, only on goget
                print(isinstance(tracker_obj.data, tuple))
                tracker_obj.process_goget_reserve_prod_data()
                print(isinstance(tracker_obj.data, tuple))
                # input('Check if there was a change')
                # clean_capacity and coordinate qc
                # tracker_obj.clean_num_data()
                # tracker_obj.transform_to_gdf()
                    
                            
            # clean_capacity and coordinate qc
            tracker_obj.clean_num_data()
            tracker_obj.transform_to_gdf()
            tracker_obj.split_goget_ggit()
            tracker_obj.assign_conversion_factors(conversion_df)
        
        map_obj.rename_and_concat_gdfs()
        map_obj.set_capacity_conversions()
        map_obj.map_ready_statuses_and_countries()
        map_obj.create_search_column()
        map_obj.capacity_hide_goget_gcmt()
        map_obj.set_fuel_goit()
        map_obj.last_min_fixes()
        map_obj.save_file()
        
    list_of_map_objs_mapversion.append(map_obj) # this will be the map obj with the filtered cleaned concatted one gdf
            
    return list_of_map_objs_mapversion

# # clean coordinat qc
# df_map, issues_coords = coordinate_qc(df) DONE

# # get into gdf format with proper coords for non geojson

# df = clean_capacity(df)
# #                     df = df.replace('*', pd.NA).replace('Unknown', pd.NA).replace('--', pd.NA) DONE
#                     # df = df.fillna('') DONE

# df = semicolon_for_mult_countries_gipt(df)
# df = fix_status_inferred(df)        
# # harmonize_countries(df, countries_dict, test_results_folder) # find countries_dict
# df= rename_cols(df)
# df = remove_missing_coord_rows(df)

# input_to_output(df, output_file)
# df = remove_implied_owner(df)
# df = formatting_checks(df)

# conversion_df = create_conversion_df(conversion_key, conversion_tab)
# cleaned_dict_by_map_one_gdf_with_better_statuses = map_ready_statuses(cleaned_dict_map_by_one_gdf_with_conversions)

# cleaned_dict_by_map_one_gdf_with_better_countries = map_ready_countries(cleaned_dict_by_map_one_gdf_with_better_statuses)

# renamed_one_gdf_by_map_with_search = create_search_column(renamed_one_gdf_by_map)


# df = filter_cols(df,final_cols=['gem-location-id', 'gem-phase-id', 'country/area', 'phase-name', 'project-name', 'project-name-in-local-language-/-script',
#                                 'other-name(s)', 'capacity-(mw)', 'status', 'start-year', 'retired-year', 'location-accuracy',
#                                     'owner', 'lat', 'lng', 'state/province', 'operator', 'technology-type',
#                                 'region', 'url', 'owner-name-in-local-language-/-script', 'operator-name-in-local-language-/-script'         
#                                 ])

# DONE
# def transform_to_gdf(df): 
    
        
#     if 'latitude' in df_map.columns:
#         print('latitude in cols')
#         gdf = convert_coords_to_point(df_map) 
#         print(f'len of gdf after convert coords: {len(gdf)}')
#         # append gdf to list of gdfs for map - though now we can have it as a csv for faster AET non tile load
#         list_gdfs_by_map.append(gdf)
#         # gdf_to_geojson(gdf, f'{path_for_test_results}{mapname}_{tracker}_gdf_{iso_today_date}.geojson')
#         with open(f'local_pkl/{mapname}_{tracker}_gdf_{iso_today_date}.pkl', 'wb') as f:
#             pickle.dump(gdf, f)
#             print(f'File is: {f}')
#             count_of_files += 1

#         print(f"GeoDataFrames have been saved to {path_for_test_results}{mapname}_{tracker}_gdf_{iso_today_date}.pkl")         
#         # if gdf['tracker-acro'].iloc[0] == 'GCTT':
#         #     print(gdf)
#         #     input('This is gctt gdf ... ')
#     elif 'WKTFormat' in df.columns:
#         # print('Latitude not in cols')
#         print(tracker)
#         # input('check if eu pipelines eventually come up here - if so check the next inputs that they are not empty until "GeoDataFrames have been saved to"')

#         # df_map = insert_incomplete_WKTformat_ggit_eu(df_map)
#         # if 'WKTFormat' in df.columns:

#         gdf = convert_google_to_gdf(df_map) # this drops all empty WKTformat cols
        
#         print(f'len of gdf after convert_google_to_gdf: {len(gdf)}')

#         list_gdfs_by_map.append(gdf)
#         return gdf
    
    


# # assign conversion acro


# DONE
# def split_goget_ggit(dict_list_gdfs_by_map):
#     custom_dict_list_gdfs_by_map = {}
    
#     for mapname, list_gdfs in dict_list_gdfs_by_map.items():
#         custom_list_of_gdfs = []
#         # # printf'This is length before: {len(list_gdfs)} for {mapname}')
#         for gdf in list_gdfs:
#             # # # printdf['tracker-acro'])
#             gdf = gdf.reset_index(drop=True)
#             if gdf['tracker-acro'].iloc[0] == 'GOGET':
#                 # # # printgdf.columns)
#                 # oil
#                 gdf = gdf.copy()
#                 # df_goget_missing_units.to_csv('compilation_output/missing_gas_oil_unit_goget.csv')
#                 # gdf['tracker_custom'] = gdf.apply(lambda row: 'GOGET - gas' if row['Production - Gas (Million m³/y)'] != '' else 'GOGET-oil', axis=1)
#                 gdf['tracker_custom'] = 'GOGET-oil'
#                 custom_list_of_gdfs.append(gdf)
                
#             elif gdf['tracker-acro'].iloc[0] == 'GGIT-lng':
#                 gdf_ggit_missing_units = gdf[gdf['FacilityType']=='']
#                 # # printf'GGIT LNG missing units: {gdf_ggit_missing_units}')
#                 # # # ##(input('Pause to check missing units for GGIT LNG important to know how to calculate capacity factor because differs import and export')
#                 # gdf_ggit_missing_units.to_csv('compilation_output/missing_ggit_facility.csv')
#                 gdf = gdf[gdf['FacilityType']!='']
#                 gdf['tracker_custom'] = gdf.apply(lambda row: 'GGIT-import' if row['FacilityType'] == 'Import' else 'GGIT-export', axis=1)
#                 # # # printgdf[['tracker_custom', 'tracker-acro', 'FacilityType']])
#                 custom_list_of_gdfs.append(gdf)

#             else:
#                 gdf['tracker_custom'] = gdf['tracker-acro']
            
#                 custom_list_of_gdfs.append(gdf)
#         custom_dict_list_gdfs_by_map[mapname] = custom_list_of_gdfs
#         # # printf'This is length after: {len(custom_list_of_gdfs)} for {mapname}')
#     # # printcustom_dict_list_gdfs_by_map.keys())
#     # # # ##(input('check that there are enough maps')

#     return custom_dict_list_gdfs_by_map


# # adding conversion factors

#DONE
# def assign_conversion_factors(custom_dict_list_gdfs_by_map, conversion_df):
#     # add column for units 
#     # add tracker_custom
#     # TODO change these because dict not a list now! dict key is map name, value is list of filtered df of gdf
#     # # printcustom_dict_list_gdfs_by_map.keys())
#     # # # ##(input('check enough maps')
#     # # # ##(input('STOP HERE to see if all maps or not')
#     custom_dict_list_gdfs_by_map_with_conversion = {}
#     for mapname, list_of_gdfs in custom_dict_list_gdfs_by_map.items():
#         custom_list_of_gdfs = []
#         # # printmapname)
#         # # # ##(input('check mapname in assign_conversion_factors')
#         for gdf in list_of_gdfs:

#             gdf_initial = gdf.copy()

#             # # printgdf['tracker-acro'].loc[0])
#             # # printgdf['official_name'].loc[0])

#             if gdf['tracker-acro'].iloc[0] == 'GOGET': 
#                 # # # printf'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')

#                 for row in gdf.index:
#                     if gdf.loc[row, 'tracker_custom'] == 'GOGET-oil':
#                         gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['original_units'].values[0]
#                         gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GOGET-oil']['conversion_factor'].values[0]
#                     # elif gdf.loc[row, 'tracker_custom'] == 'GOGET - gas':  
#                     #     gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker-acro']=='GOGET - gas']['original_units'].values[0]
#                     #     gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker-acro']=='GOGET - gas']['conversion_factor'].values[0]
#                 # gdf['tracker-acro'] = 'GOGET' # commenting out not needed
#                 gdf = gdf.reset_index(drop=True)
#                 custom_list_of_gdfs.append(gdf)
                
#             elif gdf['tracker-acro'].iloc[0] == 'GGIT-lng':
#                 # # # printf'We are on tracker: {gdf["tracker"].iloc[0]} length: {len(gdf)}')
#                 for row in gdf.index:
#                     if gdf.loc[row, 'tracker_custom'] == 'GGIT-export':
#                         gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-export']['original_units'].values[0]
#                         gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-export']['conversion_factor'].values[0]
#                     elif gdf.loc[row, 'tracker_custom'] == 'GGIT-import':  
#                         gdf.loc[row, 'original_units'] = conversion_df[conversion_df['tracker']=='GGIT-import']['original_units'].values[0]
#                         gdf.loc[row, 'conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT-import']['conversion_factor'].values[0]
#                 gdf = gdf.reset_index(drop=True)

#                 custom_list_of_gdfs.append(gdf)
                
#             elif gdf['tracker-acro'].iloc[0] == 'GGIT-eu':
#                 gdf.loc[row, 'tracker_custom'] = 'GGIT'
#                 gdf['original_units'] = conversion_df[conversion_df['tracker']=='GGIT']['original_units'].values[0]
#                 gdf['conversion_factor'] = conversion_df[conversion_df['tracker']=='GGIT']['conversion_factor'].values[0]
#                 gdf = gdf.reset_index(drop=True)

#                 custom_list_of_gdfs.append(gdf)  
                
#             else:
#                 # print(f'We are on tracker: {gdf['tracker-acro'].iloc[0]} length: {len(gdf)}')
#                 # This should apply to all rows not just one.
#                 if len(gdf) > 0:
#                     gdf = gdf.reset_index(drop=True)
#                     conversion_df = conversion_df.reset_index(drop=True)
#                     # print(f'printing this out to troubleshoot no zero: {gdf}')
#                     gdf['tracker_custom'] = gdf["tracker-acro"].iloc[0]
#                     tracker = gdf["tracker-acro"].iloc[0]
#                     # print(tracker)
#                     # print(len(gdf))
#                     # print(len(conversion_df))
#                     gdf['original_units'] = conversion_df[conversion_df['tracker']==tracker]['original_units'].values[0]
#                     gdf['conversion_factor'] = conversion_df[conversion_df['tracker']==tracker]['conversion_factor'].values[0]
#                     custom_list_of_gdfs.append(gdf)                
#                 else:
#                     print("gdf is empty!")
                

#         custom_dict_list_gdfs_by_map_with_conversion[mapname] = custom_list_of_gdfs
#     # # printf'This is custom dict: {custom_dict_list_gdfs_by_map_with_conversion}')
#     # # # ##(input('Check it, should have all trackers not just pipes!')
    
#     # # printcustom_dict_list_gdfs_by_map_with_conversion.keys())
#     # # # ##(input('check that there are enough maps')
#     return custom_dict_list_gdfs_by_map_with_conversion



# # rename cols and concat into one df

# DONE at map level!
# def rename_gdfs(custom_dict_list_gdfs_by_map_with_conversion):
#     # This function takes a dictionary and renames columns for all dataframes within
#     # then it concats by map type all the dataframes
#     # so you're left with a dictionary by maptype that holds one concatted dataframe filterd on geo and tracker type needed
#     renamed_one_gdf_by_map = {}
#     # # printcustom_dict_list_gdfs_by_map_with_conversion.keys())
#     # # # ##(input('STOP HERE to see if all maps or not')
#     for mapname, list_of_gdfs in custom_dict_list_gdfs_by_map_with_conversion.items():
        
#         renamed_gdfs = []
#         path_for_test_results = gem_path + mapname + '/test_results/'
#         # # printmapname)
#         # # printlen(list_of_gdfs))
#         # # printgdf['tracker-acro']) for gdf in list_of_gdfs]
#         # # # ##(input('Check if all trackers are there')
#         for gdf in list_of_gdfs:
#             # for col in gdf.columns:
#             #     print(col)
#             # print(gdf.columns)
#             # if 'Countries' in gdf.columns:
#             #     print(gdf['Countries'])
#             # declare which tracker we are at in the list so we can rename columns accordingly
#             tracker_sel = gdf['tracker-acro'].iloc[0] # GOGPT, GGIT, GGIT-lng, GOGET
            
#             # if tracker_sel == 'GCTT':
#             #     print(gdf)
#             #     input('GCTT gdf here')
#             print(f'renaming on tracker: {tracker_sel}')
#             # all_trackers.append(tracker_sel)
#             # select the correct renaming dict from config.py based on tracker name
#             renaming_dict_sel = renaming_cols_dict[tracker_sel]
#             # rename the columns!
#             gdf = gdf.rename(columns=renaming_dict_sel) 
            
#             # print(gdf['areas'].value_counts())
#             # ##(input('check value counts for area after rename')
#             gdf.reset_index(drop=True, inplace=True)  # Reset index in place
#             # print('here are the cols newly renamed ')
#             # for col in gdf.columns:
#             #     print(col)
#             renamed_gdfs.append(gdf)
#             # print(f'This is renamed_gdfs so far {renamed_gdfs}')
#             # #(input('tChek this')


#         # print(f'This is renamed_gdfs after the look {renamed_gdfs}')

    
#         one_gdf = pd.concat(renamed_gdfs, sort=False, verify_integrity=True, ignore_index=True) 
#         # one_gdf = one_gdf.drop_duplicates('id').reset_index(drop=True)
#         # print(one_gdf.index)

#         cols_to_be_dropped = set(one_gdf.columns) - set(final_cols)
#         # # if slowmo:
#             # # ##(input('Pause to check cols before filtering out all cols in our gdf that are not in final cols, there will be a problem if our gdf does not have a col in final_cols.')
#         final_gdf = one_gdf.drop(columns=cols_to_be_dropped)
#         # instead of filtering on a preset list, drop the extra columns using cols_to_be_dropped
#         # final_gdf = one_gdf[final_cols]
        
#         # final_gdf.to_csv(f'{path_for_test_results}renamed_one_df_{iso_today_date}.csv',  encoding="utf-8")
#         renamed_one_gdf_by_map[mapname] = final_gdf 
#         # # print'Going on to next mapname')
#     return renamed_one_gdf_by_map


# # do capacity conversions 


# DONE
# def capacity_conversions(cleaned_dict_map_by_one_gdf): 

# # you could multiply all the capacity/production values in each tracker by the values in column C, 
# # "conversion factor (capacity/production to common energy equivalents, TJ/y)."
# # For this to work, we have to be sure we're using values from each tracker that are standardized
# # to the same units that are stated in this sheet (column B, "original units").

# # need to get nuances for each tracker, it's just GGIT if point then do lng terminal if line then do pipeline
#     cleaned_dict_map_by_one_gdf_with_conversions = {}
#     for mapname, one_gdf in cleaned_dict_map_by_one_gdf.items():
#         gdf_converted = one_gdf.copy()
#         if mapname in gas_only_maps:
#             print('no need to handle for hydro having two capacities')
#             print(gdf_converted.columns)
#             # continue
#         else:
#             # first let's get GHPT cap added 
#             # # printmapname) # africa
#             # # printset(gdf_converted['tracker-acro'].to_list())) # only pipeline
             
#             ghpt_only = gdf_converted[gdf_converted['tracker-acro']=='GHPT'] # for GGPT we need to re run it to get it 
#             print(mapname)
#             # ##(input('check')
#             gdf_converted = gdf_converted[gdf_converted['tracker-acro']!='GHPT']
#             for col in ghpt_only.columns:
#                 print(col)
#             print(ghpt_only['tracker_custom'])
#             print(ghpt_only['capacity'])
#             ghpt_only['capacity'] = ghpt_only.apply(lambda row: row['capacity'] + row['capacity2'], axis=1) 
#             gdf_converted = pd.concat([gdf_converted, ghpt_only],sort=False).reset_index(drop=True)
#         # # # printlen(gdf_converted))
    
#         gdf_converted['cleaned_cap'] = pd.to_numeric(gdf_converted['capacity'], errors='coerce')

#         total_counts_trackers = []
#         avg_trackers = []
#         print(gdf_converted.columns)
#         # print(f"this is all trackers: {set(gdf_converted['tracker-acro'].to_list())}")
        
#         # gdf_converted['tracker-acro'] = gdf_converted['tracker-acro']
#         # # printf"this is all trackers: {set(gdf_converted['tracker-acro'].to_list())}")
        
#         gdf_converted = gdf_converted[gdf_converted['tracker-acro']!=''] # new to filter out nan


#         for tracker in set(gdf_converted['tracker-acro'].to_list()):
#             # for singular map will only go through one
#             total = len(gdf_converted[gdf_converted['tracker-acro'] == tracker])
#             sum = gdf_converted[gdf_converted['tracker-acro'] == tracker]['cleaned_cap'].sum()
#             avg = sum / total
#             total_pair = (tracker, total)
#             total_counts_trackers.append(total_pair)
#             avg_pair = (tracker, avg)
#             avg_trackers.append(avg_pair)
            
#         for row in gdf_converted.index:
#             cap_cleaned = gdf_converted.loc[row, 'cleaned_cap']
#             tracker = gdf_converted.loc[row, 'tracker-acro']
#             if pd.isna(cap_cleaned):
#                 for pair in avg_trackers:
#                     if pair[0] == tracker:
#                         gdf_converted.loc[row, 'cleaned_cap'] = pair[1]
#             cap_cleaned = gdf_converted.loc[row, 'cleaned_cap']
#             # if pd.isna(cap_cleaned):
#                 # print'still na')
#                 # # ##(input('still na')
    

#         pd.options.display.float_format = '{:.0f}'.format
#         # gdf_converted['ea_scaling_capacity'] = gdf_converted.apply(lambda row: conversion_equal_area(row), axis=1) # square root(4 * capacity / pi)

#         gdf_converted['scaling_capacity'] = gdf_converted.apply(lambda row: conversion_multiply(row), axis=1)
#         # must be float for table to sort
#         gdf_converted['capacity-table'] = gdf_converted.apply(lambda row: pd.Series(workaround_table_float_cap(row, 'capacity')), axis=1)
#         gdf_converted['units-of-m'] = gdf_converted.apply(lambda row: pd.Series(workaround_table_units(row)), axis=1)
#         # gdf_converted['units-of-m'] = gdf_converted.apply(lambda row: '' if 'GOGET' in row['tracker-acro'] else row['units-of-m'], axis=1)

#         # below doesn't work cap details was empty all the time
#         # gdf_converted = workaround_no_sum_cap_project(gdf_converted) # adds capacity-details for singular maps we can just disregard
#         # TODO nov 13 test this I think it now adds all cap for a project and applies the original units to it 
#         # gdf_converted['capacity-details-unit'] = gdf_converted.apply(lambda row: workaround_display_cap(row, 'capacity-details'), axis=1)
    
#         cleaned_dict_map_by_one_gdf_with_conversions[mapname] = gdf_converted
    
        
#     # # printcleaned_dict_map_by_one_gdf_with_conversions.keys())
#     # # # ##(input('check that there are enough maps')
#     return cleaned_dict_map_by_one_gdf_with_conversions

# DONE
# # map ready statuses
# DONE
# # map ready areas

# # filter legend cols check

# DONE
# # create owner search col if possible DONE


# # workaround for capacity production edge case

#DONE 
# def workarounds_eg_interim_goget_gcmt(cleaned_dict_by_map_one_gdf_with_better_countries):
#     # this function mostly creates a new col for correctly formatted info when there is multiple countries, especially for the details card 
#     # it also handles oil and gas for goget, TODO should add removal of oil for gas only map maybe? 
#     one_gdf_by_maptype = {}
#     for mapname, gdf in cleaned_dict_by_map_one_gdf_with_better_countries.items():
#         gdf = gdf.copy()

#         list_invalid_goget = []
#         list_invalid_gcmt = []
#         if mapname in ['GIPT', 'Global']:
#             # does not have goget
#             one_gdf_by_maptype[mapname] = gdf 
            
#         else:
#             # # # printgdf.columns)
#             # # # ##(input('Check if prod-oil is there in columns')
#             for row in gdf.index:

#                 tracker = (gdf.loc[row, 'tracker-acro'])
#                 #if goget then make capacity table and capacity details empty
                

#                 if tracker == 'GOGET':
#                     gdf.loc[row, 'capacity-table'] = np.nan
#                     gdf.loc[row, 'capacity-details'] = ''
#                     prod_oil = gdf.loc[row, 'prod_oil']
#                     prod_gas = gdf.loc[row, 'prod_gas']
#                     prod_oil = check_and_convert_float(prod_oil) # NEW TO TEST FOR ROUNDING ALL GETTING CAUGH TIN INVALID GOGET
#                     prod_gas = check_and_convert_float(prod_gas)

#                     # try: # NEW TO DO TEST REMOVING THIS
#                     #     # round it then if either is '' we can remove it later we filter on it before adding to table or details
#                     #     prod_oil = prod_oil.replace(r'[^\d.-]', '', regex=True)
#                     #     prod_oil= prod_oil.replace('', np.nan)
#                     #     prod_oil = prod_oil.astype(float)     
    
#                     #     prod_oil = str(float(round(prod_oil, 2)))

#                     #     gdf.loc[row, 'prod-oil-table'] = f'{prod_oil} million bbl/y'
#                     #     gdf.loc[row, 'prod-oil-details'] = f'{prod_oil} (million bbl/y)'
#                     #     gdf['prod_year_gas'] = gdf['prod_year_gas'].fillna('')
#                     #     gdf['prod_year_oil'] = gdf['prod_year_oil'].fillna('')
#                     #     # # prod oil year an prod gas year replace -1 with not found, this was what Scott had done to replace not stated, once incorporated his code we can see if we can adjust then remove this
#                     #     # not needed in map file because js does filtering to empty stringbut to be consistent
#                     #     gdf['prod_year_gas'] = gdf['prod_year_gas'].apply(lambda x: str(x).replace('-1', '[not found]'))
#                     #     gdf['prod_year_oil'] = gdf['prod_year_oil'].apply(lambda x: str(x).replace('-1', '[not found]'))
                                
#                     # except:
#                     #     list_invalid_goget.append(prod_oil)
#                     #     # # print'invalid goget')
#                     #     # TODO handle these cases and then create a test to confirm it's fixed
                        
                        
#                     # try:
#                     #     prod_gas = prod_gas.replace(r'[^\d.-]', '', regex=True)
#                     #     prod_gas  = prod_gas .replace('', np.nan)

#                     #     prod_gas = str(float(round(prod_gas, 2)))
#                     #     prod_gas  = prod_gas.astype(float)

#                     #     gdf.loc[row, 'prod-gas-table'] = f'{prod_gas} million m³/y'
#                     #     gdf.loc[row, 'prod-gas-details'] = f'{prod_gas} (million m³/y)'
                        
#                     # except:
#                     #     list_invalid_goget.append(prod_gas)

#                     #     # # print'invalid goget')
#                         # TODO handle these cases and then create a test to confirm it's fixed
#                 elif tracker == 'GCMT':
#                     gdf.loc[row, 'capacity-table'] = np.nan
#                     gdf.loc[row, 'capacity-details'] = ''
#                     prod_coal = gdf.loc[row, 'prod-coal']                    
#                 else:
#                     continue
#         one_gdf_by_maptype[mapname] = gdf 
#     # # printone_gdf_by_maptype.keys())
#     return one_gdf_by_maptype


# # make owner search col  DONE
# def create_search_column(dict_of_gdfs):
#     # this can be one string with or without spaces 
#     # this creates a new column for project and project in local language
#     # in the column it'll be removed of any diacritics 
#     # this allows for quick searching
#     #     for mapname, one_gdf in cleaned_dict_map_by_one_gdf.items():
#     dict_of_gdfs_with_search = {}
#     for mapname, one_gdf in dict_of_gdfs.items():

#         # print('testing create_search_column with no diacritics for first time')
#         col_names = ['plant-name', 'parent(s)', 'owner(s)', 'operator(s)', 'name', 'owner', 'parent']
#         for col in col_names:
#             if col in one_gdf.columns:
#                 # print(one_gdf[col].head(10))
#                 new_col_name = f'{col}_search'
#                 one_gdf[new_col_name] = one_gdf[col].apply(lambda x: remove_diacritics(x))
#                 # print(one_gdf[new_col_name].head(10))
        
#         dict_of_gdfs_with_search[mapname] = one_gdf
        
#         # print(dict_of_gdfs_with_search.keys)
#         # print('above are keys in dict_of_gdfs_with_search')
#     return dict_of_gdfs_with_search

    

# # last min fixes.. 

# DONE
# def last_min_fixes(one_gdf_by_maptype):
#     one_gdf_by_maptype_fixed = {}
#     # # printone_gdf_by_maptype.keys())
#     # # # ##(input('check that GIPT is in the above')
#     for mapname, gdf in one_gdf_by_maptype.items():            # do filter out oil
#         gdf = gdf.copy()
#         # # printlen(gdf))
#         # gdf['name'] = gdf['name'].fillna('')
#         # gdf['url'] = gdf['url'].fillna('')
#         # gdf['geometry'] = gdf['geometry'].fillna('')
#         # # printgdf.columns)
#         # TODO for now remove drop to understand why all GOGET empty is now not being filled and also prod doesn't come through
#         # gdf = gdf.drop(['original_units','conversion_factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'Latitude', 'Longitude'], axis=1) # 'cleaned_cap'
#         # handle countries/areas ? 
#         # gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) # reverse this one special case back 
#         # # printf'Missing areas: {gdf[gdf["areas"]==""]}') # check if missing!!   
#         # # # ##(input('Handle missing countries')
#         # handle situation where Guinea-Bissau IS official and ok not to be split into separate countries 
#         gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Guinea,Bissau','Guinea-Bissau')) 
#         gdf['areas'] = gdf['areas'].apply(lambda x: x.replace('Timor,Leste','Timor-Leste')) 
        
#         # something is happening when we concat, we lose goget's name ... 
#         # gdf_empty_name = gdf[gdf['name']=='']
#         # # # printf"This is cols for gdf: {gdf.columns}")
#         gdf['name'].fillna('',inplace=True)
#         gdf['name'] = gdf['name'].astype(str)

#         gdf['wiki-from-name'] = gdf.apply(lambda row: f"https://www.gem.wiki/{row['name'].strip().replace(' ', '_')}", axis=1)
#         # row['url'] if row['url'] != '' else 
#         # handles for empty url rows and also non wiki cases SHOULD QC FOR THIS BEFOREHAND!! TO QC
#         # need to switch to '' not nan so can use not in
#         gdf['url'].fillna('',inplace=True)
#         gdf['url'] = gdf.apply(lambda row: row['wiki-from-name'] if 'gem.wiki' not in row['url'] else row['url'], axis=1)
        
#         # gdf['name'] = gdf.apply(lambda row: row['name'] if row['name'] != '' else row['url'].split('www.gem.wiki/')[1].replace('_', ' '))

#         # gdf_empty_url = gdf[gdf['url'] == '']

#         # assign Africa to all regions
#         # gdf['region'] = 'Africa'
#         # list_of_needed_geo_countries = needed_geo_for_region_assignment[mapname][1]
#         # # printlist_of_needed_geo_countries)
#         # DO WE WANT THIS FOR SOME REASON? probalby not for the cross-continental ones...
#         # # # ##(input('Check this is a list of countries, otherwise may need to adjust how we access the 2nd value of the dictionary') # if it is then we can assign a region based off of it
#         # if 'Brazil' in list_of_needed_geo_countries:
#         #     gdf['region'] = 'Americas'
#         # elif 'China' in list_of_needed_geo_countries:
#         #     gdf['region'] = 'Asia'
#         # elif 'Mozambique' in list_of_needed_geo_countries:
#         #     gdf['region'] = 'Africa'
#         # elif 'United Kingdom' in list_of_needed_geo_countries:
#         #     gdf['region'] = 'Europe'
#         # else:
#         #     gdf['region'] = ''
#             # # printf'No region found for gdf: {gdf["tracker"].iloc[0]} for map: {mapname}')
            
#         # print(gdf.columns)

#         gdf.columns = [col.replace('_', '-') for col in gdf.columns] 
#         gdf.columns = [col.replace('  ', ' ') for col in gdf.columns] 
#         gdf.columns = [col.replace(' ', '-') for col in gdf.columns] 

#         # print(gdf.columns)
#         # ##(input('check cols')
#         # gdf['tracker-acro'] = gdf['tracker-acro']   
#         # let's also look into empty url, by tracker I can assign a filler
        
#         # gdf['url'] = gdf['url'].apply(lambda row: row[filler_url] if row['url'] == '' else row['url'])
        
#         # gdf['capacity'] = gdf['capacity'].apply(lambda x: x.replace('--', '')) # can't do that ... 
        
#         # translate acronyms to full names 
        
#         gdf['tracker-display'] = gdf['tracker-custom'].map(tracker_to_fullname)
#         gdf['tracker-legend'] = gdf['tracker-custom'].map(tracker_to_legendname)
#         # # # printset(gdf['tracker-display'].to_list()))
#         # # # printf'Figure out capacity dtype: {gdf.dtypes}')
#         gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('--', ''))
#         gdf['capacity'] = gdf['capacity'].apply(lambda x: str(x).replace('*', ''))

#         gdf.dropna(subset=['geometry'],inplace=True)
#         # gdf['capacity'] = gdf['capacity'].fillna('')
#         # gdf['capacity'] = gdf['capacity'].apply(lambda x: x.replace('', pd.NA))
#         # gdf['capacity'] = gdf['capacity'].astype(float) # Stuck with concatting like strings for now? ValueError: could not convert string to float: ''
#                 # remove units-of-m if no capacity value ... goget in particular
#         for row in gdf.index:
#           if gdf.loc[row, 'capacity'] == '':
#               gdf.loc[row, 'units-of-m'] = ''
#           elif gdf.loc[row, 'capacity-details'] == '':
#               gdf.loc[row, 'units-of-m'] = ''
#           elif gdf.loc[row, 'capacity-table'] == np.nan:
#               gdf.loc[row, 'units-of-m'] = ''

#         year_cols = ['start-year', 'prod-year-gas', 'prod-year-oil']

#         for col in year_cols:
#             gdf[col] = gdf[col].apply(lambda x: str(x).split('.')[0])
#             gdf[col].replace('-1', 'not stated')
#         # TODO add check that year isn't a -1 ... goget.. for egt
        
#         if mapname == 'europe':
#             print(mapname)
#             gdf = pci_eu_map_read(gdf)
#             # gdf = assign_eu_hydrogen_legend(gdf)
#             # gdf = gdf[gdf['tracker-acro']!='GGIT']
#             # gdf = manual_lng_pci_eu_temp_fix(gdf)
#             # gdf = swap_gas_methane(gdf)
        
#         one_gdf_by_maptype_fixed[mapname] = gdf
#     # # printone_gdf_by_maptype_fixed.keys())
#     return one_gdf_by_maptype_fixed



# # make map file!


# def create_map_file(one_gdf_by_maptype_fixed):
#     final_dict_gdfs = {}
#     # # printone_gdf_by_maptype_fixed.keys())
#     # # # ##(input('STOP HERE - why only one map being printed??')

#     for mapname, gdf in one_gdf_by_maptype_fixed.items():
#         print(mapname)
#         print(f'Saving file for map {mapname}')
#         print(f'This is len of gdf {len(gdf)}')
#         path_for_download_and_map_files = gem_path + mapname + '/compilation_output/'
#         path_for_download_and_map_files_af = gem_path + f'{mapname}-energy' + '/compilation_output/'
#         # # printf'We are on map: {mapname} there are {len(one_gdf_by_maptype_fixed)} total maps')
#         # # printf"This is cols for gdf: {gdf.columns}")
#         # # # ##(input('STOP HERE')
#         # drop columns we don't need because has a list in it and that csuses issues when printing to files
#         # if 'count_of_semi' in gdf.columns.to_list(): # TODO THIS should be in all ggit trackers so odd that it didnt' get pinged
#         #     gdf = gdf.drop(['count_of_semi', 'multi-country', 'original-units', 'conversion-factor', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1)
#         print(gdf.columns)
#         # #(input('check if prod-coal is there')
#         if mapname in gas_only_maps: # will probably end up making all regional maps all energy I would think
#             gdf = gdf.drop(['count-of-semi', 'multi-country', 'original-units', 'conversion-factor', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1) # 'multi-country', 'original-units', 'conversion-factor', 'cleaned-cap', 'wiki-from-name', 'tracker-legend']
        
#         else:
#             gdf = gdf.drop(['count-of-semi','multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend'], axis=1) #  'multi-country', 'original-units', 'conversion-factor', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2', 'cleaned-cap', 'wiki-from-name', 'tracker-legend']

#         # # # printgdf.info())
#         check_for_lists(gdf)
#         # # if slowmo:
#             # # ##(input('Check what is a list')
#         if mapname == 'africa':
#             gdf.to_file(f'{path_for_download_and_map_files_af}{mapname}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
#             gdf.to_excel(f'{path_for_download_and_map_files_af}{mapname}_{iso_today_date}.xlsx', index=False)
#             gdf.to_file(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{mapname}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
#             gdf.to_excel(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{mapname}_{iso_today_date}.xlsx', index=False)
            
#             newcountriesjs = set(gdf['areas'].to_list())
#             rebuild_countriesjs(mapname, newcountriesjs)
            

#         else:
#             gdf.to_file(f'{path_for_download_and_map_files}{mapname}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
#             gdf.to_file(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{mapname}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
#             # if mapname == 'africa':
#             #     gdf.to_file(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/africa-energy/c/{mapname}_{iso_today_date}.geojson', driver='GeoJSON', encoding='utf-8')
#             # gdf_to_geojson(gdf, f'{path_for_download_and_map_files}{geojson_file_of_all_africa}')
#             # # printf'Saved map geojson file to {path_for_download_and_map_files}{mapname}_{iso_today_date}.geojson')

#             gdf.to_excel(f'{path_for_download_and_map_files}{mapname}_{iso_today_date}.xlsx', index=False)
#             gdf.to_excel(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{mapname}_{iso_today_date}.xlsx', index=False)
#             newcountriesjs = set(gdf['areas'].to_list())
#             rebuild_countriesjs(mapname, newcountriesjs)
            
#         # if mapname == 'africa':
#         #     gdf.to_excel(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/africa-energy/compilation_output/{mapname}_{iso_today_date}.xlsx', index=False)
#         # # printf'Saved xlsx version just in case to {path_for_download_and_map_files}{mapname}_{iso_today_date}.xlsx')
#         final_dict_gdfs[mapname] = gdf
#     # print(final_dict_gdfs.keys())
#     return final_dict_gdfs




# def capacity_conversion_check(dict_holding_sdfs):
#     print('Starting the check for major capacity conversion mistakes! Pipelines and GOGET most susceptible.')
#     issues = []
#     for value_list in dict_holding_sdfs.values():
#         for df in value_list:
#             tracker = df['tracker-acro'].iloc[0]
#             # print(f"Tracker: {tracker}")

#             # print(df.head()) #lng
#             total_len = len(df)
#             # print(total_len)
#             df.columns = df.columns.str.strip()
#             # print(df.columns) # non lng

#             # rename columns why did this not get caught? GNPT only one?
#             # df.rename(columns={'capacity (mw)': 'capacity'}, inplace=True)
#             # input(f'check df cols for {tracker}')
#             # Create a dictionary to store the total capacity per country
#             try:
#                 # Convert all values in the 'capacity' column to numeric, making non-numeric values NaN
#                 df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
                
#                 # Create a dictionary to store the total capacity per country
#                 country_cap_tot_dict = df.groupby('areas')['capacity'].sum().to_dict()
#                 # print(f'This is coutnry cap tot for this tracker: {tracker}: {country_cap_tot_dict}')
#                 # Save the country_cap_tot_dict to a CSV file
#                 country_cap_tot_df = pd.DataFrame(list(country_cap_tot_dict.items()), columns=['Country', 'Total Capacity'])
#                 country_cap_tot_df.to_csv(f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/country_cap_tot {tracker} {iso_today_date}.csv', index=False)
#                 # input('check out the cap tot for country')
#             except TypeError as e:
#                 print(e)
#                 print(df['capacity'])
#                 # For rows in df, if capacity is a string, add to a set and return it.
#                 invalid_capacity_values = set(df['capacity'].apply(lambda x: x if isinstance(x, str) else None).dropna())
#                 print(f"Invalid capacity values: {invalid_capacity_values}")
#                 input('Check this error please')
#                 issues.append((tracker, f'Error with capacity column turning it into a numeric to get the total country cap value. {invalid_capacity_values}'))
#             # Add a new column to the dataframe to show the total capacity per country
#             df['country_total'] = df['areas'].map(country_cap_tot_dict)

#             for row in df.index:
#                 try:
#                     try:
#                         capacity_val = df.loc[row, 'capacity']
#                         country = df.loc[row, 'areas']
#                         country_total = df.loc[row, 'country_total']

#                         if isinstance(capacity_val, str):
#                             capacity_val = capacity_val.replace(',', '')
#                             capacity_val = capacity_val.replace(' ', '')
#                             capacity_val = capacity_val.replace('', '0') 
#                             capacity_val = float(capacity_val)                      

#                         # Print out issues if any capacity value is greater than the total capacity of the country

#                         if capacity_val > country_total:
#                             issues.append((row, f'Capacity value {capacity_val} exceeds total capacity {country_total} for country {df.loc[row, "areas"]}'))
#                             input('YIKES CHECK THIS')


#                     except KeyError:
#                         print(f"Capacity column not found for tracker {tracker}")
#                         print(f'Not seeing cap or cap MW here')
#                         input(f'Check columns: {df.columns}')
#                 except ValueError as e:
#                     issues.append((row, f'Error with capacity column not being a float or int: {e}'))
#                     df.drop(row, inplace=True)
#                 except TypeError as e:
#                     issues.append((row, f'Error with capacity column not being a float or int: {e}'))
#                     df.drop(row, inplace=True)
     
#     # input('Check this while we iterate on creating the test capacity_conversion_check')
#     return dict_holding_sdfs



# def mis_cols(d):
#     # result is a file if not empty sep by tabs for cols and tracker
#     missing_cols_check = ['Latitude', 'Longitude', 'status', 'url', 'areas', 'capacity', 'name', 'id'] 
#     misformatted = {}
#     missing = {}

#     filename = f'issues/pre-check-results-{iso_today_date}.xlsx'
#     with pd.ExcelWriter(filename, engine='openpyxl') as writer: 
        
#         for value_list in d.values():
#             for df in value_list:
#                 tracker = df['tracker-acro'].iloc[0]
#                 print(df['tracker-acro'].iloc[0])
#                 df['error messages'] = ''
#                 print('numeric col check')
#                 for col in ['Latitude', 'Longitude', 'capacity', 'prod-coal', 'prod_oil', 'prod_gas', 'start_year']: # 'areas', 'geometry', 'route'
#                     df[col] = df[col].to_numeric(df[col], errors='coerce')

#                     # print(col)
#                     if col in df.columns:
#                         ser = df[col].replace('', np.nan)
#                         try:
#                             ser_float = ser.astype(float)
#                         except:
#                             for row in ser.index:
#                                 val = ser.iloc[row]
#                                 try:
#                                     val_float = float(val)
#                                 except:
#                                     # print("Error!" + f" val couldn't be converted to float: {val}")
#                                     df.iloc[row, 'error messages'] += "Error!" + f" In col {col}, val couldn't be converted to float: '{val}'; "         
#                         df['error messages'] = df['error messages'].fillna('')
#                         if len(set(df['error messages'].to_list())) > 1:
#                             # more than 1 because if all are emtpy strings then it'd have a value of 1
                            
#                             df_misformatted = df[df['error messages']!='']
                            
#                             misformatted[f'{tracker}-{col}'] = df_misformatted
                            
#                             df_misformatted = df_misformatted.map(remove_illegal_characters)

#                             # TODO check thisremove_illegal_charactersremove_illegal_characters
#                             df_misformatted.to_excel(writer, sheet_name=f'{tracker}-{col}-misformatted', index=False)

                
#             print('do we want to write misformatted to a file orjust missing?')                   
            
#             for col in missing_cols_check:
#                 # print('check for missing crucial map data')
#                 # print(col)
#                 if col in df.columns:
#                     print(f"Data type of column '{col}': {df[col].dtype}")
#                     print(f"Number of missing values in column '{col}': {df[col].isna().sum()}")                
#                     print(len(df))
#                     df_missing_nan = df.loc[df[col].isna()]
#                     print(len(df_missing_nan))
#                     df_missing_blank = df[df[col]=='']
#                     df_missing = pd.concat([df_missing_nan, df_missing_blank], axis=0)
#                     df_missing = df_missing.drop_duplicates(subset=['id'])
#                     if len(df_missing) > 0:
#                         missing[f'{tracker}-{col}'] = df_missing
#                         df_missing.to_excel(writer, sheet_name=f'{tracker}-{col}-missing', index=False)

# def check_pipeline_capacity_conversions(d):
#     # from maisie 100 million barrels of oil per day
#     # from baird https://docs.google.com/spreadsheets/d/1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek/edit?gid=893060859#gid=893060859
#     filename = f'issues/check_pipeline_capacity_conversions-{iso_today_date}.xlsx'
#     with pd.ExcelWriter(filename, engine='openpyxl') as writer:
#         for value_list in d.values():
#             for df in value_list:
#                 df['error messages'] = ''

#                 tracker = df['tracker-acro'].iloc[0]
#                 print(tracker)
#                 if tracker in ['GOIT', 'GGIT', 'GGIT-eu']:
#                     print('This is a pipelines dataset! Let us check the capacity columns:')
#                     if tracker == 'GOIT':
#                         for row in df.index:
#                             # find value of capacity col and check if more than 100m
#                             capacityboed = df.loc[row, 'capacity']
#                             if capacityboed > 100_000_000:
#                                 print(f"Capacity {capacityboed:.1e} exceeds 100 million more than overall oil production")
#                                 input('ISSUE on capacityboed')
#                                 df.at[row, 'error messages'] += "Error!" + f" Capacity {capacityboed:.1e} exceeds 100 million more than overall oil production; "         
                            
#                     elif tracker in ['GGIT', 'GGIT-eu']:
#                     # 549 bcm Billion cubic meters (bcm)
#                         for row in df.index:
#                             capacitybcmy = df.loc[row, 'capacity']
#                             if capacitybcmy > 549:
#                                 print(f"Capacity {capacitybcmy:.1e} exceeds 549 bcm/y more than overall lng production")
#                                 input('ISSUE on capacitybcmy')                            
#                                 df.at[row, 'error messages'] += "Error!" + f" Capacity {capacitybcmy:.1e} exceeds 549 bcm/y more than overall lng production; "         
#                     elif tracker == 'GGIT-lng':
#                         # 474 mtpa in 2024
#                         for row in df.index:
#                             capacitymtpa = df.loc[row, 'capacity']
#                             if capacitymtpa > 474:
#                                 print(f"Capacity {capacitymtpa:.1e} exceeds 474 mtpa more than overall lng terminal capacity")
#                                 input('ISSUE on capacitymtpa')                            
            
#                                 df.at[row, 'error messages'] += "Error!" + f" Capacity {capacitymtpa:.1e} exceeds 474 mtpa more than overall lng terminal capacity; "                                         
                    
#             df_issues = df[df['error messages'] != '']
#             df_issues.to_excel(writer, index=False)
         
