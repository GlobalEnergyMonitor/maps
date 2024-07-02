// TODO: continue adjusting this based on live version of AET
// this is combo of integrated new and geothermal 
// add in new params and make sure it'll work as expected 

// var config = {
//     geojson: '',
//     color: { /* will be processed both into style json for paint circle-color property, and for legend. 
//             what's right property name?? is color also listing values used in the summary? 
//             should this just be made part of the filter? that might allow to address multiple properties */
//         field: 'Type',
//         values: {
//             'bioenergy': 'blue',
//             'coal': 'red',
//             'geothermal': 'blue',
//             'hydropower': 'blue',
//             'nuclear': 'blue',
//             'oil/gas': 'red',
//             'solar': 'green',
//             'wind': 'green'
//         }
//     },
    
//     filters: [
//         {
//             field: 'Type',
//             values: ['coal','oil/gas','nuclear','geothermal','hydropower','bioenergy','solar','wind'],
//             primary: true
//         },
//         {
//             field: 'Status',
//             /* values need to be specified for ordering */
//             values: ['operating','construction','pre-construction','announced','retired','cancelled','shelved','mothballed']
//         }
//     ],
//     nameField: 'Plant/project name',
//     statusField: 'Status',
//     statusDisplayField: 'Status',
//     capacityField: 'Capacity (MW)',
//     capacityDisplayField: 'Capacity (MW)',
//     capacityLabel: 'Capacity (MW)',
//     linkField: 'Wiki URL',
//     urlField: 'Wiki URL',
//     countryField: 'Country',
//     searchFields: { 'Project': ['Plant/project name'], 
//         'Companies': ['Owner', 'Parent'],
//         'Start Year': ['Start year']
//     },
//     assetFullLabel: "plants",
//     assetLabel: "Plants",
//     img_detail_zoom: 15,
//     tableHeaders: {
//         values: ['Plant/project name','Unit/phase name', 'Owner', 'Parent', 'Capacity (MW)', 'Status', 'Subnational unit(s)', 'Country', 'Start year'],
//         labels: ['Plant/project name','Unit/phase name','Owner','Parent','Capacity (MW)','Status','Subnational unit (province/state)','Country','Start year'],
//         clickColumns: 'Plant/project name'
//     },
//     detailView: {
//         'Plant/project name': {'display': 'heading'},
//         'Type': {'label': 'Type'},
//         'Owner': {'label': 'Owner'},
//         'Parent': {'label': 'Parent'},
//         'Technology': {'display': 'join', 'label': ['Technology', 'Technologies']},
//         'Fuel': {'display': 'join', 'label': ['Fuel Type', 'Fuel Types']},
//         'Start year': {'display': 'range', 'label': ['Start Year', 'Start Year Range']},
//         'Subnational unit (province/state)': {'display': 'location'},
//         'Country': {'display': 'location'}
//     },

//     showCapacityTable: false, 

// };
var config = {
    json: './data/africa_energy_tracker_2024-07-02.geojson',
    geometries: ['Point','LineString'],
    center: [30, 0],
    zoomFactor: 1.5,
    statusField: 'status',
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
            values: ['operating','proposed-plus','pre-construction-plus','construction-plus','retired-plus','cancelled','mothballed-plus','shelved'],
            values_labels: ['Operating','Proposed / Announced / Discovered','Pre-construction / Pre-permit / Permitted', 'Construction / In development','Retired / Closed / Decommissioned','Cancelled','Mothballed / Idle / Shut in','Shelved']

        }
    ],
    capacityField: 'scaling-capacity',
    
    capacityDisplayField: 'capacity',
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
    capacityLabel: '',
    capItemLabel:  {
            field: 'tracker-custom',
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
        values: ['tracker-display','name','unit-name', 'owner', 'parent', 'capacity', 'production','status', 'areas', 'start-year'],
        labels: ['Tracker', 'Name','Unit','Owner', 'Parent','Capacity', 'Production','Status','Countries','Start year'],
        clickColumns: ['project'],
        rightAlign: ['unit','capacity','production','start-year'],
        removeLastComma: ['areas'], // TODO change this to ;
        // displayValue: {'tracker-display': "assetLabel"},
        appendValue: {'capacity': "capItemLabel"},
        appendValue: {'production': "prodItemLabel"},
        appendValue: {'capacity-oil': "prodItemLabel"},
        appendValue: {'capacity-gas': "prodItemLabel"},

    },
    searchFields: { 'Project': ['name'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start-year']
    },
    detailView: {
        'name': {'display': 'heading'},
        'production': {'label': 'Production'},
        'capacity': {'label': 'Capacity'},
        'capacity-oil': {'label': 'Production Oil'},
        'capacity-gas': {'label': 'Production Gas'},
        'prod-year-oil': {'label': 'Production year - oil (Million bbl/y)'},
        'prod-year-gas': {'label': 'Production year - gas (Milliion m³/y)'},
        'start-year': {'label': 'Start Year'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'river': {'label': 'River'},
        'tracker-display': {'label': 'Tracker'},
        'subnat': {'display': 'location'},
        'areas': {'display': 'location'}
    }

};