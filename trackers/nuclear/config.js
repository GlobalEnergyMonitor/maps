var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    // csv: 'data.csv',
    csv: 'data/data-2024-07-17.csv',
    /* zoom level to set map when viewing all phases */
    phasesZoom: 10,
    /* initial load zoom multiplier */
    // zoomFactor: 2,
    center: [0, 0],

    colors: {
        'red greeninfo': '#c00',
        'light blue greeninfo': '#74add1',
        'blue greeninfo': '#4575b4',
        'green greeninfo': '#7dd47d',
        'light grey greeninfo': '#ccc',
        'grey greeninfo': '#666',
        'orange greeninfo': '#fd7e14',
        'yellow greeninfo': '#f3ff00'
    },

    /* define the column and associated values for color application */
    color: {
        field: 'status',
        values: {
            'operating': 'green greeninfo',
            'construction': 'yellow greeninfo',
            'pre-construction': 'orange greeninfo',
            'announced': 'red greeninfo',
            'mothballed': 'blue greeninfo',
            'shelved': 'light blue greeninfo',
            'retired': 'grey greeninfo',
            'cancelled': 'light grey greeninfo',
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
    assetFullLabel: "Nuclear Power Plant Units",
    assetLabel: 'units',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'project-name',


    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['project-name', 'capacity-(mw)', 'reactor-type', 'status', 'owner', 'operator',  'country'],
        labels: ['Project name','Capacity (MW)','Reactor','Status','Owner', 'Operator', 'Country/Area(s)'],
        clickColumns: ['project-name'],
        rightAlign: ['capacity-(mw)'],
        toLocaleString: ['capacity-(mw)'],

    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['project-name'], 
        'Companies': ['owner', 'operator'],

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
        // 'status': {'label': 'Status'},
        // 'capacity-(mw)': {'label': 'Capacity (MW)'},
        'owner': {'label': 'Owner'},
        'operator': {'label': 'Operator'},
        'country' : {'label': 'Country/Area(s)'},
        'location-accuracy': {'label': 'Location Accuracy'},
        // 'state/province': {'display': 'location'},
        // 'country': {'display': 'location'},
        'areas-subnat-sat-display': {'display': 'location'}

    },

    /* radius associated with minimum/maximum value on map */
    // minRadius: 2,
    // maxRadius: 100,
    // minLineWidth: 1,
    // maxLineWidth: 10000,

    // /* radius to increase min/max to under high zoom */
    // highZoomMinRadius: 4,
    // highZoomMaxRadius: 100,
    // highZoomMinLineWidth: 4,
    // highZoomMaxLineWidth: 32,
    
}
