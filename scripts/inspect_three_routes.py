import json

data = json.load(open('data/processed/corridors_routed.json', encoding='utf-8'))
for c in data:
    if c['id'] in ['route-623', 'route-894', 'route-548']:
        print(c['id'], c['name'])
        print('  Stops:', c['stops'])
        print('  First pt:', c['coordinates'][0], 'Last pt:', c['coordinates'][-1])
