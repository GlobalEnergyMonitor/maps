var site_config = {
    accessToken: 'pk.eyJ1IjoiZWFydGhyaXNlIiwiYSI6ImNsa2d4eGhvaTAxb3gzcHAyem5weDY5bGgifQ.dir6j-9L6fv7Q9g_DwT51w',
    mapStyle: 'mapbox://styles/earthrise/clkmx3xlm018k01qm3ek6auuv',
    img_detail_zoom: 15,
    colors: {
        'red': '#e37c79',
        'blue': '#aaabf2',
        'green': '#b5eaaa',
        'grey': '#9c9c9b'
    },
    paint: {
        'circle-opacity':.9
    },
    searchFields: { 'Project': ['project'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start_year']
    },
    tableHeaders: {
        values: ['url','project','unit', 'owner', 'parent', 'capacity', 'status', 'region', 'country', 'province', 'start_year'],
        labels: ['url', 'Plant','Unit','Owner','Parent','Capacity (MW)','Status','Region','Country','Subnational unit (province/state)','Start year'],
        clickColumn: 'url'
    },
    minRadius: 2,
    maxRadius: 10,
    highZoomMinRadius: 4,
    highZoomMaxRadius: 32,
    img_detail_zoom: 15
};
