var config = {
    /* name of the data file; use key `csv` if data file is CSV format */
    csv: 'GOGET_Earthgenome_file2024-03-26.csv',

    /* define the column and associated values for color application */
    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'in_development': 'blue',
            'discovered': 'blue',
            'shut_in': 'green',
            'abandoned': 'grey',
            'decommissioned': 'grey',
            'cancelled': 'grey',
            'exploration': 'grey',
            'UGS': 'grey'
        }
    },

    /* define the column and values used for the filter UI. There can be multiple filters listed. 
      Additionally a custom `label` can be defined (default is the field), 
      and `values_label` (an array matching elements in `values`)
      */
    filters: [
        {
            field: 'status',
            values: ['operating','in_development','discovered','shut_in','abandoned','decommissioned','cancelled','exploration','UGS'],
        }
    ],

    /* define the field for calculating and showing capacity along with label.
       this is defined per tracker since it varies widely */
    capacityField: 'capacity',
    capacityLabel: 'million bbl/y',

    /* Labels for describing the assets */
    assetFullLabel: "Oil & Gas Extraction Areas",
    assetLabel: 'areas',

    /* the column that contains the asset name. this varies between trackers */
    nameField: 'unit_name',


    /* configure the table view, selecting which columns to show, how to label them, 
        and designated which column has the link */
    tableHeaders: {
        values: ['unit_name','owner', 'parent', 'capacity', 'status', 'country', 'province', 'discovery_year','fid_year', 'production_start_year', ],
        labels: ['Unit','Owner','Parent','Production Total (million bbl/y)','Status','Country','Subnational unit (province/state)','Discovery year', 'FID year', 'Production start year'],
        clickColumns: ['unit_name'],
        rightAlign: ['unit_name','capacity','discovery_year', 'fid_year', 'production_start_year']
    },

    /* configure the search box; 
        each label has a value with the list of fields to search. Multiple fields might be searched */
    searchFields: { 'Area': ['unit_name'], 
        'Companies': ['owner', 'parent'],
        'Discovery Year': ['discovery_year'],
        'FID Year': ['fid_year'],
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
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'discovery_year': {'label': 'Discovery Year'},
        'fid_year': {'label': 'FID Year'},
        'production_start_year': {'label': 'Production Start Year'},
        'province': {'display': 'location'},
        'country': {'display': 'location'}
    } 
}


// if no capacity then remove bottom section and show status at top
