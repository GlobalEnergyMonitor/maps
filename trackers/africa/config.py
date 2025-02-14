from datetime import datetime, timedelta 
import os
import gspread

test = False
refine = False # TEST THIS SOON!
augmented = True
summary_create = False
about_create = False
map_create = True
dwlnd_create = False
local_copy = False # problem here 
slowmo = False
data_filtering = True
# Get today's date
today_date = datetime.today()
yesterday = today_date - timedelta(days=1)
iso_yesterday_date = yesterday.isoformat()
# Format the date in ISO format
iso_today_date = today_date.isoformat().split('T')[0]
iso_today_date_folder = f'{iso_today_date}/'
client_secret = "Desktop/GEM_INFO/client_secret.json"
client_secret_full_path = os.path.expanduser("~/") + client_secret
gem_path = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/'
gspread_creds = gspread.oauth(
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        credentials_filename=client_secret_full_path,
        # authorized_user_filename=json_token_name,
    )
region_cols = 'Region'
list_official_tracker_names = ['Oil & Gas Plants', 'Coal Plants', 'Solar', 'Wind', 'Hydropower', 'Geothermal', 'Bioenergy', 'Nuclear', 'Coal Mines', 'Coal Terminals', 'Oil & Gas Extraction', 'Oil Pipelines', 'Gas Pipelines', 'LNG Terminals']

gas_only_maps = ['AGT', 'EGT', 'asia', 'europe']
non_gsheet_data = ['Gas Pipelines', 'LNG Terminals', 'Oil Pipelines']
conversion_key = '1fOPwhKsFVU5TnmkbEyPOylHl3XKZzDCVJ29dtTngkew'
conversion_tab = ['data']
gcmt_closed_tab = 'Global Coal Mine Tracker (Close'
# TODO make it so that each map has it's only set of final cols, so smallest csv possible, helpful for regional gas mostly ...
final_cols = ['mapname','tracker acro','official_name','url', 'areas','name', 'unit_name', 'capacity', 'status', 'start_year', 'subnat', 'region', 'owner', 'parent', 'tracker', 'tracker_custom',
       'original_units', 'conversion_factor', 'geometry', 'river', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2',
       'production', 'Latitude', 'Longitude', 'id', 'prod_oil', 'prod_gas', 'prod_year_oil', 'prod_year_gas']

