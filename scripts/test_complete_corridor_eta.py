import json, math, os

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

def build_realistic_route(orig_name, dest_name, start_time_str="08:30"):
    o = stops_meta.get(orig_name)
    d = stops_meta.get(dest_name)
    if not o or not d:
        return None

    o_lat, o_lon = o['latitude'], o['longitude']
    d_lat, d_lon = d['latitude'], d['longitude']
    
    total_straight_dist = haversine(o_lat, o_lon, d_lat, d_lon)
    total_road_dist_est = total_straight_dist * 1.25 # Delhi road network winding factor
    
    # Vector from O to D
    vec_lat = d_lat - o_lat
    vec_lon = d_lon - o_lon
    vec_len_sq = vec_lat**2 + vec_lon**2
    
    candidates = []
    # Search corridor buffer (width proportional to total distance, max 2.5 km)
    buffer_m = min(2500, max(800, total_straight_dist * 0.18))
    
    for name, s in stops_meta.items():
        if name == orig_name or name == dest_name:
            continue
        lat, lon = s['latitude'], s['longitude']
        if vec_len_sq > 0:
            t = ((lat - o_lat)*vec_lat + (lon - o_lon)*vec_lon) / vec_len_sq
            if 0.05 <= t <= 0.95:
                proj_lat = o_lat + t * vec_lat
                proj_lon = o_lon + t * vec_lon
                dist_to_proj = haversine(lat, lon, proj_lat, proj_lon)
                if dist_to_proj <= buffer_m:
                    candidates.append({
                        'name': name,
                        't': t,
                        'dist_to_proj': dist_to_proj,
                        'latitude': lat,
                        'longitude': lon,
                        'is_hub': s.get('is_major_hub', False),
                        'boardings': s.get('monthly_boardings', 1000),
                        'alightings': s.get('monthly_alightings', 950)
                    })
    
    # Sort by progress t
    candidates.sort(key=lambda x: x['t'])
    
    # Filter candidates with realistic minimum spacing (at least 600m between stops)
    selected_stops = [o]
    last_stop = o
    
    for cand in candidates:
        dist_from_last = haversine(last_stop['latitude'], last_stop['longitude'], cand['latitude'], cand['longitude'])
        dist_to_dest = haversine(cand['latitude'], cand['longitude'], d['latitude'], d['longitude'])
        # Spacing condition: at least 700m from previous, and at least 800m before destination
        if dist_from_last >= 700 and dist_to_dest >= 800:
            selected_stops.append(cand)
            last_stop = cand
            
    selected_stops.append(d)
    
    # Compute precise distance-driven ETAs
    h, m = map(int, start_time_str.split(':'))
    start_mins = h * 60 + m
    is_peak = (7 <= h <= 10) or (17 <= h <= 20)
    # Peak commercial bus speed in Delhi is ~16.5 km/h (275 m/min); off-peak is ~22 km/h (366 m/min)
    speed_mpm = 275.0 if is_peak else 360.0
    
    cum_mins = 0.0
    cum_dist_km = 0.0
    total_cap = 65
    seat_cap = 35
    cur_pax = 34 if is_peak else 20
    
    timeline = []
    
    for i, s in enumerate(selected_stops):
        s_name = s['name']
        is_hub = s.get('is_major_hub', False)
        
        if i > 0:
            prev = selected_stops[i - 1]
            seg_straight = haversine(prev['latitude'], prev['longitude'], s['latitude'], s['longitude'])
            seg_road = seg_straight * 1.25 # winding factor
            cum_dist_km += (seg_road / 1000.0)
            
            travel_time_mins = seg_road / speed_mpm
            dwell_mins = 1.2 if is_hub else 0.6
            cum_mins += (travel_time_mins + dwell_mins)
            
            # Dynamic passenger continuity
            if i == len(selected_stops) - 1:
                cur_pax = 0
                action = f"Destination Terminus • All passengers alight"
            else:
                prog = i / (len(selected_stops) - 1)
                # Middle bottleneck surge
                if 0.3 <= prog <= 0.7 and is_peak:
                    board_surge = 12 if is_hub else 6
                    alight_drop = 3
                elif prog > 0.7:
                    board_surge = 4
                    alight_drop = 14 if is_hub else 7
                else:
                    board_surge = 8
                    alight_drop = 2
                    
                cur_pax = max(10, min(total_cap + 18, cur_pax + board_surge - alight_drop))
                diff = board_surge - alight_drop
                if diff > 5:
                    action = f"Crowd Surge (+{diff} board)"
                elif diff < -5:
                    action = f"Decongesting (-{abs(diff)} alight)"
                else:
                    action = f"Steady exchange (+{board_surge}/-{alight_drop})"
        else:
            action = f"Trip Origin • Boarding (+{cur_pax} pax)"
            
        clock_mins = start_mins + int(round(cum_mins))
        eta_label = format_time_12h(clock_mins)
        
        # Seat availability calculation
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
            'stop_name': s_name,
            'eta_time': eta_label,
            'mins_from_start': int(round(cum_mins)),
            'dist_km': round(cum_dist_km, 1),
            'onboard_pax': cur_pax,
            'capacity_pct': int(round((cur_pax / total_cap) * 100)),
            'seats_status': seats_status,
            'crowd_action': action,
            'crowd_level': crowd_lvl,
            'is_hub': is_hub
        })
        
    return {
        'total_duration': int(round(cum_mins)),
        'total_distance_km': round(cum_dist_km, 1),
        'departure_time': format_time_12h(start_mins),
        'arrival_time': format_time_12h(start_mins + int(round(cum_mins))),
        'stops_count': len(selected_stops),
        'timeline': timeline
    }

# Test 3 different corridors across Delhi:
test_cases = [
    ("Saket", "Dhaula Kuan"),
    ("Kashmere Gate", "AIIMS"),
    ("Anand Vihar ISBT", "Shivaji Stadium")
]

for orig, dest in test_cases:
    res = build_realistic_route(orig, dest)
    if res:
        print(f"\n=======================================================")
        print(f"TRIP: {orig} -> {dest}")
        print(f"Time: {res['departure_time']} -> {res['arrival_time']} ({res['total_duration']} mins | {res['total_distance_km']} km | {res['stops_count']} stops)")
        print(f"-------------------------------------------------------")
        for st in res['timeline']:
            print(f"  [{st['eta_time']} | +{st['mins_from_start']:02d}m | {st['dist_km']:4.1f}km] {st['stop_name'][:25]:25} | {st['onboard_pax']:2d}/65 pax ({st['capacity_pct']:3d}%) | {st['crowd_action']}")
