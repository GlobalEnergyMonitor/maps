processConfig();
function processConfig() {
    // Merge site-config.js and config.js
    config = Object.assign(site_config, config);
    config.baseMap = "Streets";
    config.icons = [];

    Object.keys(config.color.values).forEach((color_key) => {
        config.color.values[color_key] = config.colors[ config.color.values[color_key] ];
    });
}

/*
  Set up mapboxgljs instance, and trigger data load
*/
mapboxgl.accessToken = config.accessToken;
const map = new mapboxgl.Map({
    container: 'map',
    style: config.mapStyle,
    zoom: determineZoom(),
    center: [0, 0],
    // maxBounds: [[-180,-85],[180,85]],
    projection: 'naturalEarth'
});
map.addControl(new mapboxgl.NavigationControl({ showCompass: false }));
const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
});
map.dragRotate.disable();
map.touchZoomRotate.disableRotation();

map.on('style.load', function () {
    loadData();
});
function determineZoom() {
    let modifier = 650;
    if (window.innerWidth < 1000) { modifier = 500; }
    else if (window.innerWidth < 1500) { modifier = 575; }
    let zoom = config.zoomFactor * (window.innerWidth - modifier) / modifier;
    return zoom;
}

/*
  load data in various formats, and prepare for use in application
*/
function loadData() {
    if ("tiles" in config) {
        addTiles();
    } else if ("geojson" in config) {
        $.ajax({
            type: "GET",
            url: config.geojson,
            dataType: "json",
            success: function(jsonData) { addGeoJSON(jsonData);}
        });
    } else if ("json" in config) {
        $.ajax({
            type: "GET",
            url: config.json,
            dataType: "json",
            success: function(jsonData) {addGeoJSON(jsonData);}
        });
    } else {
        $.ajax({
            type: "GET",
            url: config.csv,
            dataType: "text",
            success: function(csvData) {
                addGeoJSON($.csv.toObjects(csvData));
            }
        });        
    }
}
function addGeoJSON(jsonData) {
    if ('type' in jsonData && jsonData['type'] == 'FeatureCollection') {
        config.geojson = jsonData;
    } else {
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
                if (key == config.capacityField) {
                    feature.properties[key] = Number(asset[key]);
                } else if (key != config.locationColumns['lng'] && key != config.locationColumns['lat']) {
                    feature.properties[key] = asset[key];
                }
            }
            config.geojson.features.push(feature);
        });

    }

    // Now that GeoJSON is created, store in processedGeoJSON, and link assets, then add layers to the map
    config.processedGeoJSON = JSON.parse(JSON.stringify(config.geojson)); //deep copy
    setMinMax();
    map.on('load', function () {
        map.addSource('assets-source', {
            'type': 'geojson',
            'data': config.processedGeoJSON
        });
        addLayers();
        map.on('idle', enableUX);
    });
}
function addTiles() {
    map.on('load', function () {
        map.addSource('assets-source', {
            'type': 'vector',
            'tiles': config.tiles,
            'minzoom': 0,
            'maxzoom': 10 // ?
        });

        /* create layer with invisible aasets in order to calculate statistics necessary for rendering the map and interface */
        let paint = config.paint;
        paint['circle-radius'] = 0;
        map.addLayer({
            'id': 'assets-minmax',
            'type': 'circle',
            'source': 'assets-source',
            'source-layer': 'integrated',
            'layout': {},
            'paint': paint
        });
        map.on('idle', geoJSONFromTiles);
    });
}
function geoJSONFromTiles() {
    map.off('idle', geoJSONFromTiles);
    config.geojson = {
        "type": "FeatureCollection", 
        "features": map.queryRenderedFeatures({layers: ['assets-minmax']}) 
    }
    config.processedGeoJSON = JSON.parse(JSON.stringify(config.geojson)); //deep copy
    setMinMax();
    map.removeLayer('assets-minmax');
    
    addLayers();
    map.on('idle', enableUX);
}
// Builds lookup of linked assets by the link column
//  and when linked assets share location, rebuilds processedGeoJSON with summed capacity and custom icon
function findLinkedAssets() {
    map.off('idle', findLinkedAssets);

    config.preLinkedGeoJSON = JSON.parse(JSON.stringify(config.processedGeoJSON));
    config.totalCount = 0;

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
        if ('geometry' in feature && feature.geometry != null) {
            if ('coordinates' in feature.geometry) {
                let key = feature.properties[config.linkField] + "," + feature.geometry.coordinates[0] + "," + feature.geometry.coordinates[1];
                if (! (key in grouped)) {
                    grouped[key] = [];
                }
                grouped[key].push(feature);
            }
        }
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

        // Build summary count of capacity across all linked assets
        //  and generate icon based on that label if more than one status
        let icon = Object.assign(...Object.keys(config.color.values).map(k => ({ [config.color.values[k]]: 0 })));
        features.forEach((feature) => {  
            icon[config.color.values[feature.properties[config.color.field]]] += Number(feature.properties[config.capacityField]);
        });
        if (Object.values(icon).filter(v => v != 0).length > 1) {
            // normalize values to 10
            let current = 0;
            let total = Object.values(icon).reduce((previous, current) => {
                return previous + Number(current);
            }, 0);
            icon = Object.assign(...Object.keys(icon).map(k => ({[k]: Math.ceil(10 * (icon[k] / total)) })));
            let string_icon = JSON.stringify(icon)
            features[0].properties['icon'] = string_icon;
            if (! config.icons.includes(string_icon)) {
                generateIcon(icon);
                config.icons.push(string_icon);
            }
        }

        // Build summary count of filters for legend
        let summary_count = {};
        config.filters.forEach((filter) => {
            summary_count[filter.field] = Object.assign(...filter.values.map(f => ({[f]: 0})));
            features.forEach((feature) => {
                summary_count[filter.field][feature.properties[filter.field]]++;
            });
        });
        features[0].properties['summary_count'] = JSON.stringify(summary_count);
        config.totalCount += features.length;

        config.processedGeoJSON.features.push(features[0]);
    });
}
function generateIcon(icon) {
    let label = JSON.stringify(icon);
    if (map.hasImage(label)) return;

    let canvas = document.createElement('canvas');
    canvas.width = 64; // set the size of the canvas
    canvas.height = 64;

    // get the canvas context
    let context = canvas.getContext('2d');
    context.globalAlpha = config.paint["circle-opacity"];

    // calculate the coordinates of the center of the circle
    let centerX = canvas.width / 2;
    let centerY = canvas.height / 2;

    let current = .75; //start at vertical
    let slices = Object.values(icon).reduce((previous, current) => {
        return previous + Number(current);
    }, 0);

    Object.keys(icon).forEach((k) => {
        let next = current + (icon[k] / slices);
        context.fillStyle = k;
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
function setMinMax() {
    config.maxCapacity = 0;
    config.minCapacity = 1000000;
    let ref = "config.processedGeoJSON.features"
    if (config.tiles) {
        ref = "map.queryRenderedFeatures({layers: ['assets-minmax']})"
    } 
    eval(ref).forEach((feature) => {
        if (parseFloat(feature.properties[config.capacityField]) > config.maxCapacity) {
            config.maxCapacity =  parseFloat(feature.properties[config.capacityField]);
        }
        if (parseFloat(feature.properties[config.capacityField]) < config.minCapacity) {
            config.minCapacity =  parseFloat(feature.properties[config.capacityField]);
        }       
    });
}

/*
  render data
*/
function enableUX() {
    map.off('idle', enableUX);

    findLinkedAssets();

    buildFilters();
    updateSummary();
    
    buildTable(); 

    enableModal();
    enableNavFilters();
}

function addLayers() {
    // First build circle layer
    //  build style json for circle-color based on config.color
    let paint = config.paint;
    if ('color' in config) {
        paint["circle-color"] = [
            "match",
            ["get", config.color.field],
            ...Object.keys(config.color.values).flatMap(key => [key, config.color.values[key]]),
            "#000000"
        ];
    }

    let interpolateExpression = ["linear"];
    if (config.interpolateExponent) {
        interpolateExpression = ["exponential", config.interpolateExponent];
    } 
    paint['circle-radius'] = [
        "interpolate", ["linear"], ["zoom"],
        1, ["interpolate", interpolateExpression,
            ["get", config.capacityField],
            config.minCapacity, config.minRadius,
            config.maxCapacity, config.maxRadius
        ],
        10, ["interpolate", interpolateExpression,
            ["get", config.capacityField],
            config.minCapacity, config.highZoomMinRadius,
            config.maxCapacity, config.highZoomMaxRadius
        ],

    ];

    
    map.addLayer({
        'id': 'assets',
        'type': 'circle',
        'source': 'assets-source',
        ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
        'layout': {},
        'paint': paint
    });

    // Add layer with proportional icons
    map.addLayer({
        'id': 'assets-symbol',
        'type': 'symbol',
        'source': 'assets-source',
        ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
        'layout': {
            'icon-image': ["get", "icon"],
            'icon-allow-overlap': true,
            'icon-size': [
                "interpolate", ["linear"], ["zoom"],
                1, ['interpolate', interpolateExpression,
                    ["to-number", ["get", config.capacityField]],
                    config.minCapacity, config.minRadius * 2 / 64,
                    config.maxCapacity, config.maxRadius * 2 / 64],
                10, ['interpolate', interpolateExpression,
                    ["to-number", ["get", config.capacityField]],
                    config.minCapacity, config.highZoomMinRadius * 2 / 64,
                    config.maxCapacity, config.highZoomMaxRadius * 2 / 64]
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
            ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
            'layout': {},
            'paint': paint,
            'filter': ['in', (config.linkField), '']
        }
    );
    map.addLayer(
        {
            'id': 'assets-labels',
            'type': 'symbol',
            'source': 'assets-source',
            ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
            'minzoom': 8,
            'layout': {
                'text-field': '{' + config.nameField + '}',
                'text-font': ["DIN Pro Italic"],
                'text-variable-anchor': ['top'],
                'text-offset': [0, 1],
                'text-size': 14
            },
            'paint': {
                'text-color': '#000000',
                'text-halo-color': "hsla(220, 8%, 100%, 0.75)",
                'text-halo-width': 1
            }
        }
    );

    map.addSource('countries', {
        'type': 'vector',
        'url': 'mapbox://mapbox.country-boundaries-v1'
    });
    map.addLayer(
        {
            'id': 'country-layer',
            'type': 'fill',
            'source': 'countries',
            'source-layer': 'country_boundaries',
            'layout': {},
            'paint': {
                'fill-color': 'hsla(219, 0%, 100%, 0%)'
            }
        }
    );

    map.addLayer({
        id: 'satellite',
        source: { "type": "raster", "url": "mapbox://mapbox.satellite", "tileSize": 256 },
        type: "raster",
        layout: { 'visibility': 'none' }
    }, 'assets');

    addEvents();
}

function addEvents() {
    map.on('click', 'assets', (e) => {
        const bbox = [ [e.point.x - 5, e.point.y - 5], [e.point.x + 5, e.point.y + 5]];
        const selectedFeatures = getUniqueFeatures(map.queryRenderedFeatures(bbox, {layers: ['assets']}), config.linkField).sort((a, b) => a.properties[config.nameField].localeCompare(b.properties[config.nameField]))
        ;

        const links = selectedFeatures.map(
            (feature) => feature.properties[config.linkField]
        );

        setHighlightFilter(...links);

        if (selectedFeatures.length == 1) {
            //if (config.tiles) {
            //    displayDetails([selectedFeatures[0]]);
            //} else {
                displayDetails(config.linked[selectedFeatures[0].properties[config.linkField]]);
            //}
        } else {
            var modalText = "<h6 class='p-3'>There are multiple " + config.assetFullLabel + " near this location. Select one for more details</h6><ul>";
            selectedFeatures.forEach((feature) => {
                //if (config.tiles) {
                //    modalText += "<li class='asset-select-option' onClick='displayDetails(\"" + JSON.stringify([feature]).replace(/"/g, '\\"') + "\")'>" + feature.properties[config.nameField] + "</li>";
                //} else {
                    modalText += "<li class='asset-select-option' onClick='displayDetails(\"" + JSON.stringify(config.linked[feature.properties[config.linkField]]).replace(/"/g, '\\"') + "\")'>" + feature.properties[config.nameField] + "</li>";
                //}
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
        const description = e.features[0].properties[config.nameField];
        popup.setLngLat(coordinates).setHTML(description).addTo(map);
    });
    map.on('mouseleave', 'assets', () => {
        map.getCanvas().style.cursor = '';
        popup.remove();
    });  

    $('#basemap-toggle').on("click", function() {
        if (config.baseMap == "Streets") {
           // $('#basemap-toggle').text("Streets");
           config.baseMap = "Satellite";
           map.setLayoutProperty('satellite', 'visibility', 'visible');
        } else {
           // $('#basemap-toggle').text("Satellite");
           config.baseMap = "Streets";
           map.setLayoutProperty('satellite', 'visibility', 'none');
        }
    });
}

/*
  legend filters
*/ 
function buildFilters() {
    countFilteredFeatures();
    config.filters.forEach(filter => {
        if (config.color.field != filter.field) {
            $('#filter-form').append('<hr/><h6 class="card-title">' + (filter.label || filter.field.replaceAll("_"," ")) + '</h6>');
        }
        for (let i=0; i<filter.values.length; i++) {
            let check_id =  filter.field + '_' + filter.values[i];
            let check = `<div class="row filter-row" data-checkid="${(check_id).replace('/','\\/')}">`;
            check += '<div class="col-sm-1 checkmark" id="' + check_id + '-checkmark"></div>';
            check += `<div class="col-sm-8"><input type="checkbox" checked class="form-check-input d-none" id="${check_id}">`;
            check += (config.color.field == filter.field ? '<span class="legend-dot" style="background-color:' + config.color.values[ filter.values[i] ] + '"></span>' : "");
            check +=  `<span id='${check_id}-label'>` + ('values_labels' in filter ? filter.values_labels[i] : filter.values[i].replaceAll("_", " ")) + '</span></div>';
            check += '<div class="col-sm-3 text-end" id="' + check_id + '-count">' + config.filterCount[filter.field][filter.values[i]] + '</div></div>';
            $('#filter-form').append(check);
        }
    });
    $('.filter-row').each(function() {
        this.addEventListener("click", function() {
            $('#' + this.dataset.checkid).click();
            toggleFilter(this.dataset.checkid);
            filterData();
        });
    });
}
function toggleFilter(id) {
    $('#' + id + '-checkmark').toggleClass('checkmark uncheckmark');
}
function selectAllFilter() {
    $('.filter-row').each(function() {
        if (! $('#' + this.dataset.checkid)[0].checked) {
            $('#' + this.dataset.checkid)[0].checked = true;
            toggleFilter(this.dataset.checkid);
        }
    });
    filterData();
}
function clearAllFilter() {
    $('.filter-row').each(function() {
        if ($('#' + this.dataset.checkid)[0].checked) {
            $('#' + this.dataset.checkid)[0].checked = false;
            toggleFilter(this.dataset.checkid);
        }
    });
    filterData();
}
function countFilteredFeatures() {
    config.filterCount = {};
    config.filters.forEach(filter => {
        config.filterCount[filter.field] = {};
        filter.values.forEach(val => {
            config.filterCount[filter.field][val] = 0;
        });
    });

    let ref = "config.processedGeoJSON.features"
    //if (config.tiles) {
    //    ref = "map.queryRenderedFeatures({layers: ['assets']})"
    //} 
    eval(ref).forEach(feature => {
        if ('summary_count' in feature.properties) {
            let summary_count = JSON.parse(feature.properties.summary_count);
            Object.keys(summary_count).forEach((filter) => {
                Object.keys(summary_count[filter]).forEach((value) => {
                    config.filterCount[filter][value] += summary_count[filter][value];
                });
            });
        } else {
            config.filters.forEach(filter => {
                filter.values.forEach(val => {
                    if (feature.properties[filter.field] == val) {
                        config.filterCount[filter.field][val]++;
                    }
                });
            });
        }
    });
}
function filterData() {
    if (config.tiles) {
        filterTiles();
    } else {
        filterGeoJSON();
    }
}

function filterTiles() {
    let filterStatus = {};
    config.filters.forEach(filter => {
        filterStatus[filter.field] = [];
    });
    $('.form-check-input').each(function() {
        if (this.checked) {
            let [field, ...value] = this.id.split('_');
            filterStatus[field].push(value.join('_'));
        }
    });

    config.filterExpression = [];
    if (config.searchText.length >= 3) {
        let searchExpression = ['any'];
        config.selectedSearchFields.split(',').forEach((field) => {
            searchExpression.push(['in', ['literal', config.searchText], ['downcase', ["get", field]]]);

        });
        config.filterExpression.push(searchExpression);
    }
    if (config.selectedCountries.length > 0) {
        config.filterExpression.push(['in', ['get', config.countryField], ['literal', config.selectedCountries]]);
    }
    for (let field in filterStatus) {
        config.filterExpression.push(['in', ['get', field], ['literal', filterStatus[field]]]);
    }
    if (config.filterExpression.length == 0) {
        config.filterExpression = null;
    } else {
        config.filterExpression.unshift("all");
    }
    map.setFilter('assets', config.filterExpression);
    map.setFilter('assets-labels', config.filterExpression);


    map.on('idle', filterGeoJSON);
}

function filterGeoJSON() {
    map.off('idle', filterGeoJSON);

    let filterStatus = {};
    config.filters.forEach(filter => {
        filterStatus[filter.field] = [];
    });
    $('.form-check-input').each(function () {
        if (this.checked) {
            let [field, ...value] = this.id.split('_');
            filterStatus[field].push(value.join('_'));
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
            if (config.selectedSearchFields.split(',').filter((field) => {
                return feature.properties[field].toLowerCase().includes(config.searchText);
            }).length == 0) include = false;
        }
        if (config.selectedCountries.length > 0) {
            if (! (config.selectedCountries.includes(feature.properties[config.countryField]))) include = false;
        }
        if (include) {
            filteredGeoJSON.features.push(feature);
        }
    });
    config.processedGeoJSON = JSON.parse(JSON.stringify(filteredGeoJSON));
    findLinkedAssets();
    updateTable();
    updateSummary();

    if (! config.tiles) {
        map.getSource('assets-source').setData(config.processedGeoJSON);
    }
}
function updateSummary() {
    $('#total_in_view').text(config.totalCount.toString())
    $('#summary').text("Total " + config.assetFullLabel + " selected");
    countFilteredFeatures();
    config.filters.forEach((filter) => {
        for (let i=0; i<filter.values.length; i++) {
            let count_id =  (filter.field + '_' + filter.values[i] + '-count').replace('/','\\/');
            $('#' + count_id).text(config.filterCount[filter.field][filter.values[i]]);
        }
    });
}

/*
  table view
*/
function buildTable() {
    $('#table-toggle').on("click", function() {
        if ($('#table-toggle-label').text().includes("Table view")) {
            $('#table-toggle-label').html("Map view <img src='../../src/img/arrow-right.svg' width='15'>");
            $('#map').hide();
            $('#sidebar').hide();
            $('#table-container').show();
            $('#basemap-toggle').hide();
            updateTable(true);
        } else {
            $('#table-toggle-label').html("Table view <img src='../../src/img/arrow-right.svg' width='15'>");
            $('#map').show();
            $('#sidebar').show();
            $('#table-container').hide();
            $('#basemap-toggle').show();
        }
    });
}
function createTable() {
    if ('rightAlign' in config.tableHeaders) {
        config.tableHeaders.rightAlign.forEach((col) => {
            $("#site-style").get(0).sheet.insertRule('td:nth-child(' + (config.tableHeaders.values.indexOf(col)+1) + ') { text-align:right }', 0);
        });
    }
    if ('noWrap' in config.tableHeaders) {
        config.tableHeaders.noWrap.forEach((col) => {
            $("#site-style").get(0).sheet.insertRule('td:nth-child(' + (config.tableHeaders.values.indexOf(col)+1) + ') { white-space: nowrap }', 0);
        });        
    }
    config.table = $('#table').DataTable({
        data: geoJSON2Table(),
        searching: false,
        pageLength: 100,
        fixedHeader: true,
        columns: config.tableHeaders.labels.map((header) => { return {'title': header}})
    });
}
function updateTable(force) {
    // table create/update with large number of rows is slow, only do it if visible
    if ($('#table-container').is(':visible') || force) {
        if (config.table == null) {
            createTable();
        } else if (config.tableDirty) {
            config.table.clear();
            config.table.rows.add(geoJSON2Table()).draw();
        }
        config.tableDirty = false;
    } else {
        config.tableDirty = true;
    }
}
function geoJSON2Table() {
    return config.preLinkedGeoJSON.features.map(feature => {
        return config.tableHeaders.values.map((header) => {
            if ('clickColumns' in config.tableHeaders && config.tableHeaders.clickColumns.includes(header)) {
                return "<a href='" + feature.properties[config.linkField] + "' target='_blank'>" + feature.properties[header] + '</a>'; 
            } else {
                return feature.properties[header];
            }
        });
    });
}
function geoJSON2Headers() {
    return Object.keys(config.geojson.features[0].properties).map((k) => {
        return {'title': k}
    });
}

/*
  modals
*/
function enableModal() {
    config.modal = new bootstrap.Modal($('#modal'));
    $('#modal').on('hidden.bs.modal', function (event) {
        setHighlightFilter('');
    })
}
function setHighlightFilter(links) {
    let filter;
    if (config.filterExpression != null) {
        filter = JSON.parse(JSON.stringify(config.filterExpression));
        filter.push([
            '==',
            ["get", config.linkField],
            ["literal", links]
        ]);
    } else {
        filter = [
            '==',
            ["get", config.linkField],
            ["literal", links]
        ];
    }
    map.setFilter('assets-highlighted',filter);
}

function displayDetails(features) {
    if (typeof features == "string") {
        features = JSON.parse(features);
    }
    var detail_text = '';
    var location_text = '';
    Object.keys(config.detailView).forEach((detail) => {
        if (Object.keys(config.detailView[detail]).includes('display')) {

            if (config.detailView[detail]['display'] == 'heading') {

                detail_text += '<h4>' + features[0].properties[detail] + '</h4>';

            } else if (config.detailView[detail]['display'] == 'join') {

                let join_array = features.map((feature) => feature.properties[detail]);
                join_array = join_array.filter((value, index, array) => array.indexOf(value) === index);
                if (join_array.length > 1) {
                    if (Object.keys(config.detailView[detail]).includes('label')) {
                        detail_text += '<span class="fw-bold">' + config.detailView[detail]['label'][1] + '</span>: ';
                    }
                    detail_text += '<span class="text-capitalize">' + join_array.join(',').replaceAll('_',' ') + '</span><br/>';
                } else {
                    if (Object.keys(config.detailView[detail]).includes('label')) {
                        detail_text += '<span class="fw-bold">' +config.detailView[detail]['label'][0] + '</span>: ';
                    }
                    detail_text += '<span class="text-capitalize">' + join_array[0].replaceAll('_',' ') + '</span><br/>';;
                }

            } else if (config.detailView[detail]['display'] == 'range') {

                let greatest = features.reduce((accumulator, feature) => {
                        return (feature.properties[detail] != '' && feature.properties[detail] > accumulator ?  feature.properties[detail] : accumulator);
                    },
                    0
                ); 
                let least = features.reduce((accumulator, feature) => {
                        return (feature.properties[detail] != '' && feature.properties[detail] < accumulator ?  feature.properties[detail] : accumulator);
                 },
                 5000
                );
                if (least != 5000) {
                    if (least == greatest) {
                        detail_text += '<span class="fw-bold">' + config.detailView[detail]['label'][0] + '</span>: ' + least.toString() + '<br/>';
                    } else {
                        detail_text += '<span class="fw-bold">' + config.detailView[detail]['label'][1] + '</span>: ' + least.toString() + ' - ' + greatest.toString() + '<br/>';          
                    }
                }
                
            } else if (config.detailView[detail]['display'] == 'location') {

                if (Object.keys(features[0].properties).includes(detail)) {
                    if (location_text.length > 0) {
                        location_text += ', ';
                    }
                    location_text += features[0].properties[detail];
                }

            }
        } else {
            if (features[0].properties[detail] != '') {
                if (Object.keys(config.detailView[detail]).includes('label')) {
                    detail_text += '<span class="fw-bold">' + config.detailView[detail]['label'] + '</span>: ' + features[0].properties[detail] + '<br/>';
                } else {
                    detail_text += features[0].properties[detail] + '<br/>';
                }
            }
        }
    });

    let filterIndex = 0;
    for (const[index, filter] of config.filters.entries()) {
        if (filter.field == config.statusField) {
            filterIndex = index;
        }
    }
    let capacity = Object.assign(...config.filters[filterIndex].values.map(f => ({[f]: 0})));
    let count = Object.assign(...config.filters[filterIndex].values.map(f => ({[f]: 0})));

    features.forEach((feature) => {
        capacity[feature.properties[config.statusField]] += feature.properties[config.capacityField];
        count[feature.properties[config.statusField]]++;
    });

    let detail_capacity = '';
    Object.keys(capacity).forEach((k) => {
        if (capacity[k] != 0) {
           detail_capacity += '<div class="row"><div class="col-5"><span class="legend-dot" style="background-color:' + config.color.values[ k ] + '"></span>' + k + '</div><div class="col-4">' + capacity[k] + '</div><div class="col-3">' + count[k] + " of " + features.length + "</div></div>";
        }
    });

    //Location by azizah from <a href="https://thenounproject.com/browse/icons/term/location/" target="_blank" title="Location Icons">Noun Project</a> (CC BY 3.0)
    $('.modal-body').html('<div class="row m-0">' +
        '<div class="col-sm-5 rounded-top-left-1" id="detail-satellite" style="background-image:url(' + buildSatImage(features) + ')">' +
            '<img id="detail-location-pin" src="../../src/img/location.svg" width="30">' +
            '<span class="detail-location">' + location_text + '</span><br/>' +
            '<span class="align-bottom p-1" id="detail-more-info"><a href="' + features[0].properties[config.linkField] + '" target="_blank">MORE INFO</a></span>' +
            (config.showAllPhases && features.length > 1 ? '<span class="align-bottom p-1" id="detail-all-phases"><a onClick="showAllPhases(\'' + link + '\')">ALL PHASES</a></span>' : '') +
        '</div>' +
        '<div class="col-sm-7 py-2" id="total_in_view">' + detail_text + 
            '<div">' + 
                '<div class="row pt-2 justify-content-md-center">Total ' + config.assetLabel + ': ' + features.length + '</div>' +
                '<div class="row" style="height: 2px"><hr/></div>' +
                '<div class="row "><div class="col-5 text-capitalize">' + config.color.field + '</div><div class="col-4">' + config.capacityLabel + '</div><div class="col-3">#&nbsp;of&nbsp;' + config.assetLabel + '</div></div>' +
                detail_capacity +
            '</div>' +
        '</div></div>');

    setHighlightFilter(features[0].properties[config.linkField]);
}
function buildSatImage(features) {
    let location_arg = '';
    let bbox = [];
    let coords = [];
    let geojson_arg = '';
    features.forEach((feature) => {
        var feature_lng = Number(feature.geometry.coordinates[0]);
        var feature_lat = Number(feature.geometry.coordinates[1]);
        if (bbox.length == 0) {
            bbox[0] = feature_lng;
            bbox[1] = feature_lat;
            bbox[2] = feature_lng;
            bbox[3] = feature_lat;
        } else {
            if (feature_lng < bbox[0]) bbox[0] = feature_lng;
            if (feature_lat < bbox[1]) bbox[1] = feature_lat;
            if (feature_lng > bbox[2]) bbox[2] = feature_lng;
            if (feature_lat > bbox[3]) bbox[3] = feature_lat;
        }
        coords.push([feature_lng,feature_lat]);
    });
    if (bbox[0] == bbox[2] && bbox[1] == bbox[3]) {
        location_arg = bbox[0].toString() + ',' + bbox[1].toString() + ',' + config.img_detail_zoom.toString();
    } else {
        location_arg = '[' + bbox.join(',') + ']';
       // geojson_arg = 'geojson(' + encodeURIComponent(JSON.stringify({'type': 'Feature','properties':{},'geometry': {'type': 'MultiPoint', 'coordinates': coords}})) + ')/';
    }

    return 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/' + geojson_arg + location_arg + '/350x350?attribution=false&logo=false&access_token=' + config.accessToken;
}
function showAllPhases(link) {
    config.modal.hide();
    setHighlightFilter(link);
    var bbox = [];
    config.linked[link].forEach((feature) => {
        var feature_lng = Number(feature.geometry.coordinates[0]);
        var feature_lat = Number(feature.geometry.coordinates[1]);
        if (bbox.length == 0) {
            bbox[0] = feature_lng;
            bbox[1] = feature_lat;
            bbox[2] = feature_lng;
            bbox[3] = feature_lat;
        } else {
            if (feature_lng < bbox[0]) bbox[0] = feature_lng;
            if (feature_lat < bbox[1]) bbox[1] = feature_lat;
            if (feature_lng > bbox[2]) bbox[2] = feature_lng;
            if (feature_lat > bbox[3]) bbox[3] = feature_lat;
        }
    });

    map.flyTo({center: [(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2], zoom: config.phasesZoom});
}

/* 
  toolbar filters
*/

function enableNavFilters() {
    enableSearch();
    enableSearchSelect();
    enableCountrySelect();

    document.addEventListener("DOMContentLoaded", function() {

        // make it as accordion for smaller screens
        if (window.innerWidth < 992) {
        
        // close all inner dropdowns when parent is closed
         $('.navbar .dropup').forEach((everydropdown) => {
            everydropdown.addEventListener('hidden.bs.dropdown', function () {
              // after dropdown is hidden, then find all submenus
                $('.submenu').forEach((everysubmenu) => {
                  // hide every submenu as well
                  everysubmenu.style.display = 'none';
                });
            })
          });
        
        $('.dropdown-menu a').forEach((element) => {
            element.addEventListener('click', function (e) {
                let nextEl = this.nextElementSibling;
                if(nextEl && nextEl.classList.contains('submenu')) {	
                  // prevent opening link if link needs to open dropdown
                  e.preventDefault();
                  if(nextEl.style.display == 'block'){
                    nextEl.style.display = 'none';
                  } else {
                    nextEl.style.display = 'block';
                  }
        
                }
            });
          })
        }
        // end if innerWidth
    }); 
}
function enableCountrySelect() {
    Object.keys(countries).forEach((continent) => {
        let dropdown_html = `<li><hr class="dropdown-divider"></li><li><a class="country-dropdown-item dropdown-item h4" data-countries="${countries[continent].join(',')}" data-countryText="${continent}" href="#">${continent}</a>`;
        dropdown_html += '<ul class="submenu dropdown-menu">';
        countries[continent].forEach((country, idx) => {
            dropdown_html += `<li><a class="h5 country-dropdown-item dropdown-item" data-countries="${country}" data-countryText="${country}" href="#">${country}</a></li>`;
            if (idx != countries[continent].length - 1) {
                dropdown_html += '<li><hr class="dropdown-divider"></li>';
            }
        });
        dropdown_html += "</ul></li>";
        $('#country_select').append(dropdown_html);
    });

    $('.country-dropdown-item').each(function() {
        this.addEventListener("click", function() {
            config.selectedCountryText = this.dataset.countrytext;
            config.selectedCountries = (this.dataset.countries.length > 0 ?  this.dataset.countries.split(",") : []);
            $('#selectedCountryLabel').text(config.selectedCountryText || "all");
            filterData();
        });
    });

    config.selectedCountries = [];
    config.selectedCountryText = '';
}
function enableSearch() {
    $('#search-text').on('keyup paste', debounce(function() {
        config.searchText = $('#search-text').val().toLowerCase();
        filterData();
    }, 500));
    config.searchText = '';
}
function enableSearchSelect() {
    let dropdown_html = '';
    let allSearchFields = [];
    Object.keys(config.searchFields).forEach((field_label) => {
        dropdown_html += `<li><a class="h5 search-dropdown-item dropdown-item" data-searchFieldText="${field_label}" data-searchFields="${config.searchFields[field_label].join(',')}" href="#">${field_label}</a></li>`;
        allSearchFields = allSearchFields.concat(config.searchFields[field_label]);
    });
    dropdown_html = `<li><a class="h5 search-dropdown-item dropdown-item" data-searchFieldText="all" data-searchFields="${allSearchFields.join(',')}" href="#">all</a></li>` 
        + dropdown_html;
    $('#search_type_select').append(dropdown_html);

    $('.search-dropdown-item').each(function() {
        this.addEventListener("click", function() {
            config.selectedSearchFields = this.dataset.searchfields;
            $('#selectedSearchLabel').text(this.dataset.searchfieldtext);
            filterData();
        });
    });

    config.selectedSearchFields = allSearchFields.join(',');
}

/* 
  Util functions
*/

function getUniqueFeatures(features, comparatorProperty) {
    const uniqueIds = new Set();
    const uniqueFeatures = [];
    for (const feature of features) {
        const id = feature.properties[comparatorProperty];
        if (!uniqueIds.has(id)) {
            uniqueIds.add(id);
            uniqueFeatures.push(feature);
        }
    }
    return uniqueFeatures;
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
