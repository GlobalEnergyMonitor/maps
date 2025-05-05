var config = {
    geometries: ['Point','LineString'],

    json: 'compilation_output/ggit_2025-05-01.geojson', //'data/ggit_2024-12-20.geojson',
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
    capacityLabel: {
        field: 'tracker-custom',
        values: {
            'GGIT': 'bcm/y of gas',
            'GGIT-import': 'MTPA of natural gas',
            'GGIT-export': 'MTPA of natural gas',            
        }
    },
    
    assetFullLabel: {
        field: 'tracker-custom',
        values: {
            'GGIT': 'Pipelines',
            'GGIT-import': 'Terminals',
            'GGIT-export': 'Terminals',            
        }
    },
    
    assetLabel: {
        field: 'tracker-custom',
        values: {
            'GGIT': 'segments',
            'GGIT-import': 'trains',
            'GGIT-export': 'trains',            
        }
    },
    nameField: 'name', 
    tableHeaders: {
        values: ['name','unit-name', 'owner', 'parent', 'capacity-table', 'units-of-m', 'status', 'region', 'areas', 'subnat', 'start-year', 'tracker-display'],
        labels: ['Project','Unit','Owner','Parent','Capacity', '','Status','Region','Country/Area(s)','Subnational unit (province/state)','Start year', 'Type'],
        clickColumns: ['name'],
        rightAlign: ['unit-name','capacity-table','start-year'],
        toLocaleString: ['capacity-table'],
    
    },
    searchFields: { 'Infrastructure Type': ['tracker-custom'],
        'Project': ['name'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start-year']
    },
    detailView: {
        'name': {'display': 'heading'},
        // 'status': {'label': 'Status'},
        // 'capacity-table': {'label': 'Capacity'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'start-year': {'label': 'Start Year'},
        'tracker-display': {'label': 'Type'},
        'areas-subnat-sat-display': {'display': 'location'}
    },

showMaxCapacity: false,
multiCountry: true,

minLineWidth: 1,
maxLineWidth: 4,
highZoomMinLineWidth: 2,
highZoomMaxLineWidth: 5,

minRadius: 3,
maxRadius: 10,
// /* radius to increase min/max to under high zoom */
highZoomMinRadius: 5,
highZoomMaxRadius: 30,

    


};
