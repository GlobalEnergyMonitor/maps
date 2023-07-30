var config = {
    csv: 'data.csv',
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
    capacityField: 'capacity',
    capacityLabel: 'Capacity (MW)',
    assetFullLabel: "Gas Units",
    assetLabel: 'units',
    nameField: 'project',
    tableHeaders: {
        values: ['url','project','unit', 'owner', 'parent', 'capacity', 'status', 'region', 'country', 'province', 'start_year'],
        labels: ['url', 'Plant','Unit','Owner','Parent','Capacity (MW)','Status','Region','Country','Subnational unit (province/state)','Start year'],
        clickColumn: 'url'
    },
    searchFields: { 'Plant': ['project'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start_year']
    },
    detailView: {
        'project': {'display': 'heading'},
        'project_loc': {},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'technology': {'display': 'join', 'label': ['Technology', 'Technologies']},
        'fuel_type': {'display': 'join', 'label': ['Fuel Type', 'Fuel Types']},
        'start_year': {'display': 'range', 'label': ['Start Year', 'Start Year Range']},
        'province': {'display': 'location'},
        'country': {'display': 'location'}
    } 
};
