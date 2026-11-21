import json

stops = json.load(open('data/processed/stop_profiles.json', encoding='utf-8'))
print("=== AUROBINDO CORRIDOR STOPS IN STOP_PROFILES.JSON ===")
for s in stops:
    name = s['name'].lower()
    if any(k in name for k in ['green park', 'adhchini', 'safdarjung', 'mehrauli terminal', 'iit gate', 'qutub minar']):
        print(f"{s['name']:<40}: ({s['latitude']:.5f}, {s['longitude']:.5f}) - Hub: {s.get('is_major_hub', False)}")
