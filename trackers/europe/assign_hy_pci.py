import pandas as pd
import geopandas as gpd
import numpy as np
# here we need to assign gas pipes with hydrogen and or pci5 pci6
# we will use the data from last release, grab the id, then apply that to this dataset
# we will have a new pipes data for map but not data download
# in the config.js we'll build a section in the legend and a new type for these attributes

# pci own columns
# hydrogen vs methane tracker legend value add
eupath = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/europe/'
file = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/europe/ggit-pipeline-pci-hydrogen-dec-2023.csv'
mapfile = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/europe/compilation_output/europe_2024-10-02.geojson'
hyfile = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/europe/Copy of Pipelines (Gas_Oil_NGL) - main - for EGT briefing in Feb 2024 - Gas pipelines.csv'
release_file = '/Users/gem-tah//GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GGIT-Gas-Pipelines-2023-12 copy.geojson'
def create_df(file, map_file, hyfile):
   
    # hydrogen data
    # key = '1F0NlPH9ntS6AuKx-ZwojjEgadw7quYuTiBRfBK_V17I'
    # tab = ['Gas pipelines']
    cols = ['Fuel', 'Countries', 'PCI5', 'PCI6', 'ProjectID', 'PipelineName','Status',
            'Owner','Start year 1', 'CapacityBcm/y', 'CapacityBOEd', 'LengthKnownKm', 
            'FuelSource', 'Parent', 'StartState/Province',
            'StartCountry', 'EndState/Province','EndCountry', 'Route', 'WKTFormat',
            'Wiki']
    # hypci_df = gspread_access_file_read_only(key, tab)
    hypci_df = pd.read_csv(hyfile)
    hypci_df = hypci_df[cols]
    print(set(hypci_df['Fuel'].to_list()))
    # filter for only hydrogen and gas 
    hypci_df = hypci_df[hypci_df['Fuel'].isin(['Gas','Hydrogen'])]
    # hypci_df_not_oil = hypci_df[hypci_df['Fuel'] != 'Oil'] # maybe this includes other that we need to include

    print(hypci_df)
    print(hypci_df[hypci_df['Fuel']=='Hydrogen'])
    # df = pd.read_csv(file, encoding='utf-16')
    # print(df.info())
    # # print(set(df['type'].to_list()))
    # # filter type to pipes
    # # columns only needed
    # col_list = ['project', 'unit', 'pci5', 'pci6', 'type', 'url']
    # df = df[df['type'].isin(['gas_pipeline', 'hydrogen_pipeline'])]
    # print(len(df))
    # df = df[(col_list)]
    # print(df.info())
    #  0   project  855 non-null    object
    #  1   unit     145 non-null    object
    #  2   pci5     14 non-null     object
    #  3   pci6     38 non-null     object
    #  4   type     855 non-null    object
    gdf = gpd.read_file(map_file)
    # print(gdf.info())
    
    # merge gdf and df on unit and unit-name or project and name
    # find if there is any overlap between two dataframes based on a common column
    # outer so include new hydrogen
    print(hypci_df.columns)
    hypci_df = hypci_df.rename(columns={
                                'Fuel':'fuel',
                                'Countries': 'areas',
                                'ProjectID': 'id',
                                'PipelineName': 'name'})
    gdf = pd.merge(gdf, hypci_df, left_on='id', right_on='ProjectID', how='outer')
    # print(gdf)
    # print(gdf.info())
    
    # 113
    # print(gdf[gdf['Fuel']=='Hydrogen'][['url','PCI5', 'PCI6', 'areas', 'name', 'id', 'ProjectID', 'unit-name']])
    # # 3653 Fuel == Gas
    # # 631 tracker == GGIT
    # print(gdf[gdf['tracker-acro']=='GGIT'][['url','PCI5', 'PCI6', 'areas', 'name', 'id', 'ProjectID', 'unit-name']])
    # test = gdf[gdf['tracker-acro']=='GGIT'][['url','PCI5', 'PCI6', 'areas', 'name', 'id', 'ProjectID', 'unit-name']]
    # print(set(test['PCI5'].to_list())) # should be 14
    # print(set(test['PCI6'].to_list())) # east med gas pipeline should be gas/methane and pci6, 2! malta-italy gas pipe as well 
    # print(test[test['PCI5']=='yes']) # should be 14, only 7 oh but I did this on project id not unit ... 
    # print(test[test['PCI6']=='yes']) # should be 2, got 0

    # print(gdf[gdf['name'] == 'East Med Gas Pipeline']) #EastMed to East Med

    # I need to merge up the pipeline file with the official release and find the total number of methane hydrogen pci5 pci6
    return hypci_df, gdf

def get_list_pci(gdf):
    list_pci = []
    # pci5
    # pci6
    # unit project
    gdf['PCI5-legend'] = gdf['PCI5'].replace('yes', 'pci5')
    gdf['PCI6-legend'] = gdf['PCI5'].replace('yes', 'pci6')

    return gdf


def get_list_hy_meth(gdf):
    list_hy_meth = []
    # type
    # unit project
    gdf['tracker-legend'] = gdf['tracker-acro']
    print(set(gdf['tracker-legend'].to_list()))
    gdf['tracker-legend'] = gdf['tracker-legend'].fillna('GGIT-hy')
    print(set(gdf['tracker-legend'].to_list()))
    gdf['tracker-display'] = gdf['tracker-display'].fillna('hydrogen pipeline')    
    gdf['tracker-display'] = gdf['tracker-display'].replace('gas pipeline')    

    return gdf

def do_all_map_conversions(gdf):
    # status
    # gdf['status'] = gdf['Status']
    # gdf['status-legend'] = gdf['Status']
    # capacity
    # all columns
    return gdf

def write_to_file(gdf):
    gdf.to_file(f'{eupath}europe-map-with-hy.geojson', driver='GeoJSON')
    print('Saved new map file!')
    print('You will want to merge them in the main script to create a new data download and map file from start')
    print('You also need capacity to go through conversion and scaling, and status, and countries')


# then once that lines up with last map numbers incorporate into multi map script 

# call

df, gdf = create_df(file, mapfile, hyfile)
gdf = get_list_pci(gdf)
gdf = get_list_hy_meth(gdf)
write_to_file(gdf)