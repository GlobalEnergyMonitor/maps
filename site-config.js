var site_config = {
    /* Mapbox Access Token */
    accessToken: 'pk.eyJ1IjoiZWFydGhyaXNlIiwiYSI6ImNsa2d4eGhvaTAxb3gzcHAyem5weDY5bGgifQ.dir6j-9L6fv7Q9g_DwT51w',

    /* Mapbox Base Map Style */
    mapStyle: 'mapbox://styles/earthrise/clkmx3xlm018k01qm3ek6auuv',

    /* Zoom level that asset detail cards open at; this is a good one to override in tracker config,
     depending on scale of facilities */

    img_detail_zoom: 15,

    /* Define labels for sitewide colors, referenced in tracker config */
    colors: {
        'red': '#e37c79',
        'blue': '#aaabf2',
        'green': '#b5eaaa',
        'grey': '#9c9c9b'
    },

    /* Mapbox styling applied to all trackers */
    paint: {
        'circle-opacity':.9
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
