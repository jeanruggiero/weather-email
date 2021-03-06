import json

with open('../data/cities.json') as f:
    cities = json.load(f)

with open('locations.json', 'w') as f:
    f.write('[')
    i = 1
    for record in cities['records']:
        f.write(f'''{{
        "model": "newsletter.location",
        "pk": {i},
        "fields": {{
            "city": "{record['fields']['city']}",
            "state": "{record['fields']['state']}",
            "latitude": {record['fields']['coordinates'][0]},
            "longitude": {record['fields']['coordinates'][1]}
        }}
        }},\n''')
        i = i + 1

    f.write(']')
