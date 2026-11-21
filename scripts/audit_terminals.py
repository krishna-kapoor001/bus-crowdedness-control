import json

stops = json.load(open('data/processed/stop_profiles.json', encoding='utf-8'))

# Check which ones are actual terminals/depots/ISBTs
major_keywords = ['isbt', 'terminal', '(t)', 'depot', 'bus stand']

actual_terminals = []
for s in stops:
    name_low = s['name'].lower()
    if any(k in name_low for k in major_keywords):
        actual_terminals.append(s)

print(f"Total stops: {len(stops)}")
print(f"Stops with actual terminal/depot/ISBT in name: {len(actual_terminals)}")
for t in actual_terminals:
    print(f"  {t['name']} -> ({t['latitude']}, {t['longitude']})")
