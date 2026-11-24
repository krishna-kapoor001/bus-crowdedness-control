import sys, os
sys.path.insert(0, os.path.abspath('.'))

def format_time_12h(mins_from_midnight: int) -> str:
    mins = mins_from_midnight % (24 * 60)
    h = mins // 60
    m = mins % 60
    ampm = "PM" if h >= 12 else "AM"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12:02d}:{m:02d} {ampm}"

stops = ["Saket", "Hauz Khas", "IIT Gate", "Munirka Village", "R K Puram", "Dhaula Kuan"]
total_dur = 48
peak_load = 82
start_time_24 = "08:30"

h, m = map(int, start_time_24.split(':'))
start_mins = h * 60 + m
arr_mins = start_mins + total_dur
print(f"Departure: {format_time_12h(start_mins)} -> Arrival: {format_time_12h(arr_mins)} ({total_dur} mins)")

n = len(stops)
prev = 0
for i, s in enumerate(stops):
    prog = i / (n - 1)
    cum = int(round(total_dur * prog))
    t = format_time_12h(start_mins + cum)
    if i == 0:
        cur = int(peak_load * 0.55)
        act = f"Boarding (+{cur} pax)"
    elif i == n - 1:
        cur = 0
        act = f"All {prev} pax alight"
    else:
        if prog < 0.6:
            cur = int(peak_load * (0.6 + 0.4 * (prog / 0.6)))
        else:
            cur = int(peak_load * (1.0 - 0.5 * ((prog - 0.6) / 0.4)))
        diff = cur - prev
        act = f"Surge (+{diff})" if diff > 5 else (f"Alight (-{abs(diff)})" if diff < -5 else "Normal")
    print(f"  [{t} | +{cum:02d}m] {s:18} | Pax: {cur:2d}/65 | Action: {act}")
    prev = cur
