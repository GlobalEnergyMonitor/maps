from datetime import date
import os

# Get today's date
today_date = date.today()
# Format the date in ISO format
iso_today_date = today_date.isoformat()
iso_today_date_folder = f'{iso_today_date}/'
client_secret = "Desktop/GEM_INFO/client_secret.json"

client_secret_full_path = os.path.expanduser("~/") + client_secret

gem_path = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/'

tracker_folder = 'africa-energy'
path_for_test_results = gem_path + tracker_folder + '/test_results/'
path_for_data_dwnld = gem_path + tracker_folder + '/dt_dwnld/'

geojson_file_of_all_africa = f'africa_energy_tracker_{iso_today_date}.geojson'
path_for_download_and_map_files = gem_path + tracker_folder + '/compilation_output/' + iso_today_date_folder

goit_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GOIT-Oil-NGL-Pipelines-2024-05-13.geojson'
ggit_lng_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GGIT-LNG-Terminals-2024-01.geojson'
ggit_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GGIT-Gas-Pipelines-2023-12.geojson'

os.makedirs(path_for_download_and_map_files, exist_ok=True)
os.makedirs(path_for_data_dwnld, exist_ok=True)


africa_countries = [
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso',
    'Burundi', 'Cameroon', 'Cape Verde', 'Central African Republic', 'Chad',
    'Comoros', "Côte d'Ivoire", 'Djibouti', 'DR Congo', 'Egypt', 
    'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 
    'The Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya', 
    'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi',
    'Mali', 'Mauritania', 'Mauritius', 'Mayotte (France)', 'Morocco', 
    'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Republic of the Congo', 
    'Réunion (France)', 'Rwanda', 'Saint Helena, Ascension and Tristan da Cunha (UK)', 
    'São Tomé and Príncipe', 'Senegal',
    'Seychelles', 'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 
    'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda',
    'Western Sahara', 'Zambia', 'Zimbabwe', 
]

filler_url_tracker = {}

bbox_africa = '-24.433851,-45.706179,69.257813,39.232253' #lng lat epsg 4326
prep_file_key = '12ltof1T1pxwc_iDTN4PpkcfygLXhAHJ7Or0caJvbmNk'
prep_file_tab = ['prep']

conversion_key = '1fOPwhKsFVU5TnmkbEyPOylHl3XKZzDCVJ29dtTngkew'
conversion_tab = ['data']

final_cols = ['url', 'areas','name', 'unit_name', 'capacity', 'status', 'start_year', 'subnat', 'region', 'owner', 'parent', 'tracker', 'tracker_custom',
       'original_units', 'conversion_factor', 'geometry', 'river', 'area', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2',
       'production', 'Latitude', 'Longitude', 'id', 'prod_oil', 'prod_gas', 'prod_year_oil', 'prod_year_gas']



