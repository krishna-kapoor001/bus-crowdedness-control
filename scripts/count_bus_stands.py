import sqlite3

conn = sqlite3.connect('data/flowpulse.db')
c = conn.cursor()

c.execute('SELECT count(*) FROM stops WHERE is_major_hub = 1')
hubs_count = c.fetchone()[0]

c.execute('SELECT count(*) FROM stops WHERE is_major_hub = 0')
stops_count = c.fetchone()[0]

c.execute('SELECT count(*) FROM stops')
total_count = c.fetchone()[0]

print(f"Total Unique Locations in Delhi: {total_count}")
print(f"Total Major Bus Stands / Terminals / Depots (Black Dots): {hubs_count}")
print(f"Total Regular Bus Stops (Blue Dots): {stops_count}")

# Breakdown by type
c.execute("""
SELECT name FROM stops WHERE is_major_hub = 1 ORDER BY name
""")
all_hubs = [r[0] for r in c.fetchall()]

terminals = [h for h in all_hubs if 'terminal' in h.lower()]
depots = [h for h in all_hubs if 'depot' in h.lower()]
isbts = [h for h in all_hubs if 'isbt' in h.lower()]
bus_stands = [h for h in all_hubs if 'stand' in h.lower()]
other_major_hubs = [h for h in all_hubs if h not in terminals and h not in depots and h not in isbts and h not in bus_stands]

print(f"\nBreakdown of {hubs_count} Bus Stands & Major Hubs:")
print(f"  1. Bus Terminals (e.g. Shahdara, Mori Gate, Nehru Place): {len(terminals)}")
print(f"  2. DTC Bus Depots (e.g. Yamuna Vihar Depot, Shadipur Depot): {len(depots)}")
print(f"  3. Inter-State Bus Terminals / ISBTs (Kashmere Gate, Anand Vihar, Sarai Kale Khan): {len(isbts)}")
print(f"  4. Designated Regional Bus Stands (e.g. Najafgarh Bus Stand, Alipur): {len(bus_stands)}")
print(f"  5. Key Transit Junctions / Corridors Hubs (e.g. Dhaula Kuan, Darya Ganj): {len(other_major_hubs)}")

print("\nSample List of Bus Stands / Depots / Terminals:")
for h in all_hubs[:20]:
    print(f"  • {h}")

conn.close()
