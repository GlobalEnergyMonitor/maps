var config = {
    geojson: 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/mapfiles/gcct_map_2025-05-30.geojson', // Saying can't be found? TODO march 24th

    colors: {
        'light red': '#f28b82',
        'red': '#c74a48',
        'light blue': '#5dade2',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
        'light green': '#66c26e',
        'light grey': '#e0e0e0',
        'grey': '#8f8f8e',
        'orange': '#FF8C00',
        'yellow': '#f3ff00',
        'black': '#000000',
        'purple': '#9370db'
    },
    
    color: { 
        field: 'status', // prod type
        values: {
            'announced': 'red',
            'construction': 'red',
            'operating': 'red',
            'operating-pre-retirement': 'green',
            'cancelled': 'green',
            'retired': 'green',
            'mothballed': 'blue',
            'unknown': 'black'
        },
        },
        filters: [
        {
            field: 'status',
            label: 'Status',
            values: ['announced', 'construction', 'operating', 'operating-pre-retirement', 'cancelled', 'retired', 'mothballed', 'unknown'],
            values_labels: ['Announced', 'Construction', 'Operating', 'Operating Pre-Retirement', 'Cancelled', 'Retired', 'Mothballed', 'Unknown'],
            primary: true
        },
        {
            field: 'plant-type',
            label: 'Plant type',
            values: ['clinker only', 'grinding', 'integrated', ''],
            values_labels: ['Clinker only', 'Grinding', 'Integrated', 'Not found']
        },
        {
            field: 'prod-type',
            label: 'Production type',
            values: ['dry', 'mixed', 'semidry', 'wet', '', 'n/a'],
            values_labels: ['Dry', 'Mixed', 'Semi-dry', 'Wet', 'Not found', 'N/A']
        },
        {
            field: 'color',
            label: 'Color',
            values: ['both', 'grey', 'white', ''],
            values_labels: ['Both', 'Grey', 'White', 'Not found']
        }
        ],

        linkField: 'pid',
        urlField: 'url',
        statusField: 'status-legend',
        statusDisplayField: 'status',
        countryField: 'areas',
        capacityField: 'scaling-capacity', // change to scaling col once added
    capacityDisplayField: 'capacity-display',

    capacityLabel: '',  //(millions metric tonnes per annum)
    // context-layers: [
    //     {
    //         field: 'coalfield',
    //         'label': 'Coal Fields',
    //         'tileset': '[mapbox tile url]',
    //         paint: {}
    //     }
    // ],


    /* Labels for describing the assets */
    assetFullLabel: "Projects",
    assetLabel: 'projects',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'name',

    
    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['name','owner', 'status', 'Cement-Capacity-(millions-metric-tonnes-per-annum)', 'start-year','plant-type','prod-type', 'subnat','areas'],
        labels: ['Project','Owner','Status', 'Cement Capacity (millions metric tonnes per annum)', 'Start date', 'Plant type', 'Production type','Subnational Unit','Country/Area'],
        clickColumns: ['name'],
        rightAlign: [],
        removeLastComma: ['areas'], 
        toLocaleString: ['Cement-Capacity-(millions-metric-tonnes-per-annum)'], 

    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Project': ['name', 'plant-name-(other-language)', 'other-plant-names-(english)', 'other-plant-names-(other-language)'], 
        'Companies': ['owner', 'parent', 'loc-owner', 'entity-id'],
        'Type ': ['plant-type', 'prod-type','color']
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
        'prod-type': {'label': 'Production Type'},
        'Cement Capacity (millions metric tonnes per annum)': {'label': 'Cement Capacity (millions metric tonnes per annum)'},
        'Clinker Capacity (millions metric tonnes per annum)': {'label': 'Clinker Capacity (millions metric tonnes per annum)'},
        'color': {'label': 'Cement Color'},
        'owner': {'label': 'Owner'},
        'start_year': {'label': 'Start date'},
        'location-accuracy': {'label': 'Coordinate Accuracy'},
        'subnat': {'display': 'location'},
        'areas': {'display': 'location'}
    },
    multiCountry: true,
    // maxCapacityLabel: 'millions metric tonnes per annum',
    showMaxCapacity: true,
    
}