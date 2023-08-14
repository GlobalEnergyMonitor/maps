var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    json: 'coal.json',

    /* define the column and associated values for color application */
    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'construction': 'blue',
            'announced': 'green',
            'permitted': 'green',
            'pre-permit': 'green',
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
            values: ['operating','construction','announced','permitted','pre-permit','retired','cancelled','mothballed','shelved'],
        }
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity',
    capacityLabel: 'Capacity (MW)',

    /* Labels for describing the assets */
    assetFullLabel: "Coal-fired Units",
    assetLabel: 'units',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'plant',


    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['url','plant','unit','chinese_name','owner', 'parent', 'capacity', 'status', 'region', 'country', 'subnational', 'year'],
        labels: ['url', 'Plant','Unit','Chinese Name','Owner','Parent','Capacity (MW)','Status','Region','Country','Subnational unit (province/state)','Start year'],
        clickColumn: 'url'
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Plant': ['plant'], 
        'Companies': ['owner', 'parent'],
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
        'plant': {'display': 'heading'},
        'chinese_name': {},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'year': {'display': 'range', 'label': ['Start Year', 'Start Year Range']},
        'subnational': {'display': 'location'},
        'country': {'display': 'location'}
    } 
}