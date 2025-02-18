var site_config = {
    /* Mapbox Access Token */
    accessToken: 'pk.eyJ1IjoiZ2VtdGVhbTEiLCJhIjoiY2xtbm90dThtMDB2azJrbnhuZ2JhbGZ4NCJ9.eBYvRjhtNJYgZDXQymTmlQ',

    /* Mapbox Base Map Style */
    mapStyle: 'mapbox://styles/gemteam1/cls98k6sf02li01p2fqtu67lc',

    center: [0, 0],
    projection: 'naturalEarth',

    /* Zoom level that asset detail cards open at; this is a good one to override in tracker config,
     depending on scale of facilities */

    img_detail_zoom: 15,

    /* Define labels for sitewide colors, referenced in tracker config */
    colors: {
        'red': '#c74a48',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
        'grey': '#8f8f8e'
    },
    /* style test parameters!

    /* Mapbox styling applied to all trackers */
    pointPaint: {
        'circle-opacity':.85
    },
    linePaint: {
        'line-opacity':.85
    },
    lineLayout: {
        'line-cap': 'round', 
        'line-join': 'round'
    },
    
    /* radius associated with minimum/maximum value on map */
    minRadius: 2,
    maxRadius: 10,
    minLineWidth: 1,
    maxLineWidth: 10,

    /* radius to increase min/max to under high zoom */
    highZoomMinRadius: 4,
    highZoomMaxRadius: 32,
    highZoomMinLineWidth: 4,
    highZoomMaxLineWidth: 32,
    
    /* define column names to pull data from */
    linkField: 'url',

    urlField: 'url',

    countryField: 'country',
    statusField: 'status',
    statusDisplayField: 'status',
    capacityField: 'capacity',
    capacityDisplayField: 'capacity',
    locationColumns:{
        lat: 'lat',
        lng: 'lng'
    },

    /* by default, no all phases link; override in tracker config where appropriate */
    showAllPhases: false,
    showMaxCapacity: true,

    /* zoom level to set map when viewing all phases */
    phasesZoom: 8,

    /* initial load zoom multiplier */
    zoomFactor: 1.25,

    countryFile: '../../src/countries.js', 
    allCountrySelect: true,
    multiCountry: false,

    hitArea: 5, 

    geometries: ['Point']
};
