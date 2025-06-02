import pandas as pd
# from all_config import *
from all_config import *
# from helper_functions import *
from helper_functions import *
from make_map_tracker_objs import make_map_tracker_objs
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
        
        with open(f"{logpath}tracker_data_log.txt", "a") as log_file:
            log_file.write(f"Stopping on Map name: {map_obj.name}\n")
            log_file.write("Trackers in map:\n")
            [log_file.write(f"{tracker_obj.name}\n") for tracker_obj in map_obj.trackers]
            log_file.write("Confirm all trackers in map\n")

        for tracker_obj in map_obj.trackers:
            # if tracker_obj.acro == 'GGIT' or tracker_obj.acro == 'GOIT':
            #     print(f'Len of {tracker_obj.acro} is {len(tracker_obj.data)}')
            #     input('CHECK GOIT GGIT MISSING')
            # this gets to each df within each map
            # first I should combine goget so we can stop filtering by tuple
            if isinstance(tracker_obj.data, tuple):
                # for goget and gogpt EU
                # print(tracker_obj.name)
                # input('check') # passed, only on goget
                print(isinstance(tracker_obj.data, tuple))
                if tracker_obj.acro == 'GOGPT-eu' or tracker_obj.name == 'GOGPT EU':
                    # TODO april 19th left off here, we need to make sure gogpt eu is handled correctly
                    # it cannot be concatted, needs to be kept separate as two dfs
                    # if map_obj.geo in ['europe']:
                    # TODO make sure these methods work correctly using GOGPT EU as a tuple now 
                    # print('We are in make map for gogpt eu! about to set fuel and maturity and deduplicate!')
                    # input('NEW - DOES THIS HAPPEN?')
                    tracker_obj.set_fuel_filter_eu() # this fuel filter needs to happen for gogpt eu before they get merged into one
                    tracker_obj.set_maturity_eu()
                    # this one should create one gdf for the map
                    tracker_obj.deduplicate_gogpt_eu() # this is where gogpt-eu gets renamed 
                    # print(len(tracker_obj.data))
                    # print(type(tracker_obj.data))
                    # input('Check length and type after all that, shouldnot be 2 tuple')
                    
                elif tracker_obj.name == 'Oil & Gas Extraction':
                    tracker_obj.process_goget_reserve_prod_data()
                    if map_obj.geo in ['europe']:
                        # TODO look into why this isn't hit
                        input('europe hit for map adjustments goget') 
                        tracker_obj.set_fuel_filter_eu() # this fuel filter should happen after goget is put into one and only if its for a europe map
                        tracker_obj.set_maturity_eu()                       
                # print(isinstance(tracker_obj.data, tuple))
                # input('Check if there was a change') 
                # clean_capacity and coordinate qc
                # tracker_obj.clean_num_data()
                # tracker_obj.transform_to_gdf()
            elif tracker_obj.name == 'GOGPT EU':
                print('Odd that it is not a tuple?')
                print(tracker_obj.data['tracker-acro'])
                print(len(tracker_obj.data))
                print(type(tracker_obj.data))
                input("Check type for GOGPT EU")
            
            # this should happen if not tuple so not gogpt eu or goget but IS in europe
            else:       
                if tracker_obj.name in ['LNG Terminals EU', 'Gas Pipelines EU']:
                    # input('europe hit for map adjustments') 
                    tracker_obj.set_fuel_filter_eu() # this fuel filter should happen when we are at this point of non tuple ville and just needs to happen to these other eu specific tracker dfs
                    tracker_obj.set_maturity_eu() 
                    
                elif tracker_obj.name in ['Cement and Concrete']: 
                    tracker_obj.gcct_changes()              
            
            
            # [print(col) for col in tracker_obj.data.columns if col == 'fuel-filter']
            # # input('Is fuel filter printed?')
            
            # this should happen to ALL
            # clean_capacity and coordinate qc
            # TODO should lower case all cols at ONE point ... chaotic for split_goget because europe has lowercase and all else is unchanged unitl rename_and_concat
            
            
            tracker_obj.clean_num_data()

            tracker_obj.transform_to_gdf()
            
            tracker_obj.split_goget_ggit()
  
            tracker_obj.assign_conversion_factors(conversion_df)

        map_obj.rename_and_concat_gdfs() # we account for GOGPT eu that already aritficially set tracker-acro according to differences in columns of hy and plants in gogpt eu

        map_obj.set_capacity_conversions()

        map_obj.map_ready_statuses_and_countries()

        map_obj.create_search_column()

        map_obj.capacity_hide_goget_gcmt()

        map_obj.set_fuel_goit()

        map_obj.last_min_fixes()

        map_obj.save_file()

        
    list_of_map_objs_mapversion.append(map_obj) # this will be the map obj with the filtered cleaned concatted one gdf
            
    return list_of_map_objs_mapversion
