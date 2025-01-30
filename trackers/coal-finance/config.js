var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    json: 'output/coal-finance-eg-map 2024-10-28.geojson',
    /* define the column and associated values for color application */
    geometries: ['Point','LineString'],
    center: [8, 30],
    zoomFactor: 1.9,
    img_detail_zoom: 10,
    linkField: 'tid',
    urlField: 'wiki',
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
            values: ['operating','construction','permitted','pre-permit', 'announced','retired','cancelled', 'shelved','mothballed'],
        },
        {
            type: 'Domestic/International',
            values: ['Domestic', 'International', 'Not found']
        }
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'megawatts',
    capacityLabel: 'Capacity (MW)',

    /* Labels for describing the assets */
    assetFullLabel: "Coal-fired Units",
    assetLabel: 'units',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'project-name',
    countryField: 'target_country',

    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['plant-name','unit-name','plant-name-(local)','owner', 'parent', 'capacity', 'status', 'start-year', 'retired-year', 'region', 'country/area', 'subnational'],
        labels: ['Plant','Unit','Plant name (local)','Owner','Parent','Capacity (MW)','Status','Start year', 'Retired year','Region','Country/Area','Subnational unit (province, state)'],
        clickColumns: ['plant-name'],
        rightAlign: ['unit-name','capacity','start-year','retired-year']
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['project-name'], 
        'Companies': ['financer', 'parent'],
        'Start Year': ['close-year']
    },

    /* define fields and how they are displayed. 
      `'display': 'heading'` displays the field in large type
      `'display': 'range'` will show the minimum and maximum values.
      `'display': 'join'` will join together values with a comma separator
      `'display': 'location'` will show the fields over the detail image
      `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'plant-name': {'display': 'heading'},
        'plant-name-(local)': {'label': 'Local plant name'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'start-year': {'display': 'range', 'label': ['Start Year', 'Start Year Range']},
        'retired-year': {'display':'range', 'label': ['Retired Year', 'Retired Year Range']},
        'subnational': {'display': 'location'},
        'country/area': {'display': 'location'}
    } 
}
