var config = {
    csv: 'data.csv',
    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
        field: 'status',
        values: {
            //update this list
            'operating': '#e37c79',
            'pre-construction': '#b5eaaa',
            'construction': '#aaabf2',
            'retired': '#9c9c9b',
            'cancelled': '#9c9c9b',
            'pre-permit': '#b5eaaa',
            'shelved': '#9c9c9b',
            'mothballed': '#9c9c9b',
            'announced': '#b5eaaa',
            'permitted': '#aaabf2'
            // contining
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
    searchFields: ['name', 'country', 'company'], /* company could be owner, operator or parent, need to specify */
    searchField: 'project', /* temporary single value rather list */
    assetLabel: "Gas Plants",
    img_detail_zoom: 15
};