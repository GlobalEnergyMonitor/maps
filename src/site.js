processConfig();

function processConfig() {
    // Merge site-config.js and config.js
    config = Object.assign(site_config, config);
    if (!('linkField' in config)) config.linkField = 'url';
    if (!('locationColumns' in config)) {
        config.locationColumns = {};
        config.locationColumns['lng'] = 'lng';
        config.locationColumns['lat'] = 'lat';
    }
}

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
    buildFilters();
    loadData();
    enableSearch();
    enableModal();
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

    jsonData.forEach((asset) => {
        let feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [asset[config.locationColumns['lng']], asset[config.locationColumns['lat']]]
            },
            "properties": {}
        }
        for (let key in asset) {
            if (key != config.locationColumns['lng'] && key != config.locationColumns['lat']) {
                feature.properties[key] = asset[key];
            }
        }
        config.geojson.features.push(feature);
    });

    // Now that GeoJSON is created, store in processedGeoJSON, and link assets, then add layers to the map
    config.processedGeoJSON = JSON.parse(JSON.stringify(config.geojson)); //deep copy
    findLinkedAssets();
    addLayers();  
    buildTable(); 
    updateSummary();
}

// Builds lookup of linked assets by the link column
//  and when linked assets share location, rebuilds processedGeoJSON with summed capacity and custom icon
function findLinkedAssets() {
    // First, create a lookup table for linked assets based on linkField
    config.linked = {};
    config.processedGeoJSON.features.forEach((feature) => {
        if (! (feature.properties[config.linkField] in config.linked)) {
            config.linked[feature.properties[config.linkField]] = [];
        } 
        config.linked[feature.properties[config.linkField]].push(feature);
    });

    // Next find linked assets that share location. 
    let grouped = {};
    config.processedGeoJSON.features.forEach((feature) => {
        let key = feature.properties[config.linkField] + "," + feature.geometry.coordinates[0] + "," + feature.geometry.coordinates[1];
        if (! (key in grouped)) {
            grouped[key] = [];
        }
        grouped[key].push(feature);
    });

    // Rebuild GeoJSON with summed capacity, and custom icon for single point display of the grouped assets
    config.processedGeoJSON = {
        "type": "FeatureCollection",
        "features": []
    };
    Object.keys(grouped).forEach((key) => {
        let features = JSON.parse(JSON.stringify(grouped[key])); //deep copy

        // Sum capacity across all linked assets
        let capacity = features.reduce((previous, current) => {
            return previous + Number(current.properties[config.capacityField]);
        }, 0);
        features[0].properties[config.capacityField] = capacity;

        // Build summary count of status across all linked assets
        //  and generate icon based on that label if more than one status
        let icon = Object.assign(...Object.keys(config.color.values).map(k => ({ [k]: 0 })));
        features.forEach((feature) => {  
            icon[feature.properties[config.color.field]] += Number(feature.properties[config.capacityField]);
        });
        if (Object.values(icon).filter(v => v != 0).length > 1) {
            features[0].properties['icon'] = JSON.stringify(icon);
            generateIcon(icon);
        }

        config.processedGeoJSON.features.push(features[0]);
    });
}

function addLayers() {
    map.on('load', function () {
        map.addSource('assets-source', {
            'type': 'geojson',
            'data': config.processedGeoJSON
        });

        // First build circle layer
        //  build style json for circle-color based on config.color
        let paint = config.paint;
        if ('color' in config) {
            paint["circle-color"] = [
                "match",
                ["get", config.color.field],
                ...Object.keys(config.color.values).flatMap(key => [key, config.color.values[key]]),
                "#000000"
              ]
        }
        map.addLayer({
            'id': 'assets',
            'type': 'circle',
            'source': 'assets-source',
            'layout': {},
            'paint': paint
        });

        // Add layer with proportional icons
        map.addLayer({
            'id': 'assets-symbol',
            'type': 'symbol',
            'source': 'assets-source',
            'layout': {
                'icon-image': ["get", "icon"],
                'icon-allow-overlap': true,
                'icon-size': [
                    'interpolate',
                    ['linear'],
                    ["to-number", ["get", config.capacityField]],
                    // Note...  this should be generated by a config setting that sets min and max size of dot over value range
                    // and makes it consistent across the three layers
                    0, 8/64, 
                    10000, .6 
                  ]
            }
        });

        // Add highlight layer
        paint = config.paint;
        paint["circle-color"] = '#FFEA00';
        map.addLayer(
            {
                'id': 'assets-highlighted',
                'type': 'circle',
                'source': 'assets-source',
                'layout': {},
                'paint': paint,
                'filter': ['in', (config.linkField), '']
            }
        );

        addEvents();
    }); 
}

