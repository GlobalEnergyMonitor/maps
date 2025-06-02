var config = {

    geojson: 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/mapfiles/gcmt_map_2025-06-02.geojson', //'compilation_output/gcmt_2025-05-05.geojson',

    colors: {
        'red': '#c74a48',
        'light blue greeninfo': '#74add1',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
        'light grey greeninfo': '#ccc',
        'grey': '#8f8f8e',
        'dark grey': '#4B4B4B',
        'orange': '#FF8C00',
        'yellow': '#f3ff00'
    },

    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
        field: 'status',
        values: {
            'operating': 'red',
            'proposed': 'blue',
            'cancelled': 'green',
            'retired': 'orange',
            'shelved': 'dark grey',
            'mothballed': 'grey'
        }
    },
    filters: [
        {
            field: 'status',
            /* values need to be specified for ordering */
            values: ['operating','proposed','cancelled','retired','shelved','mothballed'],
            // values_labels: ['operating','proposed','cancelled','retired','shelved','mothballed'],
            primary: true
        },
        {
            field: 'mine-type',
            label: 'Mine Type',
            values: ['surface','underground','underground & surface', '-'],
            values_labels: ['Surface','Underground','Underground & Surface', 'Not found']

        },
        {
            field: 'coal-grade',
            label: 'Coal Grade',
            values: ['thermal','met','thermal & met','-'],
            /* value_labels must match order/number in values */
            values_labels: ['Thermal','Met','Thermal & Met','Not found']
        }
    ],
    capacityField: 'scaling-capacity',
    capacityDisplayField: 'capacity-details',
    // capacityLabel: '(Mt)', 
    capacityLabel: '',
    countryField: 'areas',
    // context_layers: [
    //     {
    //         field: 'coalfield',
    //         'label': 'Coal Fields',
    //         'tileset': '[mapbox tile url]',
    //         paint: {}
    //     }
    // ],


    /* Labels for describing the assets */
    assetFullLabel: "Coal Mine Projects",
    assetLabel: 'projects',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'name',

    
    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['name','owner', 'parent', 'capacity', 'prod-coal', 'prod-year', 'status', 'workforce', 'coalfield', 'areas', 'region', 'start-year', 'end-year'], 
        labels: ['Project','Owner','Parent','Capacity (Mt)', 'Production (Mt)', 'Production year','Status', 'Workforce', 'Coal Field', 'Country/Area', 'Region','Opening year', 'Closing year'], // , 'Closing year'
        clickColumns: ['name'],
        removeLastComma: ['areas'],
        rightAlign: ['prod-coal','capacity','start-year'], //'end-year' 
        toLocaleString: ['capacity', 'prod-coal'],
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['name', 'noneng-name'], 
        'Companies': ['owner', 'parent', 'owners-noneng'],
        'Opening Year': ['start-year']
    },

    /* define fields and how they are displayed. 
        `'display': 'heading'` displays the field in large type
        `'display': 'range'` will show the minimum and maximum values.
        `'display': 'join'` will join together values with a comma separator
        `'display': 'location'` will show the fields over the detail image
        `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'name': {'display': 'heading'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'capacity': {'label': 'Capacity (Mt)'},
        'prod-coal': { 'label': 'Production (Mt)' },
        'workforce': {'label': 'Estimated Workforce'},
        'start-year': {'label': 'Opening Year'},
        'end-year': {'label': 'Closing Year'},
        'coalfield': {'label': 'Coal Field'},
        'areas-subnat-sat-display': {'display': 'location'},
    }, 

    showMaxCapacity: false,
    
}
