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

path_for_download_and_map_files = gem_path + tracker + '/compilation_output/' + iso_today_date_folder
os.makedirs(path_for_download_and_map_files, exist_ok=True)
path_for_download_and_map_files_test = gem_path + tracker + '/test/'
os.makedirs(path_for_download_and_map_files_test, exist_ok=True)


gmet_key = '12ldx50_HANStnL5bwYDDrbo08jsb2-KM53rOyLVNE3Q'
gmet_tabs = ['Coal Mines', 'Oil and Gas Extraction Areas', 'Oil and Gas Reserves', 'Pipelines', 'Plumes']
