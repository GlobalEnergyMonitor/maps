var config = {
    // csv: 'coal-mine.csv', (Mikel's file)
    csv: 'data/data.csv',

    colors: {
        'red': '#c74a48',
        'light blue greeninfo': '#74add1',
        'blue': '#5c62cf',
        // 'green': '#4c9d4f',
        'light grey greeninfo': '#ccc',
        'grey': '#8f8f8e',
        'dark grey': '#4B4B4B',
        'orange': '#FF8C00',
        // 'yellow': '#f3ff00'
    },

    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
        field: 'tracker',
        label: 'Plume and Infrastructure Projects',
        values: {
            'plumes-attrib': 'red',
            'plumes-unattrib': 'orange',
            'oil-and-gas-extraction-areas': 'blue',
            'coal-mines': 'blue',
        }
    },
    filters: [
        {
            field: 'tracker',
            label: 'Plume and Infrastructure Projects',
            values: ['plumes-attrib', 'plumes-unattrib','oil-and-gas-extraction-areas', 'coal-mines'],
            values_labels: ['Plumes Attributed', 'Plumes Unattributed','Oil and Gas Extraction Areas', 'Coal Mines'],
            primary: true
        },
        // {
        //     field: 'infra-filter',
        //     label: 'Attributed Plume',
        //     values: ['Y', 'N'],
        //     values_labels: ['Yes', 'No'],
        //     // primary: true
        // },
        {
            field: 'status-legend',
            label: 'Infrastructure Status',
            values: ['proposed-plus','construction-plus','mothballed-plus', 'retired-plus', 'unknown-plus'], // pre-construction-plus
            /* value_labels must match order/number in values */
            values_labels: ['Proposed / Announced / Discovered' ,'Construction / In development','Mothballed / Idle / Shut in','Retired / Closed / Decommissioned','Not applicable / Unknown'] // 'Pre-construction / Pre-permit / Permitted'
        }
    ],

    // # O&G extraction areas and coal mines by status 
    // plumes by "has attribution information"
    // infrastructure emissions estimates
    
    capacityField: 'scaling_col',
    capacityLabel: 'Emissions (kg/hr)',

    // context_layers: [
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

    wikiField: 'url',
    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['name','plume_emissions', 'emission_uncertainty','infra_type', 'date','infra_name','well_id', 'gov_assets', 'infra_url', 'subnational', 'areas'],
        labels: ['Project', 'Emissions (kg/hr)', 'Emissions Uncertainity (kg/hr)','Type of Infrastructure','Observation Date','GEM Infrastructure Name', 'Government Well ID', 'California VISTA and other Government ID Assets','Infrastructure Wiki', 'Subnational', 'Country/Area'],
        clickColumns: ['name'],
        rightAlign: ['Government Well ID','plume_emissions','date']
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Country': ['country']
        // 'Project': ['name'], 
        // 'Companies': ['owners'],
        // 'Type of Infrastructure': ['infra_type'],
        // 'Government Well ID': ['well_id'],
        // // 'California VISTA and other Government ID Assets': ['gov_assets']
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
        // 'tracker': {'label': 'Tracker Type'},
        'owners': {'label': 'Owner'},
        'est_emissions': {'label': 'Estimated emissions'},
        'plume_emissions': {'label': 'Emissions (kg/hr)'},
        'emission_uncertainty': {'label': 'Emissions Uncertainity (kg/hr)'},
        'infra_type': {'label': 'Type of Infrastructure'},
        'infra_name': { 'label': 'Attributed Infrastructure Project Name'},
        'date': {'label': 'Observation Date'},
        'status': {'label': 'Status'},
        'instrument': {'label': 'Instrument'},
        'infra_url': {'display': 'hyperlink'},
        'subnational': {'display': 'location'},
        'country': {'display': 'location'}
    }, 

    linkField: 'map_id',

    showCapacityTable: false
}
