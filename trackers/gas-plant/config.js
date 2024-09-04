var config = {
    csv: 'data/data-2024-08-29.csv',
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
        values: ['project','unit', 'owner', 'parent', 'capacity', 'status', 'region', 'country', 'province', 'start_year'],
        labels: ['Plant','Unit','Owner','Parent','Capacity (MW)','Status','Region','Country/Area(s)','Subnational unit (province/state)','Start year'],
        clickColumns: ['project'],
        rightAlign: ['unit','capacity','start_year']
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
