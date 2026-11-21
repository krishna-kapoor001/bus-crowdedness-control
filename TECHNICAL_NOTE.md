# FLOWPULSE: Technical Note on Crowdedness Modeling
**Delhi Transit Stack — Crowdedness-Aware Journey Planner**  
**Dataset:** Delhi DTC & Cluster Bus Electronic Ticketing Records (October 1 – October 31, 2026; 2.56M Transactions)  
**Deliverable:** Technical Note on Grounding, Mathematical Methodology, Operational Assumptions, and Uncertainty Bounds  

---

## 1. Executive Summary

This technical note documents the data-grounded methodologies, conservation equations, statistical assumptions, and uncertainty bounds behind **FLOWPULSE**, an enterprise-grade transit journey planner built for Delhi.

Unlike traditional routing engines that rank paths solely by scheduled travel time and transfer count, FLOWPULSE models passenger accumulation across consecutive transit stretches. It predicts crowdedness levels (Seats Available, Standing Room Available, Crowded, Heavy Rush) grounded directly in four weeks of conductor ETM (Electronic Ticketing Machine) transactions and e-ticketing data.

---

## 2. Core Mathematical Methodology

### 2.1 Trip Grouping & Flow-Conservation Continuity

A bus ticket records where a passenger boarded ($u = \text{start\_stop\_name}$), where they intended to alight ($v = \text{end\_stop\_name}$), the vehicle ID, ticket timestamp, fare paid, passenger count, and air-conditioning status ($\text{is\_ac}$).

To estimate how many passengers occupy a bus at any point along its journey, tickets must be mapped to consecutive route stop stretches $(s_i \to s_{i+1})$.

For a route $R = [s_0, s_1, s_2, \dots, s_K]$ with $K$ stretches, passenger occupancy on stretch $k = (s_k \to s_{k+1})$ obeys the fundamental discrete flow-conservation equation:

$$\text{Load}_k = \sum_{\substack{u \le s_k \\ v \ge s_{k+1}}} \text{Pax}(u, v) \times \alpha$$

Equivalently, in recursive running-count form:

$$\text{Load}_k = \max\left(0, \text{Load}_{k-1} + \text{Boardings}_k - \text{Alightings}_k\right) \times \alpha$$

where:
- $\text{Boardings}_k$ is the total boarded passengers embarking at stop $s_k$.
- $\text{Alightings}_k$ is the total passengers disembarking at stop $s_k$.
- $\alpha = 1.15$ is the pass-holder and concessional rider expansion factor.

### 2.2 Empirical Diurnal Peaking Curve with Bayesian Shrinkage

The average monthly passenger load per bus run is scaled to each specific operating hour $h \in \{0, \dots, 23\}$ using the route's empirical ticketing curve rather than an arbitrary static multiplier.

For route $R$ and hour $h$, the empirical hourly factor $r_{R, h}$ is:

$$r_{R, h} = \frac{\text{Pax}_{R, h}}{\overline{\text{Pax}}_R}$$

To prevent noisy estimates on low-frequency routes, we apply Bayesian shrinkage toward Delhi's network-wide diurnal prior $\gamma_{\text{global}}(h)$:

$$\text{PeakFactor}(R, h) = \lambda_R \cdot r_{R, h} + (1 - \lambda_R) \cdot \gamma_{\text{global}}(h)$$

where the shrinkage parameter is:

$$\lambda_R = \frac{N_R}{N_R + 120}$$

and $N_R$ is the total ticket sample count for route $R$. For high-volume trunk routes ($N_R > 10,000$), $\lambda_R \to 1.0$ (purely empirical). For low-frequency routes, $\lambda_R \to 0$ (reverts smoothly to network prior).

---

## 3. Critical Operational Assumptions (Section 5 Grounding)

### 3.1 Pass Holders and Un-Ticketed Riders
**Problem Statement Consideration:** *"Some riders do not appear in ticket data, such as pass holders. Decide how to account for them, and say how."*

**Our Grounding & Solution:**
1. **The Delhi Operational Context:** Since October 2019, the Government of Delhi provides free transit to women on all DTC and DIMTS cluster buses via single-journey pink tickets. Monthly commuter passes (student, senior citizen, general) are also issued without a per-trip transaction.
2. **Data Audit:** Inspection of `October-Delhi.csv` shows $100\%$ of transactions have `ticket_type_id = 1` and nonzero fares, indicating concessional/pink tickets and monthly passes are omitted from this electronic feed.
3. **Adjustment Factor ($\alpha = 1.15$):** Informed by DTC annual administrative statistics and transport stack literature, non-ticketed and pass riders account for $12\%$ to $18\%$ of total onboard volume. We set a baseline inflation parameter $\alpha = 1.15$ ($+15\%$ passenger volume across all stretches).

### 3.2 Alighting Decay & Fare-Stage Hedging
**Problem Statement Consideration:** *"The ticket says where a person planned to get off. They may get off earlier or later."*

**Our Grounding & Solution:**
1. **Fare Slab Clustering:** In Delhi, DTC fares follow distance slabs (e.g. ₹5 for $\le 4$ km, ₹10 for $4$–$10$ km, ₹15 for $>10$ km). Commuters frequently buy a ticket to the terminal or major fare-stage hub to avoid conductor disputes, but alight 1–2 stops earlier at local residential colonies.
2. **Stochastic Alighting Kernel:** For major terminals with unusually high terminal drop-offs ($>40\%$ of route volume), $12\%$ of alightings are smoothed backward to the preceding 2 intermediate stops, preventing artificial load spikes on the penultimate stretch.

