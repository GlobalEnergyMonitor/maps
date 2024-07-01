var config = {
    json: './data/africa_energy_tracker-2024-06-26.2.geojson',
    geometries: ['Point','LineString'],
    center: [30, 0],
    zoomFactor: 1.5,
    statusField: 'status-legend',
    statusDisplayField: 'status',
    color: {
        field: 'status-legend',
        values: {
            'operating': 'red',
            'pre-construction-plus': 'blue',
            'proposed-plus': 'green',
            'construction-plus': 'blue',
            'retired-plus': 'grey',
            'cancelled': 'grey',
            'mothballed-plus': 'grey',
            'shelved': 'grey'
        }
    },
    //filter values should have no spaces
    filters: [
        {
            field: 'status-legend',
            values: ['operating','proposed-plus','construction-plus','pre-construction-plus','retired-plus','cancelled','mothballed-plus','shelved'],
            values_labels: ['Operating','Proposed+','Construction+','Pre-Construction+','Retired+','Cancelled','Mothballed+','Shelved']

        }
    ],
    capacityField: 'scaling_capacity',
    capacityDisplayField: 'capacity',
    //interpolate: ["cubic-bezier", 0, 0, 0, 1],
    //can be string for single value, or hash. always single value is showMaxCapacity is true
    capacityLabel: {
        field: 'tracker_custom',
        values: {
            'GCPT': 'MW',
            'GOGPT': 'MW',
            'GBPT':	'MW',
            'GNPT':	'MW',
            'GSPT':	'MW',
            'GSPT':	'MW',
            'GWPT':	'MW',
            'GHPT':	'MW',
            'GGPT':	'MW',
            'GOGET - oil':	'million boe/y',
            'GOGET - gas':	'million m³/y',
            'GOIT': 'boe/d',
            'GGIT':	'Bcm/y of natural gas',
            'GGIT - import': 'MTPA of natural gas',
            'GGIT - export': 'MTPA of natural gas',
            'GCMT':	'million tonnes coal/y',
            'GCTT':	'million tonnes coal/y'
        }
    },
    
    showMaxCapacity: false,

    assetFullLabel: "",
    //can be string for single value, or hash
    assetLabel: {
        field: 'tracker_custom',
        values: {
            'GCPT': 'coal power',
            'GOGPT': 'oil/gas power',
            'GBPT': 'bioenergy power',
            'GNPT': 'nuclear',
            'GSPT': 'solar thermal',
            'GSPT':	'solar PV',
            'GWPT':	'wind',
            'GHPT':	'hydropower',
            'GGPT':	'geothermal',
            'GOGET - oil': 'oil and gas extraction - oil',
            'GOGET - gas': 'oil and gas extraction - gas',
            'GOIT': 'oil pipelines',
            'GGIT': 'gas pipelines',
            'GGIT - import': 'LNG terminals - import',
            'GGIT - export': 'LNG terminals - export',
            'GCMT': 'coal mines',
            'GCTT': 'coal terminals'
        }
    },
    nameField: 'name',
//    linkField: 'id',

    countryFile: 'countries.js',
    allCountrySelect: false,
    countryField: 'areas',
    //if multicountry, always end values with a comma
    multiCountry: true,

    tableHeaders: {
        values: ['tracker_custom','name','unit_name', 'owner', 'parent', 'capacity', 'status', 'areas', 'start_year'],
        labels: ['Tracker', 'Name','Unit','Owner', 'Parent','Capacity','Status','Countries','Start year'],
        clickColumns: ['project'],
        rightAlign: ['unit','capacity','start_year'],
        removeLastComma: ['areas'],
        displayValue: {'tracker_custom': "assetLabel"},
        appendValue: {'capacity': "capacityLabel"}
    },
    searchFields: { 'Project': ['name'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start_year']
    },
    detailView: {
        'name': {'display': 'heading'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'river': {'label': 'River'},
        'tracker': {'label': 'Tracker'},
        'subnat': {'display': 'location'},
        'areas': {'display': 'location'}
    }

};
