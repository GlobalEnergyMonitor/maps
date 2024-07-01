var config = {
    tiles: [
        'https://gem.dev.c10e.org/pipeline-test-2024-06-03/{z}/{x}/{y}.pbf'
        // 'https://bucketeer-cf25e1cc-bfe0-4e0f-957c-65e8e9492475.s3.amazonaws.com/maps/integrated-2024-03-14/{z}/{x}/{y}.pbf'
        'http://127.0.0.1:8000/trackers/asia_gas_tracker/lines-2024-06-03.dir/{z}/{x}/{y}.pbf'

        ],
    /* make tileconfig consist of set of array of layer / type */ /* but there can only be one line, one polygon */
    tileLineSourceLayer: 'lines',
    tilePointSourceLayer: 'points',
    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'proposed_plus': 'green',
            'construction_plus': 'blue',
            'retired': 'grey',
            'cancelled': 'grey',
            'shelved': 'grey'
        }
    },
    filters: [
        {
            field: 'status',
            values: ['operating','construction_plus','proposed_plus','retired','cancelled','shelved'],
        }
    ],
    capacityField: 'capacity',
    capacityLabel: 'Capacity (MW)',
    assetFullLabel: "Gas Units",
    assetLabel: 'units',
    nameField: 'project',
    countryField: 'countries',
    tableHeaders: {
        values: ['project','unit', 'type', 'parent', 'capacity', 'status', 'countries', 'start_year'],
        labels: ['Plant','Unit', 'Type','Parent','Capacity (MW)','Status','Countries','Start year'],
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
        'type': {'display': 'join', 'label': ['Type', 'Types']},
        'start_year': {'display': 'range', 'label': ['Start Year', 'Start Year Range']},
        'countries': {'display': 'location'}
    }
};
