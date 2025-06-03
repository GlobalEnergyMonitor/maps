var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    csv: 'compilation_output/Geothermal-map-file-2025-03-18.csv',
    // csv: 'Geothermal_Power_Tracker_May_2024_FINAL_2024-05-14.csv',

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
      and `values_label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'status',
            values: ['operating','construction','pre-construction', 'announced','shelved', 'mothballed','retired','cancelled'],
        }
    ],


    linkField: 'gem-location-id',

    countryField: 'country/area',
    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'unit-capacity-(mw)',
    capacityDisplayField: 'unit-capacity-(mw)',
    capacityLabel: 'Capacity (MW)',

    /* Labels for describing the assets */
    assetFullLabel: "Units",
    assetLabel: 'units',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'project-name',


    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['project-name', 'unit-name','unit-capacity-(mw)', 'technology', 'status', 'start-year', 'owner', 'operator',  'country/area'],
        labels: ['Plant', 'Unit','Capacity (MW)','Technology','Status','Start year', 'Owner', 'Operator', 'Country/Area(s)'],
        clickColumns: ['project-name'],
        rightAlign: ['unit-capacity-(mw)','start-year'],
        toLocaleString: ['unit-capacity-(mw)'],

    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Plant': ['project-name', 'project-name-in-local-language-/-script', 'other-name(s)'], 
        'Companies': ['owner', 'operator', 'operator-name-in-local-language-/-script', 'owner-name-in-local-language-/-script'],
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
        'project-name': {'display': 'heading'},
        'owner': {'label': 'Owner'},
        'operator': {'label': 'Operator'},
        'start-year': {'label': 'Start Year'},
        'state/province': {'display': 'location'},
        'country/area': {'display': 'location'},

    },


    /* Mapbox styling applied to all trackers */
    pointPaint: {
        'circle-opacity':.85
    },
    
    // /* radius associated with minimum/maximum value on map */
    // minRadius: 4,
    // maxRadius: 14,

    // /* radius to increase min/max to under high zoom */
    // highZoomMinRadius: 8,
    // highZoomMaxRadius: 32,


    showCapacityTable: true, 
}
