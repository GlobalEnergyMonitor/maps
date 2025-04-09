from all_config import *
import pandas as pd
###
### pull in each final map file by map and tracker
### make list of all areas
### compare to previous file
### add new ones and then sort
# tracker_folder_path = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/'


def rebuild_countriesjs(mapname, newcountriesjs):

        prev_countriesjs = f'{tracker_folder_path}{mapname}/countries.js'
        prev_countriesjs = pd.read_csv(prev_countriesjs)
        print(prev_countriesjs)
    
        # cycle through folder to find new countries.js file and do a comparison
        
        # from map file, create new countries.js based on sorted countries
        missing_countries_areas = set(newcountriesjs) - set(prev_countriesjs)
        
        if len(missing_countries_areas) > 0:
            print(f'paste in this sorted list of new countries into {mapname} file')
            # save the sorted file
            newcountriesjs = newcountriesjs.sort()
            cjs = {'countries': newcountriesjs}
            cjs_df = pd.DataFrame(data=cjs)
            cjs_df.to_csv(f'{tracker_folder_path}{mapname}/countriesjsnew{iso_today_date}.js')
            input('check file in tracker folder countriesjsnew DATE.js')
    