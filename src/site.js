mapboxgl.accessToken = config.accessToken;
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/light-v11',
    zoom: 2,
    center: [0, 0],
    maxBounds: [[-180,-85],[180,85]],
    projection: 'naturalEarth'
});
map.addControl(new mapboxgl.NavigationControl());

map.on('mouseenter', 'assets', () => {
    map.getCanvas().style.cursor = 'pointer';
});
map.on('mouseleave', 'assets', () => {
    map.getCanvas().style.cursor = '';
});

$(document).ready(function() {
    if ("json" in config) {
        $.ajax({
            type: "GET",
            url: config.json,
            dataType: "json",
            success: function(jsonData) {makeGeoJSON(jsonData);}
        });
    } else {
        $.ajax({
            type: "GET",
            url: config.csv,
            dataType: "text",
            success: function(csvData) {
                makeGeoJSON($.csv.toObjects(csvData));
            }
        });        
    }
    buildFilters();
});

function makeGeoJSON(jsonData) {
    config.geojson = {
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
        config.geojson.features.push(feature);
    });

    addLayer(config.geojson);   
}

function addLayer(geojson) {
    map.on('load', function () {
        let paint = config.paint;
        if ('color' in config) {
            paint["circle-color"] = [
                "match",
                ["get", config.color.field],
                ...Object.keys(config.color.values).flatMap(key => [key, config.color.values[key]]),
                "#000000" // fallback color if status value not found in hash
              ]
        }
        console.log(paint);
        map.addLayer({
            'id': 'assets',
            'type': 'circle',
            'source': {
                'type': 'geojson',
                'data': geojson
            },
            'layout': {},
            'paint': paint
        });
    }); 
}

function buildFilters() {
    config.filters.forEach(filter => {
        $('#filter-form').append('<h4 class="card-title">' + (filter.label || filter.field.replaceAll("_"," ")) + '</h4>');
        for (let i=0; i<filter.values.length; i++) {
            let check = '<div class="form-check"><input type="checkbox" checked class="form-check-input" id="' + filter.field + ':' + filter.values[i] + '">';
            check += '<label class="form-check-label" for="exampleCheck1">' + 
                ('values_labels' in filter ? filter.values_labels[i] : filter.values[i].replaceAll("_", " ")) 
                + '</label></div>';
            $('#filter-form').append(check);
        }
    });
    $('.form-check-input').each(function() {
        this.addEventListener("click", function() {
            filterGeoJSON();
        });
    });
}

function filterGeoJSON() {
    let filterStatus = {};
    config.filters.forEach(filter => {
        filterStatus[filter.field] = [];
    });
    $('.form-check-input').each(function() {
        if (this.checked) {
            let [field, value] = this.id.split(':');
            filterStatus[field].push(value);
        }
    });
    let filteredGeoJSON = {
        "type": "FeatureCollection",
        "features": []
    };
    config.geojson.features.forEach(feature => {
        let include = true;
        for (let field in filterStatus) {
            if (! filterStatus[field].includes(feature.properties[field])) include = false;
        }
        if (include) {
            filteredGeoJSON.features.push(feature);
        }
    });
    map.getSource('assets').setData(filteredGeoJSON);
}
