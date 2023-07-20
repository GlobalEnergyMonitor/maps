var config = {
    csv: 'data.csv',
    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
        field: 'status',
        values: {
            'operating': 'red',
            'pre-construction': 'green',
            'permitted': 'green',
            'construction': 'blue',
            'retired': 'grey',
            'cancelled': 'grey',
            'shelved': 'grey',
            'mothballed': 'grey',
            'inactive': 'grey',
            'announced': 'green'
        }
    },
    minRadius: 2,
    maxRadius: 10,
    highZoomMinRadius: 4,
    highZoomMaxRadius: 32,
    filters: [
        {
            field: 'status',
            /* values need to be specified for ordering */
            values: ['operating','construction','pre-construction','permitted','announced','retired','cancelled','shelved','mothballed','inactive'],
            primary: true

        }
    ],
    capacityField: 'capacity',
    searchFields: { 'Project': ['project'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start_year']
    },
    assetLabel: "Gas Plants",
    img_detail_zoom: 15,
    tableHeaders: {
        values: ['url','project','unit', 'owner', 'parent', 'capacity', 'status', 'region', 'country', 'province', 'start_year'],
        labels: ['url', 'Plant','Unit','Owner','Parent','Capacity (MW)','Status','Region','Country','Subnational unit (province/state)','Start year'],
        clickColumn: 'url'
    }
};
