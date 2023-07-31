var config = {
    csv: 'data.csv',
    color: {
        field: 'status',
        values: {
            //update this list
            'operating': 'red',
            'construction': 'blue',
            'pre-construction': 'green',
            'announced': 'green',
            'shelved': 'grey',
            'mothballed': 'grey',
            'retired': 'grey',
            'cancelled': 'grey'
        }
    },
    filters: [
        {
            field: 'status',
            /* values need to be specified for ordering */
            values: ['operating','construction','pre-construction','announced','shelved','mothballed','retired','cancelled']
        },
        {
            field: 'type',
            label: 'Type',
            //may need label here "Offshore unknown mount" on live site
            values: ['offshore_hard_mount','offshore_floating','offshore_mount_unknown','onshore','unknown']
        }
    ],
    capacityField: 'capacity',
    capacityLabel: 'Capacity (MW)',
    assetFullLabel: 'Wind Farm Phases',
    assetLabel: 'phases',
    nameField: 'project',
    tableHeaders: {
        values: ['url','project','unit','project_local','type','capacity','status', 'start_year', 'operator', 'owner', 'country'],
        labels: ['url', 'Project Name','Phase name','Project Name in Local Language / Script','Installation Type','Capacity (MW)' ,'Status','Start Year','Operator', 'Owner','Country'],
        clickColumn: 'url'
    },
    searchFields: { 'Project': ['project'], 
        'Companies': ['owner', 'operator'],
        'Start Year': ['start_year']
    },
    img_detail_zoom: 13,
    detailView: {
        'project': {'display': 'heading'},
        'project_local': {},
        'owner': {'label': 'Owner'},
        'operator': {'label': 'Operator'},
        'type': {'display': 'join', 'label': ['Type', 'Types']},
        'start_year': {'display': 'range', 'label': ['Start Year', 'Start Year Range']},
        'accuracy': {'display': 'join', 'label': ['Accuracy','Accuracy']},
        'country': {'display': 'location'}
    },
    showAllPhases: true
}