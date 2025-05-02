import pandas as pd
from numpy import absolute
import geopandas as gpd
from .map_class import MapObject
from .tracker_class import TrackerObject
from tqdm import tqdm # can adapt more, special tweaking for dataframe!

def create_map_objs(map_tab_df,row, prep_dict):
    map_obj = MapObject(
        name=map_tab_df.loc[row, 'mapname'],
        source=map_tab_df.loc[row, 'source'],
        geo=map_tab_df.loc[row, 'geo'], 
        needed_geo=[], # changes to list of countries from geo via get needed geo
        fuel=map_tab_df.loc[row, 'fuel'],
        pm=map_tab_df.loc[row, 'PM'], 
        trackers=[],
        aboutkey = map_tab_df.loc[row, 'about_key'],
        about=pd.DataFrame(),
    )
    
     
    # call all object methods here
    # map_obj.get_needed_geo()
    map_obj.get_about()
    # create tracker objs
    # create a tracker obj for each item in map source
    for item in map_obj.source:
        print(f'Creating source object for: {map_obj.name} {item}')
        # input('Check') # working

        tracker_source_obj = TrackerObject(
            key = prep_dict[item]['gspread_key'],
            name = prep_dict[item]['official name'], 
            off_name = prep_dict[item]['official tracker name'], 
            tabs = prep_dict[item]['gspread_tabs'],
            release = prep_dict[item]['latest release'],
            acro = prep_dict[item]['tracker-acro'],
            geocol = prep_dict[item]['geocol'],
            fuelcol = prep_dict[item]['fuelcol'],
            about_key = prep_dict[item]['about_key'],
            about = pd.DataFrame(),
            data = pd.DataFrame()  # Initialize as an empty DataFrame
        )
        
        tracker_source_obj.set_df()
        tracker_source_obj.get_about()
            
        # set data and about attributes for each tracker
        if tracker_source_obj.acro == 'GOGPT-eu':
            
            print("TrackerObject Attributes:")
            print(f"Key: {tracker_source_obj.key}")
            print(f"Name: {tracker_source_obj.name}")
            print(f"Off Name: {tracker_source_obj.off_name}")
            print(f"Tabs: {tracker_source_obj.tabs}")
            print(f"Release: {tracker_source_obj.release}")
            print(f"Acro: {tracker_source_obj.acro}")
            print(f"Geocol: {tracker_source_obj.geocol}")
            print(f"Fuelcol: {tracker_source_obj.fuelcol}")
            print(f"About DataFrame: {tracker_source_obj.about}")
            print(f"Data DataFrame: {tracker_source_obj.data}")
            input('Check if tracker object attributes look right for GOGPT-eu') #working
            # append tracker obj to map obj attribute trackers 
        map_obj.trackers.append(tracker_source_obj)
        

    # test if data got added
    for i, tracker in enumerate(map_obj.trackers):  # Iterate through tracker objects
        # df = tracker.data # TODO check if this is right
        
        try:
            print(f"DataFrame BEFORE {i}{tracker.acro}: {tracker.data.shape}")
            # filter by geo and fuel and check result

            tracker.create_filtered_geo_fuel_df(map_obj.geo, map_obj.fuel)
            print(f"DataFrame AFTER {i}{tracker.acro}: {tracker.data.shape}")

            input('Check after geo filter')
            
        except AttributeError:

            main_or_h2 = tracker.data[0]
            prod_or_og = tracker.data[1]
            print(f"DataFrame {i}main{tracker.acro}: {main_or_h2.shape}")
            print(f"DataFrame {i}prod{tracker.acro}: {prod_or_og.shape}")

            tracker.create_filtered_geo_fuel_df(map_obj.geo, map_obj.fuel)
            main_or_h2 = tracker.data[0]
            prod_or_og = tracker.data[1]
            print(f"DataFrame {i}main geo filt{tracker.acro}: {main_or_h2.shape}")
            print(f"DataFrame {i}prod geo filt{tracker.acro}: {prod_or_og.shape}")

            # input('Check after geo filter')

        except TypeError as e:
            print(f'Fix error for {map_obj.name}: \n{e}')
            input('Check TypeError')
    

            
        
    return map_obj