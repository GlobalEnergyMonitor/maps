mapboxgl.accessToken = config.accessToken;
const map = new mapboxgl.Map({
    container: 'map',
    // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
    style: 'mapbox://styles/mapbox/light-v11',
    zoom: 2,
    center: [0, 0],
    projection: 'naturalEarth'
});

$(document).ready(function() {
    if ("json" in config) {
        $.ajax({
            type: "GET",
            url: config.json,
            dataType: "json",
            success: function(jsonData) {makeGeoJSON(jsonData);}
        });
    }
});

function makeGeoJSON(jsonData) {
    let geojson = {
        "type": "FeatureCollection",
        "features": []
    };
    jsonData.forEach((asset) => {
        let feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [asset['lng'], asset['lat']]
            },
            "properties": {}
        }
        for (let key in asset) {
            if (key != 'lng' && key != 'lat') {
                feature.properties[key] = asset[key];
            }
        }
        geojson.features.push(feature);
    });

    map.on('load', function () {
        map.addLayer({
            'id': 'assets',
            'type': 'circle',
            'source': {
                'type': 'geojson',
                'data': geojson
            },
            'layout': {},
            'paint': {}
        });
    });    
}
    
map.addControl(new mapboxgl.NavigationControl());

// Change the cursor to a pointer when the mouse is over the places layer.
map.on('mouseenter', 'pipeline', () => {
    map.getCanvas().style.cursor = 'pointer';
});

// Change it back to a pointer when it leaves.
map.on('mouseleave', 'pipeline', () => {
    map.getCanvas().style.cursor = '';
});