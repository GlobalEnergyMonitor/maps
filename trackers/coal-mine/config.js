var config = {
    // csv: 'coal-mine.csv', (Mikel's file)
    csv: 'data.csv',

    colors: {
        'red': '#c74a48',
        'light blue greeninfo': '#74add1',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
        'light grey greeninfo': '#ccc',
        'grey': '#8f8f8e',
        'dark grey': '#4B4B4B',
        'orange': '#FF8C00',
        'yellow': '#f3ff00'
    },

    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
        field: 'status',
        values: {
            'operating': 'red',
            'proposed': 'blue',
            'cancelled': 'green',
            'retired': 'orange',
            'shelved': 'dark grey',
            'mothballed': 'grey'
        }
    },
    filters: [
        {
            field: 'status',
            /* values need to be specified for ordering */
            values: ['operating','proposed','cancelled','retired','shelved','mothballed'],
            primary: true
        },
        {
            field: 'mine-type',
            label: 'Mine Type',
            values: ['surface','underground','underground_and_surface', 'unknown'],
            values_labels: ['Surface','Underground','Underground & Surface', 'Unknown']

        },
        {
            field: 'coal-grade',
            label: 'Coal Grade',
            values: ['thermal','met','thermal_and_met','unknown'],
            /* value_labels must match order/number in values */
            values_labels: ['Thermal','Met','Thermal & Met','Unknown']
        }
    ],
    capacityField: 'circle_value',
    // capacityDisplayField: 'circle_value',
    // capacityLabel: '(Mt)', # to accomodate new feature Mikel put in, 
    capacityLabel: '',
    // context_layers: [
    //     {
    //         field: 'coalfield',
    //         'label': 'Coal Fields',
    //         'tileset': '[mapbox tile url]',
    //         paint: {}
    //     }
    // ],


    /* Labels for describing the assets */
    assetFullLabel: "Coal Mine Projects",
    assetLabel: 'projects',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'project',

    
    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['project','owner', 'parent', 'capacity', 'production', 'status', 'workforce', 'coalfield', 'country', 'region', 'opening_year', 'closing_year'],
        labels: ['Project','Owner','Parent','Capacity (Mt)', 'Production (Mt)', 'Status', 'Workforce', 'Coal Field', 'Country', 'Region','Opening year', 'Closing year'],
        clickColumns: ['project'],
        rightAlign: ['production','capacity','opening_year, closing_year']
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['project'], 
        'Companies': ['owner', 'parent'],
        'Opening Year': ['opening_year']
    },

    /* define fields and how they are displayed. 
        `'display': 'heading'` displays the field in large type
        `'display': 'range'` will show the minimum and maximum values.
        `'display': 'join'` will join together values with a comma separator
        `'display': 'location'` will show the fields over the detail image
        `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'project': {'display': 'heading'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'capacity': {'label': 'Capacity (Mt)'},
        'production': { 'label': 'Production (Mt)' },
        'workforce': {'label': 'Estimated Workforce'},
        'opening_year': {'label': 'Opening Year'},
        'coalfield': {'display': 'location'},
        'country': {'display': 'location'}
    }, 
    showCapacityTable: false,
    showMaxCapacity: false,
    
}
