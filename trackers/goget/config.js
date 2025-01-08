var config = {

    /* name of the data file; use key `csv` if data file is CSV format */
    csv: 'GOGET_Earthgenome_file2024-04-01.csv',
    
    /* Define labels for sitewide colors, referenced in tracker config */
    colors: {
        'red': '#c74a48',
        'blue': '#5c62cf',
        'green': '#4c9d4f',
        'grey': '#8f8f8e',
        'black': '#000000',
    },

    /* define the column and associated values for color application */

    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'in_development': 'blue',
            'discovered': 'blue',
            'shut_in': 'green',
            'decommissioned': 'green',
            'cancelled': 'green',
            'abandoned': 'grey',
            'UGS': 'grey',
            '': 'black'
        }
    },

    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values_label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'status',
            values: ['operating', 'in_development', 'discovered', 'shut_in', 'decommissioned', 'cancelled', 'abandoned', 'UGS', ""],
            values_labels: ['Operating','In development','Discovered','Shut in','Decommissioned','Cancelled','Abandoned','UGS','Unknown']
        }
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity',
    // capacityLabel: 'million boe/y',
    capacityLabel: '',
    /* Labels for describing the assets */
    assetFullLabel: "Oil & Gas Extraction Areas",
    assetLabel: 'areas',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'unit_name',

    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    
    tableHeaders: {
        values: ['unit_name', 'operator', 'status', 'country', 'province', 'production_oil', 'production_gas', 'production_oil_year', 'production_gas_year', 'production_start_year',],
        labels: ['Extraction Area', 'Operator', 'Status','Country/Area(s)','Subnational unit (province/state)', 'Production - Oil (Million bbl/y)', 'Production - Gas (Million m³/y)', 'Production Year - Oil', 'Production Year - Gas', 'Production start year',],
        clickColumns: ['unit_name'],
        rightAlign: ['unit_name','discovery_year', 'fid_year', 'production_start_year', 'production_gas_year', 'production_gas', 'production_oil_year', 'production_oil', ]
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Extraction Area': ['unit_name'], 
        'Companies': ['owner', 'operator', 'parent'],
        'Discovery Year': ['discovery_year'],
        'Production start year': ['production_start_year']
    },

    /* define fields and how they are displayed. 
      `'display': 'heading'` displays the field in large type
      `'display': 'range'` will show the minimum and maximum values.
      `'display': 'join'` will join together values with a comma separator
      `'display': 'location'` will show the fields over the detail image
      `'label': '...'` prepends a label. If a range, two values for singular and plural.
    */
    detailView: {
        'unit_name': {'display': 'heading'},
        'status': {'label': 'Status'},
        'loc_accuracy': {'label': 'Location Accuracy'},
        'operator': {'label': 'Operator'},
        'discovery_year': {'label': 'Discovery Year'},
        'fid_year': {'label': 'FID Year'},
        'production_start_year': {'label': 'Production Start Year'},
        'production_oil_year': {'label': 'Production Year - Oil'},
        'production_gas_year': {'label': 'Production Year - Gas'},
        'production_oil': {'label': 'Production - Oil (Million bbl/y)'},
        'production_gas': {'label': 'Production - Gas (Million m³/y)'},
        'province': {'display': 'location'},
        'country': {'display': 'location'}
    },
    countryFile: './countries.js'
}
