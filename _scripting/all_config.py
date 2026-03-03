from datetime import datetime
import os
import gspread
from numpy import true_divide
from creds import *
import logging
from pathlib import Path
import json

# Format the date in ISO format
# Get today's date
today_date = datetime.today()

iso_today_date = today_date.isoformat().split('T')[0]
iso_today_date_folder = f'{iso_today_date}/'

list_of_all_official = [
    "Oil & Gas Plants",
    "Coal Plants",
    "Solar",
    "Wind",
    "Nuclear",
    "Hydropower",
    "Bioenergy",
    "Geothermal",
    "Coal Terminals",
    "Oil & Gas Extraction",
    "Coal Mines",
    "LNG Terminals",
    "Gas Pipelines",
    "Oil Pipelines",
    "Iron & Steel",
    "Iron Ore Mines",
    "Plumes",
    "Chemicals",
    "Cement and Concrete",
    'Gas Finance',
    'Coal Project Finance'

]

pm_preview_mode = False # For Baird's testing work
trackers_to_update = ["Oil & Gas Extraction"]  # tab name in map tracker log sheet # Gas Finance

new_release_date = 'March_2026' # for within about page NEEDS TO BE FULL MONTH
releaseiso = '2026-03'
new_release_dateinput = input(f'In {new_release_date} format, with no spaces, tell me the public release date. Or press enter if {new_release_date} is the right month.')
if new_release_dateinput == '':
    new_release_dateinput = new_release_date

dd_only = False
nostopping = True
# add test local
localtestfile = '' #'../testinputfile.xlsx'
testval = '' #Mampak Oil and Gas Field (Brunei) #'Toscana FSRU' #optional for debugging Canatxx LNG Terminal 
testfilekey = '' # '1ivc-DkGvbAz8BW0LV2Q0XcZaB7s6q5hoUuVZTdxmxk8' #optional for debugging
testtracker = ''  #'ggit-lng'
simplified = False # True False to make a very barebones map files with coords and name and url (for speed tests gipt)
new_h2_data = False
priority = ["latam"]   # tracker_mapnames "europe", "asia", "latam", "africa", "ggit"
force_refresh_flag = True 
tracker_mapnames = ["europe", "africa", "integrated", "asia", "latam", "ggit", "goit", "goget", "gctt", "gcpt", "gcmt", "gogpt", "gspt", "gwpt", "gnpt", "gbpt", "ggpt", "ghpt", "gist", "gmet", "giomt", "ggft"]
about_templates_key = '1wrPJBqNuf5o-vzKYljlrWbjDtf_Ui7hR4JQM1p8gV7I' # new initiative to build about page for teams
final_cols = []
# st_path = Path(__file__).parent / '_steel_cols.json'
fcl_path = Path(__file__).parent / '_final_cols.json'
rd_path = Path(__file__).parent / '_renaming_cols.json'
# what is thetype here? 
# with open(st_path) as f:
#     steel_cols_list = json.load(f)
    # print(steel_cols) # dict
    # print(type(steel_cols))
with open(fcl_path) as f:
    final_cols_list = json.load(f)
    print(type(final_cols)) # list


with open(rd_path) as f:
    renaming_cols_dict = json.load(f)

def ensure_compilation_folders():
    """Ensure compilation_output folders exist in all tracker directories"""
    trackers_dir = Path(__file__).parent / 'trackers'
    
    for tracker_dir in trackers_dir.iterdir():
        if tracker_dir.is_dir() and not tracker_dir.name.startswith('.'):
            compilation_dir = tracker_dir / 'compilation_output'
            compilation_dir.mkdir(exist_ok=True)

ensure_compilation_folders() # should add to make folder for brand new tracker


# make necessary directories if they don't exist
folders_needed = ["logfiles/", 'local_pkl/', "metadata_files/"]
for folder in folders_needed:
    if not os.path.exists(folder): # TODO in future move to be ../logfiles
        os.mkdir(f"{folder}")
    # folder_dir = os.path.join(os.path.dirname(__file__), folder)
    # os.makedirs(folder_dir, exist_ok=True)
