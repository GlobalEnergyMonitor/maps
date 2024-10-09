var config = {
    geometries: ['Point','LineString'],

    json: 'compilation_output/ggit_2024-10-08.geojson',
    color: {
        field: 'status-legend',
        values: {
            'operating': 'red',
            'proposed-plus': 'green',
            // 'pre-construction-plus': 'green',
            'construction-plus': 'blue',
            'retired-plus': 'grey',
            'cancelled': 'grey',
            'shelved': 'grey',
            'mothballed-plus': 'grey',
            'announced': 'green'
        }
    },
    filters: [
        {
            field: 'status-legend',
            label: 'Status',
            values: ['operating','proposed-plus','construction-plus','retired-plus','cancelled','mothballed-plus','shelved'],
            values_labels: ['Operating','Proposed/Announced/Discovered', 'Construction/In development','Retired/Closed/Decommissioned','Cancelled','Mothballed/Idle/Shut in','Shelved']

        },
        {
            field: 'tracker-custom',
            label: 'Infrastructure Type',
            // cannot have any spaces in the values!
            values: ['GGIT-import', 'GGIT-export', 'GGIT'],
            values_labels: ['LNG Terminals (Import)', 'LNG Terminals (Export)', 'Gas Pipelines']
        }
    ],
    capacityField: 'scaling-capacity',
    capacityDisplayField: 'capacity-table', 
    capacityLabel: '',
    assetFullLabel: "Pipelines / Terminals", 
    assetLabel: '',
    nameField: 'name', 
    tableHeaders: {
        values: ['name','unit-name', 'owner', 'parent', 'capacity-table', 'status', 'region', 'areas', 'subnat', 'start-year', 'tracker-display'],
        labels: ['Project','Unit','Owner','Parent','Capacity','Status','Region','Country/Area(s)','Subnational unit (province/state)','Start year', 'Type'],
        clickColumns: ['name'],
        rightAlign: ['unit-name','capacity-table','start-year']
    },
    searchFields: { 'Infrastructure Type': ['tracker-custom'],
        'Project': ['name'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start-year']
    },
    detailView: {
        'name': {'display': 'heading'},
        'status': {'label': 'Status'},
        'capacity-table': {'label': 'Capacity'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'start-year': {'label': 'Start Year'},
        'tracker-display': {'label': 'Type'},
        'areas-subnat-sat-display': {'display': 'location'}
    },

showMaxCapacity: false,
multiCountry: true,


};
