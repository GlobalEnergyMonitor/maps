var config = {
    json: 'data/data.geojson',

    colors: {
        'red': '#c74a48',
        'light blue greeninfo': '#74add1',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
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
            'coal-mines': 'green',
        }
    },
    filters: [
        {
            field: 'tracker',
            label: 'Plume and Infrastructure Projects',
            values: ['oil-and-gas-extraction-areas', 'coal-mines','plumes-attrib', 'plumes-unattrib'],
            values_labels: ['Oil and Gas Extraction Areas', 'Coal Mines','Plumes (has attribution information) ', 'Plumes (no attribution information)'],
            primary: true
        },
        {
            field: 'status-legend',
            label: 'Infrastructure Status',
            values: ['operating', 'proposed-plus','pre-construction-plus','construction-plus','mothballed-plus', 'retired-plus', 'unknown-plus'], // pre-construction-plus
            /* value_labels must match order/number in values */
            values_labels: ['Operating', 'Proposed / Announced / Discovered', 'Pre-construction / Exploration','Construction / In development','Mothballed / Idle / Shut in / Abandoned','Retired / Closed / Decommissioned / Cancelled','Not applicable / Unknown / UGS'] // 'Pre-construction / Pre-permit / Permitted / Exploration'
        }
    ],

    statusDisplayField: 'status',
    statusField: 'status-legend',

    // # O&G extraction areas and coal mines by status 
    // plumes by "has attribution information"
    // infrastructure emissions estimates
    
    capacityField: 'scaling_col',
    capacityLabel: '', // for gmet that has no capacity but only emissions data

    // capacityLabel: 'not applicable'

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


    // urlField: 'url', // wikiField

    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {

        values: ['name', 'status','plume_emissions', 'emission_uncertainty','infra_type', 'date','subnational', 'country','infra_name', 'infra_url', 'well_id', 'gov_assets'],
        labels: ['Project', 'Status','Emissions (kg/hr)', 'Emissions Uncertainty (kg/hr)','Type of Infrastructure','Observation Date', 'Subnational', 'Country/Area(s)','Nearby Infrastructure Project Name', 'Infrastructure Wiki', 'Government Well ID', 'Other Government ID Assets'],
        clickColumns: ['name'],
        rightAlign: ['Government Well ID','plume_emissions','date'],
        removeLastComma: ['country'],
        toLocaleString: ['scaling_col'], // not displayed

    },
    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Country/Area(s)': ['country'],

        'Project Type': ['tracker'],
        'Project': ['name'], 
        'Companies': ['operator'],
        'Type of Infrastructure': ['infra_type'],
        'Government Well ID': ['well_id'],
        'Other Government ID Assets': ['gov_assets']

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
        'owner': {'label': 'Owner'},
        'operator': {'label': 'Operator'},
        'plume_emissions': {'label': 'Emissions (kg/hr)'},
        'emission_uncertainty': {'label': 'Emissions Uncertainity (kg/hr)'},
        'infra_type': {'label': 'Type of Infrastructure'},
        'infra_name': { 'label': 'Nearby Infrastructure Project Name'},
        'related_cm_field': {'label': 'ClimateTrace Field'},
        'mtyr-gcmt_emissions': {'label': 'GEM Coal Mine Methane Emissions Estimate (mt/yr)'},
        'capacity_output': {'label': 'Coal Output (Annual, Mst)'},
        'capacity_prod': {'label': 'Production (Mtpa)'},
        'tonnesyr-pipes_emissions': {'label': 'Emissions if Operational (tonnes/yr)'},
        'length': {'label': 'Length (km)'},
        'capacity': {'label': 'Capacity (cubic meters/day)'},
        'tonnes-goget_emissions': {'label': 'Climate TRACE Field Emissions (tonnes)'},
        'tonnes-goget-reserves_emissions': {'label': 'Emissions for whole reserves (tonnes)'},
        'date': {'label': 'Observation Date'},
        'status': {'label': 'Status'},
        'instrument': {'label': 'Instrument'},
        'country': {'label': 'Country/Area(s)'},
        // 'infra_url': {'display': 'hyperlink'},
        // 'subnational': {'display': 'location'},
        'areas-subnat-sat-display': {'display': 'location'}
    }, 

    linkField: 'map_id',

    multiCountry: true,

    showMaxCapacity: false
}
