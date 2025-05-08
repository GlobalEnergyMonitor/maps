import pandas as pd
import geopandas as gpd
import numpy as np
import time
import subprocess
from shapely.geometry import MultiPolygon
import pickle
# from all_config import *
import os
# import gem_tracker_maps.trackers.save_file_to_s3 as save_file_to_s3
# import save_file_to_s3



tfile_map = f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/testing/final/{self.name}_map_{iso_today_date}.geojson'

tfile_dd = f'/Users/gem-tah/GEM_INFO/GEM_WORK/earthrise-maps/gem_tracker_maps/trackers/{self.name}/testing/{self.name}-data-download_{new_release_date}_{iso_today_date}_test.xlsx'

source_dd = f'/Users/gem-tah/Downloads/GlobalCoalMineTracker,May2025DTC_md_2025-05-05.parquet'

last_map = f'gem_tracker_maps/trackers/coal-mine/compilation_output/data.csv'

