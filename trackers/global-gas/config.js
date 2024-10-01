var config = {
    json: 'compilation_output/global_gas_2024-09-30.geojson',
    geometries: ['Point','LineString'],
    center: [8, 30],
    zoomFactor: 1.9,
    img_detail_zoom: 10,
    statusField: 'status-legend',
    statusDisplayField: 'status',
    // linkField: 'id',
    color: {
        field: 'tracker-acro',
        values: {
            'GOGPT': 'blue',
            'GOGET': 'red',
            'GGIT': 'green',
            'GGIT-lng':'green',

        }
    },
    //filter values should have no spaces
    filters: [
        {
            field: 'tracker-acro',
            values: ["GOGPT",  "GGIT", "GGIT-lng", "GOGET", ], 
            values_labels: ['oil&gas units', 'gas pipelines', 'LNG terminals', 'oil&gas extraction areas',],
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

    // capItemLabel:  {
    //         field: 'tracker-custom',
    //         values: {
    //             'GCPT': 'MW',
    //             'GOGPT': 'MW',
    //             'GBPT':	'MW',
    //             'GNPT':	'MW',
    //             'GSPT':	'MW',
    //             'GWPT':	'MW',
    //             'GHPT':	'MW',
    //             'GGPT':	'MW',
    //             // 'GOGET - oil':	'million boe/y',
    //             // 'GOGET - gas':	'million m³/y',
    //             'GOIT': 'boe/d',
    //             'GGIT':	'Bcm/y of natural gas',
    //             'GGIT - import': 'MTPA of natural gas',
    //             'GGIT - export': 'MTPA of natural gas',
    //             // 'GCMT':	'million tonnes coal/y',
    //             'GCTT':	'million tonnes coal/y'
    //         }
    //     },
    // prodItemLabel: {
    //     field: 'tracker-custom',
    //         values: {
    //             'GOGET - oil':	'million boe/y',
    //             'GOGET - gas':	'million m³/y',
    //             'GCMT':	'million tonnes coal/y'
    //         }
    // },
    //productionLabel NEED a productionLabel
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
//    linkField: 'id',  

    countryFile: 'countries.js',
    allCountrySelect: true, // TODO bug when clicking Africa nothing gets selected but clicking all it does 
    countryField: 'areas',
    //if multicountry, always end values with a comma
    multiCountry: true,

    tableHeaders: {
        values: ['tracker-display','name','unit-name', 'owner', 'parent', 'capacity-table', 'status', 'areas', 'start-year', 'prod-oil', 'prod-year-oil', 'prod-gas', 'prod-year-gas'],
        labels: ['Type', 'Name','Unit','Owner', 'Parent','Capacity (MW)', 'Status','Country/Area(s)','Start year', 'Production (million bbl/y)','Production year (oil)', 'Production (Million m³/y)', 'Production year (gas)'],
        
        // 'capacity-oil', 'capacity-gas'
        // 'Production oil (Million bbl/y)', 'Production Gas (Milliion m³/y)'
        clickColumns: ['project'],
        rightAlign: ['unit','capacity','prod-oil', 'prod-gas','start-year', 'prod-year-oil', 'prod-year-gas'], 
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
        'Infrastructure Type': ['tracker-display'],
        'Status': ['status'],
        'Province/State': ['subnat']
    },
    detailView: {
        'name': {'display': 'heading'},
        // 'status': {'lable': 'Status'}, // THIS NEEDS TO BE FIXED it breaks the click option saying not included
        // 'prod-gcmt': {'label': 'Production (MTPA)'}, // if its GCMT or GOGET should be 
        'capacity-details': {'label': 'Project Level Capacity'}, // interim until summary capacity can be customized by tracker
        'prod-oil': {'label': 'Production (Million bbl/y)'},
        'prod-gas': {'label': 'Production (Million m³/y)'},
        'prod-year-oil': {'label': 'Production Year - Oil'},
        'prod-year-gas': {'label': 'Production Year - Gas'},
        'start-year': {'label': 'Start Year'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'river': {'label': 'River'},
        'tracker-display': {'label': 'Type'},
        'areas': {'label': 'Country/Area(s)'},
        'areas-subnat-sat-display': {'display': 'location'}, 
        // 'areas-display': {'display': 'location'} // TODO pull out first one only if ; in it

    },
/* Mapbox styling applied to all trackers */
pointPaint: {
    'circle-opacity':.45
},
linePaint: {
    'line-opacity':.65
},
lineLayout: {
    'line-cap': 'round', 
    'line-join': 'round'
},

/* radius associated with minimum/maximum value on map */
minRadius: 3,
maxRadius: 40,
minLineWidth: 1,
maxLineWidth: 10,

/* radius to increase min/max to under high zoom */
highZoomMinRadius: 30,
highZoomMaxRadius: 50,
highZoomMinLineWidth: 4,
highZoomMaxLineWidth: 32,

/* zoom level to set map when viewing all phases */
phasesZoom: 8,

/* initial load zoom multiplier */
zoomFactor: 1.25,

hitArea: 10, 

};