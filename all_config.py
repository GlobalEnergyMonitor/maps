
from datetime import datetime, timedelta 
import os
import gspread
from numpy import true_divide
import sys
from trackers.creds import *



trackers_to_update = ['Coal Mines']# ['Hydropower']# ['Gas Pipelines'] #['Iron & Steel']
new_release_date = 'May_2025' # for within about page NEEDS TO BE FULL MONTH
releaseiso = '2025-05'
priority = [''] # europe # NOTE NEEDS TO BE [''] to be skipped NEEDS TO BE mapname in map_tab internal
                    # africa
                    # integrated
                    # europe
                    # asia
                    # latam
                    # ggit
                    # goit
                    # goget
                    # gctt
                    # gcpt
                    # gcmt
                    # gogpt
                    # gspt
                    # gwpt
                    # gnpt
                    # gbpt
                    # ggpt
                    # ghpt
                    # gist
                    # gmet
                    # giomt

augmented = True
data_filtering = True

#### CREATE ####
map_create = True # work on subnat
dwlnd_create = True
about_create = True 
# summary_create = False

#### TEST #####
run_pre_tests = False # TODO need to add so that there is utility here
run_post_tests = False
map_to_test = '' # change if testing a single map not a regional one

#### REFINE ####
refine = False 
local_copy = False  # TODO issue when not local for refining! # no local_pkl/europe_Oil & Gas Plants_gdf_2024-12-12.pkl' file!
final_formatting = False


tracker_folder_path = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/'
# goget_orig_file = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/Global Oil and Gas Extraction Tracker - 2024-03-08_1205 DATA TEAM COPY.xlsx'
# goget_orig_tab = ['Main data','Production and reserves']

egt_dd_key = '1h8Nr8lJJiUIsSIzEmwnici4Js9Brxt7GChDo_DBQF2s' 
goget_global_key = '1wI11cMqhqZXTK7MVD2semkZIqlF4DSpfsNTaSPBWWO0'

egt_ggit_pipes = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-EGT-Gas-Hydrogen-Pipelines-2025-02 DATA TEAM COPY.geojson'
egt_ggit_terminals = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-EGT-Terminals-2025-02 DATA TEAM COPY.geojson'

region_key = '1yaKdLauJ2n1FLSeqPsYNxZiuF5jBngIrQOIi9fXysAw'
region_tab = ['mapping']

centroid_key = '1ETg632Bkwnr96YQbtmDwyWDpSHqmg5He0GQwJjJz8IU'
centroid_tab = ['centroids']
# Format the date in ISO format
# Get today's date
today_date = datetime.today()

iso_today_date = today_date.isoformat().split('T')[0]
iso_today_date_folder = f'{iso_today_date}/'
client_secret_full_path = os.path.expanduser("~/") + client_secret
gem_path = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/'
gem_path_tst = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/testing/'
path_for_pkl = gem_path + '/local_pkl/'
gspread_creds = gspread.oauth(
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        credentials_filename=client_secret_full_path,
        # authorized_user_filename=json_token_name,
    )
dtype_spec = {} #{'Latitude': float, 'Longitude': float}
numeric_cols = ['capacity', 'start_year', 'capacity2', 'prod_start_year', 'prod_gas', 'prod_year_gas', 'prod_oil', 'prod_year_oil', 'prod-coal', ] #STOPPED AT GCMT March 3rd 2025
list_official_tracker_names = ['Oil & Gas Plants', 'Coal Plants', 'Solar', 'Wind', 'Hydropower', 'Geothermal', 'Bioenergy', 'Nuclear', 'Coal Mines', 'Coal Terminals', 'Oil & Gas Extraction', 'Oil Pipelines', 'Gas Pipelines', 'LNG Terminals']

maps_with_needed_conversion = ['asia', 'europe', 'africa', 'latam', 'ggit']
gas_only_maps = ['AGT', 'EGT', 'asia', 'europe', 'ggit'] 
non_gsheet_data = ['Gas Pipelines', 'LNG Terminals', 'Oil Pipelines', 'Gas Pipelines EU', 'LNG Terminals EU', 'GOGPT EU']

conversion_key = '1fOPwhKsFVU5TnmkbEyPOylHl3XKZzDCVJ29dtTngkew'
conversion_tab = ['data']
gcmt_closed_tab = 'Global Coal Mine Tracker (Close'


