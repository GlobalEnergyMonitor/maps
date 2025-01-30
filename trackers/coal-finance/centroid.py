import pandas as pd
import geopandas as gpd
import numpy as np
import time
from shapely.geometry import Point, LineString
from datetime import date
import matplotlib.pyplot as plt

centroids = {
    'Australia': [133.7751, -25.2744],
    'Austria': [14.5501, 47.5162],
    'Bahamas': [-77.3963, 25.0343],
    'Bangladesh': [90.3563, 23.685],
    'Barbados': [-59.5432, 13.1939],
    'Belgium': [4.4699, 50.5039],
    'Bosnia and Herzegovina': [17.6791, 43.9159],
    'Botswana': [24.6849, -22.3285],
    'Brazil': [-51.9253, -14.235],
    'Cambodia': [104.991, 12.5657],
    'Canada': [-106.3468, 56.1304],
    'Chile': [-71.543, -35.6751],
    'China': [104.1954, 35.8617],
    'Colombia': [-74.2973, 4.5709],
    'Costa Rica': [-83.7534, 9.7489],
    'Czech Republic': [15.473, 49.8175],
    "Côte d'Ivoire": [-5.5471, 7.5399],
    'Dominican Republic': [-70.1627, 18.7357],
    'Egypt': [30.8025, 26.8206],
    'El Salvador': [-88.8965, 13.7942],
    'France': [1.8883, 46.6034],
    'Germany': [10.4515, 51.1657],
    'Guatemala': [-90.2308, 15.7835],
    'Honduras': [-86.2419, 15.2],
    'Hong Kong': [114.1694, 22.3193],
    'India': [78.9629, 20.5937],
    'Indonesia': [113.9213, -0.7893],
    'Iran': [53.688, 32.4279],
    'Ireland': [-7.6921, 53.1424],
    'Italy': [12.5674, 41.8719],
    'Japan': [138.2529, 36.2048],
    'Kazakhstan': [66.9237, 48.0196],
    'Kenya': [37.9062, -0.0236],
    'Kuwait': [47.4818, 29.3117],
    'Luxembourg': [6.1296, 49.8153],
    'Malawi': [34.3015, -13.2543],
    'Malaysia': [101.9758, 4.2105],
    'Mauritius': [57.5522, -20.3484],
    'Mongolia': [103.8467, 46.8625],
    'Morocco': [-7.0926, 31.7917],
    'Mozambique': [35.5296, -18.6657],
    'Netherlands': [5.2913, 52.1326],
    'Niger': [8.0817, 17.6078],
    'Nigeria': [8.6753, 9.082],
    'Pakistan': [69.3451, 30.3753],
    'Panama': [-80.7821, 8.5379],
    'Philippines': [121.774, 12.8797],
    'Poland': [19.1451, 51.9194],
    'Portugal': [-8.2245, 39.3999],
    'Qatar': [51.1839, 25.3548],
    'Romania': [24.9668, 45.9432],
    'Russia': [105.3188, 61.524],
    'Saudi Arabia': [45.0792, 23.8859],
    'Serbia': [21.0059, 44.0165],
    'Singapore': [103.8198, 1.3521],
    'Slovenia': [14.9955, 46.1512],
    'South Africa': [22.9375, -30.5595],
    'South Korea': [127.7669, 35.9078],
    'Spain': [-3.7492, 40.4637],
    'Sri Lanka': [80.7718, 7.8731],
    'Sweden': [18.6435, 60.1282],
    'Switzerland': [8.2275, 46.8182],
    'Taiwan': [120.9605, 23.6978],
    'Tajikistan': [71.2761, 38.861],
    'Thailand': [100.9925, 15.87],
    'Togo': [0.8248, 8.6195],
    'Türkiye': [35.2433, 38.9637],
    'UAE': [53.8478, 23.4241],
    'US': [-95.7129, 37.0902],
    'United Arab Emirates': [53.8478, 23.4241],
    'United Kingdom': [-3.436, 55.3781],
    'United States': [-95.7129, 37.0902],
    'Uzbekistan': [64.5853, 41.3775],
    'Vietnam': [108.2772, 14.0583],
    'Zambia': [27.8493, -13.1339],
    'Not found': [71.000, -40.000]
}

# Define a function to create an arc between two points
def create_arc(start, end, random_factor=0.3): # 0.1 start
    # Create midpoint with randomization
    mid_lat = (start.y + end.y) / 2 + np.random.uniform(-random_factor, random_factor)
    mid_lon = (start.x + end.x) / 2 + np.random.uniform(-random_factor, random_factor)
    midpoint = Point(mid_lon, mid_lat)
    
    # Return a LineString (arc) from start to midpoint to end
    return LineString([start, midpoint, end])

