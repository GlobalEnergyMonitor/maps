var config = {
    accessToken: 'pk.eyJ1IjoiZWFydGhyaXNlIiwiYSI6ImNqeDExNmtrZzAwM2E0OW16eHZ1dzg1eWEifQ.8LTFXyY-n7OsZOoWN9ONPQ',
    json: 'coal.json',
    paint: {
        'circle-radius': ["/", ["to-number", ["get", "capacity"]], 200],
        'circle-color': [
            'match', ['get', 'status'],
                'operating', '#845440',
                'construction', '#ff0000',
                'retired',  '#58a1a1',
                'cancelled', '#4cdb4c',
                'mothballed', '#d6a490',
                'pre-permit', '#ffa500',
                'shelved', '#5974a2',
                'announced', '#f3ff00',
                'permitted', '#f26c4f',
                /* other */ '#000000'
            ]
    }
}