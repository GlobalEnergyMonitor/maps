var config = {
    csv: 'compilation_output/Iron & Steel-map-file-2025-03-18.csv',

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
    // {'Electric_arc_furnaces', 'DRI_furnaces', 'Open_hearth_furnaces', 'Basic_oxygen_furnaces', 'Blast_furnaces'}
    color: { 
        field: 'tab-type', // prod type
        values: {
            // 'BOF': 'red',
            // 'EAF': 'blue',
            // 'BOF; EAF': 'green',
            // 'BF': 'orange',
            // 'DRI': 'dark grey',
            // 'integrated (bf)': 'grey',
            // 'integrated (dri)': 'grey',
            // 'integrated (bf and dri)': 'grey',
            // 'Steel other/unspecified': 'grey',
            // 'Iron other/unspecified': 'grey'
            'Electric_arc_furnaces': 'red',
            'Basic_oxygen_furnaces': 'blue',
            'Open_hearth_furnaces': 'green',
            'Blast_furnaces': 'orange',
            'DRI_furnaces': 'yellow',
            // 'Unknown': 'grey',

        }
    },
    filters: [
        {
            field: 'tab-type',
            /* values need to be specified for ordering */
            // values: ['BOF','EAF','BOF; EAF','BF','DRI','integrated (bf)', 'integrated (dri)', 'integrated (bf and dri)',
            //     'Steel other/unspecified','Iron other/unspecified',],
            // values_labels: ['Oxygen','Electric','Electric, Oxygen','Blast Furnace','Ironmaking (BF)', 'Ironmaking (DRI)', 
            //     'Integrated (BF)',  'Integrated (DRI)', 'Integrated (BF and DRI)','Steelmaking (other)', 'Ironmaking (other)',]
            values: ['Electric_arc_furnaces', 'Basic_oxygen_furnaces', 'Open_hearth_furnaces', 'Blast_furnaces', 'DRI_furnaces',],
            values_labels: ['Electric arc furnaces', 'Basic oxygen furnaces', 'Open hearth furnaces', 'Blast furnaces', 'DRI furnaces'],
        },
        {
            field: 'status',
            label: 'Status',
            values: ['operating','announced', 'construction','operating_pre-retirement','cancelled', 'retired','mothballed_pre-retirement','mothballed'],
            values_labels: ['Operating','Announced', 'Construction','Operating Pre-Retirement', 'Cancelled', 'Retired', 'Mothballed Pre-Retirement', 'Mothballed',]

        }
    ],

    linkField: 'plant-id',

    urlField: 'gem-wiki-page',

    countryField: 'country/area',
    capacityField: 'current-capacity-(ttpa)', // For steel this will need to be at unit level for steel and iron according to prod_type
    capacityDisplayField: 'current-capacity-(ttpa)',

    capacityLabel: 'ttpa', //'TTPA', 
    // context_layers: [
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
        values: ['plant-name-(english)','unit-name','owner', 'parent', 'current-capacity-(ttpa)', 'status_display', 'start-date','tab-type-display','main-production-equipment', 'subnational-unit-(province/state)','country/area'],
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
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'start-date': {'label': 'Start date'},
        'main-production-equipment': {'label': 'Main Production Equipment'},
        'steel-products': {'label': 'Steel Products'},
        'most-recent-relining': {'label': 'Most Recent Relining'},
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