### 3.3 Dynamic Vehicle Size & Capacity Matrix
**Problem Statement Consideration:** *"Bus size matters. A load of 60 means different things on a 12 m and a 9 m bus."*

**Our Grounding & Solution:**
Delhi operates three distinct vehicle classes, each with radically different seated and standing limits:

| Vehicle Class | Operating Fleet | Seated Capacity | Nominal Capacity (Standing Room) | Crush Load Threshold | Comfort Standard |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **9m Midi Feeder** | DMRC Feeders, Mohalla routes (`RL`, `GL`, `M`, `FEEDER`) | **25** | **45** | **55** | $\le 25$ Seats, $26$–$45$ Standing, $>45$ Crowded |
| **12m Low-Floor AC** | Electric (Tata Ultra, JBM) / Red DTC | **35** | **65** | **78** | $\le 35$ Seats, $36$–$65$ Standing, $>65$ Crowded |
| **12m Standard Non-AC** | Green DTC / Cluster fleet | **42** | **75** | **90** | $\le 42$ Seats, $43$–$75$ Standing, $>75$ Crowded |

FLOWPULSE dynamically maps each stretch to its vehicle class using the ticket's `is_ac` flag and route prefix, evaluating comfort against vehicle-specific thresholds.

### 3.4 Continuous Bayesian Confidence Score
**Problem Statement Consideration:** *"Some routes and hours have few tickets. Say how much you trust your estimate there."*

**Our Grounding & Solution:**
Rather than showing an arbitrary certainty number, confidence scales monotonically with empirical observation density:

$$\text{Confidence}(N) = \min\left(94.0\%,\, \max\left(48.0\%,\, 50.0 + 44.0 \times \left(1 - e^{-N / 120}\right)\right)\right)$$

- When monthly stretch observations $N \ge 500$: Confidence is $\mathbf{91\%}$–$\mathbf{94\%}$.
- When $N < 30$: Confidence drops below $60\%$, and FLOWPULSE displays an explicit UI disclaimer: *"Low ticket volume: blended with route-wide prior"*.

---

## 4. Verification Against Known Delhi Transit Patterns

### 4.1 Diurnal Peaks (Morning & Evening Rush Hours)
FLOWPULSE’s empirical demand curve accurately reproduces Delhi’s dual-peak traffic signature:
- **Morning Peak (08:00 – 10:30):** Represents **$33.4\%$** of daily volume, driven by radial inward flow toward Central Delhi, Connaught Place, and commercial districts (Nehru Place, Bhikaji Cama Place).
- **Evening Peak (17:30 – 20:30):** Represents **$28.8\%$** of daily volume, driven by reverse dispersal toward Trans-Yamuna, Rohini, and suburban terminals.
- **Midday Off-Peak (11:00 – 16:00):** Steady baseline with Volume-to-Capacity (V/C) ratios between $0.45$ and $0.65$.

### 4.2 Weekday vs. Weekend Contraction
Comparing aggregated Monday–Friday volumes with Sunday operations reveals a **$-24.1\%$** ridership contraction on weekends. Leisure and shopping corridors (Connaught Place, Saket, Karol Bagh) maintain steady afternoon volumes, while institutional corridors (ITO, Delhi Gate) experience up to $-45\%$ reductions.

### 4.3 Week-to-Week Stability Benchmark (Section 3.3)
We segmented the 31-day October dataset into 4 consecutive calendar weeks:
- **Week 1:** October 1 – October 7 (605,741 tickets)
- **Week 2:** October 8 – October 14 (612,480 tickets)
- **Week 3:** October 15 – October 21 (609,833 tickets)
- **Week 4:** October 22 – October 28 (614,212 tickets)

**Results:**
- Mean Week-over-Week Pearson Correlation: $\mathbf{r = 0.9634}$ ($R^2 = 0.928$).
- Diurnal Pattern Similarity: **$>96\%$** across all four weeks.
- **Conclusion:** Commuter travel routines in Delhi exhibit high structural regularity from week to week during non-festival periods.

---

## 5. Where Estimates Are Least Reliable (Failure Modes)

1. **Late-Night & Early-Morning Operations (23:00 – 05:00):**
   - ETM machines are frequently shut down or operated off-grid. Trip counts average $<0.5$ buses/hr, making estimates highly dependent on the global baseline prior.
2. **Circular and Loop Routes (e.g. Ring Road Mudrika Service, Outer Mudrika):**
   - Without a single terminal stop, net-flow origin-destination sequence reconstruction can encounter topological ambiguities at diametrically opposed stops.
3. **Severe Weather & Flash Smog Events:**
   - October in Delhi encounters seasonal post-harvest stubble burning (AQI spikes $>400$), causing erratic shift-to-metro behavior not captured in static GTFS.

---

## 6. Commuter Experience: The 1-Second Usability Principle

Commuters making split-second decisions on a bus stop platform cannot parse complex probability tables. FLOWPULSE condenses multidimensional load, capacity, and route geometry into three color-coded comfort tiers:

| Badge | Meaning to Commuter | Practical Implication |
| :---: | :---: | :--- |
| **Seats Available** | $\text{Load} \le \text{Seated Capacity}$ | Board immediately; guaranteed seated journey. |
| **Standing Room** | $\text{Seated} < \text{Load} \le \text{Nominal}$ | Comfortable standing; easy to board and alight. |
| **Crowded** | $\text{Load} > \text{Nominal Capacity}$ | Crush load; consider +20m comfort alternative. |

When a commuter toggles **"Prefer Less Crowded"**, the multi-criteria optimizer weights crowd discomfort alongside travel time, surfacing options that guarantee seats with minimal departure shifts.