# TODO make it so that each map has it's only set of final cols, so smallest csv possible, helpful for regional gas mostly ...



# TODO maybe keep all location data in there, and keep a preserved country and subnat col
# TODO keep in retired year or closed year for longitudinal, and make sure start year is there too
final_cols = ['facilitytype','unit_id', 'loc-oper', 'loc-owner', 'tech-type','ea_scaling_capacity', 'operator', 'Operator', 'Binational', 'binational', 'loc-accu','units-of-m','mapname','tracker-acro','official_name','url', 'areas','name', 'unit_name', 'capacity',
              'status', 'start_year', 'subnat', 'region', 'owner', 'parent', 'tracker', 'tracker_custom', 'operator-name-(local-lang/script)', 'owner-name-(local-lang/script)',
        'original_units', 'location-accuracy','conversion_factor', 'geometry', 'river', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2',
        'prod-coal', 'Latitude', 'Longitude', 'pid','id', 'prod_oil', 'prod_gas', 'prod_year_oil', 'prod_year_gas', 'fuel', 'PCI5', 'PCI6', 'pci5','pci6','WKTFormat', 'Fuel', 'maturity', 'fuel-filter', 
        'pci-list', 'coal-grade', 'mine-type', 'prod-coal', 'owners_noneng', 'noneng_name', 'coalfield', 'workforce', 'prod_year', 'opening-year', 'closing-year', 'opening_year', 'closing_year']

