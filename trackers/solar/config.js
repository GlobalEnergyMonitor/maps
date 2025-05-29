var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    // csv: 'data.csv',
    csv: 'compilation_output/Solar-map-file-2025-02-04.csv',

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
        field: 'status',
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
    interpolate: ["cubic-bezier", 0, 0, 0, 1],

    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values_label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'status',
            values: ['operating', 'announced', 'construction', 'pre-construction', 'mothballed', 'shelved', 'cancelled', 'retired'],
            values_labels: ['operating', 'announced', 'construction', 'pre-construction', 'mothballed', 'shelved',  'cancelled', 'retired'],
            primary: true
        },
        {
            field: 'technology-type',
            label: 'Technology Type',
            values: ['Solar-Thermal', 'PV', 'Assumed-PV'],
            values_labels: ['Solar Thermal', 'PV', 'Assumed PV']

        },
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity-(mw)',
    capacityDisplayField: 'capacity-(mw)',
    capacityLabel: '(MW)',

    /* Labels for describing the assets */
    assetFullLabel: "Solar photovoltaic farm phases",
    assetLabel: 'phase',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'project-name',
    linkField: 'gem-location-id',
    urlField: 'url',
    countryField: 'country/area',

    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['project-name', 'phase-name', 'capacity-(mw)', 'technology-type', 'status', 'start-year', 'owner', 'operator', 'location-accuracy', 'state/province', 'country/area'],
        labels: ['Project', 'Phase','Capacity (MW)', 'Technology Type', 'Status', 'Start year', 'Owner', 'Operator','Location Accuracy', 'State/Province', 'Country/Area'],
        clickColumns: ['project-name'],
        toLocaleString: ['capacity-(mw)'],
        rightAlign: ['capacity-(mw)','start-year']
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
        searchFields: { 'Project': ['project-name', 'project-name-in-local-language-/-script', 'other-name(s)'], 
            'Companies': ['owner', 'operator', 'owner-name-in-local-language-/-script', 'operator-name-in-local-language-/-script'],
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
        'project-name-in-local-language-/-script': {'label': 'Project in Local Language / Script'},
        'owner': {'label': 'Owner'},
        'operator': {'label': 'Operator'},
        'start-year': {'label': 'Start Year'},
        'technology-type': {'label': 'Technology Type'},
        'location-accuracy': {'label': 'Location Accuracy'},
        'state/province': {'display': 'location'},
        'country/area': {'display': 'location'},

    },

    // /* radius associated with minimum/maximum value on map */
    // minRadius: 2,
    // maxRadius: 10,
    // minLineWidth: 1,
    // maxLineWidth: 10,

    // /* radius to increase min/max to under high zoom */
    // highZoomMinRadius: 4,
    // highZoomMaxRadius: 32,
    // highZoomMinLineWidth: 4,
    // highZoomMaxLineWidth: 32,

    /* radius associated with minimum/maximum value on map */
    minRadius: .8,
    maxRadius: 10,
    // /* radius to increase min/max to under high zoom */
    highZoomMinRadius: 4,
    highZoomMaxRadius: 32,
    // showAllPhases: true,

    statusField: 'status', // this strays from default, make it all the same!!
    statusDisplayField: 'status', // this strays from default, make it all the same!!
    showMinCapacity: true
}
