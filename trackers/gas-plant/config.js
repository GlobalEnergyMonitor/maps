var config = {
    csv: 'data.csv',
    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
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
    paint: {
        /* this could be made dynamic based on the range of values in the data */
        'circle-radius': ["max", 3, ["/", ["to-number", ["get", "capacity"]], 500]],
        'circle-opacity':.85

    },
    filters: [
        {
            field: 'status',
            /* values need to be specified for ordering */
            values: ['operating','construction','pre-construction','retired','cancelled','shelved','mothballed','announced'],
            primary: true

        }
    ],
    capacityField: 'capacity',
    searchFields: { 'Project': ['project'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start_year']
    }, 
//['project', 'owner', 'start_year'], /* company could be owner, operator or parent, need to specify */
    assetLabel: "Gas Plants",
    img_detail_zoom: 15
};