renaming_cols_dict = {'GOGPT': {'GEM location ID':'pid', 'GEM unit ID': 'id','Wiki URL': 'url','Country/Area': 'areas', 'Plant name': 'name', 'Unit name': 'unit_name', 
                                'Capacity (MW)': 'capacity', 'Status': 'status', 'Fuel': 'fuel', 'Owner(s)': 'owner', 'Parent(s)': 'parent',
                                'Start year': 'start_year', 'State/Province': 'subnat', 'Region': 'region'},
                      'GCPT': {'GEM location ID':'pid', 'GEM unit/phase ID': 'id','Country/Area': 'areas', 'Wiki URL':'url',
                                   'Plant name': 'name', 'Unit name':'unit_name',
                                   'Owner': 'owner', 'Parent': 'parent', 'Capacity (MW)': 'capacity', 'Status': 'status', 
                                   'Start year': 'start_year', 'Subnational unit (province, state)': 'subnat', 'Region': 'region'},
                      'GSPT': {'GEM location ID':'pid', 'GEM phase ID':'id','Country/Area': 'areas', 'Project Name': 'name', 'Phase Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GWPT': {'GEM location ID':'pid', 'GEM phase ID': 'id','Country/Area': 'areas', 'Project Name': 'name', 'Phase Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GNPT': {'GEM location ID':'pid', 'GEM unit ID': 'id','Country/Area': 'areas', 'Project Name': 'name', 'Unit Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start Year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GHPT': {'GEM location ID':'pid', 'GEM unit ID':'id','Country/Area 1': 'areas', 'Country/Area 2': 'area2','Project Name': 'name', 
                               'Country/Area 1 Capacity (MW)': 'capacity', 'Country/Area 2 Capacity (MW)': 'capacity2',
                               'Status': 'status', 'Start Year': 'start_year', 'Owner': 'owner', 'Operator': 'operator', 'Binational': 'binational',
                               'Region 1': 'region', 'Region 2': 'region2','State/Province 1':'subnat', 'State/Province 2':'subnat2', 'Owner Name (local lang/script)': 'loc-owner', 
                               'Operator Name (local lang/script)': 'loc-oper',
                               'Wiki URL': 'url', 'River / Watercourse': 'river', 'Location Accuracy': 'loc-accu', 'Technology Type': 'tech-type'},
                      'GBPT': {'GEM location ID':'pid', 'GEM phase ID':'id','Country/Area': 'areas', 'Project Name': 'name', 'Unit Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start Year': 'start_year', 'Owner(s)': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GGPT': {'GEM location ID':'pid', 'GEM unit ID':'id', 'Country/Area': 'areas', 'Project Name': 'name', 'Unit Name': 'unit_name',
                               'Unit Capacity (MW)': 'capacity', 'Status': 'status', 'Start Year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      # TODO TO DECIDE need to copy for infra and extraction non power to make a pid copy of the unit id, for ease of use, or just apply unit logic to power
                      
                      'GCTT': {'GEM Terminal ID':'pid', 'GEM Unit/Phase ID': 'unit_id','Coal Terminal Name': 'name', 'Coal Terminal Name (detail or other)': 'other_name','Parent Port Name': 'port','Wiki URL': 'url', 'Status': 'status', 'Owner': 'owner', 'Capacity (Mt)':'capacity',
                               'Start Year': 'start_year', 'Region': 'region', 'State/Province':'subnat', 'Country/Area': 'areas'},
                      'GOGET': {'Unit ID':'id', 'Wiki name': 'name', 'Country/Area': 'areas', 'Subnational unit (province, state)': 'subnat', 'Status': 'status', 'Discovery year': 'start_year', 'Production start year': 'prod_start_year',
                                'GEM region': 'region','Owner': 'owner', 'Parent': 'parent', 'Wiki URL': 'url', 'Production - Oil (Million bbl/y)': 'prod_oil', 'Production - Gas (Million m³/y)': 'prod_gas',
                                'Production - Total (Oil, Gas and Hydrocarbons) (Million boe/y)': 'capacity','Production Year - Oil': 'prod_year_oil', 'Production Year - Gas': 'prod_year_gas'
                                , 'Country List':'mult_countries', 'Fuel type': 'fuel'},
                      'GCMT': {'GEM Mine ID':'pid','Country / Area': 'areas', 'Mine Name': 'name', 'Mine Name (Non-ENG)': 'noneng_name','Status': 'status', 'Owners': 'owner', 'Owners (Non-ENG)': 'owners_noneng','Parent Company': 'parent', 'Capacity (Mtpa)': 'capacity', 
                               'Production (Mtpa)':'prod-coal', 'Year of Production': 'prod_year','Opening Year': 'opening_year', 'Closing Year': 'closing_year','State, Province': 'subnat', 'Region': 'region', 'GEM Wiki Page (ENG)': 'url', 'GEM Wiki Page (Non-ENG)': 'urlchina', 'Coalfield': 'coalfield', 'Workforce Size': 'workforce', 'Coal Grade': 'coal-grade',
                               'Mine Type': 'mine-type'},
                      'GOIT': {'ProjectID':'pid','Countries': 'areas', 'Wiki': 'url', 'PipelineName': 'name', 'SegmentName': 'unit_name', 'Status': 'status', 'Owner': 'owner',
                               'Parent': 'parent', 'CapacityBOEd': 'capacity', 'StartYear1': 'start_year', 'EndState/Province':'subnat', 'StartRegion': 'region',
                               'EndRegion': 'region2'},
                      'GGIT': {'ProjectID':'pid','Countries': 'areas','Wiki': 'url',
                                   'PipelineName':'name', 'SegmentName':'unit_name', 'Status':'status', 'Owner':'owner', 'Parent': 'parent',
                                   'StartYear1': 'start_year', 'CapacityBcm/y': 'capacity', 'StartState/Province': 'subnat',
                                   'StartRegion': 'region', 'EndState/Province': 'subnat2', 'EndRegion': 'region2'
                                   }, 
                      'GGIT-lng': {'ComboID':'pid','Wiki': 'url', 'TerminalName': 'name',
                                   'UnitName': 'unit_name', 'Status': 'status', 'Country': 'areas', 'Owner': 'owner', 
                                   'Parent': 'parent', 'CapacityInMtpa': 'capacity', 'StartYearEarliest': 'start_year', 'Region': 'region', 
                                   'State/Province': 'subnat'},
                    #   'GGIT-eu': {'ProjectID':'id','Countries': 'areas','Wiki': 'url', 'Fuel': 'fuel',
                    #                'PipelineName':'name', 'SegmentName':'unit_name', 'Status':'status', 'Owner':'owner', 'Parent': 'parent',
                    #                'StartYear1': 'start_year', 'CapacityBcm/y': 'capacity', 'StartState/Province': 'subnat',
                    #                'StartRegion': 'region', 'EndState/Province': 'subnat2', 'EndRegion': 'region2',
                    #                },
                      
                      # TODO fix this today april 14th
                        # Gas Pipelines EU	GGIT-eu
                        # LNG Terminals EU	GGIT-lng-eu
                        # GOGPT EU	GOGPT-eu
                      # gogpt-eu fuel, h2%, h2-usage-proposed-%, pci5, pci6
                    #   'GOGPT-eu': {},
                    # 'GOGPT-eu': {'gem-location-id':'pid', 'gem-unit-id': 'id','wiki-url': 'url','country/area': 'areas', 'plant-name': 'name', 'unit-name': 'unit_name', 
                    #                                 'capacity-(mw)': 'capacity', 'status': 'status', 'fuel': 'fuel', 'owner(s)': 'owner', 'parent(s)': 'parent',
                    #                                 'start-year': 'start_year', 'subnational-unit-(province,-state)': 'subnat', 'region': 'region', 'owner':'owner', 'parent': 'parent'},
                    'plants': {'gem-location-id':'pid', 'gem-unit-id': 'id','wiki-url': 'url','country/area': 'areas', 'plant-name': 'name', 'unit-name': 'unit_name',
                            'capacity-(mw)': 'capacity', 'owner(s)': 'owner', 'parent(s)': 'parent', 'plant-name-in-local-language-/-script': 'other-local', 'other-name(s)': 'other-name',
                            'start-year': 'start_year', 'state/province': 'subnat'},

                    'plants_hy': {'gem-location-id':'pid', 'gem-unit-id': 'id','wiki-url': 'url','country/area': 'areas', 'plant-name': 'name', 'unit-name': 'unit_name',
                            'capacity-(mw)': 'capacity', 'owner(s)': 'owner', 'parent(s)': 'parent', 'plant-name-in-local-language-/-script': 'other-local', 'other-name(s)': 'other-name',
                            'start-year': 'start_year', 'state/province': 'subnat'},

                    #   'extraction': {'unit-id':'id', 'wiki-name': 'name', 'country': 'areas', 'subnational-unit-(province,-state)': 'subnat', 'discovery-year': 'start_year', 'production-start-year': 'prod_start_year',
                    #             'gem-region': 'region', 'wiki-url': 'url', 'production---oil-(million-bbl/y)': 'prod_oil', 'production---gas-(million-m³/y)': 'prod_gas',
                    #             'production---total-(oil,-gas-and-hydrocarbons)-(million-boe/y)': 'capacity','production-year---oil': 'prod_year_oil', 'production-year---gas': 'prod_year_gas',
                    #             'country-list':'mult_countries', 'fuel-type': 'fuel'},

                      'EGT-gas': {'projectid':'pid','countries': 'areas','wiki': 'url',
                                   'pipelinename':'name', 'segmentname':'unit_name',
                                   'startyear1': 'start_year', 'capacity': 'given_capacity','capacitybcm/y': 'capacity', 'startstate/province': 'subnat',
                                   'startregion': 'region', 'endstate/province': 'subnat2', 'endregion': 'region2', 'otherenglishnames': 'other-name',
                                    'otherlanguageprimarypipelinename': 'other-local',
                                   },
                      'EGT-term': {'comboid':'pid','wiki': 'url', 'terminalname': 'name',
                                   'unitname': 'unit_name', 'country': 'areas', 'capacity': 'given_capacity','capacityinmtpa': 'capacity', 'startyear1': 'start_year', 'region': 'region',
                                   'state/province': 'subnat', 'otherlanguagename': 'other-name'},
                        }

# which trackers do have meaningful project ids


final_order_datadownload = ['Oil & Gas Plants', 'Coal Plants', 'Solar', 'Wind', 'Nuclear', 'Hydropower', 'Bioenergy', 'Geothermal', 'Coal Terminals', 'Oil & Gas Extraction', 'Coal Mines', 'Oil Pipelines', 'Gas Pipelines', 'LNG Terminals']
tracker_mult_countries = ['GGIT', 'GOIT'] # mult_countries Country List, Countries do not span multiple columns for goget 

tracker_to_fullname = {
                    "GCPT": "coal power station",
                    "GOGPT": "oil & gas power station",
                    "GBPT": "bioenergy power station",
                    "GNPT": "nuclear power plant",
                    "GSPT": "solar power plant",  # GSPT is used for both "solar thermal" and "solar PV"
                    "GWPT": "wind power plant",
                    "GHPT": "hydropower plant",
                    "GGPT": "geothermal power plant",
                    "GOGET-oil": "oil & gas extraction area",
                    # "GOGET - gas": "gas extraction area",
                    "GOIT": "oil pipeline",
                    # "GGIT-eu": "gas pipeline",
                    "GGIT": "gas pipeline",
                    "GGIT-import": "LNG import terminal",
                    "GGIT-export": "LNG export terminal",
                    "GCMT": "coal mine",
                    "GCTT": "coal terminal"
}


tracker_to_legendname = {
                    "GCPT": "coal-power-station",
                    "GOGPT": "oil-gas-power-station",
                    "GBPT": "bioenergy-power-station",
                    "GNPT": "nuclear-power-plant",
                    "GSPT": "solar-power-plant",  # GSPT is used for both "solar thermal" and "solar PV"
                    "GWPT": "wind-power-plant",
                    "GHPT": "hydropower-plant",
                    "GGPT": "geothermal-power-plant",
                    "GOGET-oil": "oil & gas extraction area",
                    # "GOGET - gas": "gas-extraction-area",
                    "GOIT": "oil-pipeline",
                    "GGIT": "gas-pipeline",
                    "GGIT-import": "LNG-import-terminal",
                    "GGIT-export": "LNG-export-terminal",
                    "GCMT": "coal-mine",
                    "GCTT": "coal-terminal"
}

# TODO ideally get this from map log gsheet
# DO THIS NOW TODO so that aet and gipt look done and latam still needs to do
# trackers_to_update = ['Coal Plants', 'Nuclear', 'Oil & Gas Plants'] # ['Coal Plants', 'Nuclear', 'Oil & Gas Plants']
# new_release_date = 'February 2025' # get from spreadsheet I manage 15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8
# previous_release = 'data/Africa-Energy-Tracker-data-July-2024.xlsx' # key 1B8fwCQZ3ZMCf7ZjQPqETKNeyFN0uNFZMFWw532jv480
# previous_map = 'data/africa_energy_tracker_2024-07-10.geojson' 
prev_key_dict = {'africa': '128rAsbENoUzzKJAv1V0Z3AuCc6kNanCclKJVGkSOmhM', 'latam': '1ZKY-jSs2vxXSq5dLkp6-qGbhaxhz9Sh9Xo50ZG3LG7Q', 'asia': '1x-n4YLSRA3RIz80Jm5yfyWiMtbVfYHhOtHXsWhg3d-k', 'europe': '1h8Nr8lJJiUIsSIzEmwnici4Js9Brxt7GChDo_DBQF2s', 'integrated': '1SZVpnXQ1iE5kJJfmAZQ64q9LaG4wfq4urVX7jdBmIlk'} # ideally pull this from the results tabs in the map log sheet
# also TODO ideally save new release data file of map to gsheets and put htat link in the results tab
# if in colab could save to tracker release and update this dict automatically
# print('Handle multi tracker map creation for more than just AET')

multi_tracker_log_sheet_key = '15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8'
source_data_tab = ['source']
map_tab = ['map']
regional_multi_map_tab = ['regional_multi_map'] # regional 

multi_tracker_countries_sheet = '1UUTNERZYT1kHNMo_bKpwSGrUax9WZ8eyGPOyaokgggk'
# will be commenting all this out soon! get to map file
# tracker_folder = 'africa-energy'
# path_for_test_results = gem_path + tracker_folder + '/test_results/'
# path_for_data_dwnld = gem_path + tracker_folder + '/dt_dwnld/'

# geojson_file_of_all_africa = f'africa_energy_tracker_{iso_today_date}.geojson'
# path_for_download_and_map_files = gem_path + tracker_folder + '/compilation_output/' + iso_today_date_folder

# os.makedirs(path_for_download_and_map_files, exist_ok=True) not needed can likely delet
# os.makedirs(path_for_data_dwnld, exist_ok=True)

testing_path = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/'

# use about page from global releases

about_page_ggit_goit = {
    "LNG Terminals": "1nyhaAHdIG7ds5ypC8QNPD6HODNo0hh6VYKL9CjG2WnE",
    "Gas Pipelines": "1llzDMAXX7xJn3j4d6JQ2UjebgVpRFDBkZ4QTtUPmSHg",
    "Oil Pipelines": "12bhnTJ5kaia187ZvX9qWshfs4btmZuTpzPj2Jz7ct6Y", 
}

goit_geojson = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GOIT-Oil-NGL-Pipelines-2024-10-29.geojson'#'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GOIT-Oil-NGL-Pipelines-2024-06 copy.geojson'
ggit_lng_geojson = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GGIT-LNG-Terminals-2024-09 DATA TEAM COPY.geojson'
ggit_geojson = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GGIT-Gas-Pipelines-2024-12.geojson' #'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GGIT-Gas-Pipelines-2023-12 copy.geojson'

ggit_lng_eu_geojson = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-EGT-Terminals-2025-02 DATA TEAM COPY.geojson'
ggit_eu_geojson = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-EGT-Gas-Hydrogen-Pipelines-2025-02 DATA TEAM COPY.geojson'


# fixed routes and capacity conversions goit (capacity boed) and ggit (route) Oct 23rd 2024
# merge on projectID only specific columns so as to keep rest of data consistent with public release 
# temporary until next release
goit_cap_updated = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GOIT-Oil-NGL-Pipelines-2024-10-29.geojson'
# shouldn't need these anymore FEB 24th
# ggit_routes_updated = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/GEM-GGIT-Gas-Pipelines-2024-12 DATA TEAM COPY.geojson'
# ggit_eu_temp = '/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/source/Europe-Gas-Tracker-2024-05 DATA TEAM COPY.xlsx' # convert to geojson and add in missing coords from global json file 


full_country_list = [
    "Algeria", "Angola", "Benin", "Botswana", "British Indian Ocean Territory", "Burkina Faso", 
    "Burundi", "Cabo Verde", "Cameroon", "Central African Republic", "Chad", "Comoros", "DR Congo", 
    "Republic of the Congo", "Côte d'Ivoire", "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", 
    "Eswatini", "Ethiopia", "French Southern Territories", "Gabon", "The Gambia", "Ghana", "Guinea", 
    "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania", 
    "Mauritius", "Mayotte", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria", "Réunion", "Rwanda", 
    "Saint Helena, Ascension, and Tristan da Cunha", "Sao Tome and Principe", "Senegal", "Seychelles", 
    "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia", 
    "Uganda", "Western Sahara", "Zambia", "Zimbabwe",
    
    "Anguilla", "Antigua and Barbuda", "Argentina", "Aruba", "Bahamas", "Barbados", "Belize", "Bermuda", 
    "Bolivia", "Bonaire, Sint Eustatius, and Saba", "Bouvet Island", "Brazil", "Canada", "Cayman Islands", 
    "Chile", "Colombia", "Costa Rica", "Cuba", "Curaçao", "Dominica", "Dominican Republic", "Ecuador", 
    "El Salvador", "Falkland Islands", "French Guiana", "Greenland", "Grenada", "Guadeloupe", "Guatemala", 
    "Guyana", "Haiti", "Honduras", "Jamaica", "Martinique", "Mexico", "Montserrat", "Nicaragua", "Panama", 
    "Paraguay", "Peru", "Puerto Rico", "Saint Barthélemy", "Saint Kitts and Nevis", "Saint Lucia", 
    "Saint Martin (French part)", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", 
    "Sint Maarten (Dutch part)", "South Georgia and the South Sandwich Islands", "Suriname", 
    "Trinidad and Tobago", "Turks and Caicos Islands", "United States", "Uruguay", "Venezuela", 
    "Virgin Islands (British)", "Virgin Islands (U.S.)",
    
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia", "China", 
    "Cyprus", "Georgia", "Hong Kong", "India", "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan", 
    "Kazakhstan", "North Korea", "South Korea", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Macao", 
    "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal", "Oman", "Pakistan", "Palestine", "Philippines", 
    "Qatar", "Saudi Arabia", "Singapore", "Sri Lanka", "Syria", "Taiwan", "Tajikistan", "Thailand", 
    "Timor-Leste", "Türkiye", "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen",
    
    "Åland Islands", "Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", 
    "Bulgaria", "Croatia", "Czech Republic", "Denmark", "Estonia", "Faroe Islands", "Finland", "France", 
    "Germany", "Gibraltar", "Greece", "Guernsey", "Holy See", "Hungary", "Iceland", "Ireland", "Isle of Man", 
    "Italy", "Jersey", "Kosovo", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "North Macedonia", 
    "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "Norway", "Poland", "Portugal", "Romania", 
    "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Svalbard and Jan Mayen", "Sweden", 
    "Switzerland", "Ukraine", "United Kingdom",
    
    "American Samoa", "Australia", "Christmas Island", "Cocos (Keeling) Islands", "Cook Islands", "Fiji", 
    "French Polynesia", "Guam", "Heard Island and McDonald Islands", "Kiribati", "Marshall Islands", 
    "Micronesia", "Nauru", "New Caledonia", "New Zealand", "Niue", "Norfolk Island", 
    "Northern Mariana Islands", "Palau", "Papua New Guinea", "Pitcairn", "Samoa", "Solomon Islands", 
    "Tokelau", "Tonga", "Tuvalu", "United States Minor Outlying Islands", "Vanuatu", "Wallis and Futuna"
]

africa_countries = [
    "Algeria", "Angola", "Angola-Republic of the Congo", "Benin", "Botswana",
    "British Indian Ocean Territory", "Burkina Faso", "Burundi", "Cabo Verde",
    "Cameroon", "Central African Republic", "Chad", "Comoros", "Côte d'Ivoire",
    "Djibouti", "DR Congo", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini",
    "Ethiopia", "French Southern Territories", "Gabon", "Ghana", "Guinea",
    "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar",
    "Malawi", "Mali", "Mauritania", "Mauritius", "Mayotte", "Morocco",
    "Mozambique", "Namibia", "Niger", "Nigeria", "Republic of the Congo",
    "Réunion", "Rwanda", "Saint Helena, Ascension, and Tristan da Cunha",
    "Sao Tome and Principe", "Senegal", "Senegal-Mauritania", "Seychelles",
    "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan",
    "Tanzania", "The Gambia", "Togo", "Tunisia", "Uganda", "Western Sahara",
    "Zambia", "Zimbabwe"
]


asia_countries = [
    # South Asia
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Iran",
    "Maldives", "Nepal", "Pakistan", "Sri Lanka",

    # Southeast Asia
    "Brunei", "Cambodia", "Indonesia", "Laos", "Malaysia",
    "Myanmar", "Philippines", "Singapore", "Thailand",
    "Timor-Leste", "Vietnam", "Thailand-Malaysia",  "Vietnam-Malaysia",

    # East Asia
    "China", "China-Japan", "Hong Kong", "Japan", "Macao",
    "Mongolia", "North Korea", "South Korea", "Taiwan",

    # Multinational or Maritime Areas
    "South China Sea"
]


europe_countries = [
    'Åland Islands', 'Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 
    'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Czech Republic', 
    'Denmark', 'Estonia', 'Faroe Islands', 'Finland', 'France', 'Germany', 
    'Gibraltar', 'Greece', 'Guernsey', 'Holy See', 'Hungary', 'Iceland', 
    'Ireland', 'Isle of Man', 'Italy', 'Jersey', 'Kosovo', 'Latvia', 
    'Liechtenstein', 'Lithuania', 'Luxembourg', 'North Macedonia', 'Malta', 
    'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'Norway', 'Poland', 
    'Portugal', 'Romania', 'Israel', 'San Marino', 'Serbia', 'Slovakia', 
    'Slovenia', 'Spain', 'Svalbard and Jan Mayen', 'Sweden', 'Switzerland', 
    'Ukraine', 'United Kingdom', 'Cyprus', 'Türkiye'
]



latam_countries = [
    # Caribbean
    "Anguilla", "Antigua and Barbuda", "Aruba", "Bahamas", "Barbados",
    "Belize", "Cayman Islands", "Cuba", "Curaçao", "Dominica",
    "Dominican Republic", "Grenada", "Guadeloupe", "Haiti", "Jamaica",
    "Martinique", "Montserrat",  "Saint Barthélemy",
    "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin (French part)",
    "Saint Vincent and the Grenadines", "Sint Maarten (Dutch part)",
    "Trinidad and Tobago", "Turks and Caicos Islands", "Virgin Islands (British)",
   # "Virgin Islands (U.S.)", "Puerto Rico", -  gregor excludes

    # Central America
    "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Mexico",
    "Nicaragua", "Panama",

    # South America
    "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
    "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname",
    "Uruguay", "Venezuela",

    # Special Cases
    "Bonaire, Sint Eustatius, and Saba", "Bouvet Island",
    "Falkland Islands", "South Georgia and the South Sandwich Islands",
    "Venezuela-Trinidad and Tobago"
]



geo_mapping = {'africa': africa_countries,
            'asia': asia_countries,
            'europe': europe_countries,
            'latam': latam_countries,
            'global': full_country_list,
            '': full_country_list
            }
    # when was in map class
    # geo = self.geo
    # self.needed_geo = geo_mapping[geo]
    
dd_tab_mapping = {'africa': 'Africa Energy',
            'asia': 'Asia Gas',
            'europe': 'Europe Gas',
            'latam': 'Portal Energético',
            'internal': 'internal',
            
            }