metadata_dir = os.path.join(os.path.dirname(__file__), 'metadata_files')
os.makedirs(metadata_dir, exist_ok=True)
local_pkl_dir = os.path.join(os.path.dirname(__file__), 'local_pkl')
os.makedirs(local_pkl_dir, exist_ok=True)
about_sheets_pkl_path = os.path.join(local_pkl_dir, f"About_sheets_{iso_today_date}.pkl")

# create logging functionality 
logpath = 'logfiles/'
logger = logging.getLogger(__name__)
log_file_path = f'{logpath}log_file_{iso_today_date}.log' 
logger.setLevel(logging.DEBUG)  # Set the lowest logging level for the logger
 
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# def getLogger(tracker_name): # TODO use Hannah's code to make logger better

    # iso_date = datetime.now().strftime("%Y-%m-%d")

    # # Create a logger
    # logger = logging.getLogger("my_logger")
    # logger.setLevel(logging.DEBUG)  # Set the lowest logging level for the logger

    # # Create a handler for INFO and greater messages
    # log_file_name_info = f"../logfiles/{tracker_name}_{iso_date}_generation.log"
    # info_handler = logging.FileHandler(log_file_name_info, encoding="utf-8")
    # info_handler.setLevel(logging.INFO)  # Set the level to INFO

    # # Create a handler for ERROR and greater messages
    # log_file_name_error = f"../logfiles/{tracker_name}_{iso_date}_serious_errors.log"
    # error_handler = logging.FileHandler(log_file_name_error, encoding="utf-8")
    # error_handler.setLevel(logging.ERROR)  # Set the level to ERROR

    # # Create a formatter to define the log message format
    # formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # # Set the formatter for both handlers
    # info_handler.setFormatter(formatter)
    # error_handler.setFormatter(formatter)

    # # Add the handlers to the logger
    # logger.addHandler(info_handler)
    # logger.addHandler(error_handler)


METADATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metadata_files')
os.makedirs(METADATA_DIR, exist_ok=True)


tracker_folder_path = 'trackers/'

# run this first so all aws commands work later
s3_setup = (
    f'aws configure set s3.max_concurrent_requests 100'
) 
# if awskeyres == 'done':
#     pass
# else:
#     awskeyres = input('Go into 1password and set up the aws access key locally, if already done, type done.')

# subprocess.run(s3_setup, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# TODO explore why aws configure set s3.max_concurrent_requests 100 doesn't recognize aws David add to requirements

# github pages folder name to map log internal name when they do not match
mapname_gitpages = {
    "africa": "africa-energy",
    "latam": "LATAM",
    "goit": "GOIT",
    "goget": "GOGET",
    "gcpt": "coal-plant",
    "gcmt": "coal-mine",
    "gogpt": "gas-plant",
    "gspt": "solar",
    "gwpt": "wind",
    "gnpt": "nuclear",
    "gbpt": "bioenergy",
    "ggpt": "geothermal",
    "ghpt": "hydro",
    'gctt': "coal-terminals",
    'ggit-lng': 'ggit',
    'egt-gas': 'europe',
    'egt-term': 'europe',
    'gogpt-eu': 'europe',
    
}

