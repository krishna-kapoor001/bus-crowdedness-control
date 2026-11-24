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

def resolve_universal_corridor(orig_name, dest_name, dep_time_str="08:30"):
    o = stops_meta[orig_name]
    d = stops_meta[dest_name]
    straight_km = haversine(o['latitude'], o['longitude'], d['latitude'], d['longitude'])
    road_km = max(1.8, round(straight_km * 1.25, 1))
    
    o_lat, o_lon = o['latitude'], o['longitude']
    d_lat, d_lon = d['latitude'], d['longitude']
    v_lat, v_lon = d_lat - o_lat, d_lon - o_lon
    v_len_sq = v_lat**2 + v_lon**2
    
    buffer_km = 0.9 if road_km < 6 else (1.5 if road_km < 15 else 2.2)
    candidates = []
    for name, s in stops_meta.items():
        if name == orig_name or name == dest_name:
            continue
        lat, lon = s['latitude'], s['longitude']
        if v_len_sq > 0:
            t = ((lat - o_lat)*v_lat + (lon - o_lon)*v_lon) / v_len_sq
            if 0.04 <= t <= 0.96:
                proj_lat = o_lat + t * v_lat
                proj_lon = o_lon + t * v_lon
                perp_km = haversine(lat, lon, proj_lat, proj_lon)
                if perp_km <= buffer_km:
                    candidates.append({'name': name, 't': t, 'is_hub': s.get('is_major_hub', False)})
    candidates.sort(key=lambda x: x['t'])
    
    # 1. Regular Stops selection
    target_reg = max(3, min(14, int(road_km / 1.0)))
    if len(candidates) <= target_reg:
        reg_cands = candidates
    else:
        step = len(candidates) / (target_reg + 1)
        reg_cands = [candidates[int(idx * step)] for idx in range(1, target_reg + 1)]
        
    # Deduplicate while preserving order
    seen_reg = {orig_name, dest_name}
    clean_reg = []
    for c in reg_cands:
        if c['name'] not in seen_reg:
            seen_reg.add(c['name'])
            clean_reg.append(c)
    clean_reg.sort(key=lambda x: x['t'])
    reg_stops = [(orig_name, 0.0, True)] + [(c['name'], c['t'], c['is_hub']) for c in clean_reg] + [(dest_name, 1.0, True)]
    
    # 2. Express Stops selection (Major Hubs prioritized)
    hubs = [c for c in candidates if c['is_hub']]
    target_exp = max(2, min(5, int(road_km / 3.0)))
    if len(hubs) <= target_exp and hubs:
        exp_cands = hubs
    elif len(hubs) > target_exp:
        step_h = len(hubs) / (target_exp + 1)
        exp_cands = [hubs[int(idx * step_h)] for idx in range(1, target_exp + 1)]
    else:
        # If no hubs, pick from reg
        step_e = len(clean_reg) / (target_exp + 1) if clean_reg else 1
        exp_cands = [clean_reg[int(idx * step_e)] for idx in range(1, min(len(clean_reg)+1, target_exp + 1))]
        
    seen_exp = {orig_name, dest_name}
    clean_exp = []
    for c in exp_cands:
        if c['name'] not in seen_exp:
            seen_exp.add(c['name'])
            clean_exp.append(c)
    clean_exp.sort(key=lambda x: x['t'])
    exp_stops = [(orig_name, 0.0, True)] + [(c['name'], c['t'], c['is_hub']) for c in clean_exp] + [(dest_name, 1.0, True)]
    
    return road_km, reg_stops, exp_stops

test_pairs = [
    ('ISBT Kashmere Gate', 'AIIMS Transit Hub'),
    ('Anand Vihar ISBT', 'Shivaji Stadium Terminal'),
    ('C 2 B Janakpuri', 'Dhaula Kuan'),
    ('Saket', 'IIT Gate (1)'),
    ('Narela', 'Azadpur Terminal'),
    ('Badarpur Border Terminal', 'Nehru Place Terminal')
]

for o_name, d_name in test_pairs:
    road_km, reg_stops, exp_stops = resolve_universal_corridor(o_name, d_name)
    # Express timetable (Speed 22 km/h in peak, 0.8 min dwell)
    h, m = 8, 30
    start_mins = h * 60 + m
    transit_mins = (road_km / 22.0) * 60.0
    exp_tl = []
    prev_m = 0
    for i, (st, t, is_h) in enumerate(exp_stops):
        raw_m = int(round(t * transit_mins + i * 0.8))
        cum_m = 0 if i == 0 else max(prev_m + 1, raw_m)
        prev_m = cum_m
        exp_tl.append((st, format_time_12h(start_mins + cum_m), cum_m))
        
    # Regular timetable (Speed 17 km/h in peak, 0.6 min dwell)
    transit_reg = (road_km / 17.0) * 60.0
    reg_tl = []
    prev_m_reg = 0
    for i, (st, t, is_h) in enumerate(reg_stops):
        raw_m = int(round(t * transit_reg + i * 0.6))
        cum_m = 0 if i == 0 else max(prev_m_reg + 1, raw_m)
        prev_m_reg = cum_m
        reg_tl.append((st, format_time_12h(start_mins + cum_m), cum_m))
        
    print(f"=== {o_name} -> {d_name} ({road_km} km) ===")
    print(f"  EXPRESS ({len(exp_tl)} stops): {exp_tl[0][1]} -> {exp_tl[-1][1]} ({exp_tl[-1][2]} mins) [Intermediates: {', '.join([s[0] for s in exp_tl[1:-1]])}]")
    print(f"  REGULAR ({len(reg_tl)} stops): {reg_tl[0][1]} -> {reg_tl[-1][1]} ({reg_tl[-1][2]} mins) [Time saved by Express: {reg_tl[-1][2] - exp_tl[-1][2]}m]")
    print()
