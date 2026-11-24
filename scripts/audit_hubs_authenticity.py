import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

hubs = [s for s in stops if s.get('is_major_hub')]

# Non-passenger depots, workshops, military depots, minor colony loop turnarounds:
suspect_hubs = [
    'Supply Depot (Delhi Cantt)',      # Military supply depot, not a passenger bus stand
    'Ordnance Depot (Shakurbasti)',    # Military ordnance depot, not a passenger bus stand
    'Okhla Depot Iv Cws Ii',           # Central Workshop II, not a public terminal
    'Yamuna Vihar DTC Depot',          # Sits on residential alley
    'Rohini Sec 22 Terminal',          # Bare road on outer colony edge
    'Tara Apartments Terminal',        # Local apartment turnaround
    'Jai Mata Market Tri Nagar Terminal', # Local market street, not a bus stand
    'Khayala Colony Terminal',         # Local JJ colony turnaround
    'E Block Jahangir Puri Terminal',  # Minor block turnaround
    'East Vinod Nagar Depot',          # Local depot
    'Rohini Depot 2',                  # Redundant depot
    'Rohini Depot 3',                  # Redundant depot
    'Sriniwaspuri DTC Depot (SNPD)',   # Deprecated depot
    'Malka Ganj Terminal',             # Local circle, not a major hub
    'West Enclave Terminal',           # Colony gate
    'BBM DTC Depot (Kingsway Camp)',   # Maintenance depot
    'Dichau Kalan Depot',              # Rural boundary depot
    'Vivek Vihar Terminal',            # Local colony terminus
    'Ambedkar Stadium Terminal',       # 300m from Delhi Gate / Ambedkar Stadium
    'Dilshad Garden Depot Cluster',    # Cluster point, not distinct stand
    'Janak Puri B 1 Terminal',         # Just Janakpuri East metro gate
    'Kalyan Puri Terminal',            # 200m from Kalyanpuri crossing
    'Mangla Puri Terminal',            # Palam colony loop
    'Jal Vihar Terminal',              # Lajpat Nagar colony loop
    'Jheel Terminal',                  # Geeta Colony small loop
    'Karampura Terminal',              # Moti Nagar colony loop
    'Keshopur Depot',                  # Outer ring turnaround
    'Peera Garhi Depot',               # Peeragarhi crossing is the real hub
    'Pragati Maidan Terminal',         # Near Supreme Court
    'Safdurjung Terminal',             # Safdarjung hospital/tomb loop
]

print("Suspect Hubs currently marked as Major Bus Stands (Black Dots):")
for s in hubs:
    if s['name'] in suspect_hubs:
        print(f"  SUSPECT: '{s['name']}' at ({s['latitude']}, {s['longitude']}) - boardings={s.get('monthly_boardings')}")

print(f"\nTotal suspect: {len([s for s in hubs if s['name'] in suspect_hubs])} out of {len(hubs)}")