official_tracker_name_to_mapname = {
    "Oil & Gas Plants": "gogpt", # done
    "Coal Plants": "gcpt", # done
    "Solar": "gspt", #done
    "Wind": "gwpt", # done
    "Nuclear": "gnpt", # done
    "Hydropower": "ghpt", #done 
    "Bioenergy": "gbpt", #done 
    "Geothermal": "ggpt", #done
    "Coal Terminals": "gctt", 
    "Oil & Gas Extraction": "goget",
    "Coal Mines": "gcmt",
    "LNG Terminals": "ggit-lng",
    "Gas Pipelines": "ggit",
    "Oil Pipelines": "goit",
    "Gas Pipelines EU": "egt-gas",
    "LNG Terminals EU": "egt-term",
    "GOGPT EU": "gogpt-eu",
    "Iron & Steel": "gist",
    "Plumes": "gmet",
    "Iron Ore Mines": "giomt",
    "coal finance": "gcpft",
    "Energy Ownership": "ownership",
    "Integrated": "integrated",
    "Cement and Concrete": "gcct",
    "Chemicals": "GChI",
    "Gas Finance": 'ggft',
    "Coal Project Finance": 'gcpft'
}



# for configuring appropriate js format for legend
# RUlE is: no _ no spaces for values or section title
# TODO finish filling out
legcols_bymap = {
    "gcmt": ["status", "coal-grade", "mine-type"],
    "gcct": ["status", "plant-type", "prod-type"]
    
}
gcmt_closed_tab = 'Global Coal Mine Tracker (Close'

region_key = '1yaKdLauJ2n1FLSeqPsYNxZiuF5jBngIrQOIi9fXysAw'
region_tab = ['mapping']

# gem standard representative points Latitude_rep_point	Longitude_rep_point	GEM Standard Country Name
# centroid_key = '1ETg632Bkwnr96YQbtmDwyWDpSHqmg5He0GQwJjJz8IU'  # Country/Area Copy of Fill In Coordinates from Country Centroid
# centroid_tab = ['centroids']
centroid_key = '1Yke2VQYWZn3UvbqenP2KXvOKR_ZuS43m6C0gd4lwLOQ'  # GEM Standard Country Name
centroid_tab = ['lev1reppoints']


client_secret_full_path = os.path.expanduser("~/") + client_secret
gem_path = os.path.join(os.path.dirname(__file__), 'trackers/')
path_for_pkl = gem_path + 'local_pkl/'
gspread_creds = gspread.oauth(
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        credentials_filename=client_secret_full_path,
    )
# WIP to handle numeric columns in an organized way
# dtype_spec = {} #{'Latitude': float, 'Longitude': float}
# numeric_cols = ['capacity', 'start_year', 'capacity2', 'prod_start_year', 'prod_gas', 'prod_year_gas', 'prod_oil', 'prod_year_oil', 'prod-coal', ] #STOPPED AT GCMT March 3rd 2025
# list_official_tracker_names = ['Oil & Gas Plants', 'Coal Plants', 'Solar', 'Wind', 'Hydropower', 'Geothermal', 'Bioenergy', 'Nuclear', 'Coal Mines', 'Coal Terminals', 'Oil & Gas Extraction', 'Oil Pipelines', 'Gas Pipelines', 'LNG Terminals']

# helpful to pass over specialty logic
gas_only_maps = ['asia', 'europe', 'ggit'] 
non_gsheet_data = ['Gas Pipelines', 'Oil Pipelines', 'Gas Pipelines EU']
non_regional_maps = ['gist', 'gmet', 'giomt', 'gcct', 'gchi', 'ggft']

conversion_key = '1fOPwhKsFVU5TnmkbEyPOylHl3XKZzDCVJ29dtTngkew'
conversion_tab = ['data']

