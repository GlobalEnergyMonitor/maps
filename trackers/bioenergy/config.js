var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    // csv: 'data.csv',

    csv: 'compilation_output/GBPT-map-file-2024-09-23.csv',

    /* zoom level to set map when viewing all phases */
    phasesZoom: 10,
    /* initial load zoom multiplier */
    // zoomFactor: 2,
    center: [0, 0],
    countryField: 'country/area',

    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'pre-construction': 'green',
            'construction': 'blue',
            'retired': 'grey',
            'cancelled': 'grey',
            'shelved': 'grey',
            'mothballed': 'grey',
            'announced': 'green'
        }
    },


    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values-label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'status',
            values: ['operating','construction','pre-construction', 'announced','shelved','mothballed','retired','cancelled'],
        }
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity-(mw)',
    capacityDisplayField: 'capacity-(mw)',
    capacityLabel: 'Capacity (MW)',

    /* Labels for describing the assets */
    assetFullLabel: "Bioenergy Power Units",
    assetLabel: 'units',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'project-name',


    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['project-name', 'capacity-(mw)', 'status', 'owner(s)', 'operator(s)',  'country/area', 'fuel'],
        labels: ['Project name','Capacity (MW)','Status','Owner', 'Operator', 'Country/Area(s)','Fuel',],
        clickColumns: ['project-name'],
        rightAlign: ['capacity-(mw)'],
        toLocaleString: ['capacity-(mw)'],
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['project-name'], 
        'Companies': ['owner(s)', 'operator(s)'],
        'Status': ['status'], 

    },

    /* define fields and how they are displayed. 
      `'display': 'heading'` displays the field in large type
      `'display': 'range'` will show the minimum and maximum values.
      `'display': 'join'` will join together values with a comma separator
      `'display': 'location'` will show the fields over the detail image
      `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'project-name': {'display': 'heading'},
        // 'status': {'label': 'Status'}, # handled in summary of capacity and status section
        // 'capacity-(mw)': {'label': 'Capacity (MW)'},
        'owner(s)': {'label': 'Owner'},
        'operator(s)': {'label': 'Operator'},
        'country/area' : {'label': 'Country/Area(s)'},
        'location-accuracy': {'label': 'Location Accuracy'},
        'state/province': {'display': 'location'},
        'country': {'display': 'location'},
        // 'areas-subnat-sat-display': {'display': 'location'}

    },
    showCapacityTable: true, 
}