function addEvents() {
    map.on('click', 'assets', (e) => {
        const bbox = [ [e.point.x - 5, e.point.y - 5], [e.point.x + 5, e.point.y + 5]];
        const selectedFeatures = map.queryRenderedFeatures(bbox, {layers: ['assets']});

        const links = selectedFeatures.map(
            (feature) => feature.properties[config.linkField]
        );

        map.setFilter('assets-highlighted', [
            'in',
            config.linkField,
            ...links
        ]);

        if (selectedFeatures.length == 2) {
            displayDetails(selectedFeatures[0].properties[config.linkField]);
        } else {
            var modalText = "<ul>";
            selectedFeatures.forEach((feature) => {
                modalText += "<li class='asset-select-option' onClick=\"displayDetails('" + feature.properties[config.linkField] + "')\">" + feature.properties[config.linkField] + "</li>";
            });
            modalText += "</ul>"
            $('.modal-body').html(modalText);
            $('.modal-title').text('choose');
        }

        config.modal.show();
    });
    map.on('mouseenter', 'assets', (e) => {
        map.getCanvas().style.cursor = 'pointer';
        const coordinates = e.features[0].geometry.coordinates.slice();
        const description = e.features[0].properties[config.linkField];
        popup.setLngLat(coordinates).setHTML(description).addTo(map);
    });
    map.on('mouseleave', 'assets', () => {
        map.getCanvas().style.cursor = '';
        popup.remove();
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
        if (config.searchText.length >= 3) {
            if (! feature.properties[config.searchField].toLowerCase().includes(config.searchText)) include = false;
        }
        if (include) {
            filteredGeoJSON.features.push(feature);
        }
    });
    config.processedGeoJSON = JSON.parse(JSON.stringify(filteredGeoJSON));
    findLinkedAssets();
    map.getSource('assets-source').setData(config.processedGeoJSON);
    updateTable();
    updateSummary();
}

function generateIcon(icon) {
    let label = JSON.stringify(icon);
    if (map.hasImage(label)) return;

    let canvas = document.createElement('canvas');
    canvas.width = 64; // set the size of the canvas
    canvas.height = 64;

    // get the canvas context
    let context = canvas.getContext('2d');
    context.globalAlpha = 0.5;

    // calculate the coordinates of the center of the circle
    let centerX = canvas.width / 2;
    let centerY = canvas.height / 2;

    let current = 0;
    let slices = Object.values(icon).reduce((previous, current) => {
        return previous + Number(current);
    }, 0);

    Object.keys(icon).forEach((k) => {
        let next = current + (icon[k] / slices);
        context.fillStyle = config.color.values[k];
        context.beginPath();
        context.moveTo(centerX, centerY);
        context.arc(centerX, centerY, canvas.width / 2, Math.PI * 2 * current, Math.PI * 2 * next);
        context.fill();

        current = next;
    });

    // create a data URI for the canvas image
    let dataURL = canvas.toDataURL();

    // add the image to the map as a custom icon
    map.loadImage(dataURL, (error, image) => {
        if (error) throw error;
        if (! map.hasImage(label)) map.addImage(label, image);
    });
}

function buildTable() {

    config.table = $('#table').DataTable({
        data: geoJSON2Table(),
        searching: false,
        pageLength: 100,
        columns: geoJSON2Headers()
    });

    $('#table-toggle').on("click", function() {
        if ($('#table-toggle').text() == "Table view") {
            $('#table-toggle').text("Map view");
            $('#map').hide();
            $('#sidebar').hide();
            $('#table-container').show();
        } else {
            $('#table-toggle').text("Table view");
            $('#map').show();
            $('#sidebar').show();
            $('#table-container').hide();
        }
    });
}
function updateTable() {
    config.table.clear();
    config.table.rows.add(geoJSON2Table()).draw();
}
function geoJSON2Table() {
    return config.processedGeoJSON.features.map(feature => Object.values(feature.properties)
    ); 
}
function geoJSON2Headers() {
    return Object.keys(config.geojson.features[0].properties).map((k) => {
        return {'title': k}
    });
}

function updateSummary() {
    var text = config.processedGeoJSON.features.length.toString() + " " + config.assetLabel;
    $('#summary').text(text);
}

function enableSearch() {
    $('#search-text').on('keyup paste', debounce(function() {
        config.searchText = $('#search-text').val().toLowerCase();
        filterGeoJSON();
    }, 500));
    config.searchText = '';
}

function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
};

function enableModal() {
    config.modal = new bootstrap.Modal($('#modal'));
    $('#modal').on('hidden.bs.modal', function (event) {
        map.setFilter('assets-highlighted', [
            '==',
            config.linkField,
            ''
        ]);
    })
}
function displayDetails(link) {
    $('.modal-body').html(link + "<br/>" + config.linked[link].length);
    $('.modal-title').text('details');

    map.setFilter('assets-highlighted', [
        '==',
        config.linkField,
        link
    ]);
}