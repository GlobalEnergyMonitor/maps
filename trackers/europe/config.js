var config = {
    geojson: 'compilation_output/europe_2025-01-31_colab.geojson',
    geometries: ['Point','LineString'],
    center: [8, 30],
    zoomFactor: 1.9,
    img_detail_zoom: 10,
    statusField: 'status-legend',
    statusDisplayField: 'status',
    color: {
        // field: 'fuel-filter',
        // values: {
        //     'hy': 'blue',
        //     'methane': 'green',
        //     'blend': 'red'
        // }
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
            field: 'fuel-filter',
            label: 'Hydrogen',
            values: ['hy', 'blend', 'methane'],
            values_labels: ['100%', 'Blended', 'Methane Only'],
            // values_hover_text: ['hover text for fuels', '', '']
            field_hover_text: 'Hydrogen projects are classified as either planning to blend hydrogen into methane gas or use 100% hydrogen. For the projects that plan to use hydrogen but do not specify a percentage, it is assumed they are blending. Blended projects only appear as hydrogen projects and do not also appear as methane projects, though they will use both fuel types.',
            primary: true
        },
        {
            field: 'tracker-custom',
            label: 'Type',
            values: ["GOGPT", "GGIT","GGIT-import", "GGIT-export","GOGET-oil"], 
            values_labels: ['Gas power units','Gas pipelines', 'LNG import terminals', 'LNG export terminals',  "Gas extraction areas",],
        },
        {
            field: 'status-legend',
            label: 'Status',
            values: ['operating','proposed-plus','pre-construction-plus','construction-plus','retired-plus','cancelled','mothballed-plus','shelved', 'not-found'],
            values_labels: ['Operating','Proposed/Announced/Discovered','Pre-construction', 'Construction/In development','Retired/Closed/Decommissioned','Cancelled','Mothballed/Idle/Shut in','Shelved', 'Not Found']
        },
        {
            field: 'maturity', 
            label: 'Progress Demonstrated (Hydrogen Only)', // info button explaining what it means
            values: ['y', 'n', 'none'],
            values_labels: ['yes', 'no', 'n/a'],
            // values_hover_text: ['hover tesct for fuels', '', '']
            field_hover_text: 'GEM assesses whether hydrogen projects have met criteria (specific to each infrastructure type) demonstrating progress toward completion, since many hydrogen projects lack core details or commitments from stakeholders. For more information on these criteria, see the <a href="https://globalenergymonitor.org/projects/europe-gas-tracker/methodology/">EGT methodology page</a>'

        },
        {
            field: 'pci-list',
            label: 'EU Projects of Common Interest (PCI)',
            values: ['5', '6', 'both', 'none',], // can we join both into 5 and 6??? can we merge? both should show up in pci 5 and pci 6 separately
            values_labels: ['PCI-5 only', 'PCI-6 only', 'PCI 5 & PCI 6 Overlap', 'Non-PCI'] 

        },

    ],
    capacityField: 'scaling-capacity',
    
    capacityLabel: {
        field: 'tracker-custom',
        values: {
            'GOGPT': 'MW',
            'GOGET-oil': '',	//'million boe/y', // remove because they dont have capacity is only relevant for scaling here Scott request
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
        values: ['name','unit-name', 'owner', 'parent', 'capacity-table', 'units-of-m','status', 'areas', 'start-year', 'prod-gas', 'prod-year-gas','tracker-display'],
        labels: ['Name','Unit','Owner', 'Parent','Capacity', 'units','Status','Country/Area(s)','Start year', 'Production (Million m³/y)', 'Production year (gas)', 'Type'],
        clickColumns: ['name'],
        rightAlign: ['capacity-table','prod-gas','start-year','prod-year-gas'], 
        removeLastComma: ['areas'], 

    },
    searchFields: { 'Project': ['name', 'other-name', 'local-name'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start-year'],
        // 'Infrastructure Type': ['tracker-display'],
        // 'Status': ['status'],
        // 'Province/State': ['subnat']
    },
    detailView: {
        'name': {'display': 'heading'},
        'prod-gas': {'label': 'Production (Million m³/y)'},
        'prod-year-gas': {'label': 'Production Year - Gas'},
        'start-year': {'label': 'Start Year'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        // 'river': {'label': 'River'},
        // 'tracker-display': {'label': 'Type'},
        'areas': {'label': 'Country/Area(s)'},
        'areas-subnat-sat-display': {'display': 'location'}, 
    },
    showToolTip: true,

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