var config = {
    tiles: [
        //'https://gem.dev.c10e.org/africa_energy_tracker-2024-06-11/{z}/{x}/{y}.pbf'
        'http://127.0.0.1:8000/trackers/africa-energy-tracker/data/africa_energy_tracker-2024-06-18.dir/{z}/{x}/{y}.pbf'
        ],
    tileSourceLayer: 'africa_energy_tracker',
    geometries: ['Point','LineString'],
    center: [30, 0],
    zoomFactor: 1.5,
    color: {
        field: 'status',
        values: {
            'operating': 'red',
            'announced': 'green',
            'discovered': 'green',
            'pre-construction': 'blue',
            'pre-permit': 'blue',
            'proposed': 'green',
            'construction': 'blue',
            'in development': 'blue',
            'retired': 'grey',
            'idle': 'grey',
            'cancelled': 'grey',
            'decommissioned': 'grey',
            'mothballed': 'grey',
            'shelved': 'grey',
            'shut in': 'grey'
        }
    },
    //filter values should have no spaces
    filters: [
        {
            field: 'status',
            values: ['operating','announced','discovered','proposed','pre-construction','construction','pre-permit','in development','retired','decommissioned','idle',
                'cancelled','mothballed','shelved','shut in']
        }
    ],
    capacityField: 'cleaned_cap',
    //can be string for single value, or hash. always single value is showMaxCapacity is true
    capacityLabel: {
        field: 'tracker',
        values: {
            'GWPT': 'Capacity (MW)',
            'GSPT': 'Capacity (MW)',
            'GOIT': 'Capacity (MW)',
            'GOGPT': 'Capacity (MW)',
            'GOGET': 'Production (million bbl)',
            'GHPT': 'Capacity (MW)',
            'GGIT': 'Capacity (MW)',
            'GCPT': 'Capacity (MW)',
            'GBPT': 'Capacity (MW)'
        }
    },
    showMaxCapacity: false,

    assetFullLabel: "",
    //can be string for single value, or hash
    assetLabel: {
        field: 'tracker',
        values: {
            'GWPT': 'units',
            'GSPT': 'phases',
            'GOIT': 'units',
            'GOGPT': 'units',
            'GOGET': 'extraction areas',
            'GHPT': 'units',
            'GGIT': 'units',
            'GCPT': 'units',
            'GBPT': 'units'
        }
    },
    nameField: 'name',

    countryFile: 'countries.js',
    allCountrySelect: false,
    countryField: 'area',
    //if multicountry, always end values with a comma
    multiCountry: true,

    tableHeaders: {
        values: ['tracker','project','unit', 'type', 'parent', 'capacity', 'status', 'area', 'start_year'],
        labels: ['Tracker', 'Plant','Unit', 'Type','Parent','Capacity (MW)','Status','Countries','Start year'],
        clickColumns: ['project'],
        rightAlign: ['unit','capacity','start_year']
    },
    searchFields: { 'Project': ['name'], 
        'Companies': ['owner', 'parent'],
        'Start Year': ['start_year']
    },
    detailView: {
        'name': {'display': 'heading'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'tracker': {'label': 'Tracker'},
        'area': {'display': 'location'}
    }

};
