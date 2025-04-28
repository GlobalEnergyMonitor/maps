var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    // csv: 'data.csv',
    geojson: 'ghpt_2025-04-23.geojson',

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
    countryField: 'areas',
    multiCountry: true,
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
            values: ['operating','construction','pre-construction', 'announced','shelved','mothballed','retired','cancelled'],
        }
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity',
    capacityDisplayField: 'capacity',
    capacityLabel: '(MW)',

    /* Labels for describing the assets */
    assetFullLabel: "Hydropowered Stations",
    assetLabel: 'units',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'name',


    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['name', 'capacity', 'tech-type', 'status', 'start-year', 'owner', 'operator',  'areas', 'area2'],
        labels: ['Project name','Capacity (MW)','Technology type','Status','Start year', 'Owner', 'Operator', 'Country/Area 1','Country/Area 2'],
        clickColumns: ['name'],
        rightAlign: ['capacity','start-year'],
        removeLastComma: ['areas'],
        toLocaleString: ['capacity'],
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['name'], 
        'Companies': ['owner', 'operator', 'loc-oper', 'loc-owner'],
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
        'name': {'display': 'heading'},
        'owner': {'label': 'Owner'},
        'operator': {'label': 'Operator'},
        'start-year': {'label': 'Start Year'},
        'areas' : {'label': 'Country/Area 1'},
        'binational': {'label': 'Binational'},
        'area2' : {'label': 'Country/Area 2'},
        'loc-accu': {'label': 'Location Accuracy'},
        'areas-subnat-sat-display': {'display': 'location'},

    },

}
