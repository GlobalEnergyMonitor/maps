UPDATED INSTRUCTIONS

When there is new data for a given tracker release this script is run to create the global map and any dependent regional or multi-tracker maps. A byproduct of creating dependent maps is that we also create the relevant data downloads for those subsets of data. 

The run_maps.py file is the only script you need to run on your local machine. Run it from gem_tracker_maps with ```python -m run_maps ``` 

OUTPUTS OF RUNNING run_maps.py
The output of that script is an updated map file that can be accessed by an s3 url or by the local file. It gets updated in the tracker's config.js file. The js can take csv, geojson, or json files and you alter that here:

![Screenshot 2025-05-12 at 1 14 28 PM](https://github.com/user-attachments/assets/182eeaee-cf18-4d8a-8cb0-372a84110330)

Another possible output of the script, depending on what tracker is being updated, is an excel file with the appropriate data and about pages that April / Ops can direclty upload to the website with. We share that with them in this [folder]([url](https://drive.google.com/drive/u/0/folders/1I225d18KhpPXXwhp-q7oeBU3RLFx7N60)). It's good to manually check these files. In the about pages I need to delete the first row that is the dataframe index. But for all other data downloads no change should need to be done, except for the Europe download. For that file, I update the tab names. They are purposefully different to help remember that the sources of data are different for that map and is treated like it's own tracker in some cases since it has its own annual data release, and since GOGPT gathers data about Hydrogen in a separate tab that does not get included (at time of writing) in their global data release.

FIRST TIME PRE REQUISITES TO RUNNING run_maps.py
- local version of this repo
- virtual environment created with the requirements.txt file 
boto3==1.37.24
chardet==4.0.0
duckdb==1.2.1
geopandas==0.14.3
gspread==6.2.0
gspread_dataframe==4.0.0
numpy==1.24.3
openpyxl==3.1.5
pandas==2.0.3
polyline==2.0.2
pyogrio==0.7.2
Requests==2.32.3
Shapely==2.1.0
tqdm==4.65.0
XlsxWriter==3.1.4
- creds.py file with client secret for gspread / google sheets API saved at same level as trackers folder
![Screenshot 2025-05-12 at 1 55 17 PM](https://github.com/user-attachments/assets/4df0b6c6-45f7-4671-94f2-41f8064e9c3c)
- updated tracker data file saved to this [folder]([url](https://drive.google.com/drive/folders/1Ql9V1GLLNuOGoJOotX-wK6wCtDq1dOxo)) as google sheets, and the sheet key and tab name updated in the "source" tab of the [map tracker log]([url](https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1875432780#gid=1875432780))
- NOTE: As a process we are migration from pulling the data from google sheets to pulling it from the ["latest" folder in s3]([url](https://cloud.digitalocean.com/spaces/publicgemdata?path=latest%2F)) the excel file can be downloaded locally and run through by script named "save_file_to_s3.py" (that converts it to parquet file though that's not necessary as long as you update the map_tracker_class.py function mentioned next) though in map_tracker_class.py ```set_df.py``` needs to be adjusted so that for all trackers look in s3, currently we only look for it for the data that is given to us in geojson files
- Finally update ```all_config.py```
  --  the list variable called trackers_to_update with the full name (found in the column 'official tracker name' in [source tab of map tracker log]([url](https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1875432780#gid=1875432780)))
  -- new_release_date variable
  -- releaseiso variable
  -- priority list variable if needed. If left as a list of a blank string all needed map files and data download files get created. This can help speed the script up. NOTE that it needs to be the lowercase map name in the column 'mapname' of the [map tab in the map tracker log]([url](https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1042821512#gid=1042821512))

  -- update all path variables to your own local paths by searching /Users/gem-tah/ in the all_config.py file
  -- renaming_cols_dict if any column name changes occured between last tracker update and this one
  -- final_cols if a net new column needs to be added, for trackers that have not gone through this updated script I'd recommend adding the column name to here to be safe (This can be reworked, it cuts down on the final map size which helps with load speeds) 

  
AFTER YOUR FIRST RUN PREREQUISITES
- updated tracker data file saved to this [folder]([url](https://drive.google.com/drive/folders/1Ql9V1GLLNuOGoJOotX-wK6wCtDq1dOxo)) as google sheets, and the sheet key and tab name updated in the "source" tab of the [map tracker log]([url](https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1875432780#gid=1875432780)) (SEE NOTE ABOVE IN FIRST RUN SECTION)
- Finally update ```all_config.py```
  --  the list variable called trackers_to_update with the full name (found in the column 'official tracker name' in [source tab of map tracker log]([url](https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1875432780#gid=1875432780)))
  -- new_release_date variable
  -- releaseiso variable
  -- priority list variable if needed. If left as a list of a blank string all needed map files and data download files get created. This can help speed the script up. NOTE that it needs to be the lowercase map name in the column 'mapname' of the [map tab in the map tracker log]([url](https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1042821512#gid=1042821512))
  -- renaming_cols_dict if any column name changes occured between last tracker update and this one
  -- final_cols if a net new column needs to be added, for trackers that have not gone through this updated script I'd recommend adding the column name to here to be safe (This can be reworked, it cuts down on the final map size which helps with load speeds) 
  
DEBUGGING TIPS
- Be sure to clear out the local_pkl folder for day of files when making adjustments so that the script does not pull from the locally saved tracker data or map data
- Start a 25 minute pomodoro timer, if you don't get closer to a solution, call a friend! 

DEPENDENCY MAP 

A dependency map of trackers and relevant maps can be found [here]([url](https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1875432780#gid=1875432780)) in tab "map". You will notice that some maps have more than one data source even though they are for the same GEM tracker (for example GGIT). This is because the GGIT tracker splits its data into two files, one for terminals and another for pipelines. This is relevant for the map javascript code (found in this repo) because in the tracker's config file (under the geometries variable) we let the map's javascript know if there will be line data and point data. Besides that, there are no specific accommodations for the different geographic data types that we need to worry about, it gets treated like all other assets by the javascript. 

LINE DATA CONSIDERATIONS
It is an important thing to note for the run_maps.py script because those trackers that contain line data (GGIT, GOIT) share the data via a geojson file not a google sheet. It means we can easily and directly ingest the data into a geodataframe with gpd, instead of converting the lat and lng coordinates into point data. When converting geodataframes to parquet files there is a nuance as well. The to_file method that can be found in pandas does not act the same way when called by geopandas. For all geojson final files then, which is the default currently, the script stores the geometry data appropriately before converting the dataframe to parquet file. 

The only other consideration for line data is that the scaling uses a different variable in the config file but that isn't something a typical user of this script needs to fuss with. But it's good to be aware of. In the future we might be supporting polyons for extraction data (GCMT and GOGET), but that project has not been defined as of writing. 

VISUALLY TESTING THE MAP FILE OUTPUT
You can visually test the map locally by running ```python -m http.server 8000  ``` note that you should run it from a level above the gem_tracker_maps folder (inside which you run the main data processing file we've already mentioned above ```run_maps.py```)

If it's sufficient you can push your local branch to the remote version of that branch on this "Official" repo. Then switch to a IDE window that has the [testing maps repo ]([url](https://github.com/GlobalEnergyMonitor/testing-maps))loaded up and pull down from this official repo and that same branch name you pushed your changes to. I recommend staying on the "gitpages-production" branch without creating a new branch since it's just the test repo, and so once you push to the origin remote version of that test repo's "gitpages-production" branch then the test heroku map app will be automatically re-deployed. So then you can heroku app link out to PMs to take a look. 

![Screenshot 2025-05-12 at 1 46 14 PM](https://github.com/user-attachments/assets/1a18cf49-583f-4573-9567-488d5c6c97a7)

![Screenshot 2025-05-12 at 1 45 55 PM](https://github.com/user-attachments/assets/ef6a26bc-2447-4942-a4a3-233a51374860)

NOTE: The test repo process can be confusing at first, so it'd probably be best to set up a call with the appropriate data team member (most likely Taylor at time of writing). 


BUILT IN TESTS FOR THE OUTPUTS









## 
[Steps to create and test multi-tracker maps WIP]([https://docs.google.com/document/d/1LacVuubl4T4CtGzy1KT_GsWrjV-DOI8XQFuLsUliT88]
) https://docs.google.com/document/d/1LacVuubl4T4CtGzy1KT_GsWrjV-DOI8XQFuLsUliT88



# gem_tracker_maps

GEM Tracker Maps is served entirely staticly, with no build process. Each tracker only requires a JSON based configuration file, and a data file (CSV or JSON, as currently produced for GEM Trackers).

* `/src/` contains the site code, styling information, layout, and supporting assets like images.
* `site-config.js` contains site wide configuration that applies to all trackers
* `/trackers/` contains a director for each tracker

## Create a new tracker

Clone the repo. Create a new directory under `/trackers/`. Place the data for the tracker there. Create a symlink to `index.html`: while in the new directory, `ln -s ../../src/index.html`. Create a `config.js`. Commit to GitHub.

## Configure a tracker

First, there are sitewide configurations with [`site-config.js`](site-config.js). Any parameter can be configured site wide. Documentation on the typical site wide parameters is in that file.

The [`config.js for coal-plant`](/trackers/coal-plant/config.js) has documentation on the parameters typically set for a tracker.

## Update tracker data

Fork the repository. Place new data file in the appropriate tracker directory. Test and do quality checks on that fork. When ready, make a pull request to the main repository. And accept the pull request to make the update.

## Routine tracker releases
### Global Single Tracker Maps: 
* Save a copy of the new data to the: [Tracker official releases (data team copies)](https://drive.google.com/drive/folders/1Ql9V1GLLNuOGoJOotX-wK6wCtDq1dOxo)
* Update the map tracker log sheet ([tab name prep_file](https://docs.google.com/spreadsheets/d/15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8/edit?gid=1817870001#gid=1817870001) with the new data's google sheet key from the copy of official data saved above
* In the all_config.py file add the tracker name(s) with new data to the list held in parameter: trackers_to_update = [] NOTE: This tracker name needs to match the one in prep_file tab of the log sheet
* Run run_maps.py 

### Regional / Multi-tracker Maps and Data Downloads: 
* Run multi_tracker_maps_script.py directly or from run_maps.py with subprocess
subprocess.run(["python", "/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/multi_tracker_maps_script.py"])                 


### Pre and Post Tests
* [Testing and data set up for multi tracker map files and data download files](https://docs.google.com/document/d/1LacVuubl4T4CtGzy1KT_GsWrjV-DOI8XQFuLsUliT88/edit?tab=t.0#heading=h.eooqz1k5afdy)
* Tests final dataframe size to original
* Tests capacity values to be sure none after converting to joules are larger than capacity in original units for a country


## Building vector tiles

Currently only used for GIPT map. Adjusted in the tracker/map's config file with the flag "tile" instead of "csv" or "json"

[Detailed GEM Specific Instructions for creating and updating GIPT tiles](https://docs.google.com/document/d/1Lh2GbscAGpM-UKx2UIo2ajHrmII_RWDDiLvGfhMktZg/edit)

Install [csv2geojson](https://github.com/mapbox/csv2geojson) and [tippecanoe](https://github.com/mapbox/tippecanoe)

`% csv2geojson --numeric-fields "Capacity (MW)" Global\ Integrated\ Power\ data\ 2024-02-14.xlsx\ -\ Sheet1.csv > integrated.geojson`

`% tippecanoe -e integrated-2024-02-14.dir --no-tile-compression -r1 -pk -pf --force -l integrated < integrated.geojson`

Copy local files to digital ocean spaces recursively and set public
`aws s3 cp --endpoint-url https://nyc3.digitaloceanspaces.com PATH/TO/DIR/TILES/FROM/TIPPECANOE s3://$BUCKETEER_BUCKET_NAME/NAME_OF_FOLDER_IN_DIGITAL_OCEAN/NAME_OF_SUB_FOLDER_IN_DIGITAL_OCEAN --recursive --acl public-read`



## Hosting 

This can be hosted directly from GitPages.

If hosting on another webserver, the entire repo should be available from a directory on the webserver.

Official Maps can be found at this repo: 

* https://github.com/GlobalEnergyMonitor/maps

Live branch is gitpages-production

### Test Repo 

Maps spun up for PM review before pushed to live can be found in this repo: 

* https://github.com/GlobalEnergyMonitor/testing-maps/tree/gitpages-production

Live branch is gitpages-production


## Libraries Used
* Mapbox GL JS for maps
* jQuery for document manipulation / querying
* bootstrap for styling
* DataTables for table view


## New Features Planned
* Fly to unit
* Area based scaling
* Legend overhaul
* Search overhaul 


## Next trackers to move into EG

* GMET (add in pipelines soon)

* GOIT (able to change soon)

* Steel & Iron (able to change soon, planned for early 2025) 
* Coal Project Finance Tracker (no plans)
* Global Energy Ownership (no plans, no map) 
* Private Equity tracker (no plans, no map)
