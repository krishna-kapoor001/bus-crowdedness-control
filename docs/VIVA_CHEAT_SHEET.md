# BusRoute — Presentation Cheat Sheet
## Delhi Transit Stack | Crowdedness-Aware Journey Planner

---

### Quick 30-Second Elevator Pitch
> *"BusRoute is a crowdedness-aware journey planner for Delhi commuters trained on 2.56 Million verified October 2026 ETM ticket records. While conventional planners only optimize for travel time, BusRoute predicts running onboard passenger occupancy across 2,259 DTC routes. For any trip, it provides 3 clear choices: the fastest trip with bottleneck alerts, a direct regular option, and a comfort option with guaranteed seating by shifting departure by just 15–20 minutes."*

---

### Top 8 Tricky Questions & Bulletproof Answers

#### Q1: "Data me 48.5% records me `vehicle_number` missing tha. Aapne bus trip count kaise nikala?"
* **Answer:**
  *"Sir, electronic app tickets aur QR code bookings me conductor ki ETM machine ID link nahi hoti, isliye 1.24 Million records me `vehicle_number` null tha. Agar hum naively vehicle number par group karte, toh aadha passenger ridership data drop ho jata. Humne data drop karne ke bajaye **Route Corridor + Sequential Stop Continuity + Hourly Temporal Windows** par aggregation ki. Isse zero data loss ke saath network-wide running passenger load accurately calculate hua."*

#### Q2: "Delhi me ladies ke liye ticket free hai aur pass-holders bhi hote hain. Unhe kaise model kiya?"
* **Answer:**
  *"Delhi me ladies ke liye Zero-Fare Pink Tickets conductor ETM machine se issue karta hai (`amount = 0.0`), jo raw dataset me 30.8% share rakhte hain — humne unhe valid 1-passenger boardings count kiya hai. Dusri taraf, monthly aur institutional pass-holders roz ticket nahi lete. Is under-reporting bias ko fix karne ke liye humne DIMTS empirical revenue audit ke base par **$\alpha = 1.15$ (15% expansion factor)** lagaya hai."*

#### Q3: "Aapka Machine Learning Model kaise train hua? Data Leakage kaise roka?"
* **Answer:**
  *"Humne random k-fold split use nahi kiya kyunki time-series me random split se future data leak ho jata hai. Humne **Strict Chronological Out-of-Time Split** lagaya:
  - **Train Set:** October 1 to October 24, 2026 (323,800 hourly observations)
  - **Test Set:** October 25 to October 31, 2026 (97,215 hourly observations)
  Hamara `HistGradientBoostingRegressor` model **3.007 pax/hour Test MAE** aur **0.750 $R^2$ score** achieve karta hai out-of-time test set par."*

#### Q4: "Running on-board load aur raw ticket boardings me kya farq hai?"
* **Answer:**
  *"Ek stop par 5 logon ka chadhna ye nahi batata ki bus kitni bhari hai. Bus ki bheed running occupancy par depend karti hai:
  $$\text{Load}_{s} = \max\left(0, \text{Load}_{s-1} + \text{Boardings}_s - \text{Alightings}_s\right) \times \alpha$$
  Agar pichhle 5 stops se log nahi utre hain, toh bus already crush capacity par hogi. BusRoute origin-destination pairs se running load compute karta hai."*

#### Q5: "12-meter Standard bus aur 9-meter Midi bus me crowding kaise different hoti hai?"
* **Answer:**
  *"A load of 50 passengers means **Standing Room Available** in a 12m low-floor bus (capacity 65: 35 seats + 30 standing), but the exact same 50 passengers is **Heavy Rush / Crush Load** in a 9m midi feeder bus (capacity 40: 24 seats + 16 standing). Hamara model route fleet classification (AC low-floor vs feeder) ke dynamic capacity thresholds use karta hai."*

#### Q6: "Agar kisi route par tickets bohot kam hain, toh estimate par kitna bharosa karein?"
* **Answer:**
  *"Sparse ticketing routes par prediction variance zyada hoti hai. BusRoute empirical confidence metric compute karta hai:
  $$\text{Confidence} = 100 \times \left(1 - \frac{\text{RMSE}}{\mu_{\text{route}} + \epsilon}\right)$$
  High-frequency trunk routes (e.g. 717A, 511A) par 88%–92% confidence score milta hai, jabki late-night sparse routes par system commuter ko 60%–70% confidence display karta hai."*

#### Q7: "Commuter ko is journey planner se kya practical benefit hota hai?"
* **Answer:**
  *"Problem 2 ke challenge example ke hisaab se: Agar koi commuter Anand Vihar se CP 18:00 baje jana chahta hai, toh fastest bus 45 min legi lekin middle corridor par bheed hogi. Hamara planner use 18:20 ka alternative dikhata hai jo sirf 2-3 minute zyada duration lega lekin confirmed seating milegi. Commuter ko fast vs comfortable trip ka clear, actionable choice milta hai."*

#### Q8: "Phase 1 me Static GTFS schedule ka kya role hai?"
* **Answer:**
  *"Static GTFS schedule stops aur routes ki geographical topology deta hai, lekin Delhi ke live traffic me bus schedule follow nahi hota. ETM data empirical ground-truth deta hai ki actual me kitne log chadh-utre. Dono ko combine karke humne transit network banaya jo real-world travel behavior represent karta hai."*
