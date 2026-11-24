import json, math

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops_meta = {s['name']: s for s in json.load(f)}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def format_time_12h(mins_from_midnight):
    mins = int(round(mins_from_midnight)) % (24 * 60)
    h = mins // 60
    m = mins % 60
    ampm = 'PM' if h >= 12 else 'AM'
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12:02d}:{m:02d} {ampm}"

def generate_timetable(stops_tuples, dep_time_str, road_km, speed_kmh, dwell_mins, peak_pax):
    h, m = map(int, dep_time_str.split(':'))
    start_mins = h * 60 + m
    
    transit_mins = (road_km / speed_kmh) * 60.0
    total_cap = 65
    seat_cap = 35
    
    timeline = []
    prev_mins = 0
    prev_pax = 0
    
    n = len(stops_tuples)
    for i, (name, prog, is_hub) in enumerate(stops_tuples):
        raw_transit = prog * transit_mins
        raw_dwell = i * dwell_mins
        raw_cum = int(round(raw_transit + raw_dwell))
        if i == 0:
            cum_mins = 0
        else:
            cum_mins = max(prev_mins + 1, raw_cum)
        prev_mins = cum_mins
        
        eta = format_time_12h(start_mins + cum_mins)
        dist_km = round(prog * road_km, 1)
        
        # Load calculation
        if i == 0:
            cur_pax = max(15, int(peak_pax * 0.50))
            action = f"Trip Origin • Boarding (+{cur_pax} pax)"
        elif i == n - 1:
            cur_pax = 0
            action = f"Destination Terminus • All {prev_pax} pax alight"
        else:
            if prog <= 0.55:
                cur_pax = int(peak_pax * (0.50 + 0.50 * (prog / 0.55)))
            else:
                cur_pax = int(peak_pax * (1.0 - 0.55 * ((prog - 0.55) / 0.45)))
            cur_pax = max(12, cur_pax)
            diff = cur_pax - prev_pax
            if diff >= 4:
                action = f"Crowd Surge (+{diff} board)"
            elif diff <= -4:
                action = f"Decongesting (-{abs(diff)} alight)"
            else:
                action = "Steady Headway • Normal Exchange"
                
        prev_pax = cur_pax
        
        if cur_pax <= seat_cap:
            seats_status = f"{seat_cap - cur_pax} seats available"
            crowd_lvl = "LOW"
        elif cur_pax <= total_cap:
            seats_status = f"All {seat_cap} seats full • {cur_pax - seat_cap} standing"
            crowd_lvl = "MODERATE"
        else:
            seats_status = f"Crush load ({cur_pax} pax • {cur_pax - total_cap} over capacity)"
            crowd_lvl = "HIGH"
            
        timeline.append({
            'sequence': i + 1,
            'stop_name': name,
            'eta': eta,
            'mins_from_start': cum_mins,
            'dist_km': dist_km,
            'onboard_pax': cur_pax,
            'seats_status': seats_status,
            'crowd_action': action,
            'crowd_level': crowd_lvl
        })
    return timeline

# Test on Kashmere Gate to AIIMS
o = stops_meta['ISBT Kashmere Gate']
d = stops_meta['AIIMS Transit Hub']
straight_km = haversine(o['latitude'], o['longitude'], d['latitude'], d['longitude'])
road_km = max(1.8, round(straight_km * 1.25, 1))

sample_stops = [
    ('ISBT Kashmere Gate', 0.0, True),
    ('Red Fort', 0.12, True),
    ('Delhi Gate', 0.25, True),
    ('ITO Arterial', 0.40, True),
    ('Pragati Maidan', 0.52, True),
    ('Sundar Nagar', 0.65, False),
    ('Lodhi Road Crossing', 0.78, False),
    ('South Extension', 0.90, True),
    ('AIIMS Transit Hub', 1.0, True)
]

tl = generate_timetable(sample_stops, '08:30', road_km, 22.0, 0.8, 76)
print(f"Total Stops: {len(tl)} | Road: {road_km}km | Dep: {tl[0]['eta']} -> Arr: {tl[-1]['eta']}")
for s in tl:
    print(f"#{s['sequence']:02d} | {s['eta']} (+{s['mins_from_start']:02d}m, {s['dist_km']}km) | {s['stop_name']:25s} | Pax: {s['onboard_pax']:02d} | {s['crowd_action']:35s} | {s['seats_status']}")