renaming_cols_dict = {'GOGPT': {'GEM unit ID': 'id','Wiki URL': 'url','Country': 'areas', 'Plant name': 'name', 'Unit name': 'unit_name', 
                                'Capacity (MW)': 'capacity', 'Status': 'status',
                                'Start year': 'start_year', 'Subnational unit (province, state)': 'subnat', 'Region': 'region', 'Owner':'owner', 'Parent': 'parent'},
                      'GCPT': {'GEM unit/phase ID': 'id','Country': 'areas', 'Wiki URL':' url',
                                   'Plant name': 'name', 'Unit name':'unit_name',
                                   'Owner': 'owner', 'Parent': 'parent', 'Capacity (MW)': 'capacity', 'Status': 'status', 
                                   'Start year': 'start_year', 'Subnational unit (province, state)': 'subnat', 'Region': 'region'},
                      'GSPT': {'GEM phase ID':'id','Country/Area': 'areas', 'Project Name': 'name', 'Phase Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GWPT': {'GEM phase ID': 'id','Country/Area': 'areas', 'Project Name': 'name', 'Phase Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GNPT': {'GEM unit ID': 'id','Country': 'areas', 'Project Name': 'name', 'Phase Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GHPT': {'GEM unit ID':'id','Country 1': 'area', 'Country 2': 'area2','Project Name': 'name', 'Country 1 Capacity (MW)': 'capacity1', 'Country 2 Capacity (MW)': 'capacity2',
                               'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region 1': 'region', 'Region 2': 'region2','State/Province 1':'subnat', 'State/Province 2':'subnat2', 
                               'Wiki URL': 'url', 'River / Watercourse': 'river'},
                      'GBPT': {'GEM phase ID':'id','Country': 'areas', 'Project name': 'name', 'Unit Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Operating status': 'status', 'Unit start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GGPT': {'GEM unit ID':'id','Country': 'areas', 'Project Name': 'name', 'Unit Name': 'unit_name',
                               'Unit Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GCTT': {'Terminal ID':'id','Coal Terminal Name': 'name', 'GEM Wiki': 'url', 'Status': 'status', 'Owner': 'owner', 'Capacity (Mt)':'capacity',
                               'Opening Year': 'start_year', 'Region': 'region', 'State/Province':'subnat', 'Country': 'areas'},
                      'GOGET': {'Unit ID':'id', 'Wiki name': 'name', 'Country': 'areas', 'Subnational unit (province, state)': 'subnat', 'Status': 'status', 'Discovery year': 'start_year', 'Production start year': 'prod_start_year',
                                'GEM region': 'region','Owner': 'owner', 'Parent': 'parent', 'Wiki URL': 'url', 'Production - Oil (Million bbl/y)': 'prod_oil', 'Production - Gas (Million m³/y)': 'prod_gas','Production - Total (Oil, Gas and Hydrocarbons) (Million boe/y)': 'capacity','Production Year - Oil': 'prod_year_oil', 'Production Year - Gas': 'prod_year_gas'},
                      'GCMT': {'GEM Mine ID':'id','Country': 'areas', 'Mine Name': 'name', 'Status': 'status', 'Owners': 'owner', 'Parent Company': 'parent', 'Capacity (Mtpa)': 'capacity', 
                               'Production (Mtpa)':'production', 'Opening Year': 'start_year', 'State, Province': 'subnat', 'Region': 'region', },
                      'GOIT': {'ProjectID':'id','Countries': 'areas', 'Wiki': 'url', 'PipelineName': 'name', 'SegmentName': 'unit_name', 'Status': 'status', 'Owner': 'owner',
                               'Parent': 'parent', 'CapacityBOEd': 'capacity', 'StartYear1': 'start_year', 'StartState/Province':'subnat', 'StartRegion': 'region',
                               'EndState/Province': 'subnat2', 'EndRegion': 'region2',},
                      'GGIT': {'ProjectID':'id','Countries': 'areas','Wiki': 'url',
                                   'PipelineName':'name', 'SegmentName':'unit_name', 'Status':'status', 'Owner':'owner', 'Parent': 'parent',
                                   'StartYear1': 'start_year', 'CapacityBcm/y': 'capacity', 'StartState/Province': 'subnat',
                                   'StartRegion': 'region', 'EndState/Province': 'subnat2', 'EndRegion': 'region2',
                                   }, 
                      'GGIT-lng': {'ComboID':'id','Wiki': 'url', 'TerminalName': 'name',
                                   'UnitName': 'unit_name', 'Status': 'status', 'Country': 'areas', 'Owner': 'owner', 
                                   'Parent': 'parent', 'CapacityInMtpa': 'capacity', 'StartYearEarliest': 'start_year', 'Region': 'region', 
                                   'State/Province': 'subnat'}}

tracker_to_fullname = {
                    "GCPT": "coal power station",
                    "GOGPT": "oil & gas power station",
                    "GBPT": "bioenergy power station",
                    "GNPT": "nuclear power plant",
                    "GSPT": "solar power plant",  # GSPT is used for both "solar thermal" and "solar PV"
                    "GWPT": "wind power plant",
                    "GHPT": "hydropower plant",
                    "GGPT": "geothermal power plant",
                    "GOGET - oil": "oil & gas extraction area",
                    # "GOGET - gas": "gas extraction area",
                    "GOIT": "oil pipeline",
                    "GGIT": "gas pipeline",
                    "GGIT - import": "LNG import terminal",
                    "GGIT - export": "LNG export terminal",
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
                    "GOGET - oil": "oil & gas extraction area",
                    # "GOGET - gas": "gas-extraction-area",
                    "GOIT": "oil-pipeline",
                    "GGIT": "gas-pipeline",
                    "GGIT - import": "LNG-import-terminal",
                    "GGIT - export": "LNG-export-terminal",
                    "GCMT": "coal-mine",
                    "GCTT": "coal-terminal"
}

# tracker_to_dwnld_name = {
#                     "GCPT": "coal plants",
#                     "GOGPT": "oil & gas power station",
#                     "GBPT": "bioenergy power station",
#                     "GNPT": "nuclear power plant",
#                     "GSPT": "solar power plant",  # GSPT is used for both "solar thermal" and "solar PV"
#                     "GWPT": "wind power plant",
#                     "GHPT": "hydropower plant",
#                     "GGPT": "geothermal power plant",
#                     "GOGET":,
#                     "GOIT": "oil pipeline",
#                     "GGIT": "Gas Pipelines",
#                     "GGIT": "",
#                     "GCMT": "coal mine",
#                     "GCTT": "coal terminal"
# }

# concatted_file_path = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/concatted_df2024-06-24.csv'

filler_Angola = [17.47057255231345, -12.24586903613316]


# TODO get list of all google sheet keys and tabs including GGIT, GOIT and GGIT lng
list_of_keys_tabs = []