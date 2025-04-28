var config = {
    geometries: ['LineString'],

    /* name of the data file; use key `csv` if data file is CSV format */
    // csv: 'GOGET_Earthgenome_file2024-04-01.csv',
    // can this be a s3 link but not tiles? 
    geojson: 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/latest/goit_2025-04-09.geojson',
    
    /* Define labels for sitewide colors, referenced in tracker config */
    colors: {
        'red': '#c74a48',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
        'grey': '#8f8f8e',
        'black': '#000000',
    },

    /* define the column and associated values for color application */
    countryField: 'areas',
    linkField: 'url',
    urlField: 'url',

    color: {
        field: 'status-legend',
        values: {
            'operating': 'red',
            'construction-plus': 'blue',
            'proposed-plus': 'blue',
            'mothballed-plus': 'green',
            'cancelled': 'green',
            'retired-plus': 'grey',
            'shelved': 'grey',
        }
    },

    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values_label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'status-legend',
            values: ['operating', 'proposed-plus', 'construction-plus', 'mothballed-plus', 'cancelled', 'retired-plus', 'shelved' ],
            values_labels: ['Operating','Proposed','Construction','Mothballed','Cancelled','Retired','Shelved']
        },
        {
            field: 'Fuel',
            values: ['Oil', 'NGL'],
            values_labels: ['Oil', 'NGL'],
            filterFunction: (value, selectedValue) => {
            // Check if the value contains the selectedValue (Oil or NGL)
            return value.includes(selectedValue);
            }
        }
    ],

    

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity',
    capacityDisplayField: 'capacity',
    capacityLabel: 'BOEd', 
    /* Labels for describing the assets */
    assetFullLabel: "Pipelines",
    assetLabel: 'segments',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'name',
    statusDisplayField: 'status',
    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    
    tableHeaders: {
        values: ['name', 'owner', 'parent', 'status', 'areas', 'subnat', 'capacity-table', 'units-of-m','start-year'],        
        labels: ['Name', 'Owner','Parent', 'Status','Country/Area(s)','Subnational unit (province/state)', 'Capacity', '','Start Year'],
        clickColumns: ['name'],
        rightAlign: ['name', 'start-year', 'capacity' ],
        toLocaleString: ['capacity'],
    
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Pipeline': ['name'], 
        'Companies': ['owner', 'operator', 'parent'],
        'Start Year': ['start-year'],
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
        // 'loc_accuracy': {'label': 'Location Accuracy'}, # RouteAccuracy
        'owner': {'label': 'Owner'},

        'parent': {'label': 'Parent'},
        'start-year': {'label': 'Start Year'},

        'areas-subnat-sat-display': {'display': 'location'}
    },
    // countryFile: './countries.js',
    showMaxCapacity: false,
    multiCountry: true,

}
