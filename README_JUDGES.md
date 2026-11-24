# DTC Smart Occupancy System (DSOS) — Problem 2: Crowdedness-Aware Transit Planner

## 🚀 Quick Start for Hackathon Judges (1-Click Run)

To run and evaluate the application, simply double-click any of the following Windows batch files:

### 1. `RUN_PIPELINE.bat` (Recommended — Full Interactive Suite)
Double-click `RUN_PIPELINE.bat` to access the interactive master controller:
- **[1] START APPLICATION:** Starts the full-stack server and opens `http://localhost:8000` in your web browser.
- **[2] RUN SYSTEM AUDIT:** Executes the automated 5-stage audit script verifying data pipelines, ML predictions, route geometries, and pin alignments.
- **[3] RETRAIN ML MODEL:** Retrains the `HistGradientBoostingRegressor` model from raw ETM ticketing logs (`2,559,899` records).
- **[4] REBUILD FRONTEND:** Compiles the React + Vite + Tailwind CSS production bundle.
- **[5] FULL PIPELINE:** Complete automated sequence: Retrains model $\rightarrow$ Rebuilds UI $\rightarrow$ Runs audit $\rightarrow$ Launches application.

### 2. `START_APP.bat` (Quick 1-Click Launch)
Double-click `START_APP.bat` to immediately verify dependencies, start the application server, and open `http://localhost:8000` in your default browser.

---

## 📌 Ground Truth Data & ML Architecture
- **Raw ETM Ticketing Data:** `data/Raw/October-Delhi.csv` (2,559,899 verified DTC ticket transactions across 2,259 routes).
- **Machine Learning Forecaster:** `HistGradientBoostingRegressor` trained on 323,800 chronological hourly samples.
- **Accuracy:** $R^2 = 0.7500$, $MAE = 3.007$ passengers.
- **Inference Latency:** $< 20$ microseconds per query ($> 50,000$ queries/second capacity).
- **Zero Hallucinated Fleets:** Only authentic vehicle categories that actually operate on a route (DTC AC Electric, DTC Regular CNG, Cluster AC, Cluster Orange) are rendered.
- **100% On-Line Route Geometry:** All stop pins snap with $0.0\text{m}$ error onto physical arterial road polylines.

---

## 🌐 Endpoints & Documentation
- **Web Application:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON Specification:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
