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
const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
});

$(document).ready(function() {
    loadData();
    buildFilters();
});

function loadData() {
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
}
function makeGeoJSON(jsonData) {
    config.geojson = {
        "type": "FeatureCollection",
        "features": []
    };

    //NOTE: consider making lng, lat column name a config option
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

    //filters haven't loaded yet so can't call them at this point, and next steps expect it
    config.filteredGeoJSON = JSON.parse(JSON.stringify(config.geojson));

    findLinkedAssets();
    addLayer();   
}


// iterate through, create lookup with details that lists all of them
// create new GeoJSON which has only one feature when units/phases at exact same location
// call this after filters
function findLinkedAssets() {
    // if url is shared, common asset. create lookup table
    config.linked = {};
    config.filteredGeoJSON.features.forEach((feature) => {
        if (! (feature.properties.url in config.linked)) {
            config.linked[feature.properties.url] = [];
        } 
        config.linked[feature.properties.url].push(feature);
    });

    // if url and location is shared, collect and display as 1 point
    let grouped = {};
    config.filteredGeoJSON.features.forEach((feature) => {
        let key = feature.properties.url + "," + feature.geometry.coordinates[0] + "," + feature.geometry.coordinates[1];
        if (! (key in grouped)) {
            grouped[key] = [];
        }
        grouped[key].push(feature);
    });

    // 1 feature for shared url/location.
    // sum up capacity (configure the column).
    // property for custom icon that represents breakdown of status (configure the column again)
    // add that custome icon
    config.processedGeoJSON = {
        "type": "FeatureCollection",
        "features": []
    };
    Object.keys(grouped).forEach((key) => {
        let features = JSON.parse(JSON.stringify(grouped[key]));
        if (features.length == 1) {
            config.processedGeoJSON.features.push(features[0]);
        } else {
            let capacity = features.reduce((previous, current) => {
                return previous + Number(current.properties[config.capacity_field]);
            }, 0);
            let feature = features[0];
            feature.properties[config.capacity_field] = capacity;
            config.processedGeoJSON.features.push(feature);
        }
    });

}

function addLayer() {
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
        map.addSource('assets-source', {
            'type': 'geojson',
            'data': config.processedGeoJSON
        });
        map.addLayer({
            'id': 'assets',
            'type': 'circle',
            'source': 'assets-source',
            'layout': {},
            'paint': paint
        });
        map.on('click', 'assets', (e) => {
            const bbox = [ [e.point.x - 5, e.point.y - 5], [e.point.x + 5, e.point.y + 5]];
            const selectedFeatures = map.queryRenderedFeatures(bbox, {layers: ['assets']});

            //consider adding linking column name a config option
            const urls = selectedFeatures.map(
                (feature) => feature.properties.url
            );

            map.setFilter('assets-highlighted', [
                'in',
                'url',
                ...urls
            ]);

            console.log(e.features[0]);
            console.log(config.linked[e.features[0].properties.url]);
            //const coordinates = e.features[0].geometry.coordinates.slice();
            //const description = e.features[0].properties.url;
            //console.log(coordinates);
            //console.log(description);
        });
        map.on('mouseenter', 'assets', (e) => {
            map.getCanvas().style.cursor = 'pointer';
            const coordinates = e.features[0].geometry.coordinates.slice();
            const description = e.features[0].properties.url;
            popup.setLngLat(coordinates).setHTML(description).addTo(map);
        });
        map.on('mouseleave', 'assets', () => {
            map.getCanvas().style.cursor = '';
            popup.remove();
        });

        paint = config.paint;
        paint["circle-color"] = '#FFEA00';
        map.addLayer(
            {
                'id': 'assets-highlighted',
                'type': 'circle',
                'source': 'assets-source',
                'layout': {},
                'paint': paint,
                'filter': ['in', 'url', '']
            }
        );
        //customIconTest();
        //addCustomIconLayerTest();  
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
    config.filteredGeoJSON = JSON.parse(JSON.stringify(filteredGeoJSON));
    findLinkedAssets();
    map.getSource('assets-source').setData(config.processedGeoJSON);
    //map.getSource('assets-symbol').setData(filteredGeoJSON);
}

function customIconTest() {

    config.colors.values;
    const style = {"operating":5,"proposed":2,"cancelled":0,"shelved":1,"closed":4,"mothballed":1};
    const str = JSON.stringify(style);
    //style = JSON.parse(str);


    // create a canvas element
    const canvas = document.createElement('canvas');
    canvas.width = 64; // set the size of the canvas
    canvas.height = 64;

    // get the canvas context
    const context = canvas.getContext('2d');

    // calculate the coordinates of the center of the circle
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // set the colors for the circle
    context.fillStyle = 'rgb(85, 187, 85)'; // green
    context.beginPath();
    context.moveTo(centerX, centerY);
    context.arc(centerX, centerY, canvas.width / 2, 0, Math.PI * 2 * 3 / 4);
    context.fill();

    context.fillStyle = 'rgb(255, 0, 0)'; // red
    context.beginPath();
    context.moveTo(centerX, centerY);
    context.arc(centerX, centerY, canvas.width / 2, Math.PI * 2 * 3 / 4, Math.PI * 2 * 5 / 12);
    context.fill();

    context.fillStyle = 'rgb(0, 153, 255)'; // blue
    context.beginPath();
    context.moveTo(centerX, centerY);
    context.arc(centerX, centerY, canvas.width / 2, Math.PI * 2 * 5 / 12, 0);
    context.fill();

    // create a data URI for the canvas image
    const dataURL = canvas.toDataURL();

    // add the image to the map as a custom icon
    map.loadImage(dataURL, (error, image) => {
        if (error) throw error;
        map.addImage('custom-icon', image);
    });
}

function addCustomIconLayerTest() {
    map.addLayer({
    'id': 'assets-symbol',
    'type': 'symbol',
    'source': {
        'type': 'geojson',
        'data': config.geojson
    },
    'layout': {
        'icon-image': 'custom-icon',
        'icon-allow-overlap': true,
         'icon-size': [
            'interpolate',
            ['linear'],
            ["to-number", ["get", "output"]],
            0, 8/64, // when size is 0, scale the icon to half its original size
            60, .25 // when size is 10, scale the icon to twice its original size
          ]
    }
});
}