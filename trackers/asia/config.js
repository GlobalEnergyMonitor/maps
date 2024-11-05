var config = {

    json: 'compilation_output/asia_2024-11-05.geojson',
    geometries: ['Point','LineString'],
    center: [60, 20],
    zoomFactor: 1.9,
    img_detail_zoom: 10,
    statusField: 'status-legend',
    statusDisplayField: 'status',
    allCountrySelect: false,

    color: {
        field: 'tracker-custom',
        values: {
            'GOGPT': 'blue',
            'GOGET-oil': 'red',
            'GGIT': 'green',
            'GGIT-import':'green',
            'GGIT-export':'green',


        }
    },
    

    filters: [
        {
            field: 'tracker-custom',
            values: ["GOGPT",  "GGIT", "GGIT-import", "GGIT-export","GOGET-oil", ], 
            values_labels: ['gas power units', 'gas pipelines', 'LNG import terminals', 'LNG export terminals', 'gas extraction areas',], // CHECK THAT
            primary: true
        },
        {
            field: 'status-legend',
            label: 'Status',
            values: ['operating','proposed-plus','pre-construction-plus','construction-plus','retired-plus','cancelled','mothballed-plus','shelved', 'not-found'],
            values_labels: ['Operating','Proposed/Announced/Discovered','Pre-construction/Pre-permit/Permitted', 'Construction/In development','Retired/Closed/Decommissioned','Cancelled','Mothballed/Idle/Shut in','Shelved', 'Not Found']

        },

    ],
    capacityField: 'scaling-capacity',
    
    capacityDisplayField: 'capacity-display',
    capacityLabel: '',

    showMaxCapacity: false,

    assetFullLabel: "Units / Pipelines", 
    //can be string for single value, or hash
    // not using assetLabel for now TODO
    assetLabel: '',
    // assetLabel: {
    //     // field: 'tracker-custom',
    //     // values: {
    //     //     'GCPT': 'units',
    //     //     'GOGPT': 'units',
    //     //     'GBPT': 'units',
    //     //     'GNPT': 'units',
    //     //     'GSPT': 'phases',
    //     //     'GWPT':	'phases',
    //     //     'GHPT':	'units',
    //     //     'GGPT':	'units',
    //     //     'GOGET - oil': 'areas',
    //     //     'GOGET - gas': 'areas',
    //     //     'GOIT': 'projects',
    //     //     'GGIT': 'projects',
    //     //     'GGIT - import': 'projects',
    //     //     'GGIT - export': 'projects',
    //     //     'GCMT': 'projects',
    //     //     'GCTT': 'projects'
    //     // }
    // },
    nameField: 'name',
    linkField: 'id',  

    countryFile: 'countries.js',
    countryField: 'areas',
    //if multicountry, always end values with a comma
    multiCountry: true,

    tableHeaders: {
        values: ['tracker-display','name','unit-name', 'fuel','owner', 'parent', 'capacity-table', 'status', 'areas', 'start-year',  'prod-gas', 'prod-year-gas'],
        labels: ['Type', 'Name','Unit', 'Fuel','Owner', 'Parent','Capacity (MW)', 'Status','Country/Area(s)','Start year', 'Production (Million m³/y)', 'Production year (gas)'],

        clickColumns: ['project'],
        rightAlign: ['unit','capacity', 'prod-gas','start-year','prod-year-gas'], 
        removeLastComma: ['areas'], 
  
    },
    searchFields: { 'Project': ['name'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start-year'],
        'Infrastructure Type': ['tracker-display'],
        'Status': ['status'],
        'Province/State': ['subnat']
    },
    detailView: {
        'name': {'display': 'heading'},
        'status': {'label': 'Status'}, 
        'unit-name': {'label': 'Unit Name'},
        'capacity-table': {'label': 'Capacity'}, // interim until summary capacity can be customized by tracker
        'prod-gas': {'label': 'Production (Million m³/y)'},
        'prod-year-gas': {'label': 'Production Year - Gas'},
        'start-year': {'label': 'Start Year'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'river': {'label': 'River'},
        'tracker-display': {'label': 'Type'},
        'areas': {'label': 'Country/Area(s)'},
        'areas-subnat-sat-display': {'display': 'location'}, 
    }

};