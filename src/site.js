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
    center: config.center,
    projection: config.projection
});

// add new navigation features
map.scrollZoom.enable();
map.boxZoom.enable();
map.dragRotate.enable();
map.dragPan.enable();
map.keyboard.enable();
map.doubleClickZoom.enable();
map.touchZoomRotate.enable();

// Disable spinning when user interacts with the map
[
    'mousedown',
    'wheel',
    'touchstart',
    'dragstart',
    'rotatestart',
    'zoomstart',
    'keydown'
].forEach(event => {
    map.on(event, () => {
        userInteracting = true;
    });
});

/*
    *  When a user clicks the button, `fitBounds()` zooms and pans
    *  the viewport to contain a bounding box that surrounds Kenya.
    *  The [lng, lat] pairs are the southwestern and northeastern
    *  corners of the specified geographical bounds.
    */
// document.getElementById('fit').addEventListener('click', () => {
//     // map.fitBounds([
//     //     [32.958984, -5.353521], // [lng, lat] - southwestern corner of the bounds
//     //     [43.50585, 5.615985] // [lng, lat] - northeastern corner of the bounds
//     // ]);
//     // use the output or return of getBoundingBox() instead of hardcoded default of Kenya
//     let boundingBoxSet = getBoundingBox()
//     map.fitBounds(boundingBoxSet)
// });

map.addControl(new mapboxgl.NavigationControl({ showCompass: false }));
const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
});

// declare this so you can customize features depending on if it's first load or filtering
let initialLoad = true;

map.on('load', function () {
    if (config.projection != 'globe'){
        // map.setFog({}); // Set the default atmosphere style
        // $('#btn-spin-toggle').hide();
        // $('#fit').hide();

    }
    loadData();
});
function determineZoom() {
    let modifier = 650;
    if (window.innerWidth < 1000) { modifier = 500; }
    else if (window.innerWidth < 1500) { modifier = 575; }
    let zoom = config.zoomFactor * (window.innerWidth - modifier) / modifier;
    return zoom;
}

function getStandardDeviation (array) {
    if (!array || array.length === 0) {return 0;}

    const n = array.length
    const mean = array.reduce((a, b) => a + b) / n
    return Math.sqrt(array.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n)
    }

function findDensity(gridSize = 10) {
    /* This function augmnts the getBoundingBox function so that if there are anomolies they do not skew the "should be" center
    So for issues like Reunion island being technically part of France, or the typo of a oil plant that has South Dakota listed but 
    is in Mongolia
    */

    // get the average bounding box or center for all features listed
    // or for majority of features listed 
    // and then exclude the feature(s) whos center is too far from the average
    // OR try to see if you can measure the density of a layer and have the bounding box prefer a dense view instead of 
    // the ocean or a north or south pole

    // Find the densest region of features using a grid-based approach.
    // gridSize: size of grid cell in degrees (default 1 degree)


    features = config.processedGeoJSON.features
    // handle for no features returned
    if (!features.length) {
        console.warn('No features returned will not zoom in or fly');
        // TODO figure out zoom out and respin
        // maybe clear out filter after message saying nothing found
        // if (map.getZoom() < 12) {
        //     map.setZoom(12);
        // }
        return null;
    } else {

        // Collect all coordinates acccount for point, multipoint, linestring, multi line string
        let allCoords = [];
        features.forEach(f => {
            let coords = [];
            if (f.geometry && f.geometry.type === "Point") {
                coords = [f.geometry.coordinates];
            } else if (f.geometry && f.geometry.coordinates && f.geometry.coordinates.length) {
                coords = f.geometry.coordinates.flat(Infinity)
                    .filter(c => Array.isArray(c) && c.length === 2 && isFinite(c[0]) && isFinite(c[1]))
                    .map(c => [c[0], c[1]]);
            }
            // Ensure coords is always an array of [lng, lat]
            if (Array.isArray(coords[0])) {
                coords.forEach(c => {
                    if (Array.isArray(c) && c.length === 2 && isFinite(c[0]) && isFinite(c[1])) {
                        allCoords.push([c[0], c[1]]);
                    }
                });
            } else if (coords.length === 2 && isFinite(coords[0]) && isFinite(coords[1])) {
                allCoords.push([coords[0], coords[1]]);
            }
        });

        if (allCoords.length === 0) {
            // If nothing is selected, reset to initial center and resume spinning
            userInteracting = false;
            spinGlobe();
            // Return a small bounds around the initial center to trigger fitBounds
            const center = config.center;
            const pad = 0.5;
            return [
                [center[0] - pad, center[1] - pad], // SW
                [center[0] + pad, center[1] + pad]  // NE
            ];
        }
        console.log('len of allC' + allCoords.length)
        // Build grid and count points in each cell
        const grid = {};
        allCoords.forEach(([lng, lat]) => {
            // Round to grid cell
            const x = Math.floor(lng / gridSize);
            const y = Math.floor(lat / gridSize);
            const key = `${x},${y}`;
            if (!grid[key]) grid[key] = [];
            grid[key].push([lng, lat]);
        });

        // Find the cell with the most points
        let maxCell = null;
        let maxCount = 0;
        Object.entries(grid).forEach(([key, points]) => {
            if (points.length > maxCount) {
                maxCount = points.length;
                maxCell = key;
            }
        });

        // if (!maxCell) {
        //     // fallback: use the bounding box of all points
        //     let minLng = Infinity, minLat = Infinity, maxLng = -Infinity, maxLat = -Infinity;
        //     allCoords.forEach(([lng, lat]) => {
        //         minLng = Math.min(minLng, lng);
        //         minLat = Math.min(minLat, lat);
        //         maxLng = Math.max(maxLng, lng);
        //         maxLat = Math.max(maxLat, lat);
        //     });
        //     const pad = 0.2;
        //     return [
        //         [minLng - pad, minLat - pad], // SW
        //         [maxLng + pad, maxLat + pad]  // NE
        //     ];
        // }

        // Get the densest cell's bounding box
        const [cellX, cellY] = maxCell.split(',').map(Number);
        const minLng = cellX * gridSize;
        const minLat = cellY * gridSize;
        const maxLng = minLng + gridSize;
        const maxLat = minLat + gridSize;


        // find difference between min and max lng to see if should return null
        let diffLng = Math.abs(minLng - maxLng)
        // if absolute value of diff is more than 179 return null
        if (diffLng > 270) {
            console.log('Greater than 270: ' + diffLng)
            return null;
        }
        console.log('diffLng: ' + diffLng)

        console.log('SW['+ minLng +',' + minLat +']')
        console.log('NE['+ maxLng +',' + maxLat +']')
    

        // Optionally, expand the bounding box slightly for better fit
        // if one feature padding of .5 else ... 
        const pad = 0;
        return [
            [minLng - pad, minLat - pad], // SW
            [maxLng + pad, maxLat + pad]  // NE
        ];
    }
}

function getBoundingBox(features) {
    // this function will result in two coordinate pairings that look like the example below
    // it'll be used by the mapbox fitbounds() method to re orient the map based off of the locations of selected / filtered projects or map assets
    // those projects can be selected by the user in four ways:
    // 1.) adjusting the legend filters on status or project type -- rarely will be fitBounds eligible
    // 2.) selecting a country or continent from the dropdown -- TODO implement std dev but done, instead using density but with a maxZoom
    // 3.) searching by name of the project in the search bar -- done
    // 4.) clicking an asset // USE flyTo DONE
    // TODO if user interacting do not initiate fitBounds ... do we wait? 
    // sometimes only one project or asset will be returned 
    // in most cases though many projects will be returned
    // this function should calculate the most relevant bounding box that helps focus and zoom the user into their area of interest on the map
    // [32.958984, -5.353521], // [lng, lat] - southwestern corner of the bounds
    // [43.50585, 5.615985] // [lng, lat] - northeastern corner of the bounds

    // If no features provided, use currently filtered features
    if (!features) {
        features = config.processedGeoJSON && config.processedGeoJSON.features
            ? config.processedGeoJSON.features
            : [];
    }
    if (!features.length) {
        // Return a small bounds around the initial center to trigger fitBounds
        return null;
    }
    // // Helper to flatten all coordinates from a geometry
    // function flattenCoords(geometry) {
    //     if (!geometry) return [];
    //     if (geometry.type === "Point") {
    //         return [geometry.coordinates];
    //     } else if (geometry.type === "MultiPoint" || geometry.type === "LineString") {
    //         return geometry.coordinates;
    //     } else if (geometry.type === "MultiLineString" || geometry.type === "Polygon") {
    //         return geometry.coordinates.flat();
    //     } else if (geometry.type === "MultiPolygon") {
    //         return geometry.coordinates.flat(2);
    //     }
    //     return [];
    // }

    // // Collect all coordinates from features
    // let allCoords = [];
    // features.forEach(feature => {
    //     allCoords.push(...flattenCoords(feature.geometry));
    // });
    // console.log('allCoords' + allCoords)

    // // Calculate mean and stddev for lng and lat
    // function getMeanStd(arr) {
    //     const n = arr.length;
    //     if (n === 0) return { mean: 0, std: 0 };
    //     const mean = arr.reduce((a, b) => a + b, 0) / n;
    //     const std = Math.sqrt(arr.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b, 0) / n);
    //     return { mean, std };
    // }
    // const lngs = allCoords.map(c => c[0]);
    // const lats = allCoords.map(c => c[1]);
    // const { mean: meanLng, std: stdLng } = getMeanStd(lngs);
    // const { mean: meanLat, std: stdLat } = getMeanStd(lats);

    // // Filter out features whose all coordinates are > 2 stddev from mean
    // const filteredFeatures = features.filter(feature => {
    //     const coords = flattenCoords(feature.geometry);
    //     // If any coordinate is within 2 stddev, keep the feature
    //     return coords.some(([lng, lat]) =>
    //         Math.abs(lng - meanLng) <= 2 * stdLng && Math.abs(lat - meanLat) <= 2 * stdLat
    //     );
    // });

    // // Use filteredFeatures for the rest of the function
    // let featuresGeo = filteredFeatures.map(f => f.geometry);


    let minLng = Infinity, minLat = Infinity, maxLng = -Infinity, maxLat = -Infinity;
    features.forEach(f => {
        let coords = f.geometry && f.geometry.type === "Point"
            ? f.geometry.coordinates
            : (f.geometry && f.geometry.coordinates && f.geometry.coordinates.length
                ? f.geometry.coordinates.flat(Infinity)
                : []);
        // Handle both Point and LineString/MultiPoint/MultiLineString
        if (Array.isArray(coords[0])) {
            coords.forEach(c => {
                if (Array.isArray(c) && c.length === 2) {
                    minLng = Math.min(minLng, c[0]);
                    minLat = Math.min(minLat, c[1]);
                    maxLng = Math.max(maxLng, c[0]);
                    maxLat = Math.max(maxLat, c[1]);
                }
            });
        } else if (coords.length === 2) {
            minLng = Math.min(minLng, coords[0]);
            minLat = Math.min(minLat, coords[1]);
            maxLng = Math.max(maxLng, coords[0]);
            maxLat = Math.max(maxLat, coords[1]);
        }
    });
    // If only one point, expand bounds slightly for better fit
    if (minLng === maxLng && minLat === maxLat) {
        const pad = 0.1;
        minLng -= pad; maxLng += pad;
        minLat -= pad; maxLat += pad;
    }

    // find difference between min and max lng to see if should return null
    let diffLng = Math.abs(minLng - maxLng)
    // if absolute value of diff is more than 179 return null
    if (diffLng > 270) {
        console.log('Greater than 270: ' + diffLng)
        return null;
    }
    console.log('diffLng: ' + diffLng)

    console.log('SW['+ minLng +',' + minLat +']')
    console.log('NE['+ maxLng +',' + maxLat +']')
    


    return [
        [minLng, minLat], // SW
        [maxLng, maxLat]  // NE
    ];
}