renaming_cols_dict = {'GOGPT': {'GEM unit ID': 'id','Wiki URL': 'url','Country/Area': 'areas', 'Plant name': 'name', 'Unit name': 'unit_name', 
                                'Capacity (MW)': 'capacity', 'Status': 'status',
                                'Start year': 'start_year', 'Subnational unit (province, state)': 'subnat', 'Region': 'region', 'Owner':'owner', 'Parent': 'parent'},
                      'GCPT': {'GEM unit/phase ID': 'id','Country/Area': 'areas', 'Wiki URL':'url',
                                   'Plant name': 'name', 'Unit name':'unit_name',
                                   'Owner': 'owner', 'Parent': 'parent', 'Capacity (MW)': 'capacity', 'Status': 'status', 
                                   'Start year': 'start_year', 'Subnational unit (province, state)': 'subnat', 'Region': 'region'},
                      'GSPT': {'GEM phase ID':'id','Country/Area': 'areas', 'Project Name': 'name', 'Phase Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GWPT': {'GEM phase ID': 'id','Country/Area': 'areas', 'Project Name': 'name', 'Phase Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GNPT': {'GEM unit ID': 'id','Country/Area': 'areas', 'Project Name': 'name', 'Phase Name': 'unit_name',
                               'Capacity (MW)': 'capacity', 'Status': 'status', 'Start year': 'start_year', 'Owner': 'owner',
                               'Region': 'region', 'State/Province':'subnat', 'Wiki URL': 'url'},
                      'GHPT': {'GEM unit ID':'id','Country 1': 'areas', 'Country 2': 'area2','Project Name': 'name', 'Country 1 Capacity (MW)': 'capacity1', 'Country 2 Capacity (MW)': 'capacity2',
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
                                'GEM region': 'region','Owner': 'owner', 'Parent': 'parent', 'Wiki URL': 'url', 'Production - Oil (Million bbl/y)': 'prod_oil', 'Production - Gas (Million m³/y)': 'prod_gas',
                                'Production - Total (Oil, Gas and Hydrocarbons) (Million boe/y)': 'capacity','Production Year - Oil': 'prod_year_oil', 'Production Year - Gas': 'prod_year_gas'
                                , 'Country List':'mult_countries'},
                      'GCMT': {'GEM Mine ID':'id','Country': 'areas', 'Mine Name': 'name', 'Status': 'status', 'Owners': 'owner', 'Parent Company': 'parent', 'Capacity (Mtpa)': 'capacity', 
                               'Production (Mtpa)':'production', 'Opening Year': 'start_year', 'State, Province': 'subnat', 'Region': 'region', },
                      'GOIT': {'ProjectID':'id','Countries': 'areas', 'Wiki': 'url', 'PipelineName': 'name', 'SegmentName': 'unit_name', 'Status': 'status', 'Owner': 'owner',
                               'Parent': 'parent', 'CapacityBOEd': 'capacity', 'StartYear1': 'start_year', 'StartState/Province':'subnat', 'StartRegion': 'region',
                               'EndState/Province': 'subnat2', 'EndRegion': 'region2'},
                      'GGIT': {'ProjectID':'id','Countries': 'areas','Wiki': 'url',
                                   'PipelineName':'name', 'SegmentName':'unit_name', 'Status':'status', 'Owner':'owner', 'Parent': 'parent',
                                   'StartYear1': 'start_year', 'CapacityBcm/y': 'capacity', 'StartState/Province': 'subnat',
                                   'StartRegion': 'region', 'EndState/Province': 'subnat2', 'EndRegion': 'region2'
                                   }, 
                      'GGIT-lng': {'ComboID':'id','Wiki': 'url', 'TerminalName': 'name',
                                   'UnitName': 'unit_name', 'Status': 'status', 'Country': 'areas', 'Owner': 'owner', 
                                   'Parent': 'parent', 'CapacityInMtpa': 'capacity', 'StartYearEarliest': 'start_year', 'Region': 'region', 
                                   'State/Province': 'subnat'}}

final_order_datadownload = ['Oil & Gas Plants', 'Coal Plants', 'Solar', 'Wind', 'Nuclear', 'Hydropower', 'Bioenergy', 'Geothermal', 'Coal Terminals', 'Oil & Gas Extraction', 'Coal Mines', 'Oil Pipelines', 'Gas Pipelines', 'LNG Terminals']
tracker_mult_countries = ['GGIT', 'GOIT'] # mult_countries Country List, Countries need this so don't filter on region and miss ones where region start or end is asia not africa bi continental GGIT 8 missing africa GOGET is different because only one region and its created by Scott for the map file so go by region

dtype_spec = {} #{'Latitude': float, 'Longitude': float}
numeric_cols = [] #TODO 

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

# TODO ideally get this from map log gsheet
# DO THIS NOW TODO so that aet and gipt look done and latam still needs to do
trackers_to_update = ['Coal Plants', 'Nuclear', 'Oil & Gas Plants'] # ['Coal Plants', 'Nuclear', 'Oil & Gas Plants']
new_release_date = 'September 2024' # get from spreadsheet I manage 15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8
previous_release_date = 'July 2024'
# previous_release = 'data/Africa-Energy-Tracker-data-July-2024.xlsx' # key 1B8fwCQZ3ZMCf7ZjQPqETKNeyFN0uNFZMFWw532jv480
# previous_map = 'data/africa_energy_tracker_2024-07-10.geojson' 
prev_key_dict = {'africa': '1B8fwCQZ3ZMCf7ZjQPqETKNeyFN0uNFZMFWw532jv480', 'latam': '1rhGsbtGrg1VjeaYRmlzvpEZ-FT963AkITV7ORyDsv9A', 'asia': '1q_Zwn_FlLulFvyJPi2pAjJOR7inDvo5nvIlQuZKAwrs', 'europe': '1IYM9SPoq2xSu4dr3H2sXXwuKKvb505FHG6vZKRAV_DE', 'GIPT': '1SZVpnXQ1iE5kJJfmAZQ64q9LaG4wfq4urVX7jdBmIlk'} # ideally pull this from the results tabs in the map log sheet
# also TODO ideally save new release data file of map to gsheets and put htat link in the results tab
# prev_key = '1B8fwCQZ3ZMCf7ZjQPqETKNeyFN0uNFZMFWw532jv480'

# print('Handle multi tracker map creation for more than just AET')

multi_tracker_log_sheet_key = '15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8'
multi_tracker_log_sheet_tab = ['multi_map']
prep_file_tab = ['prep_file']
multi_tracker_countries_sheet = '1UUTNERZYT1kHNMo_bKpwSGrUax9WZ8eyGPOyaokgggk'

# will be commenting all this out soon! get to map file
tracker_folder = 'africa-energy'
path_for_test_results = gem_path + tracker_folder + '/test_results/'
path_for_data_dwnld = gem_path + tracker_folder + '/dt_dwnld/'

geojson_file_of_all_africa = f'africa_energy_tracker_{iso_today_date}.geojson'
path_for_download_and_map_files = gem_path + tracker_folder + '/compilation_output/' + iso_today_date_folder

os.makedirs(path_for_download_and_map_files, exist_ok=True)
os.makedirs(path_for_data_dwnld, exist_ok=True)

testing_path = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/testing/'

# TODO Maisie likes the spreadsheet so we can all see what's going on
# TODO create a better spreadsheet


about_page_ggit_goit = {
    "LNG Terminals": "1VwxZgLNSXiuGnwzgC1CPcnLrI-PGdseP_RDQJnzLuAY",
    "Gas Pipelines": "1rcFIqHjVpZ7UFNdP1TE7BeDKmraOjXof8gLtZ49G77U",
    "Oil Pipelines": "12bhnTJ5kaia187ZvX9qWshfs4btmZuTpzPj2Jz7ct6Y", 
}

goit_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GOIT-Oil-NGL-Pipelines-2024-06.geojson'
ggit_lng_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GGIT-LNG-Terminals-2024-01.geojson'
ggit_geojson = '/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/africa-energy/compilation_input/GEM-GGIT-Gas-Pipelines-2023-12.geojson'
# TODO convert geojson to csv upload to googlesheets and use like that ... same system as other ones

tracker_summary_pages = {
    "Oil and Gas Plants": [
        "Oil and Gas Plants by Country/Area (MW)",
        "Oil and Gas Plants by Country/Area (Power Stations)",
        "Oil and Gas Plants by Country/Area (Units)",
        "Oil and Gas Plants by Region (MW)",
        "Ownership of Oil and Gas Plants in Africa (MW)",
        "Oil and Gas Plants by Technology by Country/Area (MW)"
    ],
    "Coal Plants": [
        "Coal Plants by Country/Area (MW)",
        "Coal Plants by Country/Area (Power Stations)",
        "Coal Plants by Country/Area (Units)",
        "Coal Plants by Region (MW)"
    ],
    "Geothermal": [
        "Geothermal Power Capacity by Country/Area (MW)",
        "Geothermal Unit Count by Country/Area",
        "Geothermal Power Capacity by Installation Type and Region (MW)",
        "Geothermal Operational Capacity Installed by Country/Area and Year (MW)",
        "Geothermal Prospective Capacity by Country/Area and Year (MW)"
    ],
    "Bioenergy": [
        "Bioenergy Capacity by Country/Area (MW)",
        "Bioenergy Unit Count by Country/Area",
        "Bioenergy Fuel Types by Country/Area",
        "Bioenergy Capacity by Region (MW)",
        "Bioenergy Unit Count by Region",
        "Bioenergy Fuel Types by Region",
        "Bioenergy Operational Capacity Added by Country/Area and Year (MW)"
    ],
    "Wind": [
        "Wind Farm Capacity by Country/Area (MW)",
        "Wind Farm Phase Count by Country/Area",
        "Wind Farm Capacity by Region (MW)",
        "Wind Farm Phase Count by Region",
        "Wind Farm Capacity by Installation Type and Region (MW)",
        "Wind Farm Operational Capacity by Country/Area and Year (MW)",
        "Wind Farm Prospective Capacity by Country/Area and Year (MW)"
    ],
    "Solar": [
        "Solar Farm Capacity by Country/Area (MW)",
        "Solar Farm Phase Count by Country/Area",
        "Solar Farm Capacity by Region (MW)",
        "Solar Farm Phase Count by Region",
        "Solar Farm Operational Capacity by Country/Area and Year (MW)",
        "Solar Farm Prospective Capacity by Country/Area and Year (MW)"
    ],
    "Hydropower": [
        "Hydropower Capacity by Country/Area (MW)",
        "Hydropower Project Count by Country/Area",
        "Hydropower Capacity by Region and Subregion (MW)",
        "Hydropower Project Count by Region and Subregion",
        "Hydropower Capacity by Region and Type (MW)"
    ],
    "Nuclear": [
        "Nuclear Power Capacity by Country/Area (MW)",
        "Nuclear power Unit Count by Country/Area",
        "Nuclear Power Capacity by Region and Subregion (MW)",
        "Nuclear Power Unit Count by Region and Subregion",
        "Nuclear Power Capacity by Reactor Type and Region (MW)"
    ],
    "Oil & Gas Pipelines": [
        "Gas Pipeline Length by Country/Area (km)",
        "Gas Pipeline Length by Region (km)",
        "Oil Pipeline Length by Country/Area (km)",
        "Oil Pipeline Length by Region (km)"
    ],
    "LNG Terminals": [
        "LNG Export Projects by Region",
        "LNG Export Projects by Country/Area",
        "LNG Import Projects by Region",
        "LNG Import Projects by Country/Area",
        "LNG Export Capacity by Region (mtpa)",
        "LNG Export Capacity by Country/Area (mtpa)",
        "LNG Import Capacity by Region (mtpa)",
        "LNG Import Capacity by Country/Area (mtpa)",
        "LNG Terminals by Start Year",
        "LNG Capacity by Start Year (mtpa)"
    ],
    "Coal Terminals": [
        "Number of Coal Terminals by Country/Area",
        "Coal Terminal Capacity by Country/Area",
        "Coal Terminal Capacity by Region",
        "Coal Terminal Capacity by Type (Import/Export)"
    ],
    "Oil & Gas Extraction": [
        "Oil & Gas Extraction Sites by Region",
        "Oil & Gas Extraction Sites by Country/Area",
        "Oil Production by Sub Region",
        "Oil Production by Country/Area",
        "Gas Production by Region",
        "Gas Production by Country/Area"
    ],
    "Coal Mines": [
        "Number of Coal Mines by Country/Area"
    ]
}


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

Africa_countries = [
    "Algeria",
    "Angola",
    "Benin",
    "Botswana",
    "British Indian Ocean Territory",
    "Burkina Faso",
    "Burundi",
    "Cabo Verde",
    "Cameroon",
    "Central African Republic",
    "Chad",
    "Comoros",
    "DR Congo",
    "Republic of the Congo",
    "Côte d'Ivoire",
    "Djibouti",
    "Egypt",
    "Equatorial Guinea",
    "Eritrea",
    "Eswatini",
    "Ethiopia",
    "French Southern Territories",
    "Gabon",
    "The Gambia",
    "Ghana",
    "Guinea",
    "Guinea-Bissau",
    "Kenya",
    "Lesotho",
    "Liberia",
    "Libya",
    "Madagascar",
    "Malawi",
    "Mali",
    "Mauritania",
    "Mauritius",
    "Mayotte",
    "Morocco",
    "Mozambique",
    "Namibia",
    "Niger",
    "Nigeria",
    "Réunion",
    "Rwanda",
    "Saint Helena, Ascension, and Tristan da Cunha",
    "Sao Tome and Principe",
    "Senegal",
    "Seychelles",
    "Sierra Leone",
    "Somalia",
    "South Africa",
    "South Sudan",
    "Sudan",
    "Tanzania",
    "Togo",
    "Tunisia",
    "Uganda",
    "Western Sahara",
    "Zambia",
    "Zimbabwe"
  ]