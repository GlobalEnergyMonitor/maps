var config = {
    geojson: 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/GOGET/2026-03/europe_map_2026-03-02.geojson',
    geometries: ['Point','LineString'],
    center: [8, 50],
    zoomFactor: 1.9,
    img_detail_zoom: 10,
    statusField: 'status-legend-regional-regional',
    statusDisplayField: 'status',
    color: {

        field: 'tracker-custom',
        values: {  
            'GOGPT': 'blue',
            'GGIT': 'green',
            'GGIT-import':'green',
            'GGIT-export':'green',
            'GOGET-oil': 'red',

        }
    },

    filters: [

        {
            field: 'tracker-custom',
            label: 'Type',
            values: ["GOGPT", "GGIT","GGIT-import", "GGIT-export","GOGET-oil"], 
            values_labels: ['Gas power units','Gas pipelines', 'LNG import terminals', 'LNG export terminals',  "Gas extraction areas",],
        },
        {
            field: 'status-legend-regional',
            label: 'Status',
            values: ['operating','proposed-plus','pre-construction-plus','construction-plus','retired-plus','cancelled','mothballed-plus', 'shelved', 'not-found'],
            values_labels: ['Operating','Proposed/Announced/Discovered','Pre-construction', 'Construction/In development','Retired/Closed/Decommissioned','Cancelled','Mothballed/Idle','Shelved', 'Not Found'] // removed abandoned and 'UGS', 
        },

    ],
    capacityField: 'scaling-capacity',
    // linkField: 'pid',
    capacityLabel: {
        field: 'tracker-custom',
        values: {
            'GOGPT': 'MW',
            // 'GOGET-oil': '',	//'million boe/y', // remove because they dont have capacity is only relevant for scaling here Scott request
            'GGIT': 'bcm/y of gas',
            'GGIT-import': 'MTPA of natural gas',
            'GGIT-export': 'MTPA of natural gas',            


        }
    },
    showMaxCapacity: false,

    assetFullLabel: "Units / Pipelines", 
    //can be string for single value, or hash
    assetLabel: 'units',
    // assetLabel: {
    //     field: 'tracker-custom',
    //     values: {
    //         'GOGPT': 'units',
    //         'GOGET-oil': 'areas',
    //         'GGIT': 'projects',
    //         'GGIT-import': 'projects',
    //         'GGIT-export': 'projects',

    //     }
    // },
    nameField: 'name',
    countryFile: 'countries.js',
    allCountrySelect: false,
    countryField: 'areas',
    //if multicountry, always end values with a comma
    multiCountry: true,
    capacityDisplayField: 'capacity-table',
    
    tableHeaders: {
        values: ['name','unit-name', 'owner', 'parent', 'capacity-table', 'units-of-m','status', 'areas', 'start-year', 'prod-gas', 'prod-year-gas','fuel','tracker-display'],
        labels: ['Name','Unit','Owner', 'Parent','Capacity', 'units','Status','Country/Area(s)','Start year', 'Production (Million m³/y)', 'Production year (gas)', 'Fuel','Type'],
        clickColumns: ['name'],
        rightAlign: ['capacity-table','prod-gas','start-year','prod-year-gas'], 
        removeLastComma: ['areas'], 
        toLocaleString: ['capacity-table'],


    },
    searchFields: { 'Project': ['name', 'other-name', 'local-name', 'name-search', 'pid'], 
        'Companies': ['owner', 'parent', 'owner-search', 'parent-search'],
        'Start Year': ['start-year'],
        'Infrastructure Type': ['tracker-display'],
        'Status': ['status', 'status-legend-regional'],
        'Province/State': ['subnat']
    },
    detailView: {
        'name': {'display': 'heading'},
        'location-accuracy': {'label': 'Location Accuracy'},
        'prod-gas': {'label': 'Gas Production (million m³/y)'},
        'prod-unspecified': {'label': 'Unspecified Hydrocarbons Production (million boe/y)'},
        'prod-year-gas': {'label': 'Production Year - Gas'},
        'prod-year-unspecified': {'label': 'Production Year - Hydrocarbons (unspecified)'},
        'start-year': {'label': 'Start Year'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'river': {'label': 'River'},
        'tracker-display': {'label': 'Type'},
        'areas': {'label': 'Country/Area(s)'},
        'areas-subnat-sat-display': {'display': 'location'}, 
    },
    showToolTip: true,

        /* radius associated with minimum/maximum value on map */
    // minRadius: 2,
    // maxRadius: 10,
    minLineWidth: 1,
    maxLineWidth: 3,
    
    highZoomMinLineWidth: 1,
    highZoomMaxLineWidth: 3,

    // /* radius to increase min/max to under high zoom */
    // highZoomMinRadius: 4,
    // highZoomMaxRadius: 32,
    // highZoomMinLineWidth: 4,
    // highZoomMaxLineWidth: 32,
    
    // showAllPhases: true

};