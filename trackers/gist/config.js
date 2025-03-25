var config = {
    csv: 'compilation_output/Iron & Steel-map-file-2025-03-25.csv', // Saying can't be found? TODO march 24th

    colors: {
        'light red': '#f28b82',
        'red': '#c74a48',
        'light blue': '#5dade2',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
        'light green': '#66c26e',
        'light grey': '#e0e0e0',
        'grey': '#8f8f8e',
        'orange': '#FF8C00',
        'yellow': '#f3ff00',
        'black': '#000000',
        'purple': '#9370db'
    },
    // {'cancelled', 'operating', 'mothballed', 'announced', 'retired', 'mothballed pre-retirement', 'construction', 'operating pre-retirement'}
    // {'Electric-arc-furnaces', 'DRI-furnaces', 'Open-hearth-furnaces', 'Basic-oxygen-furnaces', 'Blast-furnaces'}
    color: { 
        field: 'prod-method-tier', // prod type
        values: {
            'Electric': 'light green',
            'ElectricOxygen': 'blue',
            'Oxygen': 'orange',
            'IronmakingBF': 'light red',
            'IronmakingDRI': 'light blue',
            'IntegratedBF': 'red',
            'IntegratedBFandDRI':  'purple',
            'IntegratedDRI': 'green',
            'Integratedunknown': 'grey',
            'Steelotherunspecified': 'light grey',
            'Ironotherunspecified': 'light grey'
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
                    'IronmakingDRI', 'IntegratedDRI', 'IntegratedBF','Integratedunknown','Steelotherunspecified','Ironotherunspecified'],


            values_labels: ['Electric','Electric, oxygen','Oxygen','Ironmaking (BF)', 'Integrated (BF and DRI)', 'Ironmaking (DRI)',
                    'Integrated (DRI)', 'Integrated (BF)', 'Integrated unknown', 'Steel other/unspecified', 'Iron other/unspecified'],
            // values: ['Electric-arc-furnaces', 'Basic-oxygen-furnaces', 'Open-hearth-furnaces', 'Blast-furnaces', 'DRI-furnaces',],
            // values-labels: ['Electric arc furnaces', 'Basic oxygen furnaces', 'Open hearth furnaces', 'Blast furnaces', 'DRI furnaces'],
            primary: true
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
    statusField: 'plant-status',
    statusDisplayField: 'status_display',
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
    assetLabel: 'plants',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'plant-name-(english)',

    
    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['plant-name-(english)','owner', 'parent', 'status_display', 'start-date','prod-method-tier-display','main-production-equipment', 'subnational-unit-(province/state)','country/area'],
        labels: ['Plant','Owner','Parent', 'Plant Status', 'Start date', 'Production Method','Main Production Equipment','Subnational Unit','Country/Area'],
        clickColumns: ['plant-name-(english)'],
        rightAlign: []
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Plant': ['plant-name-(english)', 'plant-name-(other-language)', 'other-plant-names-(english)', 'other-plant-names-(other-language)'], 
        'Companies': ['owner', 'parent', 'owner-(other-language)'],
        'Production Method': ['prod-method-tier-display', 'prod-method-tier','main-production-equipment']
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
        'coordinate-accuracy': {'label': 'Coordinate Accuracy'},
        'operating-nominal-eaf-steel-capacity-(ttpa)': {'label': 'Operating nominal EAF steel capacity (ttpa)'},
        'construction-nominal-eaf-steel-capacity-(ttpa)': {'label': 'Construction nominal EAF steel capacity (ttpa)'},
        'operating-nominal-bof-steel-capacity-(ttpa)': {'label': 'Operating nominal BOF steel capacity (ttpa)'},
        'operating-nominal-bf-capacity-(ttpa)': {'label': 'Operating nominal BF capacity (ttpa)'},
        'announced-nominal-eaf-steel-capacity-(ttpa)': {'label': 'Announced nominal EAF steel capacity (ttpa)'},
        'announced-nominal-dri-capacity-(ttpa)': {'label': 'Announced nominal DRI capacity (ttpa)'},
        'mothballed-nominal-bf-capacity-(ttpa)': {'label': 'Mothballed nominal BF capacity (ttpa)'},
        'operating-other-unspecified-steel-capacity-(ttpa)': {'label': 'Operating other/unspecified steel capacity (ttpa)'},
        'mothballed-nominal-eaf-steel-capacity-(ttpa)': {'label': 'Mothballed nominal EAF steel capacity (ttpa)'},
        'mothballed-nominal-dri-capacity-(ttpa)': {'label': 'Mothballed nominal DRI capacity (ttpa)'},
        'operating-nominal-dri-capacity-(ttpa)': {'label': 'Operating nominal DRI capacity (ttpa)'},
        'announced-other-unspecified-steel-capacity-(ttpa)': {'label': 'Announced other/unspecified steel capacity (ttpa)'},
        'construction-other-unspecified-steel-capacity-(ttpa)': {'label': 'Construction other/unspecified steel capacity (ttpa)'},
        'construction-nominal-dri-capacity-(ttpa)': {'label': 'Construction nominal DRI capacity (ttpa)'},
        'operating-pre-retirement-nominal-bof-steel-capacity-(ttpa)': {'label': 'Operating pre-retirement nominal BOF steel capacity (ttpa)'},
        'announced-nominal-bf-capacity-(ttpa)': {'label': 'Announced nominal BF capacity (ttpa)'},
        'construction-nominal-bof-steel-capacity-(ttpa)': {'label': 'Construction nominal BOF steel capacity (ttpa)'},
        'construction-nominal-bf-capacity-(ttpa)': {'label': 'Construction nominal BF capacity (ttpa)'},
        'announced-nominal-bof-steel-capacity-(ttpa)': {'label': 'Announced nominal BOF steel capacity (ttpa)'},
        'cancelled-nominal-eaf-steel-capacity-(ttpa)': {'label': 'Cancelled nominal EAF steel capacity (ttpa)'},
        'retired-nominal-bf-capacity-(ttpa)': {'label': 'Retired nominal BF capacity (ttpa)'},
        'mothballed-nominal-bof-steel-capacity-(ttpa)': {'label': 'Mothballed nominal BOF steel capacity (ttpa)'},
        'cancelled-nominal-dri-capacity-(ttpa)': {'label': 'Cancelled nominal DRI capacity (ttpa)'},
        'retired-nominal-bof-steel-capacity-(ttpa)': {'label': 'Retired nominal BOF steel capacity (ttpa)'},
        'operating-pre-retirement-nominal-eaf-steel-capacity-(ttpa)': {'label': 'Operating pre-retirement nominal EAF steel capacity (ttpa)'},
        'retired-nominal-eaf-steel-capacity-(ttpa)': {'label': 'Retired nominal EAF steel capacity (ttpa)'},
        'cancelled-other-unspecified-steel-capacity-(ttpa)': {'label': 'Cancelled other/unspecified steel capacity (ttpa)'},
        'retired-nominal-ohf-steel-capacity-(ttpa)': {'label': 'Retired nominal OHF steel capacity (ttpa)'},
        'mothballed-other-unspecified-steel-capacity-(ttpa)': {'label': 'Mothballed other/unspecified steel capacity (ttpa)'},
        'operating-pre-retirement-other-unspecified-steel-capacity-(ttpa)': {'label': 'Operating pre-retirement other/unspecified steel capacity (ttpa)'},
        'operating-nominal-ohf-steel-capacity-(ttpa)': {'label': 'Operating nominal OHF steel capacity (ttpa)'},
        'mothballed-nominal-ohf-steel-capacity-(ttpa)': {'label': 'Mothballed nominal OHF steel capacity (ttpa)'},
        'subnational-unit-(province/state)': {'display': 'location'},
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