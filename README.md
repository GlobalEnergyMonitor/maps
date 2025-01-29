## 
[Steps to create and test multi-tracker maps WIP]([https://docs.google.com/document/d/1LacVuubl4T4CtGzy1KT_GsWrjV-DOI8XQFuLsUliT88]
)



# gem-tracker-maps

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

## Building vector tiles

[Detailed GEM Specific Instructions for creating and updating GIPT tiles](https://docs.google.com/document/d/1Lh2GbscAGpM-UKx2UIo2ajHrmII_RWDDiLvGfhMktZg/edit)

Install [csv2geojson](https://github.com/mapbox/csv2geojson) and [tippecanoe](https://github.com/mapbox/tippecanoe)

`% csv2geojson --numeric-fields "Capacity (MW)" Global\ Integrated\ Power\ data\ 2024-02-14.xlsx\ -\ Sheet1.csv > integrated.geojson`

`% tippecanoe -e integrated-2024-02-14.dir --no-tile-compression -r1 -pk -pf --force -l integrated < integrated.geojson`

Copy local files to digital ocean spaces recursively and set public
`aws s3 cp --endpoint-url https://nyc3.digitaloceanspaces.com PATH/TO/DIR/TILES/FROM/TIPPECANOE s3://$BUCKETEER_BUCKET_NAME/NAME_OF_FOLDER_IN_DIGITAL_OCEAN/NAME_OF_SUB_FOLDER_IN_DIGITAL_OCEAN --recursive --acl public-read`



## Hosting 

This can be hosted directly from GitPages.

If hosting on another webserver, the entire repo should be available from a directory on the webserver.

## Libraries Used
* Mapbox GL JS for maps
* jQuery for document manipulation / querying
* bootstrap for styling
* DataTables for table view


## Next trackers to move into EG

* Nuclear (changing soon)
* Asia Gas Tracker (able to change soon, and will be prioritized this summer if possible)
* Europe Gas Tracker (able to change soon, and will be prioritized this summer if possible)
* LATAM Energy Tracker (able to change soon, and will be prioritized this summer if possible)
* GMET (add in pipelines soon)

* GOIT (able to change soon)
* GGIT (able to change soon) 

* Steel & Iron (able to change soon, planned for early 2025) 
* GBPT (planned to change early Sept 2024) 

* GCTT Coal Terminals Tracker (no plans, but easily could)
* Coal Project Finance Tracker (no plans)
* Global Energy Ownership (no plans, no map) 
* Private Equity tracker (no plans, no map)
