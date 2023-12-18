var site_config = {
    /* Mapbox Access Token */
    accessToken: 'pk.eyJ1IjoiZWFydGhyaXNlIiwiYSI6ImNsa2d4eGhvaTAxb3gzcHAyem5weDY5bGgifQ.dir6j-9L6fv7Q9g_DwT51w',

    /* Mapbox Base Map Style */
    mapStyle: 'mapbox://styles/earthrise/clit4wm0101wk01pd1nm7gmro/',

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

    /* Mapbox styling applied to all trackers */
    paint: {
        'circle-opacity':.85
    },

    /* radius associated with minimum/maximum value on map */
    minRadius: 2,
    maxRadius: 10,

    /* radius to increase min/max to under high zoom */
    highZoomMinRadius: 4,
    highZoomMaxRadius: 32,

    /* define column names to pull data from */
    linkField: 'url',
    countryField: 'country',
    locationColumns:{
        lat: 'lat',
        lng: 'lng'
    },

    /* by default, no all phases link; override in tracker config where appropriate */
    showAllPhases: false,

    /* zoom level to set map when viewing all phases */
    phasesZoom: 8
};
