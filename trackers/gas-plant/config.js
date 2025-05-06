
var config = {

    csv: 'compilation_output/Oil & Gas Plants-map-file-2025-01-16.csv',
    linkField: 'gem-location-id',
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
    filters: [
        {
            field: 'status',
            values: ['operating','construction','pre-construction','announced','retired','cancelled','shelved','mothballed'],
        }
    ],
    capacityField: 'capacity-(mw)',
    capacityDisplayField: 'capacity-(mw)',
    capacityLabel: '(MW)',
    assetFullLabel: "Gas Units",
    assetLabel: 'units',
    nameField: 'plant-name',
    tableHeaders: {
        values: ['plant-name','unit-name', 'owner(s)', 'parent(s)', 'capacity-(mw)', 'status', 'region', 'country/area', 'state/province', 'start-year'],
        labels: ['Plant','Unit','Owner','Parent','Capacity (MW)','Status','Region','Country/Area(s)','Subnational unit (province/state)','Start year'],
        clickColumns: ['plant-name'],
        rightAlign: ['unit-name','capacity-(mw)','start-year'],
        toLocaleString: ['capacity-(mw)'],

>>>>>>> 81808373619ec7caaa2f0f4b2814984378a66e84
    },
    searchFields: { 'Plant': ['plant-name'], 
        'Companies': ['owner(s)', 'parent(s)', 'operator(s)'],
        'Start Year': ['start-year']
    },
    detailView: {
        'plant-name': {'display': 'heading'},
        // 'project': {},
        'owner(s)': {'label': 'Owner(s)'},
        'parent(s)': {'label': 'Parent(s)'},
        'turbine/engine-technology': {'label': 'Turbine/Engine Technology'},
        'fuel': {'label': 'Fuel'},
        'start-year': {'label': 'Start year'},
        'state/province': {'display': 'location'},
        'country/area': {'display': 'location'}
    }
};
