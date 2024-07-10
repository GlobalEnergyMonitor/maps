var config = {
    json: './data/africa_energy_tracker_2024-07-09.geojson',
    geometries: ['Point','LineString'],
    center: [30, 0],
    zoomFactor: 1.5,
    statusField: 'status-legend',
    statusDisplayField: 'status',
    color: {

        field: 'tracker',
        values: {
            'GOGPT': 'blue',
            'GOGET': 'red',
            'GOIT': 'green',
            'GGIT': 'green',
            'GGIT-lng': 'green',
            'GCPT': 'blue',
            'GCMT': 'red',
            'GCTT': 'green',
            'GBPT': 'blue',
            'GGPT': 'blue',
            'GNPT': 'blue',
            'GSPT': 'blue',
            'GWPT': 'blue',
            'GHPT': 'blue'
        }
    },
    //filter values should have no spaces
    filters: [
        {
            field: 'tracker',
            values: ["GCPT", "GOGPT", "GBPT", "GNPT", "GSPT", "GWPT", "GHPT", "GGPT", "GOIT", "GGIT", "GGIT-lng", "GCTT", "GOGET", "GCMT"], 
            values_labels: ['coal power stations', 'oil & gas power stations', 'bioenergy power stations', 'nuclear power plants', 'solar (thermal and PV) power plants', 'wind power plants', 'hydropower plants', 'geothermal power plants', 'oil pipelines', 'gas pipelines', 'LNG terminals', 'coal terminals', 'oil & gas extraction areas','coal mines'],
            primary: true
        },
        {
            field: 'status-legend',
            label: 'Status',
            values: ['operating','proposed-plus','pre-construction-plus','construction-plus','retired-plus','cancelled','mothballed-plus','shelved'],
            values_labels: ['Operating','Proposed / Announced / Discovered','Pre-construction / Pre-permit / Permitted', 'Construction / In development','Retired / Closed / Decommissioned','Cancelled','Mothballed / Idle / Shut in','Shelved']

        },

    ],
    capacityField: 'scaling-capacity',
    
    capacityDisplayField: 'capacity-display',
    capacityLabel: '',
    //interpolate: ["cubic-bezier", 0, 0, 0, 1],
    //can be string for single value, or hash. always single value is showMaxCapacity is true
    // capacityLabel: {
    //     field: 'tracker-custom',
    //     values: {
    //         'GCPT': 'MW',
    //         'GOGPT': 'MW',
    //         'GBPT':	'MW',
    //         'GNPT':	'MW',
    //         'GSPT':	'MW',
    //         'GSPT':	'MW',
    //         'GWPT':	'MW',
    //         'GHPT':	'MW',
    //         'GGPT':	'MW',
    //         'GOGET - oil':	'million boe/y',
    //         'GOGET - gas':	'million m³/y',
    //         'GOIT': 'boe/d',
    //         'GGIT':	'Bcm/y of natural gas',
    //         'GGIT - import': 'MTPA of natural gas',
    //         'GGIT - export': 'MTPA of natural gas',
    //         'GCMT':	'million tonnes coal/y',
    //         'GCTT':	'million tonnes coal/y'
    //     }
    // },
    // skipCapacitySum: '',

    capItemLabel:  {
            field: 'tracker-custom',
            values: {
                'GCPT': 'MW',
                'GOGPT': 'MW',
                'GBPT':	'MW',
                'GNPT':	'MW',
                'GSPT':	'MW',
                'GWPT':	'MW',
                'GHPT':	'MW',
                'GGPT':	'MW',
                // 'GOGET - oil':	'million boe/y',
                // 'GOGET - gas':	'million m³/y',
                'GOIT': 'boe/d',
                'GGIT':	'Bcm/y of natural gas',
                'GGIT - import': 'MTPA of natural gas',
                'GGIT - export': 'MTPA of natural gas',
                // 'GCMT':	'million tonnes coal/y',
                'GCTT':	'million tonnes coal/y'
            }
        },
    prodItemLabel: {
        field: 'tracker-custom',
            values: {
                'GOGET - oil':	'million boe/y',
                'GOGET - gas':	'million m³/y',
                'GCMT':	'million tonnes coal/y'
            }
    },
    //productionLabel NEED a productionLabel
    showMaxCapacity: false,

    assetFullLabel: "",
    //can be string for single value, or hash
    assetLabel: {
        field: 'tracker-custom',
        values: {
            'GCPT': 'units',
            'GOGPT': 'units',
            'GBPT': 'units',
            'GNPT': 'units',
            'GSPT': 'phases',
            'GWPT':	'phases',
            'GHPT':	'units',
            'GGPT':	'units',
            'GOGET - oil': 'areas',
            'GOGET - gas': 'areas',
            'GOIT': 'projects',
            'GGIT': 'projects',
            'GGIT - import': 'projects',
            'GGIT - export': 'projects',
            'GCMT': 'projects',
            'GCTT': 'projects'
        }
    },
    nameField: 'name',
//    linkField: 'id',  

    countryFile: 'countries.js',
    allCountrySelect: true, //why was this false? 
    countryField: 'areas',
    //if multicountry, always end values with a comma
    multiCountry: true,

    tableHeaders: {
        values: ['tracker-display','name','unit-name', 'owner', 'parent', 'capacity-display', 'production','status', 'areas', 'start-year'],
        labels: ['Type', 'Name','Unit','Owner', 'Parent','Capacity', 'Production','Status','Countries','Start year', ],
        
        // 'capacity-oil', 'capacity-gas'
        // 'Production oil (Million bbl/y)', 'Production Gas (Milliion m³/y)'
        clickColumns: ['project'],
        rightAlign: ['unit','capacity','production','start-year'], 
        removeLastComma: ['areas'], 
        // displayValue: {'tracker-display': "assetLabel"},
        // appendValue: {'capacity': "capItemLabel"},
        // appendValue: {'production': "prodItemLabel"},
        // appendValue: {'capacity-oil ': "prodItemLabel"},
        // appendValue: {'capacity-gas': "prodItemLabel"},

    },
    searchFields: { 'Project': ['name'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start-year'],
        'Infrastructure Type': ['tracker-display']
    },
    detailView: {
        'name': {'display': 'heading'},
        'production': {'label': 'Production'},
        'cap_total': {'label': 'Capacity'},
        'capacity-oil': {'label': 'Production Oil'},
        'capacity-gas': {'label': 'Production Gas'},
        'prod-year-oil': {'label': 'Production year - oil (Million bbl/y)'},
        'prod-year-gas': {'label': 'Production year - gas (Milliion m³/y)'},
        // 'start-year': {'label': 'Start Year'},
        // 'owner': {'label': 'Owner'},
        // 'parent': {'label': 'Parent'},
        'river': {'label': 'River'},
        'tracker-display': {'label': 'Tracker'},
        'areas': {'label': 'Country/Area(s)'},
        // 'subnat-display': {'display': 'location'}, // TODO pull out first one only if ; in it 
        // 'areas-display': {'display': 'location'} // TODO pull out first one only if ; in it
    }

};