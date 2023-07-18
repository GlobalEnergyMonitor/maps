processConfig();

function processConfig() {
    // Merge site-config.js and config.js
    config = Object.assign(site_config, config);

    // Set defaults
    if (!('linkField' in config)) config.linkField = 'url';
    if (!('countryField' in config)) config.countryField = 'country';
    if (!('locationColumns' in config)) {
        config.locationColumns = {};
        config.locationColumns['lng'] = 'lng';
        config.locationColumns['lat'] = 'lat';
    }
    config.baseMap = "Streets";
    config.icons = [];

    Object.keys(config.color.values).forEach((color_key) => {
        config.color.values[color_key] = config.colors[ config.color.values[color_key] ];
    });
}

mapboxgl.accessToken = config.accessToken;
const map = new mapboxgl.Map({
    container: 'map',
    style: config.mapStyle,
    zoom: 2,
    center: [0, 0],
    maxBounds: [[-180,-85],[180,85]],
    projection: 'naturalEarth'
});
map.addControl(new mapboxgl.NavigationControl({showCompass: false}));
const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
});
map.dragRotate.disable();
map.touchZoomRotate.disableRotation();

$(document).ready(function() {
    loadData();
    enableSearch();
    enableModal();
    enableNavSelect();
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
    buildFilters();
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

        config.processedGeoJSON.features.push(features[0]);
    });
}

function addLayers() {
    getMinMax();
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
              ];
        }

        paint['circle-radius'] = [
            "interpolate", ["linear"], ["zoom"],
            1, ["interpolate", ["linear"],
                ["get", config.capacityField],
                    config.minCapacity, config.minRadius,
                    config.maxCapacity, config.maxRadius
                ],
            10, ["interpolate", ["linear"],
            ["get", config.capacityField],
                config.minCapacity, config.highZoomMinRadius,
                config.maxCapacity, config.highZoomMaxRadius
            ],

        ];

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
                        "interpolate", ["linear"], ["zoom"],
                        1, [ 'interpolate', ['linear'],
                            ["to-number", ["get", config.capacityField]],
                            config.minCapacity, config.minRadius * 2 / 64, 
                            config.maxCapacity, config.maxRadius * 2 / 64 ],
                        10, [ 'interpolate', ['linear'],
                            ["to-number", ["get", config.capacityField]],
                            config.minCapacity, config.highZoomMinRadius * 2 / 64, 
                            config.maxCapacity, config.highZoomMaxRadius * 2 / 64 ]
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
            source: {"type": "raster",  "url": "mapbox://mapbox.satellite", "tileSize": 256},
            type: "raster",
            layout: {'visibility': 'none'}
          }, 'assets');
          

        addEvents();
    }); 
}

