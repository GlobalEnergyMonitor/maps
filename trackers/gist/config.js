var config = {
    csv: 'compilation_output/Iron & Steel-map-file-2025-03-24.csv', // Saying can't be found? TODO march 24th

    colors: {
        'red': '#c74a48',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
        'grey': '#8f8f8e',
        'orange': '#FF8C00',
        'yellow': '#f3ff00',
        'black': '#000000'
    },
    // {'cancelled', 'operating', 'mothballed', 'announced', 'retired', 'mothballed pre-retirement', 'construction', 'operating pre-retirement'}
    // {'Electric-arc-furnaces', 'DRI-furnaces', 'Open-hearth-furnaces', 'Basic-oxygen-furnaces', 'Blast-furnaces'}
    color: { 
        field: 'prod-method-tier', // prod type
        values: {
            'Electric': 'blue',
            'Electricoxygen': 'green',
            'Oxygen': 'orange',
            'IronmakingBF': 'red',
            'IronmakingDRI': 'blue',
            'IntegratedBF': 'red',
            'IntegratedBFandDRI':  'blue',//'purple',
            'IntegratedDRI': 'green',
            'Steelotherunspecified': 'grey',
            'Ironotherunspecified': 'grey'
            // "electric - light green
            // electric, oxygen - dark blue
            // oxygen - orange
            // ironmaking (BF) - light red
            // ironmaking (DRI) - light blue
            // integrated (BF) - dark red
            // integrated (BF and DRI) - purple
            // integrated (DRI) - dark green
            // integrated (unknown) - dark gray
            // Steel other/ unspecified - light gray
            // Iron other/ unspecified - light gray"
        }
    },
    filters: [
        {
            field: 'prod-method-tier',
            /* values need to be specified for ordering */
            // values: ['BOF','EAF','BOF; EAF','BF','DRI','integrated (bf)', 'integrated (dri)', 'integrated (bf and dri)',
            //     'Steel other/unspecified','Iron other/unspecified',]
            values: ['Electric', 'ElectricOxygen','Oxygen', 'IronmakingBF', 'IntegratedBFandDRI', 
                    'IronmakingDRI', 'IntegratedDRI', 'IntegratedBF','Steelotherunspecified','Ironotherunspecified', 'Integratedunknown'],


            values_labels: ['Electric','Electric, oxygen','Oxygen','Ironmaking (BF)', 'Integrated (BF and DRI)', 'Ironmaking (DRI)',
                    'Integrated (DRI)', 'Integrated (BF)', 'Steel other/unspecified', 'Iron other/unspecified', 'Integrated unknown']
            // values: ['Electric-arc-furnaces', 'Basic-oxygen-furnaces', 'Open-hearth-furnaces', 'Blast-furnaces', 'DRI-furnaces',],
            // values-labels: ['Electric arc furnaces', 'Basic oxygen furnaces', 'Open hearth furnaces', 'Blast furnaces', 'DRI furnaces'],
        },
        {
            field: 'plant-status',
            label: 'Status',
            values: ['operating','announced', 'construction','operating-pre-retirement','cancelled', 'retired','mothballed-pre-retirement','mothballed'],
            values_labels: ['Operating','Announced', 'Construction','Operating Pre-Retirement', 'Cancelled', 'Retired', 'Mothballed Pre-Retirement', 'Mothballed',]

        }
    ],

    linkField: 'plant-id',

    urlField: 'gem-wiki-page',
    statusField: 'status_display',
    countryField: 'country/area',
    capacityField: 'scaling-cap', // change to scaling col once added
    // capacityDisplayField: 'current-capacity-(ttpa)',

    capacityLabel: '', //'TTPA', 
    // context-layers: [
    //     {
    //         field: 'coalfield',
    //         'label': 'Coal Fields',
    //         'tileset': '[mapbox tile url]',
    //         paint: {}
    //     }
    // ],


    /* Labels for describing the assets */
    assetFullLabel: "Iron and Steel Plants",
    assetLabel: 'units',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'plant-name-(english)',

    
    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['plant-name-(english)','unit-name','owner', 'parent', 'current-capacity-(ttpa)', 'status-display', 'start-date','tab-type-display','main-production-equipment', 'subnational-unit-(province/state)','country/area'],
        labels: ['Plant','Unit','Owner','Parent','Current Capacity (ttpa)', 'Status', 'Start date', 'Production Method','Main Production Equipment', 'Subnational Unit','Country/Area'],
        clickColumns: ['plant-name-(english)'],
        rightAlign: ['current-capacity-(ttpa)',]
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Plant': ['plant-name-(english)', 'plant-name-(other-language)', 'other-plant-names-(english)', 'other-plant-names-(other-language)'], 
        'Companies': ['owner', 'parent', 'owner-(other-language) '],
        'Production Method': ['tab-type-display', 'main-production-equipment']
    },

    /* define fields and how they are displayed. 
        `'display': 'heading'` displays the field in large type
        `'display': 'range'` will show the minimum and maximum values.
        `'display': 'join'` will join together values with a comma separator
        `'display': 'location'` will show the fields over the detail image
        `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'plant-name-(english)': {'display': 'heading'},
        'prod-method-tier-display': {'label': 'Production Method'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'start-date': {'label': 'Start date'},
        'main-production-equipment': {'label': 'Main Production Equipment'},
        'steel-products': {'label': 'Steel Products'},
        'coordinate-accuracy': {'label': 'Coordinate Accuracy'},
        'subnational-unit-(province/state)':{'display': 'location'},
        'country/area': {'display': 'location'}
    }, 

    /* Mapbox styling applied to all trackers */
    pointPaint: {
        'circle-opacity':.85
    },
    
    /* radius associated with minimum/maximum value on map */
    minRadius: 3,
    maxRadius: 7,

    /* radius to increase min/max to under high zoom */
    highZoomMinRadius: 5,
    highZoomMaxRadius: 22,

    showMaxCapacity: true,
    
}