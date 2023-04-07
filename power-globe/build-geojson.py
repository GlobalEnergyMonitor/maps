#!/usr/bin/python3

import csv
import json
import requests

trackers = [
    {'type':'coal-plant',
     'url': 'https://greeninfo-network.github.io/coal-tracker-client/data/trackers.json'
    },
    {'type':'gas-plant',
     'url': 'https://greeninfo-network.github.io/global-gas-plant-tracker/static/data/data.csv'
    },
    {'type':'solar-power',
     'url': 'https://greeninfo-network.github.io/solar-power-tracker/static/data/data.csv'
    },
    {'type':'wind-power',
     'url': 'https://greeninfo-network.github.io/wind-power-tracker/static/data/data.csv'
    },
    {'type':'geothermal-power',
     'url': 'https://greeninfo-network.github.io/geothermal-power-tracker/static/data/data.csv'
    },
    {'type':'bioenergy-power',
     'url': 'https://greeninfo-network.github.io/bioenergy-power-tracker/static/data/data.csv'
    },
    {'type':'nuclear-power',
     'url': 'https://greeninfo-network.github.io/nuclear-power-tracker/static/data/data.csv'
    }
] 

out = []

for tracker in trackers:
    result = []
    response = requests.get(tracker['url'])
    if tracker['url'].endswith('.csv'):
        csv_data = csv.reader(response.text.splitlines())
        headers = next(csv_data)
        for row in csv_data:
            row_data = {}
            for i in range(len(headers)):
                row_data[headers[i]] = row[i]
            result.append(row_data)
    else:
        result = response.json()
    
    for r in result:
        r['tracker_type'] = tracker['type']

    out.extend(result)

geojson = {"type":"FeatureCollection", "features": []}
for item in out:
    if (abs(float(item['lat'])) <= 90):
        geojson['features'].append({'type': 'Feature', 
                                'geometry':{'type': 'Point', 'coordinates': [float(item['lng']), float(item['lat'])]},
                                'properties': { 'tracker_type': item['tracker_type'], 'capacity': int(float(item['capacity'])) if item['capacity'].strip() else 0 }
                                })

with open("out.json", "w") as outfile:
    outfile.write(json.dumps(geojson, indent=4))    

