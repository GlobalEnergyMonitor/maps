var config = {
    json: 'coal.json',
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
    filters: [
        {
            field: 'status',
            values: ['operating','construction','announced','permitted','pre-permit','retired','cancelled','mothballed','shelved'],
        }
    ],
    capacityField: 'capacity',
    capacityLabel: 'Capacity (MW)',
    assetFullLabel: "Coal-fired Units",
    assetLabel: 'units',
    nameField: 'plant',
    tableHeaders: {
        values: ['url','plant','unit','chinese_name','owner', 'parent', 'capacity', 'status', 'region', 'country', 'subnational', 'year'],
        labels: ['url', 'Plant','Unit','Chinese Name','Owner','Parent','Capacity (MW)','Status','Region','Country','Subnational unit (province/state)','Start year'],
        clickColumn: 'url'
    },
    searchFields: { 'Plant': ['plant'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start_year']
    },
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