var config = {
    tiles: [
        'https://gem.dev.c10e.org/africa_energy_tracker-2024-06-11/{z}/{x}/{y}.pbf'
        ],
    /* make tileconfig consist of set of array of layer / type */ /* but there can only be one line, one polygon */
    tileSourceLayer: 'africa_energy_tracker',
    geometries: ['Point','LineString'],
    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'announced': 'green',
            'discovered': 'green',
            'pre-construction': 'blue',
            'construction': 'blue',
            'in development': 'blue',
            'retired': 'grey',
            'Idle': 'grey',
            'cancelled': 'grey',
            'cancelled - inferred 4 y': 'grey',
            'mothballed': 'grey',
            'shelved': 'grey',
            'shelved - inferred 2 y': 'grey',
            'shut in': 'grey'
        }
    },
    filters: [
        {
            field: 'status',
            values: ['operating','announced','discovered','pre-construction','construction','in development','retired','Idle',
                'cancelled','cancelled - inferred 4 y','mothballed','shelved','shelved - inferred 2 y','shut in']
        }
    ],
    capacityField: 'capacity',
    capacityLabel: 'Capacity (MW)',
    assetFullLabel: "Gas Units",
    assetLabel: 'units',
    nameField: 'name',
    countryField: 'area',
    tableHeaders: {
        values: ['tracker','project','unit', 'type', 'parent', 'capacity', 'status', 'area', 'start_year'],
        labels: ['Tracker', 'Plant','Unit', 'Type','Parent','Capacity (MW)','Status','Countries','Start year'],
        clickColumns: ['project'],
        rightAlign: ['unit','capacity','start_year']
    },
    searchFields: { 'Plant': ['project'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start_year']
    },
    detailView: {
        'name': {'display': 'heading'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'tracker': {'label': 'Tracker'},
        'area': {'display': 'location'}
    }
};
