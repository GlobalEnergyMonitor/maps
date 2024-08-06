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
# not needed anymore, update below
# prep_file_key = '12ltof1T1pxwc_iDTN4PpkcfygLXhAHJ7Or0caJvbmNk'
# prep_file_tab = ['prep']

# last updated Jul 30th for nuclear and coal 
gsheets_acro_dict = {
    # all trackers minus goit, ggit and ggit-lng
    "GOGPT": ["1dosICr3DU05hIRawCLB0EK4rv3cn44fwBAKjTTqmLDo", "Gas & Oil Units"],
    "GCPT": ["1zrVobNcD0HiBfko4Z8N9BUaMXxEvNNrXFxzk42q2ZBI", "Units"],
    "GSPT": ["1FTGYWZsBG20e4hyTkdgpondcqdD2kTam6d9YcvqREYo", "20 MW+; 1-20 MW"],
    "GWPT": ["13Td6X2iQSZljmiu5q_Tvd1LYWf1hEMf6UwJGKjGPGGU", "Data"],
    "GNPT": ["1zCcO9LwVmiQZBOGqlwKGYgZ5lAnBKJ91hjwWcbUw5nQ", "Data"],
    "GHPT": ["1cqLe0xOx7FLpfaGZhtVnV-bhuKgaczHPtXzCRIgy_RQ", "Data"],
    "GBPT": ["10Clsb8auutXy4iBm6c7HywZjSbNKUiho9NHzZmC2-Bs", "Data"],
    "GGPT": ["1j0Q0s6koeUYlCvp-beBnJX-tW1RHh8830eNwW4LW-Sw", "Data"],
    "GCTT": ["1gY2X3cDWmBDHVFZcDesqlfY9i7aEtqSfM-fuBeUiV7o", "Coal Terminals"],
    "GOGET": ["1ZeHDitJDnktiy2TrrV20SdZOmiJS1btycqlyDQBtUeU", "Data"],
    "GCMT": ["1OJIEYKHR6L9-w1jbSPQr01X3w4Ot0qOWoKaVuZCrEc4", "Global Coal Mine Tracker (Non-C"]
}

about_page_ggit_goit = {
    "GGIT-lng": ["1VwxZgLNSXiuGnwzgC1CPcnLrI-PGdseP_RDQJnzLuAY"],
    "GGIT": ["1rcFIqHjVpZ7UFNdP1TE7BeDKmraOjXof8gLtZ49G77U"],
    "GOIT": ["12bhnTJ5kaia187ZvX9qWshfs4btmZuTpzPj2Jz7ct6Y"], 
}

goit_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GOIT-Oil-NGL-Pipelines-2024-05-13.geojson'
ggit_lng_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GGIT-LNG-Terminals-2024-01.geojson'
ggit_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GGIT-Gas-Pipelines-2023-12.geojson'

region_cols = 'Region'
trackers_to_update = [('GCPT', 'July 2024'), ('GNPT', 'July 2024')]
previous_release = 'data/Africa-Energy-Tracker-data-July-2024.xlsx' # key 1B8fwCQZ3ZMCf7ZjQPqETKNeyFN0uNFZMFWw532jv480
previous_map = 'data/africa_energy_tracker_2024-07-10.geojson' 