# # TODO keep in retired year or closed year for longitudinal, and make sure start year is there too
# final_cols = [
#                 'areas', 'feedacc','feedstock', 'secprod', 'primprod','model','reactor-type','lat', 'lng','coordinate-accuracy','total-resource-(inferred', 'parent-gem-id', 'total-reserves-(proven-and-probable','start_date', 'owner-gem-id',
#                 'owner-noneng','retired-year','plant-status','noneng_owner', 'parent_gem_id', 'status_display','owner_gem_id', 'facilitytype','unit_id', 'loc-oper', 'loc-owner', 'tech-type','ea_scaling_capacity', 'operator', 'Operator', 
#                 'Binational', 'binational', 'loc-accu','units-of-m','mapname','tracker-acro','official_name','url', 'sfid'
#                 'areas','name', 'unit_name', 'capacity','status', 'start_year', 'subnat', 'region', 'owner', 'parent', 'tracker', 'tracker_custom', 'operator-name-(local-lang/script)', 'owner-name-(local-lang/script)',
#                 'original_units', 'location-accuracy','conversion_factor', 'geometry', 'river', 'area2', 'region2', 'subnat2', 'capacity1', 'capacity2',
#                 'prod-coal', 'Latitude', 'Longitude', 'pid','id', 'prod_oil', 'prod_gas', 'prod_year_oil', 'prod_year_gas', 'fuel', 'PCI5', 'PCI6', 'pci5','pci6','WKTFormat', 'Fuel', 'maturity', 'fuel-filter', 
#                 'pci-list', 'coal-grade', 'mine-type',  'owners_noneng', 'coalfield', 'workforce', 'prod_year', 'opening-year', 'closing-year', 'opening_year', 'closing_year', 'end-year', 'pci-list', 
#                 'coal-grade', 'mine-type',  'noneng_name', 'coalfield', 'workforce', 'prod_year', 'opening-year', 'closing-year', 'opening_year', 'closing_year', 'end-year',
#                 'claycal-yn', 'altf-yn', 'ccs-yn', 'prod-type', 'plant-type', 'entity-id', 'color', 'capacity-display', 'Clinker Capacity (millions metric tonnes per annum)', 'Cement Capacity (millions metric tonnes per annum)', "cem-type",
#                 'wiki-from-name', 'capacity-details', 'parent-search', 'owner-search', 'name-search', 'areas-subnat-sat-display', 'multi-country', 'noneng-name', "prod-method-tier-display", "prod-method-tier", "main-production-equipment"]
# # add two together because gist list is so long and should be refactored soon
# final_cols.extend(steel_gist_table_cols)

# need to adjust when handle sorting column names TODO 
# TODO ASAP for gsheet get columns, use script to match them to final cols, show remiaining, and test if any have changed
# and with add a TEST that check if any key variables in configs are all empty .... or nan (to fix ggit update)
simplified_cols = ['url', 'areas','name','capacity', 'capacity-details', 'latitude', 'longitude', 'pid','id', 'type', 'areas-subnat-sat-display', 'geometry']

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
                    "GCTT": "coal terminal",
                    "GIST": 'Iron & Steel',
                    "GIOMT": 'Iron Ore Mines',
                    "GCCT": 'Cement and Concrete',
                    "GMET": 'Methane Emitters',
                    'GGFT': 'Gas Finance'
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
                    "GCTT": "coal-terminal",
                    "GIST": "iron-steel",
                    "GIOMT": "iron-mine",
                    "GMET": 'methane-emit',
                    "GChI": "chem-inventory",
                    'GGFT': 'Gas Finance'
}

multi_tracker_log_sheet_key = '15l2fcUBADkNVHw-Gld_kk7EaMiFFi8ysWt6aXVW26n8'
source_data_tab = ['source']
map_tab = ['map']

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
    "Virgin Islands (U.S.)", "Puerto Rico", 

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

    
dd_tab_mapping = {'africa': 'Africa Energy',
            'asia': 'Asia Gas',
            'europe': 'Europe Gas',
            'latam': 'Portal Energético',
            'internal': 'internal',
            
            }
    
diacritic_map = {
    'a': ["a", "á", "à", "â", "ã", "ä", "å"],
    'e': ["e", "é", "è", "ê", "ë"],
    'i': ["i", "í", "ì", "î", "ï"],
    'o': ["o", "ó", "ò", "ô", "õ", "ö", "ø"],
    'u': ["u", "ú", "ù", "û", "ü"],
    'c': ["c", "ç"],
    'n': ["n", "ñ"],
}
