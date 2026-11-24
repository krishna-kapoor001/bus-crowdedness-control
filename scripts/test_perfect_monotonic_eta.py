import json, math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def format_time_12h(mins_from_midnight: int) -> str:
    mins = int(round(mins_from_midnight)) % (24 * 60)
    h = mins // 60
    m = mins % 60
    ampm = "PM" if h >= 12 else "AM"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12:02d}:{m:02d} {ampm}"

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops_meta = {s['name']: s for s in json.load(f)}

def build_perfect_eta_corridor(orig_name, dest_name, start_time_str="08:30"):
    o = stops_meta.get(orig_name)
    d = stops_meta.get(dest_name)
    if not o or not d:
        return None

    o_lat, o_lon = o['latitude'], o['longitude']
    d_lat, d_lon = d['latitude'], d['longitude']
    
    straight_dist_km = haversine(o_lat, o_lon, d_lat, d_lon) / 1000.0
    total_road_km = max(3.5, round(straight_dist_km * 1.25, 1))
    
    # Parse departure time
    h, m = map(int, start_time_str.split(':'))
    start_mins = h * 60 + m
    is_peak = (7 <= h <= 10) or (17 <= h <= 20)
    
    # Realistic commercial speed in Delhi traffic:
    # Peak: ~17 km/h | Off-peak: ~23 km/h
    speed_kmh = 17.0 if is_peak else 23.0
    total_travel_mins = (total_road_km / speed_kmh) * 60.0
    
    # Vector from O to D
    vec_lat = d_lat - o_lat
    vec_lon = d_lon - o_lon
    vec_len_sq = vec_lat**2 + vec_lon**2
    
    # Find intermediate candidate stops along the corridor
    buffer_m = min(1800, max(600, straight_dist_km * 100))
    candidates = []
    
    for name, s in stops_meta.items():
        if name == orig_name or name == dest_name:
            continue
        lat, lon = s['latitude'], s['longitude']
        if vec_len_sq > 0:
            t = ((lat - o_lat)*vec_lat + (lon - o_lon)*vec_lon) / vec_len_sq
            if 0.08 <= t <= 0.92:
                proj_lat = o_lat + t * vec_lat
                proj_lon = o_lon + t * vec_lon
                dist_to_proj = haversine(lat, lon, proj_lat, proj_lon)
                if dist_to_proj <= buffer_m:
                    candidates.append({
                        'name': name,
                        't': t,
                        'latitude': lat,
                        'longitude': lon,
                        'is_hub': s.get('is_major_hub', False)
                    })
                    
    candidates.sort(key=lambda x: x['t'])
    
    # Pick 5 to 10 representative, well-spaced stops
    target_count = max(4, min(10, int(straight_dist_km / 1.5)))
    chosen_cands = []
    
    if len(candidates) <= target_count:
        chosen_cands = candidates
    else:
        # Pick hubs first, then evenly space
        step = len(candidates) / (target_count + 1)
        for idx in range(1, target_count + 1):
            chosen_cands.append(candidates[int(idx * step)])
            
    # Remove any duplicate names and sort strictly by t
    seen = {orig_name, dest_name}
    clean_cands = []
    for c in chosen_cands:
        if c['name'] not in seen:
            seen.add(c['name'])
            clean_cands.append(c)
    clean_cands.sort(key=lambda x: x['t'])
    
    all_stops = [{'name': orig_name, 't': 0.0, 'is_hub': o.get('is_major_hub', False)}]
    all_stops.extend(clean_cands)
    all_stops.append({'name': dest_name, 't': 1.0, 'is_hub': d.get('is_major_hub', False)})
    
    # Total duration = transit time + dwell time at intermediate stops
    total_dwell_mins = (len(all_stops) - 1) * 0.75
    final_total_mins = int(round(total_travel_mins + total_dwell_mins))
    
    total_cap = 65
    seat_cap = 35
    peak_pax = 78 if is_peak else 38
    
    timeline = []
    for i, st in enumerate(all_stops):
        prog = st['t']
        st_mins = int(round(final_total_mins * prog))
        st_km = round(total_road_km * prog, 1)
        clock_mins = start_mins + st_mins
        eta_str = format_time_12h(clock_mins)
        
        # Load profile
        if i == 0:
            cur_pax = int(peak_pax * 0.55)
            action = f"Trip Origin • Boarding (+{cur_pax} pax)"
        elif i == len(all_stops) - 1:
            cur_pax = 0
            action = f"Destination Terminus • All passengers alight"
        else:
            if prog < 0.6:
                cur_pax = int(peak_pax * (0.55 + 0.45 * (prog / 0.6)))
            else:
                cur_pax = int(peak_pax * (1.0 - 0.55 * ((prog - 0.6) / 0.4)))
            diff = cur_pax - timeline[-1]['onboard_pax']
            if diff > 3:
                action = f"Crowd Surge (+{diff} board)"
            elif diff < -3:
                action = f"Decongesting (-{abs(diff)} alight)"
            else:
                action = f"Steady Headway (Normal Exchange)"
                
        if cur_pax <= seat_cap:
            seats_status = f"{seat_cap - cur_pax} seats available"
            crowd_lvl = "LOW"
        elif cur_pax <= total_cap:
            standing = cur_pax - seat_cap
            seats_status = f"All {seat_cap} seats full • {standing} standing"
            crowd_lvl = "MODERATE"
        else:
            crush = cur_pax - total_cap
            seats_status = f"Crush load ({cur_pax} pax • {crush} over capacity)"
            crowd_lvl = "HIGH"
            
        timeline.append({
            'sequence': i + 1,
            'stop_name': st['name'],
            'eta_time': eta_str,
            'mins_from_start': st_mins,
            'dist_km': st_km,
            'onboard_pax': cur_pax,
            'capacity_pct': int(round((cur_pax / total_cap) * 100)),
            'seats_status': seats_status,
            'crowd_action': action,
            'crowd_level': crowd_lvl,
            'is_hub': st.get('is_hub', False)
        })
        
    return {
        'total_duration': final_total_mins,
        'total_distance_km': total_road_km,
        'departure_time': format_time_12h(start_mins),
        'arrival_time': format_time_12h(start_mins + final_total_mins),
        'stops_count': len(all_stops),
        'timeline': timeline
    }

# Test 4 major corridors across Delhi:
test_cases = [
    ("Saket", "Dhaula Kuan"),
    ("Kashmere Gate", "AIIMS"),
    ("Anand Vihar ISBT", "Shivaji Stadium"),
    ("Janakpuri", "Connaught Place")
]

for orig, dest in test_cases:
    res = build_perfect_eta_corridor(orig, dest)
    if res:
        print(f"\n=======================================================")
        print(f"TRIP: {orig} -> {dest}")
        print(f"Time: {res['departure_time']} -> {res['arrival_time']} ({res['total_duration']} mins | {res['total_distance_km']} km | {res['stops_count']} stops)")
        print(f"-------------------------------------------------------")
        for st in res['timeline']:
            print(f"  [{st['eta_time']} | +{st['mins_from_start']:02d}m | {st['dist_km']:4.1f}km] {st['stop_name'][:25]:25} | {st['onboard_pax']:2d}/65 pax ({st['capacity_pct']:3d}%) | {st['crowd_action']}")
