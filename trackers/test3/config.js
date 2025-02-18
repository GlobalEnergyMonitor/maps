var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    // csv: 'data.csv',
    csv: 'data.csv',

    colors: {
        'red greeninfo': '#c00',
        'light blue greeninfo': '#1e90ff',
        'blue greeninfo': '#4575b4',
        'green greeninfo': '#00b200',
        'light grey greeninfo': '#b0b0b0',
        'grey greeninfo': '#666',
        'orange greeninfo': '#fd7e14',
        'yellow greeninfo': '#ffd700'
    },

    /* define the column and associated values for color application */
    color: {
        field: 'Status',
        values: {
            'operating': 'green greeninfo',
            'construction': 'yellow greeninfo',
            'pre-construction': 'orange greeninfo',
            'announced': 'red greeninfo',
            'mothballed': 'blue greeninfo',
            'shelved': 'blue greeninfo',
            'retired': 'grey greeninfo',
            'cancelled': 'grey greeninfo',

        }
    },

    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values_label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'Status',
            values: ['operating', 'announced', 'construction', 'pre-construction', 'mothballed', 'shelved', 'cancelled', 'retired'],
            values_labels: ['operating', 'announced', 'construction', 'pre-construction', 'mothballed', 'shelved',  'cancelled', 'retired'],
            primary: true
        },
        {
            field: 'Technology-Type',
            label: 'Technology Type',
            values: ['Solar Thermal', 'PV', 'Assumed PV'],
            values_labels: ['Solar Thermal', 'PV', 'Assumed PV']

        },
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'Capacity (MW)',
    capacityDisplayField: 'Capacity (MW)',
    capacityLabel: 'Capacity (MW)',

    /* Labels for describing the assets */
    assetFullLabel: "Solar photovoltaic farm phases",
    assetLabel: 'phase',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'Project Name',
    nameField: 'Project Name',
    linkField: 'Wiki URL',
    urlField: 'Wiki URL',
    countryField: 'Country',


    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['Project Name', 'Project Name in Local Language / Script', 'Phase Name', 'Capacity (MW)', 'Status', 'Technology-Type', 'Start year', 'Owner', 'Operator', 'Location accuracy', 'State/Province', 'Country'],
        labels: ['Project', 'Project Name in Local Language / Script', 'Phase','Capacity (MW)', 'Status', 'Technology Type', 'Start year', 'Owner', 'Operator','Location Accuracy', 'State/Province', 'Country/Area'],
        clickColumns: ['Project Name'],
        rightAlign: ['Capacity (MW)','Start year']
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['Project Name'], 
        'Companies': ['Owner', 'Operator'],
        'Start Year': ['Start year']
    },

    /* define fields and how they are displayed. 
      `'display': 'heading'` displays the field in large type
      `'display': 'range'` will show the minimum and maximum values.
      `'display': 'join'` will join together values with a comma separator
      `'display': 'location'` will show the fields over the detail image
      `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'Project Name': {'display': 'heading'},
        'Status': {'label': 'Status'},
        'Capacity (MW)': {'label': 'Capacity (MW)'},
        'Owner': {'label': 'Owner'},
        'Operator': {'label': 'Operator'},
        'Start year': {'label': 'Start year'},
        'Technology-Type': {'label': 'Technology Type'},
        'Location accuracy': {'label': 'Location Accuracy'},
        'State/Province': {'display': 'location'},
        'Country': {'display': 'location'},

    },
    showCapacityTable: false, 

        /* style test parameters!

    /* Mapbox styling applied to all trackers */
    pointPaint: {
        'circle-opacity':.65
    },

    /* radius associated with minimum/maximum value on map */
    minRadius: 3,
    maxRadius: 10,


    /* radius to increase min/max to under high zoom */
    highZoomMinRadius: 9,
    highZoomMaxRadius: 96,

}