/*
  load data in various formats, and prepare for use in application
*/
function loadData() {
    // Here we could load in data from csv always minus what's needed for map dots?
    if ("tiles" in config) {
        console.log('addTiles');
        addTiles();
        Papa.parse(config.csv, {
            download: true,
            header: true,
            error: function(error, file) {
                console.log(error);
                console.log(file);
            },
            complete: function(results) {
                console.log('addGeoJSON');
                addGeoJSON(results.data);   
            }
        });
    // } else if ("parquet" in config) {
        
    //     console.log('adding parquet')
    //     const url = config.parquet
    //     const file = await asyncBufferFromUrl({ url });
    //     const data = await parquetReadObjects({ file });
        // import { parquetRead } from 'hyparquet'
        // await parquetRead({
        //     file,
        //     rowFormat: 'object',
        //     onComplete: data => console.log(data),
        //   })
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
        // $.ajax({
        //     type: "GET",
        //     url: config.csv,
        //     dataType: "text",
        //     success: function(csvData) {
        //         addGeoJSON($.csv.toObjects(csvData));
        //     }
        // });      
        Papa.parse(config.csv, {
            download: true,
            header: true,
            complete: function(results) {
                addGeoJSON(results.data);   
            }  
    });
}
}
function addGeoJSON(jsonData) {
    console.log('In addGeoJSON')
    // converts all to geojson 
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
            if (feature.properties[config['countryField']]){
                config.geojson.features.push(feature);
            }
            // else {
            //     console.log(feature)
            // }
        });

    }

    // Now that GeoJSON is created, store in processedGeoJSON, and link assets, then add layers to the map
    // config.processedGeoJSON = JSON.parse(JSON.stringify(config.geojson)); //deep copy
    config.processedGeoJSON = config.geojson; // copy

    console.log('setMinMax');
    setMinMax(); // TODO We need to change this so that the max is max of grouped units, and min is smallest unit, currently its max unit not project
    console.log('findLinkedAssets');
    findLinkedAssets(); // we should apply area-based scaling at this point, on the grouped capacity, then it'll be used in addPointLayer

    // map.addSource('assets-source', {
    //     'type': 'geojson',
    //     'data': config.processedGeoJSON
    // });
    // part to optimize csv only maps 
    if (!config.tiles) {
        map.addSource('assets-source', {
            'type': 'geojson',
            'data': config.processedGeoJSON
        });
    }

    console.log('addLayers');
    addLayers();

    setTimeout(enableUX, 3000);

    console.log('enableUX');
    map.on('idle', enableUX); // enableUX starts to render data
}

function addTiles() {
    map.addSource('assets-source', {
        'type': 'vector',
        'tiles': config.tiles,
        'minzoom': 0,
        'maxzoom': 10 // ?
    });

    /* create layer with invisible aasets in order to calculate statistics necessary for rendering the map and interface */
//     config.geometries.forEach(geometry => {
//         map.addLayer({
//             'id': geometry == "LineString" ? 'assets-minmax-line' : 'assets-minmax-point',
//             'type': geometry == "LineString" ? 'line' : 'circle',
//             'source': 'assets-source',
//             'source-layer': config.tileSourceLayer,
//             'layout': {},
//             'filter': ["==",["geometry-type"],geometry],
//             'paint': geometry == "LineString" ? {'line-width': 0, 'line-color': 'red'} : {'circle-radius': 0}
//         });
//     });

//     map.on('idle', geoJSONFromTiles);

}
function geoJSONFromTiles() {
    console.log('In geoJSONFromTiles')
    map.off('idle', geoJSONFromTiles);
    // since map not idle anymore reintroduce spinner 
    $('#spinner-container-filter').addClass('d-none')
    $('#spinner-container-filter').removeClass('d-flex')
    let layers = [];
    if (config.geometries.includes('Point')) layers.push('assets-minmax-point');
    if (config.geometries.includes('LineString')) layers.push('assets-minmax-line');
    config.geojson = {
        "type": "FeatureCollection", 
        "features": map.queryRenderedFeatures({layers: layers})  
    }

    config.processedGeoJSON = JSON.parse(JSON.stringify(config.geojson)); //deep copy
    
    setMinMax(); 
    layers.forEach(layer => {
        map.removeLayer(layer);
    });
    findLinkedAssets();
    addLayers();
    map.on('idle', enableUX); // enableUX starts to renders data 
    

}

// Builds lookup of linked assets by the link column
//  and when linked assets share location, rebuilds processedGeoJSON with summed capacity and custom icon
// what if we change this so instead of rebuilding on initial load we load the geojson directly?! to solve globe issue 
// until David implements his fix


