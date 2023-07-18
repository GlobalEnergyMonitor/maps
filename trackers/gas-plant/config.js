var config = {
    csv: 'data.csv',
    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
        field: 'status',
        values: {
            //update this list
            'operating': 'red',
            'pre-construction': 'green',
            'construction': 'blue',
            'retired': 'grey',
            'cancelled': 'grey',
            'shelved': 'grey',
            'mothballed': 'grey',
            'announced': 'green'
            // contining
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
            values: ['operating','construction','pre-construction','announced','retired','cancelled','shelved','mothballed'],
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