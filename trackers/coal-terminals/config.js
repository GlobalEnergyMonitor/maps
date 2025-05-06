// 'gem-terminal-id', 'gem-unit/phase-id', 'parent-port-name','country/area', 'coal-terminal-name', 'coal-terminal-name-(detail-or-other)',
//     'capacity-(mt)', 'status', 'start-year', 'retired-year', 'location-accuracy',
//      'owner', 'lat', 'lng', 'state/province',
//     'region', 'url'  

var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    csv: 'compilation_output/Coal Terminals-map-file-2025-01-15.csv', 
    /* define the column and associated values for color application */
    linkField: 'gem-terminal-id',
    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'construction': 'blue',
            'proposed': 'green',
            'retired': 'grey',
            'cancelled': 'grey',
            'mothballed': 'grey',
            'shelved': 'grey'
        }
    },

    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values_label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'status',
            values: ['operating','construction','proposed','retired','cancelled', 'shelved','mothballed'],
            primary: true

        }

    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity-(mt)',
    capacityDisplayField: 'capacity_mt_display',

    capacityLabel: '(Mt)',

    /* Labels for describing the assets */
    assetFullLabel: "Coal Terminals",
    assetLabel: 'terminals',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'coal-terminal-name',
    countryField: 'country/area',

    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link. Remember there are append value and display value options*/
    tableHeaders: {
        values: ['coal-terminal-name','coal-terminal-name-(detail-or-other)','owner', 'parent-port-name', 'capacity_mt_display', 'status', 'start-year', 'retired-year', 'region', 'country/area', 'state/province'],
        labels: ['Coal terminal name','Coal terminal name (detail or other)','Owner','Parent port','Capacity (Mt)','Status','Start year', 'Retired year','Region','Country/Area','Subnational unit (province, state)'],
        clickColumns: ['coal-terminal-name'],
        rightAlign: ['capacity_mt_display','start-year','retired-year'],
        toLocaleString: ['capacity'],
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Terminal name': ['coal-terminal-name'], 
        'Companies': ['owner'],
        'Start Year': ['start-year']
    },

    /* define fields and how they are displayed. 
      `'display': 'heading'` displays the field in large type
      `'display': 'range'` will show the minimum and maximum values.
      `'display': 'join'` will join together values with a comma separator
      `'display': 'location'` will show the fields over the detail image
      `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'coal-terminal-name': {'display': 'heading'},
        'coal-terminal-name-(detail-or-other)': {'label': 'Coal Terminal Name (detail or other)'},
        'owner': {'label': 'Owner'},
        'parent-port-name': {'label': 'Parent Port'},
        'start-year': {'label': 'Start Year'},
        'retired-year': {'label': 'Retired Year'},
        'subnational': {'display': 'location'},
        'country/area': {'display': 'location'}
    } 
}
