import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

# Rule-based zone checks based on well-known locality keywords
zone_rules = [
    # South Delhi keywords: Badarpur, Mehrauli, Saket, Sangam Vihar, Okhla, Kalkaji, Tuglakabad/Tehkhand, Prehladpur, Chhatarpur, Madangir, Khanpur, Lado Sarai
    (['badarpur', 'mehrauli', 'saket', 'sangam vihar', 'okhla', 'kalkaji', 'tehkhand', 'prehladpur', 'chhatarpur', 'madangir', 'khanpur', 'lado sarai'],
     lambda lat, lon: 28.45 <= lat <= 28.58 and 77.14 <= lon <= 77.32, 'South Delhi (Lat 28.45-28.58, Lon 77.14-77.32)'),

    # North / North-West keywords: Rohini, Narela, Bawana, Alipur, Badli, Azadpur, Model Town, Jahangir, Swaroop Nagar, Shahbad
    (['rohini', 'narela', 'bawana', 'alipur', 'badli', 'azadpur', 'model town', 'jahangir', 'swaroop nagar', 'shahbad'],
     lambda lat, lon: 28.68 <= lat <= 28.88 and 77.00 <= lon <= 77.22, 'North Delhi (Lat 28.68-28.88, Lon 77.00-77.22)'),

    # South-West keywords: Najafgarh, Nazafgarh, Dwarka, Kapashera, Dichau, Kair, Chhawla, Samalkha, Dhansa
    (['najafgarh', 'nazafgarh', 'dwarka', 'kapashera', 'dichau', 'kair', 'chhawla', 'samalkha', 'dhansa'],
     lambda lat, lon: 28.50 <= lat <= 28.64 and 76.90 <= lon <= 77.09, 'South-West Delhi (Lat 28.50-28.64, Lon 76.90-77.09)'),

    # East Delhi / Trans-Yamuna keywords: Mayur Vihar, Anand Vihar, Shahdara, Seelampur, Yamuna Vihar, Nand Nagri, Laxmi Nagar, Shakarpur, Dilshad Garden, Gazipur
    (['mayur vihar', 'anand vihar', 'shahdara', 'seelampur', 'seelam pur', 'yamuna vihar', 'nand nagri', 'nand nagari', 'laxmi nagar', 'shakarpur', 'dilshad garden', 'gazipur', 'geeta colony', 'kalyanpuri'],
     lambda lat, lon: 28.58 <= lat <= 28.72 and 77.25 <= lon <= 77.36, 'East Delhi (Lat 28.58-28.72, Lon 77.25-77.36)'),

    # West Delhi keywords: Janakpuri, Uttam Nagar, Punjabi Bagh, Tilak Nagar, Rajouri, Nangloi, Karampura, Mayapuri, Shadipur, Moti Nagar, Paschim Vihar, Peera Garhi
    (['janakpuri', 'uttam nagar', 'punjabi bagh', 'tilak nagar', 'rajouri', 'nangloi', 'karampura', 'mayapuri', 'maya puri', 'shadipur', 'shadi pur', 'moti nagar', 'paschim vihar', 'peera garhi', 'peeragarhi'],
     lambda lat, lon: 28.61 <= lat <= 28.69 and 77.04 <= lon <= 77.17, 'West Delhi (Lat 28.61-28.69, Lon 77.04-77.17)')
]

misplaced = []
for s in stops:
    name_low = s['name'].lower()
    lat = s['latitude']
    lon = s['longitude']
    
    for keywords, validator, zone_desc in zone_rules:
        matched_kw = [k for k in keywords if k in name_low]
        if matched_kw:
            if not validator(lat, lon):
                misplaced.append((s['name'], matched_kw, (lat, lon), zone_desc))
            break

print(f"Total misplaced stops detected by geographical zone rules: {len(misplaced)}")
for m in misplaced:
    print(f"  ! '{m[0]}' (keyword: {m[1]}): current [{m[2][0]}, {m[2][1]}] -> Expected in {m[3]}")
