var config = {
    geojson: 'https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/hydro/2026-03/LATAM_map_2026-03-19.geojson',
    geometries: ['Point','LineString'],
    center: [-60, 0], //previously was -90, -14
    zoomFactor: 1.4,
    img_detail_zoom: 10,
    statusField: 'status-legend-regional',
    statusDisplayField: 'status',
    color: {
        field: 'tracker-custom',
        values: {
            'GOGPT': 'blue',
            'GOGET-oil': 'red',
            'GOIT': 'green',
            'GGIT': 'green',
            'GGIT-import':'green',
            'GGIT-export':'green',
            'GCPT': 'blue',
            'GCMT': 'red',
            'GCTT': 'green',
            'GBPT': 'blue',
            'GGPT': 'blue',
            'GNPT': 'blue',
            'GSPT': 'blue',
            'GWPT': 'blue',
            'GHPT': 'blue'
        }
    },
    //filter values should have no spaces
    filters: [
        {
            field: 'tracker-custom',
            values: ["GCPT", "GOGPT", "GBPT", "GNPT", "GSPT", "GWPT", "GHPT", "GGPT", "GOIT", "GGIT", "GGIT-import", "GGIT-export", "GCTT", "GOGET-oil", "GCMT"], 
            values_labels: ['coal units', 'oil&gas units', 'bioenergy units', 'nuclear units', 'solar phases', 'wind phases', 'hydropower plants', 'geothermal units', 'oil pipelines', 'gas pipelines', 'LNG import terminals', 'LNG export terminals', 'coal terminals', 'oil&gas extraction areas','coal mines'],
            primary: true
        },
        {
            field: 'status-legend-regional',
            label: 'Status',
            values: ['operating','proposed-plus','pre-construction-plus','construction-plus','retired-plus','cancelled','mothballed-plus','shelved', 'not-found'],
            values_labels: ['Operating','Proposed/Announced/Discovered','Pre-construction/Pre-permit/Permitted', 'Construction/In development','Retired/Closed/Decommissioned','Cancelled','Mothballed/Idle','Shelved', 'Not Found']
            //values_labels: ['Operating','Proposed+','Pre-construction+', 'Construction+','Retired+','Cancelled','Mothballed+','Shelved', 'Not Found']
// /Announced/Discovered /Pre-permit/Permitted Closed/Decommissioned  /Idle/Shut in /In development
        },

    ],
    capacityField: 'scaling-capacity',
    
    capacityDisplayField: 'capacity-table',

    //interpolate: ["cubic-bezier", 0, 0, 0, 1],
    //can be string for single value, or hash. always single value is showMaxCapacity is true
    capacityLabel: {
        field: 'tracker-custom',
        values: {
            'GCPT': 'MW',
            'GOGPT': 'MW',
            'GBPT':	'MW',
            'GNPT':	'MW',
            'GSPT':	'MW',
            'GSPT':	'MW',
            'GWPT':	'MW',
            'GHPT':	'MW',
            'GGPT':	'MW',
            'GOGET-oil': 'million boe/y', // remove because they dont have capacity is only relevant for scaling here Scott request
            'GOIT': 'boe/d',
            'GGIT':	'bcm/y of natural gas',
            'GGIT-import': 'MTPA of natural gas',
            'GGIT-export': 'MTPA of natural gas',            
            'GCMT':	'million tonnes coal/y', 
            'GCTT':	'million tonnes coal/y'
        }
    },
    // skipCapacitySum: '',

    showMaxCapacity: false,

    assetFullLabel: "Units / Phases / Pipelines", 
    //can be string for single value, or hash
    // not using assetLabel for now TODO
    assetLabel: 'units',

    nameField: 'name',
//    linkField: 'id',  

    countryFile: 'countries.js',
    allCountrySelect: true, // TODO bug when clicking Africa nothing gets selected but clicking all it does 
    countryField: 'areas',
    //if multicountry, always end values with a comma
    multiCountry: true,

    tableHeaders: {
        values: ['name','unit-name', 'owner', 'parent', 'capacity-table', 'units-of-m','status', 'areas', 'start-year', 'prod-coal','prod-oil', 'prod-year-oil', 'prod-gas', 'prod-year-gas', 'prod-coal', 'fuel', 'tracker-display',],
        labels: ['Name','Unit','Owner', 'Parent','Capacity', '','Status','Country/Area(s)','Start year', 'Production (million tonnes coal/y)', 'Production (million bbl/y)','Production year (oil)', 'Production (Million m³/y)', 'Production year (gas)', 'Coal Production (Mt)', 'Fuel', 'Facility Type'],
        clickColumns: ['name'],
        rightAlign: ['unit','capacity-table','prod-oil', 'prod-gas','start-year', 'prod-year-oil', 'prod-year-gas'], 
        removeLastComma: ['areas'], 
        toLocaleString: ['capacity-table'],
    },
    searchFields: { 'Project': ['name', 'name-search', 'pid'], 
        'Companies': ['owner', 'parent', 'owner-search', 'parent-search'],
        'Start Year': ['start-year'],
        'Infrastructure Type': ['tracker-display'],
        'Status': ['status', 'status-legend-regional'],
        'Province/State': ['subnat']
    },
    detailView: {
        'name': {'display': 'heading'},   
        'location-accuracy': {'label': 'Location Accuracy'},
  
        'prod-oil': {'label': 'Liquids Production (million bbl/y)'},
        'prod-gas': {'label': 'Gas Production (million m³/y)'},
        'prod-unspecified': {'label': 'Unspecified Hydrocarbons Production (million boe/y)'},
        'prod-year-oil': {'label': 'Production Year - Oil'},
        'prod-year-gas': {'label': 'Production Year - Gas'},
        'prod-year-unspecified': {'label': 'Production Year - Hydrocarbons (unspecified)'},
        'prod-coal': {'label': 'Production (million tonnes coal/y)'}, 
        'start-year': {'label': 'Start Year'},
        'owner': {'label': 'Owner'},
        'parent': {'label': 'Parent'},
        'river': {'label': 'River'},
        'tracker-display': {'label': 'Type'},
        'areas': {'label': 'Country/Area(s)'},
        'areas-subnat-sat-display': {'display': 'location'}, 
    },

        /* radius associated with minimum/maximum value on map */
    // minRadius: 2,
    // maxRadius: 10,
    minLineWidth: 1,
    maxLineWidth: 3,
    
    highZoomMinLineWidth: 1,
    highZoomMaxLineWidth: 3,


    // /* radius to increase min/max to under high zoom */
    // highZoomMinRadius: 4,
    // highZoomMaxRadius: 32,
    // highZoomMinLineWidth: 4,
    // highZoomMaxLineWidth: 32,



    // showAllPhases: true
};