function findLinkedAssets() {
    
    map.off('idle', findLinkedAssets);
    // since map not idle anymore reintroduce spinner 
    $('#spinner-container-filter').addClass('d-none')
    $('#spinner-container-filter').removeClass('d-flex')
    // config.preLinkedGeoJSON = JSON.parse(JSON.stringify(config.processedGeoJSON));
    config.preLinkedGeoJSON = config.processedGeoJSON;
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
    // TODO: skip this for lines, only for points???
    let grouped = {};
    config.processedGeoJSON.features.forEach((feature) => {
        if ('geometry' in feature && feature.geometry != null) {
            if ('coordinates' in feature.geometry) {
                let key = feature.properties[config.linkField] + "," + feature.geometry.coordinates[0] + "," + feature.geometry.coordinates[1];
                if (! (key in grouped)) {
                    grouped[key] = [];
                }
                // adds feature to dictonary grouped if shares a linkField id and coords, not done for lines
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
        // TODO HERE is where we want to apply the area-based scaling formula, to THIS capacity
        // sqrt((4 * (float(cap * factor))) / np.pi) 
        // math.sqrt((4 * converted) / np.pi)
        // areaBasedScaledCapacity = Math.sqrt((4 * capacity) / Math.PI)
        // features[0].properties[config.capacityField] = areaBasedScaledCapacity;
        features[0].properties[config.capacityField] = capacity;

        // Build summary count of capacity across all linked assets
        //  and generate icon based on that label if more than one status
        if (features[0].geometry.type == 'Point') {
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


    if (initialLoad == true) {
        // Do not go through fitBounds on initialLoad 
        userInteracting = false;
        spinGlobe();
    } else {

        // Try here for fitBounds
        // if map projection is not mercator or globe do not do fitbounds 
        if (config.projection == 'globe'){
            // fit to the highlighted projects and zoom in
            // let boundingBoxSet = getBoundingBox()
            let boundingBoxSet = findDensity(); // better function that will avoid anomalies and poles
            // TODO find size of bounding box and then determine max zoom so if its small or less features higher zoom less map
            // if larger or more features or many dense clusters then low zoom more map

            // if there are no search terms or filters
            // zoom out and spin 
            

            if (boundingBoxSet) {
                // find diff 
                // if difference between max and min longitude is more than 179  +/- 
                // return to center and start spinning
                // getZoom
                // if (diff within range){
                map.fitBounds(boundingBoxSet, {
                    padding: {top: 10, bottom:25, left: 15, right: 5},
                    // maxZoom: {4},
                    // linear: true,
                    maxZoom: 2,
                    // pitch: 0,
                    // bearing: 0,
                    // offset: [0,0]
                });
                // }else {
                    
                // }
            } else {
                // if null for no features
                // return back to start
                // If nothing is selected, reset to initial center and resume spinning

                // Using easeTo options. jumpTo without animation
                // or try resetNorth and resetNorthPitch
                map.jumpTo({
                    center: [0, 0],
                    zoom: 1,

                })
                userInteracting = false;
                spinGlobe();
                // map.easeTo({
                //     center: [0,0],
                //     zoom: 1,
                //     speed: 0.2, // easeTo
                //     curve: 1, // easeTo
                //     duration: 1000, // easeTo
                //     easing(t) { // easeTo
                //         return t;
                //     }
                // })

            }
            console.log('Just fired fitBounds in filterGeoJson')

        }
    }
}


function generateIcon(icon) {
    let label = JSON.stringify(icon);
    if (map.hasImage(label)) return;

    let canvas = document.createElement('canvas');
    canvas.width = 64; // set the size of the canvas
    canvas.height = 64;

    // get the canvas context
    let context = canvas.getContext('2d');
    // context.globalAlpha = config.pointPaint["circle-opacity"];
    context.globalAlpha = Number(document.getElementById('opacity-value').textContent)
    console.log(context.globalAlpha + ' = ' + Number(document.getElementById('opacity-value').textContent))

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
    // If I can find a way to incorporate the linked asset calculation in this or before
    // this runs then we would be closer to solving the area-based scaling issue


    // Maisie says we should show the full range
    // which is smallest unit, and largest project level capacity
    // We could remove these defaults and then returns a error if no value is assigned to the min and max keys
    // But could be okay to not use project-level since easier in JS and biggest might be a project with one unit
    config.maxPointCapacity = 0;
    config.minPointCapacity = 1000000;
    config.maxLineCapacity = 0;
    config.minLineCapacity = 1000000;
    let maxCapacityKey;
    let minCapacityKey;
    config.processedGeoJSON.features.forEach((feature) => {
        if (feature.geometry.type == "LineString") {
            minCapacityKey = 'minLineCapacity';
            maxCapacityKey = 'maxLineCapacity';
        } else {
            minCapacityKey = 'minPointCapacity';
            maxCapacityKey = 'maxPointCapacity';
        }
        // this says, if the capacity is more than the max capacity so far then it should be used
        // vice versa for min capacity
        // later this is used to size the assets along smoothly by interpolation across the width between min and maxPoint and LineWidth
        // this min and max Line and Point Capacity is crucial to the scaling, along with the unit's capacity
        // we need to be using the summed project's capacity not the unit's capacity to inform this, 
        // either later in addPointLayer where we consider the unit's capacity during interpolation, or here where we find the min and max unit size
        if (parseFloat(feature.properties[config.capacityField]) > config[maxCapacityKey]) {
            config[maxCapacityKey] =  parseFloat(feature.properties[config.capacityField]);
        }
        if (parseFloat(feature.properties[config.capacityField]) < config[minCapacityKey]) {
            config[minCapacityKey] =  parseFloat(feature.properties[config.capacityField]);
        }       
    });
}

/*
  render data
*/
function enableUX() {
    map.off('idle', enableUX);
    // since map not idle anymore reintroduce spinner 
    $('#spinner-container-filter').addClass('d-none')
    $('#spinner-container-filter').removeClass('d-flex')
    if (config.UXEnabled) {
        console.log('ux already enabled');
        return
    };
    config.UXEnabled = true;
    
    console.log('buildFilters');
    buildFilters();
    console.log('updateSummary');
    updateSummary();
    console.log('buildTable');
    buildTable(); 
    console.log('enableModal');
    enableModal();
    console.log('enableNavFilters');
    enableNavFilters();
    $('#spinner-container').addClass('d-none')
    $('#spinner-container').removeClass('d-flex')
    if (config.projection == 'globe') {
        console.log('spinGlobe');
        spinGlobe();
    }
}

function addLayers() {
 
    config.layers = [];
    if (config.geometries.includes('LineString')) addLineLayer();
    if (config.geometries.includes('Point')) addPointLayer();

    map.addLayer({
        id: 'satellite',
        source: { "type": "raster", "url": "mapbox://mapbox.satellite", "tileSize": 256 },
        type: "raster",
        layout: { 'visibility': 'none' }
    }, config.layers[0]);

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
    , config.layers[0]);

    addEvents();
}

// function addLabelLayer( {

// })

function addPointLayer() {
    // First build circle layer
    // build style json for circle-color based on config.color
    let paint = config.pointPaint;
    if ('color' in config) {
        paint["circle-color"] = [
            "match",
            ["get", config.color.field],
            ...Object.keys(config.color.values).flatMap(key => [key, config.color.values[key]]),
            "#000000"
        ];
    }
    // LET"S ADD exponential NOT linear TODO Maisie 
    // ["exponential", base] if base is 1 then it is linear the same, power of 1/2 to do squareroot area based

    let interpolateExpression = ('interpolate' in config ) ? config.interpolate :  ["linear"];
    paint['circle-radius'] = [
        "interpolate", ["exponential", .5], ["zoom"],
        1, ["interpolate", interpolateExpression,
            ["to-number",["get", config.capacityField]],
            // config.minPointCapacity, config.minRadius,
            // config.maxPointCapacity, config.maxRadius
            config.minPointCapacity, Number(document.getElementById('minRadius-value').textContent),
            config.maxPointCapacity, Number(document.getElementById('maxRadius-value').textContent)

        ],
        10, ["interpolate", interpolateExpression,
            ["to-number",["get", config.capacityField]],
            // config.minPointCapacity, config.highZoomMinRadius,
            // config.maxPointCapacity, config.highZoomMaxRadius
            config.minPointCapacity, Number(document.getElementById('highZoomMinRadius-value').textContent),
            config.maxPointCapacity, Number(document.getElementById('highZoomMaxRadius-value').textContent)      
        ],
    ];

    map.addLayer({
        'id': 'assets-points',
        'type': 'circle',
        'source': 'assets-source',
        'filter': ["==",["geometry-type"],'Point'],
        ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
        'layout': {},
        'paint': paint
    });
    config.layers.push('assets-points');

    // Add layer with proportional icons
    map.addLayer({
        'id': 'assets-symbol', 
        'type': 'symbol',
        'source': 'assets-source',
        'filter': ["==",["geometry-type"],'Point'],
        ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
        'layout': {
            'icon-image': ["get", "icon"],
            'icon-allow-overlap': true,
            'icon-size': [
                "interpolate", ["exponential", .5], ["zoom"],
                1, ['interpolate', interpolateExpression,
                    ["to-number", ["get", config.capacityField]],
                    // config.minPointCapacity, config.minRadius * 2 / 64,
                    // config.maxPointCapacity, config.maxRadius * 2 / 64],
                    config.minPointCapacity, Number(document.getElementById('minRadius-value').textContent * 2 / 64),
                    config.maxPointCapacity, Number(document.getElementById('maxRadius-value').textContent * 2 / 64)],
                10, ['interpolate', interpolateExpression,
                    ["to-number", ["get", config.capacityField]],
                    // config.minPointCapacity, config.highZoomMinRadius * 2 / 64,
                    // config.maxPointCapacity, config.highZoomMaxRadius * 2 / 64]
                    config.minPointCapacity, Number(document.getElementById('highZoomMinRadius-value').textContent * 2 / 64),
                    config.maxPointCapacity, Number(document.getElementById('highZoomMaxRadius-value').textContent * 2 / 64)],  
            ]
        }
    });

    // Add highlight layer
    paint = config.pointPaint;
    paint["circle-color"] = '#FFEA00';
    map.addLayer(
        {
            'id': 'assets-points-highlighted',
            'type': 'circle',
            'source': 'assets-source',
            'filter': ["==",["geometry-type"],'Point'],
            ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
            'layout': {},
            'paint': paint,
            'filter': ['in', (config.linkField), '']
        }
    );

    // try moving this and calling it when basemap is toggled 
    map.addLayer(
        {
            'id': 'assets-labels',
            'type': 'symbol',
            'source': 'assets-source',
            'filter': ["==",["geometry-type"],'Point'],
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
}


    // // Determine actual basemap style
    // const styleUrl = map.getStyle().sprite || map.getStyle().name || map.getStyle().metadata?.['mapbox:origin'] || '';
    // Check if satellite is visible
    // const satelliteVisible = map.getLayer('Satellite') && map.getLayoutProperty('satellite', 'visibility') === 'visible';
    // set satelliteVisible it in the actual toggle for basemap
    // console.log('this is the satellite visibility' + config.satelliteVisible)
    // if (config.satelliteVisible = true) {
    //     map.addLayer(
    //         {
    //             'id': 'assets-labels',
    //             'type': 'symbol',
    //             'source': 'assets-source',
    //             'filter': ["==",["geometry-type"],'Point'],
    //             ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
    //             'minzoom': 6,
    //             'layout': {
    //                 'text-field': '{' + config.nameField + '}',
    //                 'text-font': ["DIN Pro Italic"],
    //                 'text-variable-anchor': ['top'],
    //                 'text-offset': [0, 1],
    //             },
    //             'paint': {
    //                 'text-color': '#ffffff', // white
    //                 'text-halo-color': "#000000", // Use a solid black 
    //                 'text-halo-width': .00001, // Reduce width for less distraction
    //                 'text-halo-blur': 10 // Add blur for smoother, less jagged halo
    //             }
    //         }
    //     );
    // } else {
    //     map.addLayer(
    //         {
    //             'id': 'assets-labels',
    //             'type': 'symbol',
    //             'source': 'assets-source',
    //             'filter': ["==",["geometry-type"],'Point'],
    //             ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
    //             'minzoom': 6,
    //             'layout': {
    //                 'text-field': '{' + config.nameField + '}',
    //                 'text-font': ["DIN Pro Italic"],
    //                 'text-variable-anchor': ['top'],
    //                 'text-offset': [0, 1],
    //             },
    //             'paint': {
    //                 'text-color': '#000000', // black
    //                 'text-halo-color': "rgba(255,255,255,.85)", // Use a solid white with some transparency
    //                 'text-halo-width': .00001, // Reduce width for less distraction
    //                 'text-halo-blur': 10 // Add blur for smoother, less jagged halo
    //             }
    //         }
    //     );
    // }




function addLineLayer() {
    let paint = config.linePaint;
    if ('color' in config) {
        paint["line-color"] = [
            "match",
            ["get", config.color.field],
            ...Object.keys(config.color.values).flatMap(key => [key, config.color.values[key]]),
            "#000000"
        ];
    }

    let interpolateExpression = ('interpolate' in config ) ? config.interpolate :  ["linear"];
    paint['line-width'] = [
        "interpolate", ["linear"], ["zoom"],
        1, ["interpolate", interpolateExpression,
            ["to-number",["get", config.capacityField]],
            config.minLineCapacity, config.minLineWidth,
            config.maxLineCapacity, config.maxLineWidth
        ],
        10, ["interpolate", interpolateExpression,
            ["to-number",["get", config.capacityField]],
            config.minLineCapacity, config.highZoomMinLineWidth,
            config.maxLineCapacity, config.highZoomMaxLineWidth
        ],

    ];

    map.addLayer({
        'id': 'assets-lines', //assets-lines
        'type': 'line',
        'source': 'assets-source',
        'filter': ["==",["geometry-type"],'LineString'],
        ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
        'layout': config.lineLayout,
        'paint': paint
    }); 
    config.layers.push('assets-lines');

    paint["line-color"] = '#FFEA00';
    map.addLayer(
        {
            'id': 'assets-lines-highlighted', //assets-lines-highlighted
            'type': 'line',
            'source': 'assets-source',
            'filter': ["==",["geometry-type"],'LineString'],
            ...('tileSourceLayer' in config && {'source-layer': config.tileSourceLayer}),
            'layout': config.lineLayout,
            'paint': paint,
            'filter': ['in', (config.linkField), '']
        }
    );
}

function addEvents() {
    map.on('click', (e) => {
        const bbox = [ [e.point.x - config.hitArea, e.point.y - config.hitArea], [e.point.x + config.hitArea, e.point.y + config.hitArea]];
        const selectedFeatures = getUniqueFeatures(map.queryRenderedFeatures(bbox, {layers: config.layers}), config.linkField).sort((a, b) => a.properties[config.nameField].localeCompare(b.properties[config.nameField]));
        
        // TODO since using tiles do not have coords in it so even if coords exist and are exact zoom 
        // we should use the country or subnat and use the rep point to zoom to
        // then use map.project([lat,lng]); to project into map's geo projection


        // geometry param of the quryRenderedFeatures will return the geo of the qurey region in piexles ... 
        // can we use flyTo or fitBounds with it? 

        // const selectedFeaturesGeo = getUniqueFeatures(map.queryRenderedFeatures(bbox, {layers: config.layers}), config.linkField)
        // selectedFeatures.forEach(feature => {
        //     // console.log(feature.geometry);
        // });


        if (selectedFeatures.length == 0) return;

        let bboxClick = getBoundingBox(selectedFeatures)
        console.log('bboxClick: ' + bboxClick)
        map.flyTo(bboxClick, {
                // minZoom: 4,
                });
        
        // TODO adjust zoom level at this point with jumpTo or easeTo or setZoom
        // let curr_zoom = map.getZoom();
        // // 0 and 22
        // let new_zoom = curr_zoom * 2

        map.easeTo({
            zoom: 4,
            speed: 0.7, // easeTo
            // curve: 1, // easeTo
            duration: 1000, // easeTo
            easing(t) { // easeTo
                return t;
            }
        })
        const links = selectedFeatures.map(
            (feature) => feature.properties[config.linkField]
        );

        setHighlightFilter(links);

        if (selectedFeatures.length == 1) {
            config.selectModal = '';

            displayDetails(config.linked[selectedFeatures[0].properties[config.linkField]]);
            // commenting this out because it creates a bug in summary capacity section 
            // if (config.tiles) {
            //     displayDetails([selectedFeatures[0]]); //use clicked point


            // } else {
            // displayDetails(config.linked[selectedFeatures[0].properties[config.linkField]]);


            // }
        } else {
            var modalText = "<h6 class='p-3'>There are multiple " + config.assetFullLabel + " near this location. Select one for more details</h6>";


            let ul = $('<ul>');
            selectedFeatures.forEach((feature) => {
                var link = $('<li class="asset-select-option">' + feature.properties[config.nameField] + "</li>");
                link.attr('data-feature', JSON.stringify(config.linked[feature.properties[config.linkField]]));
                link.attr('onClick', "displayDetails(this.dataset.feature)");
                ul.append(link);
            });
            modalText += ul[0].outerHTML;
            config.selectModal = modalText;
            $('.modal-body').html(modalText);
        }

        // show the modal if appropriate
        config.modal.show();
        console.log('modal show')
    });
    // Add hover animation: expand and turn yellow on mouseover, reset on mouseout
    // Animate both point and line markers on hover

    // TODO look into why or how the cursor can change from drag to point within the maps hitarea of 5 pixels
    // Currently it seems to only change when you are right ontop of the dot which is misleading I think 
    if (config.geometries.includes('Point')) {
        map.on('mousemove', 'assets-points', (e) => {
            // option to make it easier to get info but unsure if this is needed
            // const hitArea = config.hitArea || Math.max(10, 30 * (1 / map.getZoom())); 
            const features = map.queryRenderedFeatures([
                [e.point.x, e.point.y],
                [e.point.x, e.point.y]
            ], { layers: ['assets-points'] });
            if (features.length > 0) {
                map.getCanvas().style.cursor = 'pointer';
                const feature = features[0];
                const coordinates = feature.geometry.coordinates.slice();
                const description = feature.properties[config.nameField];
                // Highlight all features under the mouse (yellow and expand)
                const linkIds = features.map(f => f.properties[config.linkField]);
                // make the assets yellow on hover
                setHighlightFilter(linkIds);
                // Expand: set a larger radius for highlight layer
                map.setPaintProperty('assets-points-highlighted', 'circle-radius', [
                    "interpolate", ["linear"], ["zoom"],
                    1, config.maxRadius * 1.1,
                    10, config.highZoomMaxRadius * 1.1
                ]);
                popup.setLngLat(coordinates).setHTML(description).addTo(map);
                // console.log('set popup')
            } else {
                map.getCanvas().style.cursor = '';
                popup.remove();
                setHighlightFilter([]);
                // Reset highlight radius
                map.setPaintProperty('assets-points-highlighted', 'circle-radius', [
                    "interpolate", ["linear"], ["zoom"],
                    1, config.maxRadius,
                    10, config.highZoomMaxRadius
                ]);
            }
        });

        map.on('mouseleave', 'assets-points', () => {
            map.getCanvas().style.cursor = '';
            popup.remove();
            setHighlightFilter([]);
            // Reset highlight radius
            map.setPaintProperty('assets-points-highlighted', 'circle-radius', [
                "interpolate", ["linear"], ["zoom"],
                1, config.maxRadius,
                10, config.highZoomMaxRadius
            ]);
        });
    }
    
    if (config.geometries.includes('LineString')) {
        map.on('mousemove', 'assets-lines', (e) => {
            // // option to add and subtract padding via hitArea
            // const hitArea = config.hitArea || Math.max(10, 30 * (1 / map.getZoom()));
            const features = map.queryRenderedFeatures([
                [e.point.x, e.point.y],
                [e.point.x, e.point.y]
            ], { layers: ['assets-lines'] });

            if (features.length > 0) {
                map.getCanvas().style.cursor = 'pointer';
                const feature = features[0];
                let coordinates;
                if (feature.geometry.type === "LineString") {
                    // Use the midpoint of the line for the popup
                    const lineCoords = feature.geometry.coordinates;
                    const midIdx = Math.floor(lineCoords.length / 2);
                    coordinates = lineCoords[midIdx].slice();
                } else if (feature.geometry.type === "MultiLineString") {
                    // Use the midpoint of the first line in the MultiLineString
                    const multiLineCoords = feature.geometry.coordinates[0];
                    const midIdx = Math.floor(multiLineCoords.length / 2);
                    coordinates = multiLineCoords[midIdx].slice();
                } else {
                    // fallback for other geometry types
                    coordinates = feature.geometry.coordinates.slice();
                }
                const description = feature.properties[config.nameField];
                
                // Highlight this line (yellow and expand)
                // make the assets yellow on hover
                setHighlightFilter(feature.properties[config.linkField]);
                // Expand: set a larger width for highlight layer
                map.setPaintProperty('assets-lines-highlighted', 'line-width', [
                    "interpolate", ["linear"], ["zoom"],
                    1, config.maxLineWidth * 1.1,
                    10, config.highZoomMaxLineWidth * 1.1
                ]);
                popup.setLngLat(coordinates).setHTML(description).addTo(map);
                // console.log('set popup')
            } else {
                map.getCanvas().style.cursor = '';
                popup.remove()
                setHighlightFilter([]);
                // Reset highlight width
                map.setPaintProperty('assets-lines-highlighted', 'line-width', [
                    "interpolate", ["linear"], ["zoom"],
                    1, config.maxLineWidth,
                    10, config.highZoomMaxLineWidth
                ]);
            }
        });

        map.on('mouseleave', 'assets-lines', () => {
            map.getCanvas().style.cursor = '';
            popup.remove()
            setHighlightFilter([]);
            // Reset highlight width
            map.setPaintProperty('assets-lines-highlighted', 'line-width', [
                "interpolate", ["linear"], ["zoom"],
                1, config.maxLineWidth,
                10, config.highZoomMaxLineWidth
            ]);
        });
    }

    // TODO another time, seems like we'd need to handle for point and line so more complicated than I thought
    // add same mouse over event for labels so its easier to click
    // assets-labels
    // map.on('mousemove', 'assets-labels', (e) => {

    // });
    // // assets-labels
    // map.on('mouseleave', 'assets-labels', (e) => {
    //     map.getCanvas().style.cursor = '';
    //     popup.remove()
    // });

    // can we add it so if there is a click on a label it zooms in? 




    $('#basemap-toggle').on("click", function() {
        if (config.baseMap == "Streets") {
           // $('#basemap-toggle').text("Streets");
           config.baseMap = "Satellite";
        //    config.satelliteVisible = true; // doesn't help because it loads only once, in addLayers() onLoad()
           map.setLayoutProperty('satellite', 'visibility', 'visible');
           map.setFog({
            "range": [0.8, 8],
            "color": "#dc9f9f",
            "horizon-blend": 0.5,
            "high-color": "#245bde",
            "space-color": "#000000",
            "star-intensity": 0.3
            });
        } else {
           // $('#basemap-toggle').text("Satellite");
           config.baseMap = "Streets";
        //    config.satelliteVisible = false;
           map.setLayoutProperty('satellite', 'visibility', 'none');

           map.setFog(null);
        }
        // re run this so that the labels get added with new design
        addPointLayer()
    });

    $('#reset-all-button').on("click", function() {
        enableClearSearch(); // TODO change this so it only clears search not all filtering of legend
    });

    $('#collapse-sidebar').on("click", function() {
        $('#filter-form').hide();
        $('#all-select').hide();
        $('#all-select-section-level').hide();
        $('#collapse-sidebar').hide();
        $('#expand-sidebar').show();
    });
    $('#expand-sidebar').on("click", function() {
        $('#filter-form').show();
        $('#all-select').show();
        $('#all-select-section-level').show();
        $('#collapse-sidebar').show();
        $('#expand-sidebar').hide();
    });

}

$('#projection-toggle').on("click", function() {
    if (config.projection == 'globe') {
        config.projection = "naturalEarth";
        map.setProjection('naturalEarth');
        $('#btn-spin-toggle').hide();
        $('#fit').hide();
        map.setCenter(config.center);
        map.setZoom(determineZoom());

    } else {
        config.projection = "globe";
        map.setProjection("globe");
        map.setCenter(config.center);
        $('#btn-spin-toggle').show();
        $('#fit').show();
        spinGlobe();
        map.setZoom(determineZoom());

    }
})

/* 
    // TODO continue
        // add event listeners to dev sliders
    // re run addGeoJSON after opacity change 
*/

$('#opacity-value').on("click", function(){
    // start spinner to indicate it is re rendering
    console.log('opa clicked!')

    addGeoJSON()
    // stop spinner 
});

$('#minRadius-value').on("click", function(){
    // start spinner to indicate it is re rendering
    console.log('minRad clicked!')
    addGeoJSON()
    // stop spinner 
    
})






/*
  legend filters
*/ 

function buildFilters() {
    countFilteredFeatures();
    config.filters.forEach(filter => {
        // go through each filter in config 
        if (config.showToolTip){
            // create more space for europe legend
            if (filter.primary && filter.field_hover_text){
            $('#filter-form').append('<h7 class="card-title">' + (filter.label || filter.field.replaceAll("_"," ")) + 
            '<div class="infobox" id="infobox"><span>i</span><div class="tooltip" id="tooltip">' + filter.field_hover_text + 
            '</div></div></h7> <div class="col-12 text-left small" id="all-select-section-level"><a href="" onclick="selectAllFilterSection(\'' + filter.field + '\'); return false;">select all section</a> | <a href="" onclick="clearAllFilterSection(\'' + filter.field + '\'); return false;">clear all section</a></div>');
        // add eventlistener for infobox and tooltip to show on hover

            }
            else if (filter.field_hover_text){
            $('#filter-form').append('<hr /><h7 class="card-title">' + (filter.label || filter.field.replaceAll("_"," ")) + '<div class="infobox" id="infobox"><span>i</span><div class="tooltip" id="tooltip">' + filter.field_hover_text + 
            '</div></div></h7> <div class="col-12 text-left small" id="all-select-section-level"><a href="" onclick="selectAllFilterSection(\'' + filter.field + '\'); return false;">select all section</a> | <a href="" onclick="clearAllFilterSection(\'' + filter.field + '\'); return false;">clear all section</a></div>');

            }
            else {
            // do same as below but append infobox
            $('#filter-form').append('<hr /><h7 class="card-title">' + (filter.label || filter.field.replaceAll("_"," ")) + 
            '</div></div></h7> <div class="col-12 text-left small" id="all-select-section-level"><a href="" onclick="selectAllFilterSection(\'' + filter.field + '\'); return false;">select all section</a> | <a href="" onclick="clearAllFilterSection(\'' + filter.field + '\'); return false;">clear all section</a></div>');
            }

        }
        // this creates the section title and adds the select all feature only to the sections after the first one, if there is no tooltip logic so for all non europe maps
        else if (config.color.field != filter.field) {
            $('#filter-form').append('<hr /><h7 class="card-title">' + (filter.label || filter.field.replaceAll("_"," ")) + 
            '</div></div></h7> <div class="col-12 text-left small" id="all-select-section-level"><a href="" onclick="selectAllFilterSection(\'' + filter.field + '\'); return false;">select all section</a> | <a href="" onclick="clearAllFilterSection(\'' + filter.field + '\'); return false;">clear all section</a></div>');
        }

        for (let i=0; i<filter.values.length; i++) {
            let check_id =  filter.field + '_' + filter.values[i];
            let check = `<div class="row filter-row" data-checkid="${(check_id).replace('/','\\/')}">`;
            check += '<div class="col-1 checkmark" id="' + check_id + '-checkmark"></div>';
            check += `<div class="col-8"><input type="checkbox" checked class="form-check-input d-none" id="${check_id}">`;
            check += (config.color.field == filter.field ? '<span class="legend-dot" style="background-color:' + config.color.values[ filter.values[i] ] + '"></span>' : "");
            check +=  `<span id='${check_id}-label'>` + ('values_labels' in filter ? filter.values_labels[i] : filter.values[i].replaceAll("_", " ")) + '</span></div>';
            check += '<div class="col-3 text-end" style="text-align: right;" id="' + check_id + '-count">' + config.filterCount[filter.field][filter.values[i]] + '</div></div>';
            $('#filter-form').append(check);
        }
    // add eventlistener for infobox and tooltip to show on hover 
    $('.infobox').each(function() {
        $(this).on('mouseover', function() {
            const infoBox = document.getElementById('infobox');
            const toolTip = document.getElementById('tooltip');
            const infoBoxRect = infoBox.getBoundingClientRect();
            const toolTipRect = toolTip.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            if (infoBoxRect.top < toolTipRect.height + 20) {
                // Position the tooltip below the infobox
                toolTip.style.bottom = 'auto';
                toolTip.style.top = '110%';
            } else {
                // Position the tooltip above the infobox
                toolTip.style.top = 'auto';
                toolTip.style.bottom = '110%';
            }
            
            $(this).find('.tooltip').css({
                'opacity': '1',
                'visibility': 'visible'
            });
        });
        $(this).on('mouseout', function() {
            $(this).find('.tooltip').css({
                'opacity': '0',
                'visibility': 'hidden'
            });
        });
    });
    });
    
    $('.filter-row').each(function() {
        this.addEventListener("click", function() {
            $('#' + this.dataset.checkid).click();
            toggleFilter(this.dataset.checkid);

            $('#spinner-container-filter').removeClass('d-none')
            $('#spinner-container-filter').addClass('d-flex')

            filterData();

        });
    });

}


function toggleFilter(id) {
    $('#' + id + '-checkmark').toggleClass('checkmark uncheckmark');
}
// for legend level select all and clear all

function selectAllFilter() {
    $('.filter-row').each(function() {
        if (! $('#' + this.dataset.checkid)[0].checked) {
            $('#' + this.dataset.checkid)[0].checked = true;
            toggleFilter(this.dataset.checkid);
        }
    });

    $('#spinner-container-filter').removeClass('d-none')
    $('#spinner-container-filter').addClass('d-flex')

    filterData();

}
// for section level select all and clear all
// needs to know field name to distinguish which filter rows to clear and what not to
function selectAllFilterSection(fieldRow) {
    $('.filter-row').each(function() {
        let rowFieldName = this.dataset.checkid.split('_')[0];
        if (rowFieldName === fieldRow && !$('#' + this.dataset.checkid)[0].checked) {
            $('#' + this.dataset.checkid)[0].checked = true;
            toggleFilter(this.dataset.checkid);
        }
    });

    $('#spinner-container-filter').removeClass('d-none')
    $('#spinner-container-filter').addClass('d-flex')

    filterData();
}
// for legend level select all and clear all

function clearAllFilter(fieldRow) {
    $('.filter-row').each(function() {
        if ($('#' + this.dataset.checkid)[0].checked) {
            $('#' + this.dataset.checkid)[0].checked = false;
            toggleFilter(this.dataset.checkid);
        }
    });
    filterData();

}

// for section level select all and clear all
function clearAllFilterSection(fieldRow) {
    $('.filter-row').each(function() {
        let rowFieldName = this.dataset.checkid.split('_')[0];
        if (rowFieldName === fieldRow && $('#' + this.dataset.checkid)[0].checked) {
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

    config.maxFilteredCapacity = 0;
    config.minFilteredCapacity = 1000000;

    let ref = "config.processedGeoJSON.features";

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

        if (parseFloat(feature.properties[config.capacityField]) > config.maxFilteredCapacity) {
            config.maxFilteredCapacity =  parseFloat(feature.properties[config.capacityField]);
        }
        if (parseFloat(feature.properties[config.capacityField]) < config.minFilteredCapacity) {
            config.minFilteredCapacity =  parseFloat(feature.properties[config.capacityField]);
        }       
    });
}
function filterData() {
    // reassign initialLoad so that fly to / fitBounds / findDensity does not use default bbox
    if (initialLoad === true){
        initialLoad = false;
        userInteracting = true;
    }

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
    // TODO apply diacritic solution here for GIPT as well
    if (config.searchText.length >= 3) {
        // TODO investigate why this doesn't work to stop spin when search bar has something 
        // userInteracting = true;
        // spinGlobe();
        let searchExpression = ['any'];
        config.selectedSearchFields.split(',').forEach((field) => {
            // let mapValue = removeDiacritics(field); // too slow so we'll do it the data input way for removing diacritics in search

            searchExpression.push(['in', ['literal', config.searchText], ['downcase', ["get", field]]]);

        });
        config.filterExpression.push(searchExpression);
    }
    if (config.selectedCountries.length > 0) {
        // update to handle so doesn't catch when countries are substrings of each other (Niger/Nigeria)
        // easy solve could be to add "," at end
        let countryExpression = ['any'];
        config.selectedCountries.forEach(country => {
            if (config.multiCountry) {
                country = country + ';'; // this is needed to filter integrated file by country select but doesn't affect filtering by region
                countryExpression.push(['in', ['string', country], ['string',['get', removeLastComma(config.countryField)]]]);
            } else {
                countryExpression.push(['==', ['string', country], ['string',['get', removeLastComma(config.countryField)]]]);
            }
        })
        config.filterExpression.push(countryExpression);

    }
    for (let field in filterStatus) {
        config.filterExpression.push(['in', ['get', field], ['literal', filterStatus[field]]]);
    }
    if (config.filterExpression.length == 0) {
        config.filterExpression = null;
    } else {
        config.filterExpression.unshift("all");
    }
    config.layers.forEach(layer => {
        config.filterExpression.push(["==",["geometry-type"],
            map.getLayer(layer).type == "line" ? "LineString" : "Point"
        ]);
        map.setFilter(layer, config.filterExpression);
        config.filterExpression.pop();
    });
    if (config.geometries.includes('Point')) {
        map.setFilter('assets-labels', config.filterExpression);
    }

    if ($('#table-container').is(':visible')) {
        filterGeoJSON();
        $('btn-spin-toggle').hide();

    } else {
        map.on('idle', filterGeoJSON);
        console.log('Just fired filterGeoJSON in filterTiles')


    }

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
            userInteracting = true;

            if (config.selectedSearchFields.split(',').filter((field) => {
                // remove diacritics from mapValue
                if (feature.properties[field] != null){
                    // console.log(feature.properties[field])
                    // console.log('Before remove diacritics function')
                    let mapValue = removeDiacritics(feature.properties[field]);
                    // let mapValue = feature.properties[field];

                    // console.log(mapValue)
                    // console.log('After remove diacritics function')
                    return mapValue.toLowerCase().includes(config.searchText);
                }}).length == 0) include = false;
        }
        
        if (config.selectedCountries.length > 0) {
            userInteracting = true;
            // Check if any of the selected countries are associated with the project
            const projectCountries = feature.properties[config.countryField].split(';').map(country => country.trim());

            if (!config.selectedCountries.some(country => projectCountries.includes(country))) {
            include = false;
            }

        }
        if (include) {
            filteredGeoJSON.features.push(feature);
        }
    });
    // config.processedGeoJSON = JSON.parse(JSON.stringify(filteredGeoJSON));

    config.processedGeoJSON = filteredGeoJSON;
    
    spinGlobe();
    findLinkedAssets();
    config.tableDirty = true;
    updateTable();
    updateSummary();


    if (! config.tiles) { //maybe just use map filter for points and lines, no matter if tiles of geojson
        map.getSource('assets-source').setData(config.processedGeoJSON);
    }


}
function updateSummary() {
    $('#total_in_view').text(config.totalCount.toLocaleString())
    $('#summary').html("Total " + config.assetFullLabel + " selected");
    countFilteredFeatures();
    config.filters.forEach((filter) => {
        for (let i=0; i<filter.values.length; i++) {
            let count_id =  (filter.field + '_' + filter.values[i] + '-count').replace('/','\\/');
            $('#' + count_id).text(config.filterCount[filter.field][filter.values[i]]);
        }
    });


    if (config.showMinCapacity & config.showMaxCapacity) {
        if (config.maxCapacityLabel) {
            $('#max_capacity').text(Math.round(config.maxFilteredCapacity).toLocaleString());
            $('#capacity_summary').html("Maximum " + config.maxCapacityLabel);
            $('#min_capacity').text(Math.round(config.minFilteredCapacity).toLocaleString());
            $('#capacity_summary_min').html("Minimum " + config.maxCapacityLabel);
        } else {
            $('#max_capacity').text(Math.round(config.maxFilteredCapacity).toLocaleString());
            $('#capacity_summary').html("Maximum " + config.capacityLabel);
            $('#min_capacity').text(Math.round(config.minFilteredCapacity).toLocaleString());
            $('#capacity_summary_min').html("Minimum " + config.capacityLabel);
        }
    }

    else if (config.showMaxCapacity) {
        if (config.maxCapacityLabel) {
            $('#max_capacity').text(Math.round(config.maxFilteredCapacity).toLocaleString());
            $('#capacity_summary').html("Maximum " + config.maxCapacityLabel);
        } else {
            $('#max_capacity').text(Math.round(config.maxFilteredCapacity).toLocaleString());
            $('#capacity_summary').html("Maximum " + config.capacityLabel);
        }
    }

    $('#spinner-container-filter').addClass('d-none')
    $('#spinner-container-filter').removeClass('d-flex')
    console.log('aftr upat summary spinner addClass d-none, removes spinnr')
}


/*
  table view
*/
function buildTable() {
    $('#table-toggle').on("click", function() {
        if (! $('#table-container').is(':visible')) {
            $('#table-toggle-label').html("Map view <img src='../../src/img/arrow-right.svg' width='15' height='50' style='text-align: center;'>");
            $('#map').hide();
            $('#btn-spin').hide();
            $('#sidebar').hide();
            $('#table-container').show();
            $('#basemap-toggle').hide();
            $('btn-spin-toggle').hide();
            $('#projection-toggle').hide();
            updateTable(true);
        } else {
            $('#table-toggle-label').html("Table view <img src='../../src/img/arrow-right.svg' width='15' height='50' style='text-align: center;'>");
            $('#map').show();
            $('#btn-spin').show();
            $('#sidebar').show();
            $('#table-container').hide();
            $('#basemap-toggle').show();
            $('btn-spin-toggle').show();
            $('#projection-toggle').show();

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
        data: geoJSON2Table().map(row => {
            if ('toLocaleString' in config.tableHeaders) {
                config.tableHeaders.toLocaleString.forEach((col) => {
                    const colIndex = config.tableHeaders.values.indexOf(col);
                    if (colIndex !== -1 && row[colIndex] != null) {
                        row[colIndex] = Number(row[colIndex]).toLocaleString();
                    }
                });
            }
            return row;
        }),
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

            value = feature.properties[header];
            if ('displayValue' in config.tableHeaders && Object.keys(config.tableHeaders.displayValue).includes(header)) {
                value = config[config.tableHeaders.displayValue[header]].values[value];

            }
            if ('appendValue' in config.tableHeaders && Object.keys(config.tableHeaders.appendValue).includes(header)) {
                value += ' ' + config[config.tableHeaders.appendValue[header]].values[
                    feature.properties[config[config.tableHeaders.appendValue[header]].field]
                    ];
            }
            if ('removeLastComma' in config.tableHeaders && config.tableHeaders.removeLastComma.includes(header)) {
                value = removeLastComma(value);
            }
            if ('clickColumns' in config.tableHeaders && config.tableHeaders.clickColumns.includes(header)) {
                value =  "<a href='" + feature.properties[config.urlField] + "' target='_blank'>" + value + '</a>'; 
            } 
            return value;
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
/**
 * Updates the map layers to highlight specific features based on their link IDs.
 * 
 * @param {Array|string} links - An array of link IDs or a single link ID to highlight.
 *                               If empty, the highlight filter will be cleared.
 */
function setHighlightFilter(links) {
    if (! Array.isArray(links)) links = [links];
    let filter;
    let highlightExpression = [];
    const batchSize = 500; // Limit the number of items per batch
    for (let i = 0; i < links.length; i += batchSize) {
        const batch = links.slice(i, i + batchSize);
        highlightExpression.push(['in', ["get", config.linkField], ["literal", batch]]);
    }
    highlightExpression = ['any', ...highlightExpression];
    if (config.filterExpression != null) {
        filter = JSON.parse(JSON.stringify(config.filterExpression));
        filter.push(highlightExpression);
    } else {
        filter = ['all', highlightExpression];
    }
    // Set highlight filter only on the correct geometry layers
    if (config.geometries.includes('Point') && map.getLayer('assets-points-highlighted')) {
        let pointFilter = JSON.parse(JSON.stringify(filter));
        pointFilter.push(["==", ["geometry-type"], "Point"]);
        map.setFilter('assets-points-highlighted', pointFilter);
    }
    if (config.geometries.includes('LineString') && map.getLayer('assets-lines-highlighted')) {
        let lineFilter = JSON.parse(JSON.stringify(filter));
        lineFilter.push(["==", ["geometry-type"], "LineString"]);
        map.setFilter('assets-lines-highlighted', lineFilter);
    }
}

function displayDetails(features) {
    if (typeof features == "string") {
        features = JSON.parse(features);
    }
    var detail_text = '';
    var location_text = '';
    Object.keys(config.detailView).forEach((detail) => {
        // replace apostrophe in displayDetails to resolve invalid or unexpected token

        if (features[0].properties[detail] == "" || features[0].properties[detail] == 'unknown' || features[0].properties[detail] == 'undefined' || features[0].properties[detail] ==0 || features[0].properties[detail] == NaN || features[0].properties[detail] == 'nan' || features[0].properties[detail] == null){
            detail_text += ''
            } else if (Object.keys(config.detailView[detail]).includes('display')) {

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
            } else if (config.detailView[detail]['display'] == 'hyperlink') {

                // detail_text += '<span class="fw-bold">' + 'Infrastructure Wiki' + '</span>: ' + '<a href="' + features[0].properties[detail] + '" target="_blank"></a><br/>';
                detail_text += '<br/><a href="' + features[0].properties[detail] + '" target="_blank">More Info on the related infrastructure project here</a><br/>';
            
            } else if (config.detailView[detail]['display'] == 'location') {

                if (Object.keys(features[0].properties).includes(detail)) {
                    if (location_text.length > 0) {
                        location_text += ', ';
                    }
                    location_text += features[0].properties[detail];
                }
            } else if (config.detailView[detail]['display'] == 'colorcoded'){
                // let's do it so that if it has this then it goes to the color dictionary and mathces up the field name, uses fieldLabel to display label and then also uses color
                // to create the circle dot we have for most status 
                let colorLabel = features.map((feature) => feature.properties[detail]);
                // console.log(config.color.fieldLabel)
                detail_text += '<span class="fw-bold">' + config.color.fieldLabel + '</span>: ' +
                '<span class="legend-dot" style="background-color:' + config.color.values[ features[0].properties[config.color.field] ]
                + '"></span><span class="text-capitalize">' + features[0].properties[config.color.field] + '</span><br/>';
                console.log([ features[0].properties[config.color.field] ])

            }

        } else {


            if (features[0].properties[detail] != "" && features[0].properties[detail] != 'undefined' && features[0].properties[detail] !=0 && features[0].properties[detail] != NaN && features[0].properties[detail] != 'nan' && features[0].properties[detail] != null && features[0].properties[detail] != 'Unknown [unknown %]' && features[0].properties[detail] != 'unknown') {
                if (config.multiCountry == true && config.detailView[detail] && config.detailView[detail]['label'] && config.detailView[detail]['label'].includes('Country')) {
                    detail_text += '<span class="fw-bold">' + config.detailView[detail]['label'] + '</span>: ' + removeLastComma(features[0].properties[detail]) + '<br/>';
                }

                else if (Object.keys(config.detailView[detail]).includes('label')) { // and color config add the dot
                    detail_text += '<span class="fw-bold">' + config.detailView[detail]['label'] + '</span>: ' + features[0].properties[detail] + '<br/>';
                }
                else if (Object.keys(config.detailView[detail]).includes('label')) {
                    detail_text += '<span class="fw-bold">' + config.detailView[detail]['label'] + '</span>: ' + features[0].properties[detail] + '<br/>';
                } else {
                    console.log(features[0].properties[detail])
                    // detail_text += features[0].properties[detail] + '<br/>';
                }
            }
            else {
                console.log(features[0].properties[detail])
     

            }
        }
    });

    let assetLabel = typeof config.assetLabel === 'string'
        ? config.assetLabel 
        : config.assetLabel.values[features[0].properties[config.assetLabel.field]];

    let capacityLabel = typeof config.capacityLabel === 'string'
        ? config.capacityLabel 
        : config.capacityLabel.values[features[0].properties[config.capacityLabel.field]];

    // Need this to be customizable for trackers that do not need summary because no units 
    // Build capacity summary
    // Make sure capacity and () get removed if there is only one feature 
    if (capacityLabel != ''){
        if (features.length > 1) { 
        let filterIndex = 0;
            for (const[index, filter] of config.filters.entries()) {
                if (filter.field == config.statusField) {
                    filterIndex = index;
                }
            }

        // Initialize capacity and count objects using reduce to resolve summary build bug
        let capacity = config.filters[filterIndex].values.reduce((acc, f) => {
            acc[f] = 0;
            return acc;
        }, {});

        let count = config.filters[filterIndex].values.reduce((acc, f) => {
            acc[f] = 0;
            return acc;
        }, {});

        features.forEach((feature) => {
            let capacityInt = parseInt(feature.properties[config.capacityDisplayField], 10);

            capacity[feature.properties[config.statusField]] += capacityInt;
            count[feature.properties[config.statusField]]++;

        });

            let detail_capacity = '';

            Object.keys(count).forEach((k) => {
                if (config.color.field == config.statusField){ 

                    if (count[k] != 0) {
                        detail_capacity += '<div class="row"><div class="col-5"><span class="legend-dot" style="background-color:' + config.color.values[k] + '"></span>' + k + '</div><div class="col-4">' + Number(capacity[k]).toLocaleString() + '</div><div class="col-3">' + count[k] + " of " + features.length + "</div></div>";
                    }
                }
                else {
                    if (count[k] != 0) {
                        detail_capacity += '<div class="row"><div class="col-5">' + k + '</div><div class="col-4">' + Number(capacity[k]).toLocaleString() + '</div><div class="col-3">' + count[k] + " of " + features.length + "</div></div>";
                    }
                }
            });
            detail_text += '<div>' + 
                '<div class="row pt-2 justify-content-md-center">Total ' + assetLabel + ': ' + features.length + '</div>' +
                '<div class="row" style="height: 2px"><hr/></div>' +
                '<div class="row "><div class="col-5 text-capitalize">' + config.statusDisplayField + '</div><div class="col-4">' + capacityLabel + '</div><div class="col-3">#&nbsp;of&nbsp;' + assetLabel + '</div></div>' +
                detail_capacity +
                '</div>';
        }
        // if item = 1, for the situation where there is only one unit, 
        // status should not have a blank where color != status field SO remove the space in status 
        // so wind one unit integrated map

        // here is where you can remove Capacity () because only one feature
        else {
            // status should not have a blank where color != status field SO remove the space in status 
            // and color SHOULD be with the type when it is primary - could lay groundwork for making it interactive on color
            
            // handle capacity adjustment for solo projects where it looks redundant to have Capacity written out twice
            
            // Remove 'Capacity' prefix and parentheses from capacityLabel
            capacityLabel = capacityLabel.replace(/^Capacity\s*/i, '').replace(/[()]/g, '');

            if (config.color.field != config.statusDisplayField){
                // for filter field in filter, if primary = True then take field name "type" in intg and use it to find the color dictionary in the colors dict above
                // and then display the projects type field with the appropriate color based on the value and the dictionary
                // 
                detail_text += '<span class="fw-bold text-capitalize">Status</span>: ' +
                '<span class="text-capitalize">' + features[0].properties[config.statusDisplayField] + '</span><br/>';
                detail_text += '<span class="fw-bold text-capitalize">Capacity</span>: ' + parseInt(features[0].properties[config.capacityDisplayField], 10).toLocaleString() + ' ' + capacityLabel;
            }
            // leave as is
            else {
                detail_text += '<span class="fw-bold text-capitalize">Status</span>: ' +
                    '<span class="legend-dot" style="background-color:' + config.color.values[ features[0].properties[config.statusDisplayField] ] + '"></span><span class="text-capitalize">' + features[0].properties[config.statusDisplayField] + '</span><br/>';
                detail_text += '<span class="fw-bold text-capitalize">Capacity</span>: ' + parseInt(features[0].properties[config.capacityDisplayField], 10).toLocaleString() + ' ' + capacityLabel;
        }
        }
    }
    // This is where you can remove the colored circle primary = true
    // we should use the primary tag in config to color code the type for integrated 


    else {
        // do nothing if color not equal to status field AND there is no capacity label
        if (config.color.field != config.statusDisplayField){
            // detail_text += '<span class="fw-bold text-capitalize">Status</span>: ' +
            // '<span class="text-capitalize">' + features[0].properties[config.statusDisplayField] + '</span><br/>';
            detail_text += '';
        }

        // assign color if equal to status field BUT ignore the capacity part when no capacity label

        else {
        // add status part not capacity part 
        detail_text += '<span class="fw-bold text-capitalize">Status</span>: ' +
        '<span class="legend-dot" style="background-color:' + config.color.values[features[0].properties[config.statusDisplayField]] + '"></span><span class="text-capitalize">' + features[0].properties[config.statusDisplayField] + '</span><br/>';
        // detail_text += '';
        }
    }
    //Location by azizah from <a href="https://thenounproject.com/browse/icons/term/location/" target="_blank" title="Location Icons">Noun Project</a> (CC BY 3.0)
    //Arrow Back by Nursila from <a href="https://thenounproject.com/browse/icons/term/arrow-back/" target="_blank" title="Arrow Back Icons">Noun Project</a> (CC BY 3.0)
    $('.modal-body').html('<div class="row m-0">' +
        '<div class="col-sm-5 rounded-top-left-1" id="detail-satellite" style="background-image:url(' + buildSatImage(features) + ')">' +
            (config.selectModal != '' ? '<span onClick="showSelectModal()"><img id="modal-back" src="../../src/img/back-arrow.svg" /></span>' : '') +
            '<img id="detail-location-pin" src="../../src/img/location.svg" width="30">' +

            '<span class="detail-location">' + removeLastComma(location_text) + '</span><br/>' +
            '<span class="align-bottom p-1" id="detail-more-info"><a href="' + features[0].properties[config.urlField] + '" target="_blank">MORE INFO</a></span>' +
            (config.showAllPhases && features.length > 1 ? '<span class="align-bottom p-1" id="detail-all-phases"><a onClick="showAllPhases(\'' + features[0].properties[config.linkField] + '\')">ALL PHASES</a></span>' : '') +

        '</div>' +
        '<div class="col-sm-7 py-2" id="total_in_view">' + detail_text + '</div>' +
        '</div>');

    setHighlightFilter(features[0].properties[config.linkField]);
}
function buildSatImage(features) {
    let location_arg = '';
    let bbox = geoJSONBBox({'type': 'FeatureCollection', features: features });

    if (bbox[0] == bbox[2] && bbox[1] == bbox[3]) {
        location_arg = bbox[0].toString() + ',' + bbox[1].toString() + ',' + config.img_detail_zoom.toString();
    } else {
        location_arg = '[' + bbox.join(',') + ']';
    }

    return 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/' + location_arg + '/350x350?attribution=false&logo=false&access_token=' + config.accessToken;
}
function showAllPhases(link) {
    config.modal.hide();
    setHighlightFilter(link);
    var bbox = geoJSONBBox({'type': 'FeatureCollection', features: config.linked[link] });
    console.log('show all phases bbox:' + bbox)
    map.flyTo({center: [(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2], zoom: config.phasesZoom});
}
function showSelectModal() {
    $('.modal-body').html(config.selectModal);
}

/* 
  toolbar filters
*/

function enableNavFilters() {
    enableSearch();
    enableSearchSelect();
    enableCountrySelect();

    // this is the event that starts loading but not complete

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
    $.ajax({
        type: "GET",
        url: config.countryFile,
        dataType: "json",
        success: function(jsonData) { config.countries = jsonData; buildCountrySelect();}
    });
}
function buildCountrySelect() {
    if (config.allCountrySelect) {
        $('#country_select').append('<li><a class="country-dropdown-item dropdown-item h4" data-countries="" data-countryText="" href="#">all</a></li>');
    }
    Object.keys(config.countries).forEach((continent, continent_idx) => {
        let dropdown_html = '';
        // Add continent as a selectable item (clicking selects all countries in continent)
        dropdown_html += `<li class="continent-li"><a class="country-dropdown-item dropdown-item h4 continent-select" data-countries="${config.countries[continent].join(';')}" data-countryText="${continent}" href="#">${continent}</a>`;
        dropdown_html += '<ul class="submenu dropdown-menu">';
        config.countries[continent].forEach((country, country_idx) => {
            dropdown_html += `<li><a class="h5 country-dropdown-item dropdown-item" data-countries="${country}" data-countryText="${country}" href="#">${country}</a></li>`;
            if (country_idx != config.countries[continent].length - 1) {
                dropdown_html += '<li><hr class="dropdown-divider"></li>';
            }
        });
        dropdown_html += "</ul></li>";

        if (continent_idx != Object.keys(config.countries).length - 1) {
            dropdown_html += '<li><hr class="dropdown-divider"></li>';
        }

        $('#country_select').append(dropdown_html);
    });

    // Click handler: select continent or country
    $('.country-dropdown-item').each(function() {
        this.addEventListener("click", function(e) {
            // Only filter if not just expanding submenu
            config.selectedCountryText = this.dataset.countrytext;
            config.selectedCountries = (this.dataset.countries.length > 0 ? this.dataset.countries.split(";") : []);
            $('#selectedCountryLabel').text(config.selectedCountryText || "all");
            $('#spinner-container-filter').removeClass('d-none')
            $('#spinner-container-filter').addClass('d-flex')
            filterData();
        });
    });

    // Hover logic for continent: show submenu, keep open when moving to submenu
    $('.continent-li').each(function() {
        let $li = $(this);
        let $submenu = $li.children('.submenu');
        let submenuTimeout;

        // Show submenu on hover
        $li.children('.continent-select').on('mouseenter', function() {
            clearTimeout(submenuTimeout);
            $submenu.css({ display: 'block' });
        });

        // Hide submenu when mouse leaves both continent and submenu
        $li.children('.continent-select').on('mouseleave', function() {
            submenuTimeout = setTimeout(() => {
                $submenu.css({ display: 'none' });
            }, 200);
        });

        $submenu.on('mouseenter', function() {
            clearTimeout(submenuTimeout);
            $submenu.css({ display: 'block' });
        });

        $submenu.on('mouseleave', function() {
            submenuTimeout = setTimeout(() => {
                $submenu.css({ display: 'none' });
            }, 200);
        });
    });

    config.selectedCountries = [];
    config.selectedCountryText = '';
}

const diacriticMap = {
    a: ["a", "á", "à", "â", "ã", "ä", "å"],
    e: ["e", "é", "è", "ê", "ë"],
    i: ["i", "í", "ì", "î", "ï"],
    o: ["o", "ó", "ò", "ô", "õ", "ö", "ø"],
    u: ["u", "ú", "ù", "û", "ü"],
    c: ["c", "ç"],
    n: ["n", "ñ"],
  };
  
function removeDiacritics(value) {
    let noDiacriticsValue = value;
    for (const char of value) {
        for (const [key, values] of Object.entries(diacriticMap)) {
            if (values.includes(char)) {
                noDiacriticsValue = noDiacriticsValue.replace(char, key);
            }
        }
    }
    return noDiacriticsValue;
}


function enableSearch() {
    $('#search-text').on('keyup paste', debounce(function() {
        config.searchText = $('#search-text').val().toLowerCase();
        // console.log(config.searchText) 
        // console.log('before diacritic function')
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

            $('#spinner-container-filter').removeClass('d-none')
            $('#spinner-container-filter').addClass('d-flex')
            filterData();
        });
    });

    config.selectedSearchFields = allSearchFields.join(',');
}

function enableResetAll() { // not use anymor but keeping in case we want a clear all button
    // need to also handle for table view - it works the same no special handling needed.

    // clear country filter by returning selectedCountryLabel to 'All' DONE!
    $('#selectedCountryLabel').text("all");
    config.selectedCountryText = '';
    config.selectedCountries = [];
    
    // // clear search text by making search text ''
    config.searchText = ''; 
    $('#search-text').val('');

    // put search field category back to all
    let allSearchFields = [];
    Object.keys(config.searchFields).forEach((field_label) => {
        allSearchFields = allSearchFields.concat(config.searchFields[field_label]);
    });
    config.selectedSearchFields = allSearchFields.join(',');
    $('#selectedSearchLabel').text("all");

    // this removes the functionality that was clearing all filters when you only wnat to clear the search box
    // clear legend by checking checked boxes DONE! 
    // $('.filter-row').each(function() {
    //     if (! $('#' + this.dataset.checkid)[0].checked) {
    //         $('#' + this.dataset.checkid)[0].checked = true;
    //         toggleFilter(this.dataset.checkid);
    //     }
    // }); 

    // start the spinner
    $('#spinner-container-filter').removeClass('d-none')
    $('#spinner-container-filter').addClass('d-flex')

    // then filter data
    filterData();

}  

function enableClearSearch() {
    // need to also handle for table view - it works the same no special handling needed.

    // // clear country filter by returning selectedCountryLabel to 'All' DONE!
    // $('#selectedCountryLabel').text("all");
    // config.selectedCountryText = '';
    // config.selectedCountries = [];
    
    // // clear search text by making search text ''
    config.searchText = ''; 
    $('#search-text').val('');

    // put search field category back to all
    let allSearchFields = [];
    Object.keys(config.searchFields).forEach((field_label) => {
        allSearchFields = allSearchFields.concat(config.searchFields[field_label]);
    });
    config.selectedSearchFields = allSearchFields.join(',');
    $('#selectedSearchLabel').text("all");

    // this removes the functionality that was clearing all filters when you only wnat to clear the search box
    // clear legend by checking checked boxes DONE! 
    // $('.filter-row').each(function() {
    //     if (! $('#' + this.dataset.checkid)[0].checked) {
    //         $('#' + this.dataset.checkid)[0].checked = true;
    //         toggleFilter(this.dataset.checkid);
    //     }
    // }); 

    // // start the spinner
    // $('#spinner-container-filter').removeClass('d-none')
    // $('#spinner-container-filter').addClass('d-flex')

    // then filter data
    filterData();

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

/* from https://github.com/geosquare/geojson-bbox */
function geoJSONBBox (gj) {
    var coords, bbox;
    if (!gj.hasOwnProperty('type')) return;
    coords = getCoordinatesDump(gj);
    bbox = [ Number.POSITIVE_INFINITY,Number.POSITIVE_INFINITY,
        Number.NEGATIVE_INFINITY, Number.NEGATIVE_INFINITY,];
    return coords.reduce(function(prev,coord) {
      return [
        Math.min(coord[0], prev[0]),
        Math.min(coord[1], prev[1]),
        Math.max(coord[0], prev[2]),
        Math.max(coord[1], prev[3])
      ];
    }, bbox);
  };
  
function getCoordinatesDump(gj) {
    var coords;
    if (gj.type == 'Point') {
      coords = [gj.coordinates];
    } else if (gj.type == 'LineString' || gj.type == 'MultiPoint') {
      coords = gj.coordinates;
    } else if (gj.type == 'Polygon' || gj.type == 'MultiLineString') {
      coords = gj.coordinates.reduce(function(dump,part) {
        return dump.concat(part);
      }, []);
    } else if (gj.type == 'MultiPolygon') {
      coords = gj.coordinates.reduce(function(dump,poly) {
        return dump.concat(poly.reduce(function(points,part) {
          return points.concat(part);
        },[]));
      },[]);
    } else if (gj.type == 'Feature') {
      coords =  getCoordinatesDump(gj.geometry);
    } else if (gj.type == 'GeometryCollection') {
      coords = gj.geometries.reduce(function(dump,g) {
        return dump.concat(getCoordinatesDump(g));
      },[]);
    } else if (gj.type == 'FeatureCollection') {
      coords = gj.features.reduce(function(dump,f) {
        return dump.concat(getCoordinatesDump(f));
      },[]);
    }
    return coords;
}
// TODO change this function name to be semicolon not comma
function removeLastComma(str) {
    if (str.charAt(str.length - 1) === ';') {
        str = str.slice(0, -1);
    }
    return str;
}

// TODO
// // The following values can be changed to control rotation speed:

// At low zooms, complete a revolution every two minutes.
const secondsPerRevolution = 120;
// Above zoom level 5, do not rotate.
const maxSpinZoom = 5;
// Rotate at intermediate speeds between zoom levels 3 and 5.
const slowSpinZoom = 3;
// const btnSpinToggle = document.querySelector('#btn-spin-toggle');


let userInteracting = false;
let spinEnabled = true;

function spinGlobe() {

    const zoom = map.getZoom();
    if (config.projection == 'globe'){

        if (spinEnabled && !userInteracting && zoom < maxSpinZoom) {
            let distancePerSecond = 360 / secondsPerRevolution;
            if (zoom > slowSpinZoom) {
                // Slow spinning at higher zooms
                const zoomDif =
                    (maxSpinZoom - zoom) / (maxSpinZoom - slowSpinZoom);
                distancePerSecond *= zoomDif;
            }
            const center = map.getCenter();
            center.lng -= distancePerSecond;
            // Smoothly animate the map over one second.
            // When this animation is complete, it calls a 'moveend' event.
            map.easeTo({ center, duration: 1000, easing: (n) => n });
        }
    }
}

// Pause spinning on interaction
map.on('mousedown', () => {
    userInteracting = true;
});


// // When animation is complete, start spinning if there is no ongoing interaction
map.on('moveend', () => {
    spinGlobe();
});

// document.getElementById('btn-spin-toggle').addEventListener('click', (e) => {
//     spinEnabled = !spinEnabled;
//     if (spinEnabled) {
//         spinGlobe();
//         e.target.innerHTML = 'Pause rotation';
//     } else {
//         map.stop(); // Immediately end ongoing animation
//         e.target.innerHTML = 'Start rotation';
//     }
// });


// // # adding option to pause spin with space important for smaller screens
// document.addEventListener('keydown', (e) => {
//     spinEnabled = !spinEnabled;
//     if (e.code === "Space") {
//         if (spinEnabled) {
//             spinGlobe();
//             btnSpinToggle.innerHTML = 'Pause rotation'; // not working not sure why
//         } else {
//             map.stop(); // Immediately end ongoing animation
//             spinGlobe();
//             btnSpinToggle.innerHTML = 'Start rotation';
//         }
//     }
// });

