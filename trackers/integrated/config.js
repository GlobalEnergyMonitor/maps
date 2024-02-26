var config = {
    tiles: [
        'http://127.0.0.1:8000/trackers/integrated/integrated-2024-02-14.dir/{z}/{x}/{y}.pbf'
        ],
    tileSourceLayer: 'integrated',
    color: { /* will be processed both into style json for paint circle-color property, and for legend. 
            what's right property name?? is color also listing values used in the summary? 
            should this just be made part of the filter? that might allow to address multiple properties */
        field: 'Type',
        values: {
            'bioenergy': 'green',
            'coal': 'red',
            'geothermal': 'blue',
            'hydro': 'blue',
            'nuclear': 'grey',
            'oil/gas': 'red',
            'solar': 'green',
            'wind': 'green'
        }
    },
    minRadius: 1,
    maxRadius: 10,
    highZoomMinRadius: 4,
    highZoomMaxRadius: 32,
    interpolateExponent: 1.5,
    filters: [
        {
            field: 'Type',
            values: ['coal','oil/gas','nuclear','geothermal','hydro','bioenergy','solar','wind'],
            primary: true
        },
        {
            field: 'Status',
            /* values need to be specified for ordering */
            values: ['operating','construction','pre-construction','permitted','pre-permit','announced','retired','cancelled','shelved','mothballed','inactive']
        }
    ],
    nameField: 'Plant/project name',
    statusField: 'Status',
    capacityField: 'Capacity (MW)',
    capacityLabel: 'Capacity (MW)',
    linkField: 'Wiki URL',
    countryField: 'Country',
    searchFields: { 'Project': ['Plant/project name'], 
        'Companies': ['Owner', 'Parent'],
        'Start Year': ['Start year']
    },
    assetFullLabel: "plants",
    assetLabel: "Plants",
    img_detail_zoom: 15,
    tableHeaders: {
        values: ['Plant/project name','Unit/phase name', 'Owner', 'Parent', 'Capacity (MW)', 'Status', 'Subnational unit(s)', 'Country', 'Start year'],
        labels: ['Plant/project name','Unit/phase name','Owner','Parent','Capacity (MW)','Status','Subnational unit (province/state)','Country','Start year'],
        clickColumns: 'Plant/project name'
    },
    detailView: {
        'Plant/project name': {'display': 'heading'},
        'Owner': {'label': 'Owner'},
        'Parent': {'label': 'Parent'},
        'Technology': {'display': 'join', 'label': ['Technology', 'Technologies']},
        'Fuel': {'display': 'join', 'label': ['Fuel Type', 'Fuel Types']},
        'Start year': {'display': 'range', 'label': ['Start Year', 'Start Year Range']},
        'Subnational unit (province/state)': {'display': 'location'},
        'Country': {'display': 'location'}
    },
    zoomFactor: .8
};
