import json

stops = json.load(open('data/processed/stop_profiles.json', encoding='utf-8'))

print(f"Total stops: {len(stops)}")
print("\n--- Checking for potential location mismatches ---")

# Specific checks
suspicious = []
for s in stops:
    name = s['name']
    name_low = name.lower()
    lat, lon = s['latitude'], s['longitude']
    
    # Check 1: Nangloi should be around lat ~28.68, lon ~77.06, NOT Najafgarh (lat 28.61, lon 76.98)
    if 'nangloi' in name_low and (lat < 28.65 or lon < 77.02):
        suspicious.append((name, lat, lon, "Should be Nangloi (28.682, 77.065), not Najafgarh"))
    
    # Check 2: Rohini should be around 28.70-28.75, 77.05-77.13
    if 'rohini' in name_low and not (28.68 <= lat <= 28.76 and 77.04 <= lon <= 77.15):
        suspicious.append((name, lat, lon, "Rohini coords out of range"))
        
    # Check 3: Dwarka should be around 28.57-28.62, 77.01-77.08
    if 'dwarka' in name_low and not (28.55 <= lat <= 28.63 and 77.00 <= lon <= 77.09):
        suspicious.append((name, lat, lon, "Dwarka coords out of range"))
        
    # Check 4: Anand Vihar should be around 28.64-28.66, 77.30-77.33
    if 'anand vihar' in name_low and not (28.63 <= lat <= 28.67 and 77.30 <= lon <= 77.33):
        suspicious.append((name, lat, lon, "Anand Vihar coords out of range"))
        
    # Check 5: Kashmere Gate should be around 28.66-28.68, 77.22-77.24
    if 'kashmere' in name_low and not (28.65 <= lat <= 28.68 and 77.21 <= lon <= 77.24):
        suspicious.append((name, lat, lon, "Kashmere Gate coords out of range"))

    # Check 6: Badarpur should be around 28.49-28.51, 77.29-77.32
    if 'badarpur' in name_low and not (28.48 <= lat <= 28.52 and 77.28 <= lon <= 77.32):
        suspicious.append((name, lat, lon, "Badarpur coords out of range"))

    # Check 7: Dhaula Kuan should be around 28.58-28.60, 77.15-77.18
    if 'dhaula kuan' in name_low and not (28.58 <= lat <= 28.61 and 77.15 <= lon <= 77.18):
        suspicious.append((name, lat, lon, "Dhaula Kuan coords out of range"))

    # Check 8: Mehrauli should be around 28.51-28.53, 77.17-77.19
    if 'mehrauli' in name_low and not (28.50 <= lat <= 28.53 and 77.16 <= lon <= 77.20):
        suspicious.append((name, lat, lon, "Mehrauli coords out of range"))

    # Check 9: Janakpuri should be around 28.61-28.64, 77.07-77.10
    if 'janakpuri' in name_low and not (28.60 <= lat <= 28.64 and 77.06 <= lon <= 77.11):
        suspicious.append((name, lat, lon, "Janakpuri coords out of range"))

    # Check 10: Shahdara should be around 28.66-28.69, 77.27-77.30
    if 'shahdara' in name_low and not (28.65 <= lat <= 28.69 and 77.27 <= lon <= 77.30):
        suspicious.append((name, lat, lon, "Shahdara coords out of range"))

print(f"Suspicious mismatches found: {len(suspicious)}")
for s in suspicious:
    print(f"  {s[0]} -> ({s[1]}, {s[2]}) | Reason: {s[3]}")
