# FLOWPULSE: Intelligent Public Transportation Platform
**Tagline:** *Understand Crowd. Predict Demand. Travel Smarter.*  
**Delhi Transit Stack — Crowdedness-Aware Journey Planner**  

---

> [!IMPORTANT]
> **EVALUATORS:** See [JUDGES_GUIDE.md](file:///c:/LEFP/BUS/Transport%20Delhi/JUDGES_GUIDE.md) and [TECHNICAL_NOTE.md](file:///c:/LEFP/BUS/Transport%20Delhi/TECHNICAL_NOTE.md) for the complete evaluation breakdown, mathematical grounding proofs, operational assumptions, and 1-click execution.
> 
> **1. To Re-run the Entire Pipeline from Scratch (76s end-to-end):**
> ```powershell
> python scripts/run_pipeline.py
> ```
> *(Or double-click `run_pipeline.bat` on Windows)*
> 
> **2. To Launch the Full-Stack Application:**
> ```powershell
> python run.py
> ```
> *(Or double-click `start_app.bat` on Windows — Open **http://localhost:8000**)*
> 
> **3. To Run the Automated Test Suite:**
> ```powershell
> python scripts/test_backend.py
> ```
> *(Or double-click `run_tests.bat` on Windows)*

---

## 1. System Architecture Overview

FLOWPULSE is an enterprise-grade transit analytics and crowdedness-aware routing platform powered by the official October 2026 Delhi ETM (Electronic Ticketing Machine) dataset (2,559,897 verified ticket transactions across 2,259 bus routes and 1,619 stop names).

```
+-----------------------------------------------------------------------------------------+
|                                  FLOWPULSE CLIENT (SPA)                                 |
|               React 18 + Vite + Tailwind CSS + Lucide Icons + Leaflet Maps              |
+-----------------------------------------------------------------------------------------+
|  Overview  |  Journey Planner  |  Network Explorer  | Operator Analytics | CrowdShift   |
|  Dashboard | (Crowd Optimizer) |    (Leaflet Map)   | (Fleet Overload)   | (Simulator)  |
+-----------------------------------------------------------------------------------------+
                                           |  REST API / JSON
                                           v
+-----------------------------------------------------------------------------------------+
|                                    FASTAPI CORE ENGINE                                  |
|                         (Python 3.12 + SQLAlchemy 2.0 + Pydantic)                       |
+-----------------------------------------------------------------------------------------+
|  /api/v1/overview         -> Network KPIs, peak load distribution, corridor heatmaps    |
|  /api/v1/journey/plan     -> Multi-criteria pathfinding with stretch crowding profiles |
|  /api/v1/analytics        -> Hourly, weekday vs weekend, route and stop level drilldown |
|  /api/v1/network          -> Vector stops, arterial polylines, corridor velocity        |
|  /api/v1/simulation/shift -> CrowdShift counterfactual demand impact simulation         |
|  /api/v1/models/info      -> Chronological validation benchmarks & uncertainty bounds   |
+-----------------------------------------------------------------------------------------+
          |                                                   |
          v                                                   v
+-----------------------------+          +------------------------------------------------+
|    RELATIONAL PERSISTENCE   |          |           PREDICTIVE & ROUTING ENGINES         |
|  SQLAlchemy Database Engine |          +------------------------------------------------+
| (PostgreSQL / SQLite layer) |          | 1. Grounded Cumulative Onboard Continuity      |
| - Routes & Stops entities   |          |    Load = max(0, Load_{-1} + B - A) * 1.15     |
| - 50,000+ hourly demand rows|          | 2. Demand Forecaster: HistGradientBoosting     |
| - Model evaluation metrics  |          | 3. Multi-criteria routing engine (NetworkX)    |
+-----------------------------+          +------------------------------------------------+
```

---

## 2. Directory Structure & Key Files

```
Transport Delhi/
├── requirements.txt            # Complete Python dependencies
├── run_pipeline.bat           # 1-click Windows pipeline re-runner
├── start_app.bat              # 1-click Windows web app launcher
├── run_tests.bat              # 1-click Windows test suite runner
├── JUDGES_GUIDE.md            # Comprehensive evaluation guide
├── run.py                     # Single-command full-stack production server
├── backend/
│   └── app/
│       ├── config.py          # Environment configuration & DB connection URL
│       ├── database.py        # SQLAlchemy engine, sessionmaker & Base
│       ├── main.py            # FastAPI initialization, CORS, routers & static SPA mount
│       ├── models/
│       │   └── entities.py    # Stop, Route, HourlyDemand, ModelEvaluation, Simulation entities
│       ├── schemas/
│       │   └── schemas.py     # Pydantic request/response schemas
│       ├── services/
│       │   ├── journey_service.py # Grounded routing with stretch crowding profiles
│       │   ├── demand_service.py  # Overview KPIs, corridor heatmaps, hourly trend curves
│       │   ├── ml_service.py      # Demand forecaster, crowd classifier & uncertainty bounds
│       │   └── simulation_service.py # CrowdShift V/C elasticity counterfactual simulator
│       └── routers/
│           ├── overview.py    # /api/v1/overview
│           ├── journey.py     # /api/v1/journey/plan, /stops, /routes
│           ├── analytics.py   # /api/v1/analytics/hourly, /routes, /stops
│           ├── network.py     # /api/v1/network/geojson, /corridors
│           ├── simulation.py  # /api/v1/simulation/shift
│           └── models_info.py # /api/v1/models/info
├── data/
│   ├── Raw/
│   │   └── October-Delhi.csv  # 2.56M raw Delhi ETM ticket transactions
│   ├── processed/
│   │   ├── stretch_crowd_profiles.json # 48,418 grounded stretch crowd profiles
│   │   ├── route_stop_sequences.json   # 1,238 authentic route stop sequences
│   │   └── transit_graph_edges.json    # Consecutive transit graph edges
│   └── flowpulse.db           # SQLite relational database
├── frontend/
│   ├── dist/                  # Built production SPA assets (served by backend)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx    # Commuter & Transit Planner navigation
│   │   │   └── StatusBadge.jsx# Commuter comfort badges
│   │   ├── pages/
│   │   │   ├── Overview.jsx   # KPIs, 24-hr Demand Curve, Peak rush comparison
│   │   │   ├── JourneyPlanner.jsx # Crowdedness-aware routing with 3 alternatives
│   │   │   ├── NetworkExplorer.jsx # Leaflet map with 1,619 stops & 28 corridors
│   │   │   ├── OperatorAnalytics.jsx # Fleet overload, extra buses, hub flow imbalance
│   │   │   ├── CrowdShift.jsx # Interactive policy & elasticity simulator
│   │   │   └── Methodology.jsx# Mathematical formulations & live ML benchmarks
│   │   └── App.jsx            # Router and application state
│   └── package.json
├── scripts/
│   ├── run_pipeline.py        # Master 1-click end-to-end pipeline runner
│   ├── compute_grounded_crowding.py # Continuous onboard load & stretch continuity
│   ├── train_model.py         # Chronological split training and evaluation
│   ├── seed_database.py       # Table creation and data seeding
│   └── test_backend.py        # Comprehensive test suite for all endpoints
└── docs/
    └── TECHNICAL_NOTE.md      # Full mathematical note & methodology
```

---

## 3. Mathematical Grounding & Continuity Model

To compute true on-board bus occupancy along each route stretch rather than raw ticket sales, FLOWPULSE formulates a cumulative passenger continuity model across authentic sequenced bus stops:

$$Load(s_i \to s_{i+1}) = \max\left(0, Load(s_{i-1} \to s_i) + \text{Boardings}(s_i) - \text{Alightings}(s_i)\right) \times \alpha$$

Where:
- $\text{Boardings}(s_i)$: Verified ETM ticket issuances originating at stop $s_i$.
- $\text{Alightings}(s_i)$: Passengers whose ticket destination (`end_stop_name`) is stop $s_{i+1}$ or later.
- $\alpha$: Pass-holder expansion coefficient ($\alpha = 1.15$).

### Commuter Comfort Tiers (12m Standard Bus — 35 Seats, 65 Capacity):
- $Load \le 35$ pax: **Seats Available** (LOW)
- $35 < Load \le 65$ pax: **Standing Room Available** (MODERATE)
- $65 < Load \le 80$ pax: **Crowded (Standing Only)** (HIGH)
- $Load > 80$ pax: **Heavy Rush (Crush Load)** (VERY HIGH)

---

## 4. Machine Learning & Chronological Benchmark

- **Model:** `HistGradientBoostingRegressor` (L2 Regularized Tree Ensemble)
- **Validation Split:** Chronological (Oct 1–24 Train / Oct 25–31 Test, 0.00 Data Leakage)
- **Test MAE:** **3.007 pax/hour**
- **Baseline Historical Median MAE:** **2.713 pax/hour**
- **Out-of-Time $R^2$:** **0.750**
- **Residual Standard Deviation $\sigma$:** **5.074 pax/hour**

---

## 5. How to Run the Entire Application

### Option A: Unified Full-Stack Production Server (Recommended)
```powershell
python run.py
```
*(Or double-click `start_app.bat` on Windows)*
- Open browser at: **`http://localhost:8000`**
- Interactive Swagger API docs: **`http://localhost:8000/docs`**

### Option B: Development Mode (Vite Hot-Reload + FastAPI)
Terminal 1 (Backend):
```powershell
python -m uvicorn backend.app.main:app --port 8000 --reload
```
Terminal 2 (Frontend):
```powershell
cd frontend
npm run dev
```
- Open browser at: **`http://localhost:5173`**
