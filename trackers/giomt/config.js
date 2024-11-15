var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    // csv: 'data.csv',
    geometries: ['Point'],
    csv: 'output/data-2024-11-15.csv',
    /* zoom level to set map when viewing all phases */
    phasesZoom: 10,
    /* initial load zoom multiplier */
    // zoomFactor: 2,
    center: [0, 0],

    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'proposed': 'green',
            'retired': 'blue',
            'unknown': 'grey',
            'cancelled': 'grey',
            'shelved': 'grey',
            'mothballed': 'grey',
        }
    },


    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values-label` (an array matching elements in `values`)
      */
    filters: [
    {
        field: 'status',
        label: 'Operating Status',
        values: ['operating','proposed','retired','cancelled','mothballed','shelved', 'unknown'],
        values_labels: ['Operating','Proposed', 'Retired','Cancelled','Mothballed','Shelved', 'Unknown']

    },
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'design-capacity-(ttpa)',
    capacityDisplayField: 'design-capacity-(ttpa)',
    capacityLabel: 'Design Capacity (ttpa)',

    /* Labels for describing the assets */
    assetFullLabel: "Iron Ore assets",
    assetLabel: 'assets',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'name-(english)',

    countryField: 'country/area',
    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['name-(english)', 'name-(other-language)','design-capacity-(ttpa)', 'status', 'owner', 'parent',  'country/area'],
        labels: ['Asset name', 'Asset Name (other lang)','Design Capacity (ttpa)','Status','Owner', 'Parent', 'Country/Area(s)'],
        clickColumns: ['name-(english)'],
        rightAlign: ['design-capacity-(ttpa)']
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Asset': ['name-(english)', 'name-(other-language)'], 
        'Companies': ['owner', 'parent'],

    },
    capacityLabel: 'ttpa',
    /* define fields and how they are displayed. 
      `'display': 'heading'` displays the field in large type
      `'display': 'range'` will show the minimum and maximum values.
      `'display': 'join'` will join together values with a comma separator
      `'display': 'location'` will show the fields over the detail image
      `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'name-(english)': {'display': 'heading'},
        'status': {'label': 'Status'},
        'design-capacity-(ttpa)': {'label': 'Design Capacity (ttpa)'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'country/area' : {'label': 'Country/Area(s)'},
        'coordinate-accuracy': {'label': 'Location Accuracy'},
        'subnational-unit': {'display': 'location'},
        'country/area': {'display': 'location'},
        // 'areas-subnat-sat-display': {'display': 'location'}

    },
    // showCapacityTable: true, 
}
