import sys, os
sys.path.insert(0, ".")
sys.path.insert(0, "backend")

from backend.app.services.journey_service import journey_service

def compute_accurate_timeline(stops_with_meta, start_time_24, road_km, is_express, is_peak):
    # Base speeds in km/h
    if is_peak:
        base_speed = 24.0 if is_express else 17.5
    else:
        base_speed = 28.0 if is_express else 22.0
    
    # Dwell per stop in mins
    dwell_hub = 1.0 if is_express else 1.2
    dwell_reg = 0.4 if is_express else 0.6
    
    n = len(stops_with_meta)
    
    # 1. Calculate physical leg distances using actual stop coordinates
    coords = []
    for s_name, is_hub in stops_with_meta:
        s_info = journey_service.stops_meta.get(s_name, {})
        coords.append((s_info.get('latitude', 0), s_info.get('longitude', 0)))
    
    raw_cum_dists = [0.0]
    total_raw_dist = 0.0
    for i in range(1, n):
        lat1, lon1 = coords[i-1]
        lat2, lon2 = coords[i]
        if lat1 != 0 and lat2 != 0:
            hop = journey_service._haversine(lat1, lon1, lat2, lon2) * 1.20
        else:
            hop = road_km / (n - 1)
        total_raw_dist += hop
        raw_cum_dists.append(total_raw_dist)
    
    # Normalize cumulative distance to road_km
    final_cum_dists = []
    for i in range(n):
        if total_raw_dist > 0:
            scaled = (raw_cum_dists[i] / total_raw_dist) * road_km
        else:
            scaled = (i / (n - 1)) * road_km if n > 1 else 0.0
        final_cum_dists.append(round(scaled, 1))
    
    # 2. Compute exact minutes for each stop
    try:
        h, m = map(int, start_time_24.split(':'))
        start_mins = h * 60 + m
    except Exception:
        start_mins = 8 * 60 + 30
        
    cum_mins = 0.0
    timeline = []
    
    for i in range(n):
        s_name, is_hub = stops_with_meta[i]
        if i == 0:
            stop_mins = 0
        else:
            prev_d = final_cum_dists[i-1]
            curr_d = final_cum_dists[i]
            hop_d = max(0.2, curr_d - prev_d)
            # transit time for this hop
            transit_time = (hop_d / base_speed) * 60.0
            # previous stop dwell
            prev_hub = stops_with_meta[i-1][1]
            dwell = dwell_hub if prev_hub else dwell_reg
            cum_mins += transit_time + dwell
            stop_mins = max(timeline[-1]['mins'] + 1, int(round(cum_mins)))
            
        time_label = journey_service._format_time_12h(start_mins + stop_mins)
        timeline.append({
            'stop': s_name,
            'is_hub': is_hub,
            'km': final_cum_dists[i],
            'mins': stop_mins,
            'time': time_label
        })
        
    return timeline

# Test Saket -> Dhaula Kuan
reg_t, exp_t = journey_service._resolve_corridor_stops("Saket", "Dhaula Kuan", 12.7)
exp_timeline = compute_accurate_timeline([(s[0], s[2]) for s in exp_t], "08:30", 12.7, True, True)
reg_timeline = compute_accurate_timeline([(s[0], s[2]) for s in reg_t], "08:30", 12.7, False, True)

print("=== SAKET -> DHAULA KUAN EXPRESS (12.7 KM) ===")
for st in exp_timeline:
    print(f"  {st['time']} (+{st['mins']:02d}m, {st['km']:4.1f} km) | {st['stop']}")

print("\n=== SAKET -> DHAULA KUAN REGULAR (12.7 KM) ===")
for st in reg_timeline:
    print(f"  {st['time']} (+{st['mins']:02d}m, {st['km']:4.1f} km) | {st['stop']}")
