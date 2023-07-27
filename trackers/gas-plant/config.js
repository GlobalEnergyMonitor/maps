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
    filters: [
        {
            field: 'status',
            /* values need to be specified for ordering */
            values: ['operating','construction','pre-construction','announced','retired','cancelled','shelved','mothballed'],
            primary: true

        }
    ],
    capacityField: 'capacity',
    assetLabel: "Gas Units",
    tableHeaders: {
        values: ['url','project','unit', 'owner', 'parent', 'capacity', 'status', 'region', 'country', 'province', 'start_year'],
        labels: ['url', 'Plant','Unit','Owner','Parent','Capacity (MW)','Status','Region','Country','Subnational unit (province/state)','Start year'],
        clickColumn: 'url'
    }
};
