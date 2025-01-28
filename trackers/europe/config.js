var config = {
    csv: 'compilation_output/europe_2025-01-17-test.csv',
    geometries: ['Point','LineString'],
    center: [8, 30],
    zoomFactor: 1.9,
    img_detail_zoom: 10,
    statusField: 'status-legend',
    statusDisplayField: 'status',
    color: {
        field: 'tracker-custom',
        values: {  
            'GOGPT-hy': 'blue',
            'GOGPT': 'blue',
            'GOGET-oil': 'red',
            'GGIT-hy-eu': 'green',
            'GGIT-eu': 'green',
            "GGIT-hy-import": 'green', 
            'GGIT-import':'green',
            "GGIT-hy-export": 'green',
            'GGIT-export':'green',

        }
    },
    filters: [

        {
            field: 'tracker-custom',
            values: ["GOGPT-hy", "GOGPT",  "GGIT-hy-eu", "GGIT-eu","GGIT-hy-import", "GGIT-hy-export", "GGIT-import", "GGIT-export", "GOGET-oil", ], 
            values_labels: ['hydrogen power units', 'methane gas power units','hydrogen gas pipelines', "methane gas pipelines",'LNG - hydrogen import terminals', 'LNG - hydrogen export terminals','LNG - methane import terminals', 'LNG - methane export terminals', 'gas extraction areas',],
            primary: true
        
        },
        {
            field: 'fuel-filter',
            label: 'Fuels',
            values: ['hy', 'methane'],
            values_labels: ['Hydrogen', 'Methane'],


        },
        {
            field: 'status-legend',
            label: 'Status',
            values: ['operating','proposed-plus','pre-construction-plus','construction-plus','retired-plus','cancelled','mothballed-plus','shelved', 'not-found'],
            values_labels: ['Operating','Proposed/Announced/Discovered','Pre-construction/Pre-permit/Permitted', 'Construction/In development','Retired/Closed/Decommissioned','Cancelled','Mothballed/Idle/Shut in','Shelved', 'Not Found']
        },
        {
            field: 'pci-list',
            label: 'EU Projects of Common Interest (PCI)',
            values: ['5', '6', 'both', 'none',],
            values_labels: ['PCI-5', 'PCI-6', 'PCI-5 & PCI-6', 'Non-PCI'] 

        },
        {
            field: 'maturity',
            label: 'Hydrogen Transition Maturity',
            values: ['y', 'n', 'none'],
            values_labels: ['yes', 'no', 'inapplicable fuel type'] 

        }

    ],
    capacityField: 'scaling-capacity',
    
    // capacityDisplayField: 'capacity-display',
    capacityLabel: {
        field: 'tracker-custom',
        values: {
            'GOGPT-hy': 'MW',
            'GOGPT': 'MW',
            // 'GOGET-oil':	'million boe/y', // remove because they dont have capacity is only relevant for scaling here Scott request
            'GGIT-eu':	'bcm/y of gas', 
            'GGIT-hy-eu': 'bcm/y of gas',
            'GGIT-hy-import': 'MTPA of natural gas',
            'GGIT-hy-export': 'MTPA of natural gas',            
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

    tableHeaders: {
        values: ['name','unit-name', 'owner', 'parent', 'capacity-table', 'units-of-m','status', 'areas', 'start-year', 'prod-gas', 'prod-year-gas', 'fuel', 'tracker-display'],
        labels: ['Name','Unit','Owner', 'Parent','Capacity', '','Status','Country/Area(s)','Start year', 'Production (Million m³/y)', 'Production year (gas)', 'Fuel', 'Facility Type'],
        clickColumns: ['name'],
        rightAlign: ['unit','capacity','prod-gas','start-year','prod-year-gas'], 
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
        'prod-gas': {'label': 'Production (Million m³/y)'},
        'prod-year-gas': {'label': 'Production Year - Gas'},
        'start-year': {'label': 'Start Year'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'river': {'label': 'River'},
        'tracker-display': {'label': 'Type'},
        'areas': {'label': 'Country/Area(s)'},
        'areas-subnat-sat-display': {'display': 'location'}, 
    },

        /* radius associated with minimum/maximum value on map */
    // minRadius: 2,
    // maxRadius: 10,
    minLineWidth: 1,
    maxLineWidth: 3,

    // /* radius to increase min/max to under high zoom */
    // highZoomMinRadius: 4,
    // highZoomMaxRadius: 32,
    // highZoomMinLineWidth: 4,
    // highZoomMaxLineWidth: 32,
    
    // showAllPhases: true

};