function addEvents() {
    map.on('click', 'assets', (e) => {
        const bbox = [ [e.point.x - 5, e.point.y - 5], [e.point.x + 5, e.point.y + 5]];
        const selectedFeatures = getUniqueFeatures(map.queryRenderedFeatures(bbox, {layers: ['assets']}), config.linkField).sort((a, b) => a.properties['project'].localeCompare(b.properties['project']))
        ;

        const links = selectedFeatures.map(
            (feature) => feature.properties[config.linkField]
        );

        map.setFilter('assets-highlighted', [
            'in',
            config.linkField,
            ...links
        ]);

        if (selectedFeatures.length == 1) {
            displayDetails(selectedFeatures[0].properties[config.linkField]);
        } else {
            var modalText = "<h6 class='p-3'>There are multiple " + config.assetLabel + " near this location. Select one for more details</h6><ul>";
            selectedFeatures.forEach((feature) => {
                modalText += "<li class='asset-select-option' onClick=\"displayDetails('" + feature.properties[config.linkField] + "')\">" + feature.properties['project'] + "</li>";
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
        const description = e.features[0].properties['project'];
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

function getMinMax() {
    config.maxCapacity = 0;
    config.minCapacity = 1000000;
    config.processedGeoJSON.features.forEach((feature) => {
        if (feature.properties[config.capacityField] > config.maxCapacity) {
            config.maxCapacity =  feature.properties[config.capacityField];
        }
        if (feature.properties[config.capacityField] < config.minCapacity) {
            config.minCapacity =  feature.properties[config.capacityField];
        }       
    });
}

function buildFilters() {
    countFilteredFeatures();
    config.filters.forEach(filter => {
        if (! filter.primary) {
            $('#filter-form').append('<hr/><h6 class="card-title">' + (filter.label || filter.field.replaceAll("_"," ")) + '</h6>');
        }
        for (let i=0; i<filter.values.length; i++) {
            let check_id =  filter.field + '_' + filter.values[i];
            let check = `<div class="row filter-row" data-checkid="${check_id}"><div class="form-check col-sm-8"><input type="checkbox" checked class="form-check-input d-none" id="${check_id}">`;
            check += '<label class="form-check-label" for="' + check_id + '">' +
                (filter.primary ? '<span class="legend-dot" style="background-color:' + config.color.values[ filter.values[i] ] + '"></span>' : "") + 
                ('values_labels' in filter ? filter.values_labels[i] : filter.values[i].replaceAll("_", " ")) 
                + '</label></div><div class="col-sm-1 eye" id="' + check_id + '-eye"></div><div class="col-sm-3" id="' + check_id + '-count">' + config.filterCount[filter.field][filter.values[i]] + '</div></div>';
            $('#filter-form').append(check);
        }
    });
    $('.filter-row').each(function() {
        this.addEventListener("click", function() {
            toggleFilter(this.dataset.checkid);

        });
    });
    $('.form-check-input').each(function() {
        this.addEventListener("click", function() {
            toggleFilter(this.id);
        });
    });
}

function toggleFilter(id) {
    filterGeoJSON();
    $('#' + id + '-eye').toggleClass('eye eye-slash');
    $("label[for='" + id + "']").toggleClass('text-decoration-line-through');
    $('#' + id + '-count').toggleClass('text-decoration-line-through');
}

function countFilteredFeatures() {
    config.filterCount = {};
    config.filters.forEach(filter => {
        config.filterCount[filter.field] = {};
        filter.values.forEach(val => {
            config.filterCount[filter.field][val] = 0;
        });
    })
    config.processedGeoJSON.features.forEach(feature => {
        config.filters.forEach(filter => {
            if (! (filter.field in config.filterCount)) config.filterCount[filter.field] = {};
            if (! (feature.properties[filter.field] in config.filterCount[filter.field]))
                config.filterCount[filter.field][feature.properties[filter.field]] = 0;
            config.filterCount[filter.field][feature.properties[filter.field]]++;
        })
    });
}

function filterGeoJSON() {
    let filterStatus = {};
    config.filters.forEach(filter => {
        filterStatus[filter.field] = [];
    });
    $('.form-check-input').each(function() {
        if (this.checked) {
            let [field, value] = this.id.split('_');
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

function buildTable() {

    config.table = $('#table').DataTable({
        data: geoJSON2Table(),
        searching: false,
        pageLength: 100,
        columns: config.tableHeaders.values.map((header) => { return {'title': header}})
    });

    config.table.column(config.tableHeaders.values.indexOf(config.tableHeaders.clickColumn)).visible(false);

    $('#table-toggle').on("click", function() {
        if ($('#table-toggle').text() == "Table view") {
            $('#table-toggle').text("Map view");
            $('#map').hide();
            $('#sidebar').hide();
            $('#table-container').show();
            $('#basemap-toggle').hide();
        } else {
            $('#table-toggle').text("Table view");
            $('#map').show();
            $('#sidebar').show();
            $('#table-container').hide();
            $('#basemap-toggle').show();
        }
    });

    $('#table tbody tr').click(function() {
        window.open(config.table.row(this).data()[config.tableHeaders.values.indexOf(config.tableHeaders.clickColumn)], '_blank');
    });
}
function updateTable() {
    config.table.clear();
    config.table.rows.add(geoJSON2Table()).draw();
}
function geoJSON2Table() {
    return config.processedGeoJSON.features.map(feature => {
        return config.tableHeaders.values.map((header) => { 
            return feature.properties[header]; 
        });
    });
}
function geoJSON2Headers() {
    return Object.keys(config.geojson.features[0].properties).map((k) => {
        return {'title': k}
    });
}

function updateSummary() {
    $('#total_in_view').text(config.processedGeoJSON.features.length.toString())
    $('#summary').text("Total " + config.assetLabel + " selected");
    //TODO -- update filter counts
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
    var bbox = [];
    var start_year;
    config.linked[link].forEach((feature => {
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
            if (feature_lat< bbox[3]) bbox[3] = feature_lat;
        }
        
        if ((! start_year) || (feature.properties['start_year'] < start_year)) {
            start_year = feature.properties['start_year'];
        }
    }));
    var img_lng = (bbox[0] + bbox[2]) / 2;
    var img_lat = (bbox[1] + bbox[3]) / 2;

    var feature = config.linked[link][0];
    var detail_text = feature.properties['project'] + '<br/>' +
        (feature.properties['project_loc'] != '' ? feature.properties['project_loc'] + '<br/>' : '') +
        "Owner: " + feature.properties['owner'] + '<br/>' + 
        "Parent: " + feature.properties['parent'] + '<br/>' +
        "Technology: " + feature.properties['technology'] + '<br/>' +
        "Fuel type:" + feature.properties['fuel_type'] + '<br/>' +
        "Start year:" + start_year;
    $('.modal-body').html('<div class="row m-0">' +
        '<div class="col-sm-4 rounded-top-left-1" id="detail-satellite" style="height: 300px;background-image:url(https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/' + img_lng.toString() + ',' + img_lat.toString() + ',' + config.img_detail_zoom.toString() + ',0/200x350?access_token=' + config.accessToken + ')">' +
        '</div>' +
        '<div class="col-sm-8" id="total_in_view">' + detail_text + '</div>' +
        '</div>');
//    $('.modal-title').text('details');

    map.setFilter('assets-highlighted', [
        '==',
        config.linkField,
        link
    ]);
}

function enableNavSelect() {
    enableCountrySelect();
    enableSearchSelect();

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
            filterGeoJSON();
        });
    });

    config.selectedCountries = [];
    config.selectedCountryText = '';
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
            filterGeoJSON();
        });
    });

    config.selectedSearchFields = allSearchFields.join(',');
}