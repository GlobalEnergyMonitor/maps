var config = {
    csv: 'data/csv-data-2024-09-20.csv',
    tiles: [
        // 'https://gem.dev.c10e.org/2024-03-12/{z}/{x}/{y}.pbf'
        // 'https://bucketeer-cf25e1cc-bfe0-4e0f-957c-65e8e9492475.s3.amazonaws.com/maps/integrated-2024-03-14/{z}/{x}/{y}.pbf'
        // 'https://mapsintegrated.nyc3.cdn.digitaloceanspaces.com/maps/integrated-2024-03-14/{z}/{x}/{y}.pbf'
        // 'https://mapsintegrated.nyc3.cdn.digitaloceanspaces.com/maps/integrated-2024-05-24/{z}/{x}/{y}.pbf',
        // 'https://mapsintegrated.nyc3.cdn.digitaloceanspaces.com/maps/integrated-2024-05-30/{z}/{x}/{y}.pbf',
        // 'https://mapsintegrated.nyc3.cdn.digitaloceanspaces.com/maps/integrated-2024-06-10/{z}/{x}/{y}.pbf',
        // 'https://mapsintegrated.nyc3.cdn.digitaloceanspaces.com/maps/integrated-test-speed/{z}/{x}/{y}.pbf',
        // 'https://mapsintegrated.nyc3.cdn.digitaloceanspaces.com/maps/integrated-2024-07-31/{z}/{x}/{y}.pbf',
        'https://mapsintegrated.nyc3.cdn.digitaloceanspaces.com/maps/integrated-2024-09-20/{z}/{x}/{y}.pbf'
         ],
    tileSourceLayer: 'integrated',

    projection: 'globe',
    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
        field: 'type',
        values: {
            'bioenergy': 'blue',
            'coal': 'red',
            'geothermal': 'blue',
            'hydropower': 'blue',
            'nuclear': 'blue',
            'oil/gas': 'red',
            'solar': 'green',
            'wind': 'green'
        }

    },
    minRadius: 1,
    maxRadius: 10,
    highZoomMinRadius: 4,
    highZoomMaxRadius: 32,
    interpolate: ["cubic-bezier", 0, 0, 0, 1],
    filters: [
        {
            field: 'type',
            values: ['coal','oil/gas','nuclear','geothermal','hydropower','bioenergy','solar','wind'],
            primary: true
        },
        {
            field: 'status',
            /* values need to be specified for ordering */
            values: ['operating','construction','pre-construction','announced','retired','cancelled','shelved','mothballed']
        }
    ],
    nameField: 'plant-/-project-name',
    statusField: 'status',
    statusDisplayField: 'status',
    capacityField: 'capacity-(mw)',
    capacityDisplayField: 'capacity-(mw)',
    capacityLabel: 'Capacity (MW)',
    linkField: 'gem-location-id',
    urlField: 'gemwiki-url',
    countryField: 'country/area',
    searchFields: { 'Project': ['plant-/-project-name'], 
        'Companies': ['Owner', 'Parent'],
        'Start Year': ['Start year'],
        'Country/Area': ['country/area'],
        'Type': ['type'],
        'Status': ['status']
    },
    assetFullLabel: "units / phases",
    assetLabel: "Units / Phases",
    img_detail_zoom: 10,
    tableHeaders: {
        values: ['plant-/-project-name','unit-/-phase-name', 'owner', 'parent', 'capacity-(mw)', 'status', 'subnational-unit-(state,-province)', 'country/area', 'start-year', 'retired-year', 'type'],
        labels: ['Plant/project name','Unit/phase name','Owner','Parent','Capacity (MW)','Status','Subnational unit (province/state)','Country/Area','Start year','Retired year','Type'],
        clickColumns: 'plant-/-project-name',
        removeLastComma: ['country/area']
    },
    detailView: {
        'plant-/-project-name': {'display': 'heading'},
        'type': {'label': 'Type'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'technology': {'display': 'join', 'label': ['Technology', 'Technologies']},
        'fuel': {'display': 'join', 'label': ['Fuel Type', 'Fuel Types']},
        'start-year': {'display': 'range', 'label': ['Start Year', 'Start Year Range']},
        'subnational-unit-(state,-province)': {'display': 'location'},
        'country/area': {'display': 'location'}
    },
    zoomFactor: 1,
    multiCountry: true,
    // center: [60, 20], // 1.7 zoomFacter once we get the data loading separate from tiles
    multiCountry: true,


            /* style test parameters!

    /* Mapbox styling applied to all trackers */
    pointPaint: {
        'circle-opacity':.75
    },

    /* radius associated with minimum/maximum value on map */
    minRadius: 3,
    maxRadius: 10,


    /* radius to increase min/max to under high zoom */
    highZoomMinRadius: 40,
    highZoomMaxRadius: 320,

};
