# notes from email
# Would it be possible to filter the O&G extraction areas and coal mines by status, and the plumes by "has attribution information" (i.e., either column O or column P has an entry?). The different layers could be separated under its own heading similar to how the GCMT legend has different filters on top of each other? If it's too complex, just filtering by layer type (O&G extraction area, plume, coal mine) would work we#ll too.
# I kept all the infrastructure scaled the same size, but the plumes are sized by emissions. My preference is to keep the infrastructure emissions estimates in the pop-up information -- having infrastructure scaled by capacity and plumes by emissions in the same map could be confusing
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

tracker = 'gmet'


local_file_path = f'/Users/gem-tah/Desktop/GEM_INFO/GEM_WORK/earthrise-maps/gem-tracker-maps/trackers/gmet/test/{today_date}ready_to_be_manipulated.csv'

path_for_download_and_map_files = gem_path + tracker + '/compilation_output/' + iso_today_date_folder
os.makedirs(path_for_download_and_map_files, exist_ok=True)
path_for_download_and_map_files_test = gem_path + tracker + '/test/'
os.makedirs(path_for_download_and_map_files_test, exist_ok=True)


gmet_key = '10dMKhNtHh6gPDZllkLX1Yj7HBlKa9UP7h66AU9D1B8w'
gmet_tabs = ['Coal Mines', 'Oil and Gas Extraction Areas', 'Oil and Gas Reserves', 'Plumes'] # Pipelines

filler_wiki_url = 'https://globalenergymonitor.org/projects/global-methane-emitters-tracker/'

status_legend = {
                # proposed-plus
                'proposed': 'proposed-plus',
                'announced': 'proposed-plus',
                'discovered': 'proposed-plus',
                # pre-construction-plus
                'pre-construction': 'pre-construction-plus',
                'pre-permit': 'pre-construction-plus',
                'permitted': 'pre-construction-plus',
                # construction-plus
                'construction': 'construction-plus',
                'in development': 'construction-plus',
                # mothballed
                'mothballed': 'mothballed-plus',
                'idle': 'mothballed-plus',
                'shut in': 'mothballed-plus',
                # retired
                'retired': 'retired-plus',
                'closed': 'retired-plus',
                'decommissioned': 'retired-plus',
                # unknown
                'n/a': 'unknown-plus',
                '': 'unknown-plus'
                }

country_harm_dict = {
        'Czechia': 'Czech Republic',
        'Ivory Coast': "Côte d'Ivoire",
        "Cote d'Ivoire": "Côte d'Ivoire", # adds accent
        "Republic of Congo": "Republic of the Congo", # adds "the"
        "Rep Congo": "Republic of the Congo",
        "Democratic Republic of Congo": "DR Congo",
        "Democratic Republic of the Congo": "DR Congo", # in case step above adds "the"
        "Republic of Guinea": "Guinea",
        "Republic of Sudan": "Sudan",
        "FYROM": "North Macedonia",
        "Chinese Taipei": "Taiwan",
        "East Timor": "Timor-Leste",
        "USA": "United States",
        'Turkey': 'Türkiye',
        'Canary Islands': 'Spain', 
    }