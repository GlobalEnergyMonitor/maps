var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    csv: 'data.csv',
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
            'cancelled - inferred 4 y': 'light grey greeninfo',
            'shelved - inferred 2 y': 'light blue greeninfo'

        }
    },

    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values_label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'status',
            values: ['operating','construction','pre-construction', 'announced','shelved', 'shelved - inferred 2 y','mothballed','retired','cancelled', 'cancelled - inferred 4 y'],
        }
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity_(mw)',
    capacityDisplayField: 'capacity_(mw)',
    capacityLabel: 'Capacity (MW)',

    /* Labels for describing the assets */
    assetFullLabel: "Geothermal Plants",
    assetLabel: 'unit',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'project_name',


    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['project_name', 'capacity_(mw)', 'technology', 'status', 'start_year', 'owner', 'operator',  'country'],
        labels: ['Project name','Capacity (MW)','Technology','Status','Start year', 'Owner', 'Operator', 'Country'],
        clickColumns: ['project_name'],
        rightAlign: ['capacity_(mw)','start_year']
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['project_name'], 
        'Companies': ['owner', 'operator'],
        'Start Year': ['start_year']
    },

    /* define fields and how they are displayed. 
      `'display': 'heading'` displays the field in large type
      `'display': 'range'` will show the minimum and maximum values.
      `'display': 'join'` will join together values with a comma separator
      `'display': 'location'` will show the fields over the detail image
      `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'project_name': {'display': 'heading'},
        'status': {'label': 'Status'},
        'owner': {'label': 'Owner'},
        'operator': {'label': 'Operator'},
        'start_year': {'label': 'Start Year'},
        'state/province': {'display': 'location'},
        'country': {'display': 'location'},

    },
    showCapacityTable: true, 
}
